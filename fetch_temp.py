import requests
from datetime import datetime, timedelta
import json
from collections import defaultdict

URL = "https://www.ndbc.noaa.gov/data/realtime2/ALXN6.txt"

def c_to_f(c):
    return round((c * 9/5) + 32, 2)

def fetch_and_process():
    print(f"Fetching data from {URL}...")
    try:
        r = requests.get(URL)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    lines = r.text.strip().split("\n")
    print(f"Total lines received: {len(lines)}")

    temps_by_day = defaultdict(list)

    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 15 or parts[14] == 'MM':
            continue
        try:
            dt = datetime.strptime(" ".join(parts[0:5]), "%Y %m %d %H %M")
            temp_f = c_to_f(float(parts[14]))
            date_str = dt.date().isoformat()
            temps_by_day[date_str].append(temp_f)
        except Exception as e:
            print(f"Error parsing line: {e}")
            continue

    # Filter to just the past 7 days
    cutoff = (datetime.utcnow() - timedelta(days=7)).date()
    output = []

    for date in sorted(temps_by_day.keys()):
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        if date_obj >= cutoff:
            temps = temps_by_day[date]
            avg = round(sum(temps) / len(temps), 2)
            output.append({
                "date": date,
                "day": date_obj.strftime("%A"),
                "avg_temp_f": avg
            })

    with open("temperature.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output)} daily entries to temperature.json:")
    for row in output:
        print(row)

fetch_and_process()
