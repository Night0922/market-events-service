from __future__ import annotations

from datetime import datetime
from typing import Any


PROVIDER_B_TYPE_MAP = {
    "earnings_release": "earnings",
    "dividend_payment": "dividend",
    "stock_split": "split",
    "economic_indicator": "economic",
}


def build_dedupe_key(symbol: str, event_type: str, event_date: str, title: str) -> str:
    return f"{symbol.upper()}|{event_type}|{event_date}|{title.strip().lower()}"



def normalize_provider_a(event: dict[str, Any]) -> dict[str, Any]:
    symbol = event["ticker"].upper()
    event_type = event["type"]
    event_date = event["date"]
    title = event["title"]
    return {
        "symbol": symbol,
        "event_type": event_type,
        "event_date": event_date,
        "title": title,
        "details": event.get("details", {}),
        "provider_name": "provider_a",
        "provider_event_id": event["event_id"],
        "source_payload": event,
        "dedupe_key": build_dedupe_key(symbol, event_type, event_date, title),
    }



def normalize_provider_b(event: dict[str, Any]) -> dict[str, Any]:
    symbol = event["instrument"]["symbol"].upper()
    event_type = PROVIDER_B_TYPE_MAP[event["event"]["category"]]
    scheduled_at = event["event"]["scheduled_at"]
    event_date = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00")).date().isoformat()
    title = event["event"]["title"]

    details = {}
    for key in ["earnings_data", "dividend_data", "economic_data"]:
        if key in event["event"]:
            details = event["event"][key]
            break

    return {
        "symbol": symbol,
        "event_type": event_type,
        "event_date": event_date,
        "title": title,
        "details": details,
        "provider_name": "provider_b",
        "provider_event_id": event["id"],
        "source_payload": event,
        "dedupe_key": build_dedupe_key(symbol, event_type, event_date, title),
    }
