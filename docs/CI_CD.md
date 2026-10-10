# CI/CD pipeline

This note describes the automated checks and builds that run on GitHub for BuildScan 3D: what runs, when, how to read the results, how to run the same checks on your own PC, and what the pipeline does not cover. The workflow files are in `.github/workflows/`.

## 1. Why we have it

Three of us push to the same repository: an Android app, a Next.js web UI and a GPU reconstruction pipeline. Without automation, a change in one part can break another part and nobody notices until a demo. The pipeline checks every change on a clean machine, so the result does not depend on whose laptop it was written on.

- **CI (continuous integration):** on every push and pull request, GitHub lints and tests the Python code, builds the web UI, builds the Android app, and checks the repository for files that should not be committed.
- **CD (continuous delivery):** when code reaches `master`, GitHub runs the full CI again and then produces the deliverables (web UI bundle and Android APK). When we push a version tag such as `v0.1.0`, it also publishes a GitHub Release with both files attached.

## 2. Pipeline overview

```
push to any branch except master ─┐
pull request ─────────────────────┼─> ci.yml
manual run ───────────────────────┘     │
                                        ├─ changes        which areas were touched?
                                        ├─ python         lint + unit tests (3.10, 3.11, 3.12)
                                        ├─ web-ui         npm ci, lint, type check, production build
                                        ├─ android        Gradle assembleDebug -> APK
                                        ├─ repo-hygiene   size limit, no datasets/keys, no obvious secrets
                                        ├─ workflow-lint  checks these workflow files themselves
                                        └─ ci-ok          one pass/fail status for everything

push to master / tag v* / manual ──> cd.yml
                                        ├─ ci             full CI (all jobs forced on)
                                        ├─ build-web      web-ui-build.tar.gz artifact
                                        ├─ build-android  buildscan3d-<commit>.apk artifact
                                        └─ release        (tags only) GitHub Release with both files
```

Details of the design:

- **Only relevant jobs run.** The `changes` job checks which folders changed. A documentation-only pull request does not rebuild the Android app. Changing a workflow file runs everything. CD always runs everything.
- **Old runs are cancelled.** If I push again to the same branch while a run is in progress, the older run is cancelled (`concurrency`).
- **Caching.** pip, npm, Gradle and the Next.js build cache are cached between runs, so most runs are much faster than the first.
- **One status to watch.** `CI passed` is green only if no job failed. Skipped jobs (nothing changed there) count as fine. It is the check to mark as *required* in branch protection.
- **Least privilege.** Workflows start with read-only access to the repository. Only the release job gets write access, and only on tags.
- **Reports are kept.** Python test reports (14 days), the Android APK (14 days in CI, 30 days in CD) and the web bundle (30 days) are downloadable from the run page under *Artifacts*.

## 3. What each job checks

| Job | Checks | Fails when |
|---|---|---|
| python | `ruff` for real errors only (syntax errors, undefined names); unused code is reported as a non-blocking warning; `pytest` | an error is found or a test fails |
| web-ui | `npm ci` (exactly the locked versions), ESLint, `tsc --noEmit`, `next build` | lint error, type error or build failure |
| android | official Gradle wrapper check, `./gradlew assembleDebug` | the app does not compile |
| repo-hygiene | no tracked file over 10 MB (the ARCore samples and `docs/Research Papers` are exempt), no `.ply`/`.mp4`/`.pt`/`.pth`/`.ckpt`/`.npz`/key files, no private keys or access tokens | a rule is broken |
| workflow-lint | `actionlint` over the workflow files | a workflow file has an error |

### What the Python tests cover

The reconstruction scripts need a CUDA GPU, which GitHub's free machines do not have, so CI cannot train or run Metric3D. It tests the CPU-side logic that the whole pipeline depends on, using small synthetic captures:

- `tests/test_common_capture.py`: pose interpolation between samples, no pose outside the recorded range or inside a tracking gap, unsorted and duplicate pose rows, intrinsics, frame time offset, NaN feature points, and the tracking-loss intervals that the pipeline uses to skip unreliable frames.
- `tests/test_common_project.py`: the world-to-pixel projection and the OpenGL to OpenCV axis flip, including points behind the camera or outside the image.
- `tests/test_process_dataset.py`: `process_dataset.py` run end to end on a generated 20-frame video (frames, `transforms.json`, pose matching) and the PLY export.
- `tests/test_sources_compile.py`: every Python file under `src/`, `scratch/` and `tests/` compiles, so a syntax error in a script that only runs on the GPU PC is still caught.

## 4. Running the same checks locally

Python (from the repository root):

```
python -m pip install -r tests/requirements.txt
ruff check .
pytest
```

Web UI:

```
cd prototype/web-ui
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

Android: open `googleARCore/samples/hello_ar_java` in Android Studio, or run `./gradlew assembleDebug` there with JDK 17.

## 5. Branching and review

- `master` is the stable branch. Nobody works directly on it.
- Work happens on short-lived branches named by purpose: `feature/...`, `fix/...`, `exp/...` for experiments, `ci/...`, `docs/...`.
- A change reaches `master` through a pull request. The pull request template (`.github/pull_request_template.md`) lists what to check. The `CI passed` check has to be green before merging.
- Releases are made by tagging `master`, for example `git tag v0.1.0 && git push origin v0.1.0`. CD then builds everything and attaches it to a GitHub Release.

## 6. One-time settings that the repository owner has to make

These are GitHub settings, not files, so they cannot be committed:

1. **Actions enabled** for the repository (Settings, Actions, General).
2. **Branch protection on `master`** (Settings, Branches): require a pull request, require the `CI passed` status check, and optionally one approving review. This is what makes the pipeline a gate and not just a report.
3. **Workflow permissions** (Settings, Actions, General): allow GitHub Actions to create releases (read and write for the release job). The workflows request only the permissions they need.
4. For dependency updates, Dependabot (`.github/dependabot.yml`) opens at most a few monthly pull requests. It is optional and can be deleted.

## 7. Limits and honest notes

- **Not run on GitHub yet.** The workflow files pass `actionlint`, and the Python, lint and web UI steps pass when run locally (section 4). The Android job has not been run anywhere yet because it needs the Android SDK, so it is the most likely to need a small fix after the first run on GitHub.
- **No GPU stages.** Training, Metric3D, bundle adjustment on real data and the viewer are not run in CI. Their results are documented in `docs/Problems_and_Solutions.md` and the experiment notes.
- **Only the Python scripts' building blocks are tested.** Most of `src/arcore3dgs` runs its logic at the top level of a script, so it cannot be imported by a test. Moving that logic into functions would let us test more.
- **The Android sample has no unit tests** in this repository yet; CI only proves that it compiles.
- **CD does not deploy to a server.** The web UI uses server-side rendering, so it cannot be published as static pages. Delivery means a downloadable bundle (`npm ci --omit=dev && npm start`) and a release. Deploying to a hosting service later needs an account or tokens that the repository owner controls.
- **The job names** (`Python 3.10 (lint + tests)`, `Web UI (...)`, and so on) appear in the checks list of every pull request.

## 8. Reading a run

Open the repository on GitHub, then **Actions**. Each row is one run, with a green tick or a red cross. Click it to see the jobs, click a job to see the log of each step, and scroll down for **Artifacts**. For a pull request, the same checks appear at the bottom of the pull request page.
