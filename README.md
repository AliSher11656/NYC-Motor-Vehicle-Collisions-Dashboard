# NYC Motor Vehicle Collisions – Shiny for Python Dashboard

**Includes (advanced):**
- Live Socrata API ingestion (public, unauthenticated)
- Default last 6 months + custom date range
- Max 10,000 rows per refresh
- In-memory caching (10-minute TTL)
- Multi-page tabs: Overview, Map, Time Analysis, Risk & Streets, Causes & Vehicles
- Hour × Day heatmap (Weekday vs Hour)

## Run locally (Python 3.11)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
shiny run --reload app.py
```

## Notes
- Timezone: America/New_York
- If your selected date range contains >10k records, the API returns the latest 10k (ordered by crash_date).
- Borough dropdown is populated after the first data fetch.
