# v2: higher-fidelity .ksplat

Same scans and converter as v1, with settings that keep more detail. No new code: only converter settings change.

## Settings
| Version | Quantisation level | SH degree | Alpha threshold (/255) |
|---|---|---|---|
| v1 | 2 (SH 8-bit) | 1 | 13 |
| v2-A | 1 (16-bit) | 2 | 13 |
| v2-B | 1 (16-bit) | 2 | 1 (keeps faint splats) |
| v2-C | 0 (float32) | 2 | 1 |

## Sizes (scan 1: 148.0 MB, scan 2: 150.2 MB)
| File | Scan 1 | Scan 2 | Smaller |
|---|---|---|---|
| v1 (level 2, SH1) | 18.4 MB | 18.6 MB | 88% |
| v2-A | 40.2 MB | 40.5 MB | 73% |
| v2-B | 43.0 MB | 43.6 MB | 71% |
| v2-C | 83.5 MB | 84.8 MB | 44% |

## Image comparison (scan 1)
Method: render the original PLY and each compressed file in the same viewer at the same camera, then compare the two images. This measures loss from compression only, not accuracy against real photos. Rendered with software graphics, so only picture quality is meaningful.

| File | View 1 | View 2 | View 3 |
|---|---|---|---|
| v2-A | 63.8 dB, SSIM 0.9996 | 55.4 dB, SSIM 0.9988 | not rendered |
| v1 | 37.7 dB, SSIM 0.9972 | 32.3 dB, SSIM 0.9822 | 24.1 dB, SSIM 0.9812 |

v2-A is visually the same as the original; v1 shows a small loss that depends on the view.

## Not done yet
- v2-B, v2-C and scan 2 renders; view 3 for v2-A.
- Quality against real photos, and frame rate on the target laptop (needs a real GPU).
