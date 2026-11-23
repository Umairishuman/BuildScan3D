# Checks for Umair (Step 4)

Everything in COMPLETION_PLAN Step 4 that only Umair can do, on one page, in the order that unblocks the most.
Written 2026-11-23 by an agent for Umair (R-103); values come from each room's current run (named per room). Rooms in
the order Umair prefers: scans #6, #7, #8, newRoom, then scan #3 (poor recording, last). Scan #5 has no model yet.

How to use it: fill in the blanks (here, or on paper and an agent copies them in). Write the **tape value first, then
look at the pipeline value**, so the reading is not steered by it. When a section is done, tell the agent: it fills in
the issue, TRAINING / STATUS, and the precision / recall and threshold tables that wait on it.

| Section | Unblocks | Issue | Time (guess) |
|---|---|---|---|
| A. Room names | web cards, records | #23 | 2 min |
| B. Fixture sheets | found / missed / false per room (4.2, E3), thresholds (4.7, 4.8), are the wall gaps real (4.5) | #21 | 10–15 min per room, at the PC |
| C. newRoom: three detections | 4.4 | #22 | 3 min |
| D. Tape | room heights (4.1), size card (4.3), NFR6 (E2) | #20 | 15 min per room, in the room |
| E. Browser check | 4.3, web delivery | #24 | 5 min |
| F. scan #3 floor step | #17 | #17 | 1 min (only if you go back to that room) |

## A. Room names (#23)

| Scan | Folder | What the records say | Room name / number |
|---|---|---|---|
| #1 | `scan_001_056fe94d3399` | 46 s, your first Linux test, "Umair's room" (1 wall found) | |
| #2 | `scan_002_646070948603` | computer lab: desks, red chairs, glass partition | |
| #3 | `scan_003_6de634cbb8b2` | classroom: wooden desks with red seats, projector screen, blue curtains | |
| #4 | `newRoomAttemptSadness` | room of the best model (who recorded it is not written down) | |
| #5 | `scan_005_4aadb16181d9` | 352.5 s, not processed yet | |
| #6 | `scan_006_1e457a214ce1` | 259.8 s, L-shaped room (7 walls), 3.05 m high, door + fan | |
| #7 | `scan_007_e6d4f090f88e` | building under construction, no roof | |
| #8 | `scan_008_7b486c855ed6` | 366.5 s, 6.0 × 4.4 m, 3.16 m high | |

## B. Fixture sheets (#21)

Open the room in the viewer (`scripts/buildscan view`) and the sheet next to it; mark every row real / wrong class /
false, add what was missed. The bottom of each sheet lists the candidates the rules **rejected**: mark any that are
real (those are misses caused by the rules).

| Room (run, tag) | Sheet | Fixtures / rejected | Look at especially |
|---|---|---|---|
| scan #6 (R-059, `r1119b6`) | `dataset/scan_006_1e457a214ce1/checks_r085/fixture_check.md` | 11 / 84 | `light_switch_2` and `_5`: same spot on wall 0 = the 4.01 m wall (1.00 m along, 0.76 / 0.75 m up), one plate or two? `power_socket_1` at 1.88 m, `light_switch_4` at 0.49 m: real? `doorway_1` (0.90 m gap in the 4.39 m wall, blue in `plan.png`): a real doorway? Wall numbers in the sheet: 0 = 4.01 m, 1 = 5.26, 2 = 4.39, 3 = 1.71, 4 = 2.32, 5 = 0.74, 6 = 0.98. |
| scan #7 (R-057, `r1119c`) | `dataset/scan_007_e6d4f090f88e/work_r1118_sfm/gs_r1119c/semantic_v10/fixture_check.md` | 3 / 29 | 2 doorways (0.8, 1.0 m) + window opening 2.1 m: real openings? Any of the 29 rejected a real fitting? (probably none: building site) |
| scan #8 (R-057, `r1119c`) | `dataset/scan_008_7b486c855ed6/work_r1116w9_sfm/gs_r1119c/semantic_v10/fixture_check.md` | 10 / 58 | doorway 1.0 m (wall 1 = 6.03 m), window opening 2.0 m (wall 3 = 6.04 m) |
| newRoom (R-057, `r1119c`) | `dataset/newRoomAttemptSadness/work_r1112nr_sfm/gs_r1119c/semantic_v10/fixture_check.md` | 19 / 49 | 7 doors (cupboard doors?), doorway 0.8 m (wall 0 = 6.63 m), window opening 0.4 m at 0.5–0.9 m (wall 2 = 5.78 m) |
| scan #3 (R-057, `r1119c`) | `dataset/scan_003_6de634cbb8b2/work_r1112lev_sfm/gs_r1119c/semantic_v10/fixture_check.md` | 20 / 28 | 4 fans and 7 ceiling lights: right count? |

## C. newRoom: three new detections (#22)

In newRoom `r1119c` (sheet above), are these real?

| Fixture | Where (pipeline) | Real / wrong class / false | What it is |
|---|---|---|---|
| `door_1` | wall 4 (0.78 m), centre 1.00 m up, 0.82 × 1.80 m | | |
| `door_6` | wall 2 (5.78 m), centre 1.12 m up, 1.11 × 1.86 m | | |
| `tube_light_1` | wall 0 (6.63 m), 2.43 m up, 1.10 m long | | |

## D. Tape (#20)

Three readings each, in metres. "Across" = between two opposite walls at about waist height. `layout/plan.png` (next
to each sheet) labels walls by their **length**, not number, so walls are named here as "the 4.01 m wall". Switch / socket: height of the plate's centre above the floor.

| Room | Measure | Tape (3 readings) | Pipeline |
|---|---|---|---|
| scan #6 | floor to ceiling | | 3.05 (layout), 3.08 (semantics) |
| scan #6 | across: 4.01 m wall to 1.71 m wall / 4.01 m to 2.32 m / 5.26 m to 4.39 m | | 4.40 / 5.29 / 4.03 |
| scan #6 | door `door_1`: width × height | | 1.21 × 2.66 (looks too tall: check) |
| scan #6 | one switch (`light_switch_1`), one socket (`power_socket_1`) | | 0.74 / 1.88 |
| scan #7 | top of walls (no roof) | | 3.11 |
| scan #7 | across: 4.27 m wall to 4.42 m wall / 4.17 m to 4.12 m | | 4.14 / 4.35 |
| scan #7 | doorway in the 4.42 m wall, in the 4.17 m wall: width | | 0.80 / 1.00 |
| scan #8 | floor to ceiling | | 3.16 (layout), 3.19 (semantics) |
| scan #8 | across: 4.48 m wall to 4.28 m wall / 6.03 m to 6.04 m | | 6.03 / 4.40 |
| scan #8 | door `door_1`; one switch, one socket | | 0.47 × 1.82; `light_switch_3` 0.75, `power_socket_2` 0.78 |
| newRoom | floor to ceiling | | 2.81 (layout), 2.82 (semantics) |
| newRoom | across: 6.63 m wall to 5.78 m wall / 4.37 m to 4.57 m | | 4.37 / 6.57 |
| newRoom | one switch, one socket | | `light_switch_1` 1.40, `power_socket_2` 0.81 |
| scan #3 | floor to ceiling (lower floor level) | | 2.53 (layout), 2.58 (semantics) |
| scan #3 | across: 8.97 m wall to 7.68 m wall / 7.19 m to 3.69 m | | 7.23 / 9.05 |

## E. Browser check (#24)

`scripts/buildscan web` (or the deployed site), open Projects, open one card per room (at least scan #6 `r1119b6` and
scan #8 `r1119c`):

- [ ] splats render (not blank, not a grey blob)
- [ ] the start view is inside the room and the right way up
- [ ] clicking a fixture row or marker opens its size card (width, height, height above floor)
- [ ] the card's numbers match section D (if taped)
- Browser + device used: ______

## F. scan #3 floor step (#17)

The far end of scan #3's floor fits 8–14 cm higher over ~2 m (R-055 / #17). Is there a raised platform (teacher's
platform)? yes / no, height ____ cm. (Only if you are in that room again: scan #3 is not used for new work.)
