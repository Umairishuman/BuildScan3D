# BuildScan 3D app: changelog

What changed in each app release. **Every pull request that changes the app adds its lines under "Unreleased"**,
written for the person using the app (what they will notice), one line per change. At the release, CD
(`.github/workflows/cd.yml`, `.github/android/changelog.py`) turns "Unreleased" into the new version's entry, and that
text becomes the GitHub release notes, which the app shows in its update dialog and after an update ("What's new").
Entries up to v0.3.6 were written on 2026-11-12 from the git history and docs/progress/LOG.md.

## Unreleased

- While recording, the coverage dots stay fixed on the surfaces they mark and move smoothly with the camera image; before, they were redrawn only twice a second, so they lagged behind the image and seemed to float.
- Coverage dots are hidden while tracking is lost, instead of being drawn in the wrong place.
- The ARCore feature dots on the camera screen build up into a steady map: each point appears once ARCore has seen it a few times, stays when the camera looks away, and disappears again if its position jumps. Before, the screen showed only the handful of points from the latest update, so dots were often missing, flickered or floated away. The dots are also larger.
- Raw depth maps are saved with the time and pose of the camera frame they were measured on (new `depth/timestamps.csv` shows how each one was paired), so processing places them correctly.

## v0.3.7 · 2026-11-12

- The app checks for updates when it starts and whenever you come back to it (at most every 6 hours, never while recording), and the update dialog lists what changed.
- After an update the app shows once what is new in the installed version.
- After you allow BuildScan 3D to install updates in Android settings, the update installs without checking again.
- Recordings are numbered 1, 2, 3 on the PC; after an upload the app says "Saved on the PC as scan #N" (D-065).
- The tracking message appears only in the quality banner at the top; the bar at the bottom that repeated it and covered the navigation is gone.
- The quality check records how long it takes for every frame (`iqa_ms` in `quality.csv`), to measure NFR2.

## v0.3.6 · 2026-11-12

- Upload over a USB cable (much faster than Wi-Fi), tried first when the cable is plugged in; connection bar on the Scans screen, upload speed and time left, automatic restart after a lost connection (D-062).
- New light look from the logo, with a bottom bar for Capture, Scans and Server; new Server tab (D-064).
- Uploads check the files and the connection before they start, and can be stopped (D-064).
- The app code moved to `android/` with its own package (D-063).

## v0.3.5 · 2026-11-12

- Uploads now include `camera.csv`, `anchors.csv` and the lens files (exposure times and ARCore corrections for processing).

## v0.3.4 · 2026-11-06

- Finds the server on large networks; downloads and installs updates inside the app.
- Own package name `com.buildscan3d.app` and a private release key (D-058, D-059): installs next to older versions, which are not replaced.

## v0.3.3 · 2026-11-06

- Demo pawn / Instant Placement removed from the capture screen; clearer motion-blur messages from the quality check.
