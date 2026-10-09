@AGENTS.md

@STATUS.md

---

# MANDATORY: Keep `STATUS.md` current

`STATUS.md` (imported above, so it is already in your context) is the handoff document that
lets a new session pick up this build without re-deriving anything. It is only useful if it
stays accurate.

## Read it first

Before writing any code, read **§2 Locked Decisions** and **§5 Next Steps** in `STATUS.md`.
Section 2 records choices the user has already made — several of them deliberately contradict
`../POC_requirements.md` and the reference design PNG. **Do not "correct" a locked decision
back toward the spec.** If the spec and `STATUS.md` §2 disagree, §2 wins; ask the user if you
think it is genuinely wrong.

## Update it at the end of every step

Updating `STATUS.md` is part of the definition of done for a step — not an optional extra, and
not something to defer to the end of the session. Before you report a step complete, you must:

1. Move the finished step from §5 (Next Steps) into §4 (Completed), recording the **actual**
   files created and modified and the **actual** verification output you got.
2. Update §7 (Screen map status) and mark the new "◀ NEXT" step in §5.
3. Add any new debt, dead code, or non-functional control to §6 (Known Issues).
4. If the user made a design or architecture call during the step, add it to §2 (Locked
   Decisions) with a one-line reason. This is the highest-value part of the file.
5. Bump "Last updated" at the top and append a line to §8 (Changelog).

Do this even for small steps, and even if the user did not ask. If a step is abandoned or only
partly done, say so explicitly in `STATUS.md` rather than leaving it looking finished.

## Working agreement (also recorded in `STATUS.md` §0)

- Build **strictly one component at a time**; do not batch screens together.
- **Never invent missing files or assets.** If something referenced does not exist, stop and
  ask the user rather than fabricating a path or a placeholder.
- Review the existing code first and **match and elevate** the established design system
  instead of introducing a parallel one.
- Verify before reporting done — `npx tsc --noEmit`, `npx next build`, and
  `npx eslint src --max-warnings=0` (0 errors; see `STATUS.md` §6 for the known warnings).
  Report failures honestly with their output.
