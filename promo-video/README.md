# MyTZStudies — Start ready

An editable product advertisement using the actual MyTZStudies website, real worked answer pages, and an original instrumental soundtrack.

## Deliverables

- `../output/video/MyTZStudies-Launch-1080p.mp4`: 72 seconds, 1920 × 1080, 30 fps.
- `../output/video/MyTZStudies-Social-Vertical.mp4`: 26 seconds, 1080 × 1920, 30 fps.
- `../output/video/MyTZStudies-Poster.png`: full-resolution poster.

The MP4s use H.264, Rec.709, YUV 4:2:0, and stereo AAC at 48 kHz / 320 kbps. The films use short on-screen text instead of narration. The catalogue claims are 60 distinct papers, 60 worked answer keys and four levels, verified against the local website during capture. Answer keys are explicitly described as free with a MyTZStudies account. Tutor footage shows the real subject filter and directory; it does not promise bookings, availability, or results.

## Edit and export

```powershell
cd promo-video
npm ci
npm run dev
npm run lint
npm run render
```

The Studio contains both finished compositions and each main scene as a separate editable composition. Scenes live in `src/scenes/`; the portrait edit lives in `src/Social.tsx`. Every animation derives from the current frame, so exports are deterministic. Assets are local, including fonts.

On Windows the renderer uses installed Google Chrome. Set `REMOTION_BROWSER_EXECUTABLE` to another Chrome executable if necessary. Export one version with `node tools/render.cjs TZStudiesLaunch` or `node tools/render.cjs TZStudiesSocial`.

## Capture and soundtrack sources

`tools/capture.cjs` records the local site with Playwright. It uses an isolated preview database and a preview account; no real user accounts or outbound messages are used. Set `TZ_NODE_MODULES` to a directory containing Playwright, start the website on port 5050 with email suppressed, and install Playwright's FFmpeg component before re-recording. The raw recordings are ignored by Git. Convert them to H.264 files in `public/clips/` before exporting.

`tools/assets.py` downloads the two OFL fonts and renders the real Basic Mathematics / Form Two / 2024 answer PDF using PyMuPDF. `tools/score.py` requires Python, NumPy and SciPy; it creates both original scores at 110 BPM. The final audio WAVs are loudness normalized near −16 LUFS with a −1.5 dBTP ceiling. See `AUDIO-RIGHTS.md`.

`tools/preview.cjs` renders review stills. `tools/review.py` checks exported metadata, the full timeline, audio levels and MP4 streaming layout. Generated review files live in `qa/` and are excluded from Git. This folder is excluded from the website's Docker image.
