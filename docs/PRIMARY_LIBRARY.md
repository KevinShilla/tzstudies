# Primary library expansion

Prepared on 7 October 2026. The project now contains 208 unique papers, including 148 newly imported PDF papers/subject sections (65.0 MB). Every Standard 1-6 / Math-English-Kiswahili group has at least seven papers dated 2022 or later, counting the existing Standard 4 national papers too.

## Coverage

These are actual exam dates where printed, or dates from explicit publisher listings when a paper has no printed year. There is no promise of a paper for every subject in every year. In particular, the imported Standard 6 Math and Kiswahili collection begins in 2024; no usable 2022-2023 PDFs were found for those two groups. The table records every remaining year gap rather than inventing or relabeling papers.

| Standard | Subject | Papers | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Math | 9 | 3 | 1 | 4 | 0 | 1 |
| 1 | English | 9 | 3 | 0 | 4 | 1 | 1 |
| 1 | Kiswahili | 9 | 2 | 0 | 5 | 0 | 2 |
| 2 | Math | 9 | 2 | 2 | 2 | 2 | 1 |
| 2 | English | 9 | 2 | 1 | 2 | 3 | 1 |
| 2 | Kiswahili | 9 | 2 | 2 | 3 | 1 | 1 |
| 3 | Math | 8 | 2 | 0 | 2 | 2 | 2 |
| 3 | English | 9 | 3 | 0 | 2 | 1 | 3 |
| 3 | Kiswahili | 7 | 1 | 1 | 3 | 0 | 2 |
| 4 | Math | 12 | 2 | 2 | 2 | 6 | 0 |
| 4 | English | 8 | 1 | 1 | 1 | 5 | 0 |
| 4 | Kiswahili | 8 | 1 | 1 | 1 | 5 | 0 |
| 5 | Math | 9 | 1 | 1 | 6 | 0 | 1 |
| 5 | English | 9 | 1 | 1 | 6 | 0 | 1 |
| 5 | Kiswahili | 9 | 1 | 1 | 6 | 0 | 1 |
| 6 | Math | 9 | 0 | 0 | 7 | 1 | 1 |
| 6 | English | 9 | 1 | 0 | 6 | 1 | 1 |
| 6 | Kiswahili | 9 | 0 | 0 | 6 | 2 | 1 |

Machine-readable counts are in `docs/primary-library-coverage.csv`.

## What is included

- Math groups Mathematics, Hisabati, arithmetic and numeracy. Early-grade English/Kiswahili reading and writing assessments retain their original skills labels.
- National papers keep their existing NECTA labels. New school tests, regional mocks, joint assessments and holiday practice have their actual issuer and assessment type instead of being labeled NECTA.
- The main sources are [Darasa Huru](https://darasahuru.ac.tz/standard-one-examinations-all-subjects/) and [Msomi Bora's public primary collections](https://www.msomibora.com/2025/12/school-exams-for-english-medium-primary-schools/). Each imported paper has its specific source page, original download URL, file size, page count, SHA-256 hash and date basis in `exams/catalogue.json`.
- Original publisher attribution and question layouts are preserved. Reviewed subject sections were extracted from multi-subject packs with the original cover/pagination retained where applicable. The manifest records the original file hash and selected page numbers. One malformed source PDF had its object references repaired; active-content validation still passed after repair.
- Unreadable/unsafe files, answer-only files, duplicate copies, papers for other subjects/standards, and a Math PDF with missing fraction operands were excluded. No new exam questions or missing dates were invented.
- The existing 60 worked answer keys are retained. New imports do not claim to have a separate TZStudies worked answer key. Some original source papers include their publisher's own answers within the PDF.

## Navigation and performance

- Standards 1-6 have large shortcuts; Standard 7 and secondary papers remain accessible.
- Level, subject, year and search filters apply to the full catalogue, work without JavaScript, and are shareable in the URL.
- Pages render 18 cards, with filters preserved when moving between pages. Filter changes stay at the controls instead of jumping above the standard shortcuts.
- Only public file metadata is cached. HTML and authentication/session state remain private and uncached.
- The paper table synchronizes at application startup, rather than issuing library-table reads/writes on every homepage request. Individual view/download records still work with the existing database models.
- Public exam PDFs support byte ranges, ETags and conditional requests, with a one-day cache lifetime. Protected answer-key responses retain their access control and private caching rules.
- Desktop and 390 px mobile browser checks cover the filters, standard shortcuts, PDF viewer links, page navigation and responsive layout.
- Local warm HTTP median: 30.9 ms across 15 requests. Paginated HTML: 32,488 bytes versus 216,733 bytes for the same layout with all 208 cards (85.0% less HTML). This comparison does not measure Render cold starts, production network speed, or the previous production page.

## Deploy to your existing Render service

1. Push the primary-library commit from the existing production branch to GitHub, then deploy it on Render.
2. Keep your existing Supabase, Redis, authentication, payment and OpenAI environment variables. No new variable or database migration is required for this change; startup adds the new paper rows to the existing table.
3. After Render is live, check the homepage count, choose Standard 1 / Kiswahili / 2022, open/download a paper, then check Standard 6 / Math. Confirm the existing login and answer-key access still work.

The local preview uses a separate SQLite database and disables live payment/AI/mail calls. It does not change production data or payment settings. Unrelated video/music work was left untouched.

## Validation

Run `python tools/verify_exam_library.py` to verify imported file hashes, PDF structure/safety and all 18 coverage targets. Automated tests also cover pagination, full-catalogue filtering, cache invalidation/isolation, unchanged security controls and conditional PDF delivery.
