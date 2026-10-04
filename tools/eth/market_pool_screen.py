"""Export a separate captured discovery screen for missing liquidity adapters.

This does not fill historical ETH balances. Full-pool TVL includes every asset;
symbol classification does not verify addresses, backing, reserves or liquidity.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

from market_data_probe import EXTRA, FAMILY, T

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/eth"
PROJECTS = ["uniswap-v3", "uniswap-v4", "balancer-v2", "sushiswap"]


def run():
    source_file = DATA / "yield_pool_candidates.json"
    candidates = json.loads(source_file.read_text())
    records = [json.loads(line) for line in (ROOT / "raw/eth/2026-10-02/requests.jsonl").read_text().splitlines()]
    source = next(row for row in records if row["key"] == "yield_pools")
    rows = []
    family = FAMILY | EXTRA
    for candidate in candidates:
        if candidate["project"] not in PROJECTS:
            continue
        components = [symbol for symbol in re.split(r"[-/\s(),]+", candidate["symbol"].upper()) if symbol]
        if not set(components) & family:
            continue
        rows.append({
            "pool": candidate["pool"],
            "protocol": candidate["project"],
            "chain": candidate["normalized_chain"],
            "symbol": candidate["symbol"],
            "symbol_components": components,
            "full_pool_usd": candidate["tvlUsd"],
            "all_ETH_family_symbols": all(symbol in family for symbol in components),
            "ETH_side_usd": None,
            "ETH_side_eth": None,
            "address_identity_verified": False,
            "physical_backing_verified": False,
            "underlying_addresses": candidate.get("underlyingTokens"),
            "pool_meta": candidate.get("poolMeta"),
            "reported_apy": candidate.get("apy"),
            "reported_apy_base": candidate.get("apyBase"),
            "reported_apy_reward": candidate.get("apyReward"),
            "source_layer": "discovery_current",
            "target_snapshot_verified": False,
            "amount_meaning": "Reported full-pool USD TVL, not ETH-side principal; symbol classification is unverified.",
        })
    rows.sort(key=lambda row: -row["full_pool_usd"])

    def summarize(selected):
        all_eth = [row for row in selected if row["all_ETH_family_symbols"]]
        return {
            "pool_count": len(selected),
            "full_pool_usd": math.fsum(row["full_pool_usd"] for row in selected),
            "all_ETH_family_symbol_pool_count": len(all_eth),
            "all_ETH_family_symbol_full_pool_usd": math.fsum(row["full_pool_usd"] for row in all_eth),
            "chains": dict(sorted(Counter(row["chain"] for row in selected).items())),
            "all_ETH_family_symbol_chains": dict(sorted(Counter(row["chain"] for row in all_eth).items())),
            "ETH_side_usd": None,
            "not_eligible_for_historical_ETH_panel": True,
        }

    out = {
        "schema_version": 1,
        "financial_snapshot_timestamp": T,
        "financial_data_refreshed": False,
        "capture_timestamp": source["retrieved_at"],
        "source_HTTP_date": source["source_date"],
        "target_snapshot_verified": False,
        "label": "Latest captured ETH-related liquidity pool discovery",
        "amount_label": "Full-pool USD TVL",
        "basis": "Pools in the captured discovery feed with at least one exact ETH-family symbol component. Full-pool TVL includes non-ETH assets in mixed pools.",
        "limitation": "The feed has addresses and full-pool TVL but no reserve quantities, price ranges, token weights or token-side amounts. Mixed-pool ETH principal cannot be computed, and a 50% split is not assumed. The all-ETH-family-symbol subset is only a symbol screen; token identity, claim hierarchy and backing are not uniformly verified.",
        "coverage_limit": "These are four adapters missing ETH token observations in the historical panel. The feed and the panel are both incomplete market screens. This file is not a quantified estimate of all omitted liquidity.",
        "historical_panel_unchanged": True,
        "source": {"url": source["url"], "path": source["path"], "sha256": source["sha256"]},
        "derived_input": {"path": str(source_file.relative_to(ROOT)), "sha256": hashlib.sha256(source_file.read_bytes()).hexdigest()},
        "summary": summarize(rows),
        "protocols": [{"id": protocol, **summarize([row for row in rows if row["protocol"] == protocol])} for protocol in PROJECTS],
        "rows": rows,
    }
    destination = DATA / "market_pool_screen.json"
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(out, indent=2))
    temporary.replace(destination)
    with (DATA / "market_pool_screen.csv").open("w", newline="") as output:
        keys = ["pool", "protocol", "chain", "symbol", "full_pool_usd", "all_ETH_family_symbols", "ETH_side_usd", "reported_apy", "reported_apy_base", "reported_apy_reward"]
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    assert len({row["pool"] for row in rows}) == len(rows)
    assert all(row["ETH_side_usd"] is None for row in rows)
    print(json.dumps({"summary": out["summary"], "protocols": out["protocols"]}, indent=2))


if __name__ == "__main__":
    run()
