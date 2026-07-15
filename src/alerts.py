"""
Sends triggered signals to a Discord channel via a webhook URL.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_alert(triggered_signals: list[dict]) -> None:
    if not triggered_signals:
        return

    if not WEBHOOK_URL:
        print("  [WARN] DISCORD_WEBHOOK_URL not set in .env - skipping Discord alert.")
        return

    lines = [f"**MarketPulse: {len(triggered_signals)} signal(s) triggered**", ""]
    for sig in triggered_signals:
        lines.append(
            f"**{sig['symbol']}** - `{sig['rule_name']}`\n"
            f"{sig['details']}\n"
            f"Price at signal: ${sig['close_at_signal']:.2f}"
        )

    message = "\n\n".join(lines)

    try:
        response = requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
        response.raise_for_status()
        print(f"  Discord alert sent ({len(triggered_signals)} signal(s)).")
    except requests.exceptions.RequestException as e:
        print(f"  [WARN] Failed to send Discord alert: {e}")