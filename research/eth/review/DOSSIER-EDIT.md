# Dossier editorial review

Edited for the colleague-facing English edition on 4 October 2026. The research snapshot remains 2 October 2026, 23:59:59 UTC; public material remains dated to its stated capture on 3 October.

## Scope

Revised all 12 English dossiers in `research/eth/en/dossiers/` and, at the project lead's request, `research/eth/en/MECHANICS.md`. Original research, raw evidence, numerical derivations and source links were not changed.

## What changed

- Replaced compressed research notes with direct sentences and shorter paragraphs.
- Organized each dossier around the product, income source and payer, share accounting, fees and controls, exit, findings, and open evidence. The headings adapt to the product rather than forcing every dossier into an identical template.
- Explained specialist terms at their first meaningful use, including NAV, PPS, APY, APR, LST, LRT, HF, LT, AVS, LP, PT, SY, YT, RWA and utilization.
- Clarified the difference between a reported share value and executable withdrawal, between a token representation and verified backing, and between an unresolved difference and an established deficit.
- Made economic findings easier to read without weakening their evidence limits. CIAN attribution, Concrete issuance and ownership, Liquid Monad backing, credit exposure, and ETH-denominated versus dollar-denominated returns remain explicitly qualified.
- Split the mechanics report into readable sections for E1-E9. All equations, worked examples and stress values remain present.
- Removed prose em dashes and en dashes. The withdrawal discount range uses an ASCII hyphen. Mathematical minus signs remain in equations and negative returns.

## Preservation check at handoff

Compared each edited file with a saved pre-edit copy. All 13 files passed:

- Every original numeric token is retained, with at least its original occurrence count. The matcher recognizes grouped thousands and decimals without absorbing trailing sentence commas.
- Every original hexadecimal address is retained, including abbreviated addresses.
- Every original Markdown link target is retained.
- Every original inline evidence filename or script path ending in `.json`, `.jsonl` or `.py` is retained.
- No em dash or en dash remains in the edited files.

The preservation check establishes editorial retention, not independent financial verification. The lead's additional research on fee history, governance, borrower concentration and redemption should be integrated after this edit, with the final build and data audits rerun at project level.
