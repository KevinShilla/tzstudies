# Primary worked answer keys

All 148 imported Standard 1-6 Math, English and Kiswahili PDFs in `exams/catalogue.json` now have worked keys. The library has 208 unique papers and 208 corresponding keys, including the existing 60 keys.

The new keys cover 5,310 printed tasks/parts over 1,520 pages. Their 2,146 numerical checks use exact fractions. Content review, source hashes, rendered-page inspection and publication hashes are recorded in `output/primary-answer-key-review.json`.

| Subject | New keys | Answered parts | PDF pages |
| --- | ---: | ---: | ---: |
| Mathematics / Hisabati | 50 | 1,805 | 489 |
| English | 50 | 1,805 | 500 |
| Kiswahili | 48 | 1,700 | 531 |

## Format

The existing `tools/build_answer_keys.py` template supplies the website-only advertising cover, exam details on page two, rewritten questions, numbered worked steps, highlighted final answers, study tips and section summaries. Imported papers use their verified school/regional issuer, rather than being mislabeled NECTA. The original PDF hash and page reference tie each solution to its source.

Reading aloud and copying tasks include assessment guidance. Open-ended questions include clearly labeled model responses. Missing dictation scripts, absent pictures, printing errors and ambiguous questions are explained in the corresponding solution; a missing official response is not invented.

Some complete source packs retain extra subject sections. `tools/merge_primary_packs.py` uses original file hashes and extracted page numbers to incorporate their separately solved sections, so those tasks are covered too.

## Review and publication

1. Write and check every part in `answer_keys/solutions/<source-stem>.json`. The `reviewed` flag concerns content checking; it does not publish the key.
2. Run `python tools/review_primary_answer_keys.py` for current coverage and exact-fraction arithmetic checks.
3. Run `python tools/review_primary_answer_keys.py --render` to create unpublished drafts in `output/pdf` and render every page into `tmp/primary-answers/pdf-review`. The audit checks the cover, second-page metadata, answer count, margins, glyphs and text overlap.
4. Run `python tools/contact_primary_answers.py` and inspect the latest rendered pages. Record approval with `python tools/review_primary_answer_keys.py --approve-visual <exam-filename.pdf> ...` only for PDFs you have inspected. Approval records the exact PDF hash.
5. Run `python tools/review_primary_answer_keys.py --publish`. Publication requires the reviewed source hash, audited PDF hash, zero layout errors and explicit visual review. Existing authentication protects viewing/downloading the new keys.

`output/primary-answer-key-review.json` records actual progress, answered parts, source limitations, exact arithmetic checks and published files. Pending files are not represented as completed keys.

No new production dependency, environment variable, database migration or change to the payment system is required. The local PDF tooling is in `requirements-pdf.txt`; Render serves the completed PDFs.

## Handover

The checked website files are in `answer_keys/`; editable solutions and source figure crops are in its `solutions/` and `figures/` directories. `output/MyTZStudies-Answer-Keys.zip` contains all 208 canonical keys and a CSV index. Rebuild that optional download bundle with `python tools/package_answer_keys.py` after publishing reviewed keys locally.

Push the local answer-key commit on `main` to GitHub, then deploy that commit on the existing Render service. Keep the current production environment and payment settings. After deployment, open `/answer_keys`, confirm 208 keys, filter Standard 6 / Math, and open/download a new worked key while signed in. The local changes do not update production until you push and deploy them.

## Validation completed

All 254 application/library tests passed, including authentication, private key delivery, pagination, verified issuer labels and every imported key's approval hash. Ruff, the source secret scan and strict PDF active-content validation passed. All 148 original exam hashes still match the import manifest.

Browser checks confirmed 208 keys, nine Standard 6 Math results, mobile filtering without horizontal overflow, the login redirect and a signed-in PDF download. The downloaded file matched the reviewed website PDF. Temporary mobile sizing was reset after testing.
