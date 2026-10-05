# ETH website publication handoff

Public ETH page: https://vlad-degen.github.io/btc-yield-atlas/eth/

Original BTC page: https://vlad-degen.github.io/btc-yield-atlas/

The publication is PR https://github.com/vlad-degen/btc-yield-atlas/pull/2, merged as `9385e2736be6205b6c6b946f8a8e1f1c151f54a5`. GitHub Pages reports this commit built. Its existing source remains `main` at `/`.

## Branches and scope

- `codex/eth-research` is the local full-research branch. Its initial complete research commit is `f294441`. This branch was not pushed. Automatic approval rejected publishing the complete 550 MB working dataset under the website-publication request.
- `codex/eth-research-site` is the public website branch, commit `32b7c43777a4e05d28fa03f67d79dcf3748eb0d2`. It starts directly from original BTC commit `711a3935621cfd72da0b25ebcf5a6c173a10adbe`; the bulk research commit is not in its ancestry. The branch was kept after merging.
- The publication adds only `eth/`: 48 HTML pages, their linked assets and evidence downloads, dynamic CSV exports, figures, README and selected presentation QA. The full working datasets, analytical source pipeline, mirror and portable ZIP remain local.

`github-publication-files.json` records the 862 website files selected by following presentation links and including all CSV variants required by the interactive controls. Use a fresh link closure for future updates. Publish from a clean worktree based on current remote `main`; do not push the full local research branch as a website update.

## Verification

All 345 pre-existing tracked files retain their original Git blob IDs in remote `main`. The public BTC HTML SHA256 is `ee05709e085406a6b0da19717e974834c6ae48cea54f34840c830fbc9eaf1222`, matching the original local BTC page byte for byte.

The public ETH HTML SHA256 is `833b1907c508b61caf0106899b55f925d64b239e3e5c341f82fb5ba4b2db1794`, matching the build with 28 recorded desktop/mobile browser checks. Live ETH, supporting exhibits, briefing and a selected CSV returned HTTP 200 and matched their local hashes. The public page also initialized all eight chapters and seven carry-book rows without browser errors.

See `github-publication-verification.json` for public response hashes. The fixed financial snapshot remains 2 October 2026, 23:59:59 UTC. This publication does not change research coverage claims.


## 5 October reader alignment update

PR https://github.com/vlad-degen/btc-yield-atlas/pull/3 publishes the carry-history and analytical-synthesis revision. Website branch `codex/eth-reader-alignment` contains commit `23439ac3e3ab19c1a11759d64096d0a778033eb1`, merged as `a9b803325b24c4fbff889f62c04d9d9592577022`. The PR changes 24 files, all inside `eth/`.

The fresh presentation-link manifest selects 872 website files (73.414 MB), including all eight carry CSV views, normalized reader analysis, 48 HTML pages and current presentation QA. Existing public QA from the prior edition can remain in the repository. No full-research source history is pushed.

The new ETH HTML SHA256 is `8925df0f366e85a3cfb0362cc2360fa7bc8d027ae22b2ebc7882807111a47206`. The normalized reader bridge passed 428 financial/export checks and the website passed 38 desktop/mobile browser checks. The remote main tree preserves all 345 original BTC Git blobs. The broader local audit preserves 384 BTC files and 526 original captured responses.

Live Pages and response verification: pending build completion.
