"""
Day 1 — Live NAV Fetch
Pulls live NAV history from mfapi.in for HDFC Top 100 Direct plus 5 key
large-cap schemes, and saves each as a raw CSV.
"""
import requests
import pandas as pd

OUT_DIR = "data/raw/live"

SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}


def fetch_scheme(amfi_code):
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def save_scheme(amfi_code, label, payload):
    nav_data = payload.get("data", [])
    df = pd.DataFrame(nav_data)
    df.insert(0, "amfi_code", amfi_code)
    df.insert(1, "scheme_name", label)

    out_path = f"{OUT_DIR}/{amfi_code}_{label.replace(' ', '_')}.csv"
    df.to_csv(out_path, index=False)
    print(f"{amfi_code} ({label}): {len(df)} NAV records -> {out_path}")
    return df


if __name__ == "__main__":
    for amfi_code, label in SCHEMES.items():
        try:
            payload = fetch_scheme(amfi_code)
            save_scheme(amfi_code, label, payload)
        except requests.RequestException as e:
            print(f"{amfi_code} ({label}): fetch failed - {e}")
