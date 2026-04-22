"""
This module defines the user interface layout and styling for a Shiny dashboard
that presents analytics about New York City road safety crash data.
"""

from shiny import ui
from shinywidgets import output_widget
from datetime import timedelta
from utils import nyc_now


def create_app_ui():
    """
    Returns the complete user interface definition for the dashboard, including
    global page styling, header content, filter sidebar controls, navigation tabs,
    and all visual layout containers.
    """
    return ui.page_fluid(
        ui.tags.head(
            ui.tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
            ui.tags.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous"),
            ui.tags.link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            ),
            ui.tags.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
            ),
            ui.tags.style(
                """
                :root{
                  --bg: #0b1220;
                  --surface: rgba(255,255,255,0.06);
                  --card: rgba(255,255,255,0.08);
                  --card2: rgba(255,255,255,0.10);
                  --text: rgba(255,255,255,0.92);
                  --muted: rgba(255,255,255,0.65);
                  --border: rgba(255,255,255,0.12);
                  --shadow: 0 12px 30px rgba(0,0,0,0.25);
                  --shadow2: 0 10px 24px rgba(0,0,0,0.18);
                  --radius: 18px;
                }

                /* =========================================================
                   BASE / LAYOUT
                   ========================================================= */
                body{
                  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
                  background: radial-gradient(1200px 700px at 15% -10%, rgba(99,102,241,0.35), transparent 60%),
                              radial-gradient(900px 600px at 85% 0%, rgba(34,197,94,0.22), transparent 55%),
                              radial-gradient(900px 600px at 40% 110%, rgba(59,130,246,0.20), transparent 55%),
                              var(--bg);
                  color: var(--text);
                }

                /* Safety net: avoid black text on dark surfaces */
                body, p, span, div, label, small, strong, em, h1, h2, h3, h4, h5, h6{
                  color: var(--text);
                }

                .container-fluid{ max-width: 1400px; }

                /* Muted helper text */
                .text-muted, .help-block, .form-text{
                  color: var(--muted) !important;
                }

                /* =========================================================
                   HERO HEADER
                   ========================================================= */
                .hero{
                  border-radius: 24px;
                  padding: 22px 22px;
                  background: linear-gradient(135deg, rgba(99,102,241,0.28), rgba(34,197,94,0.16));
                  border: 1px solid var(--border);
                  box-shadow: var(--shadow);
                  margin: 18px 0 16px 0;
                }
                .hero-title{
                  font-size: 22px;
                  font-weight: 800;
                  letter-spacing: -0.02em;
                  margin: 0;
                  display:flex;
                  align-items:center;
                  gap:10px;
                }

                /* =========================================================
                   SIDEBAR
                   ========================================================= */
                .sidebar{
                  background: rgba(255,255,255,0.05) !important;
                  border: 1px solid var(--border);
                  border-radius: var(--radius);
                  padding: 14px 14px;
                  box-shadow: var(--shadow2);
                }
                .sidebar, .sidebar *{
                  color: var(--text) !important;
                }
                .sidebar h4{
                  font-weight: 800;
                  letter-spacing: -0.01em;
                  margin-bottom: 10px;
                }
                .form-label, .control-label{
                  color: rgba(255,255,255,0.85) !important;
                  font-weight: 600;
                  margin-bottom: 6px;
                }

                /* Inputs */
                .selectize-input, .form-control{
                  border-radius: 14px !important;
                  border: 1px solid rgba(255,255,255,0.18) !important;
                  background: rgba(0,0,0,0.14) !important;
                  color: rgba(255,255,255,0.92) !important;
                  box-shadow: none !important;
                }
                .form-control::placeholder{
                  color: rgba(255,255,255,0.55) !important;
                }

                /* Selectize dropdown */
                .selectize-dropdown{
                  border-radius: 14px !important;
                  border: 1px solid rgba(255,255,255,0.18) !important;
                  background: #0b1220 !important;
                  color: rgba(255,255,255,0.92) !important;
                  overflow: hidden;
                }
                .selectize-dropdown-content div{
                  color: rgba(255,255,255,0.92) !important;
                }
                .selectize-dropdown-content div:hover{
                  background: rgba(255,255,255,0.12) !important;
                }

                /* Date picker popup */
                .datepicker, .datepicker table, .datepicker table td, .datepicker table th{
                  background-color: #0b1220 !important;
                  color: rgba(255,255,255,0.92) !important;
                }
                .datepicker table td.active, .datepicker table td.active:hover{
                  background: rgba(99,102,241,0.85) !important;
                  color: #fff !important;
                }

                /* Buttons */
                .btn-primary{
                  border-radius: 14px;
                  padding: 10px 12px;
                  font-weight: 700;
                  border: 1px solid rgba(255,255,255,0.16) !important;
                  background: linear-gradient(135deg, rgba(99,102,241,0.95), rgba(59,130,246,0.85)) !important;
                  box-shadow: 0 10px 18px rgba(0,0,0,0.25);
                  color: #fff !important;
                }
                .btn-primary:disabled{
                  opacity: 0.45;
                  box-shadow: none;
                }
                .btn, .btn *{
                  color: #fff !important;
                }

                /* =========================================================
                   TABS
                   ========================================================= */
                .nav-tabs{
                  border-bottom: 1px solid var(--border);
                  gap: 8px;
                }
                .nav-tabs .nav-link{
                  border-radius: 14px 14px 0 0;
                  border: 1px solid transparent;
                  color: rgba(255,255,255,0.75) !important;
                  font-weight: 700;
                  padding: 10px 14px;
                }
                .nav-tabs .nav-link.active{
                  color: rgba(255,255,255,0.95) !important;
                  background: rgba(255,255,255,0.08);
                  border-color: var(--border);
                }

                /* =========================================================
                   CARDS
                   ========================================================= */
                .card{
                  background: rgba(255,255,255,0.06) !important;
                  border: 1px solid var(--border) !important;
                  border-radius: var(--radius) !important;
                  box-shadow: var(--shadow2);
                  overflow: hidden;
                }
                .card, .card *{
                  color: rgba(255,255,255,0.92) !important;
                }
                .card:hover{
                  transform: translateY(-2px);
                  transition: 0.18s ease;
                  background: rgba(255,255,255,0.075) !important;
                }
                .card-header{
                  background: rgba(255,255,255,0.05) !important;
                  border-bottom: 1px solid var(--border) !important;
                  font-weight: 800;
                  letter-spacing: -0.01em;
                  color: rgba(255,255,255,0.95) !important;
                }

                /* =========================================================
                   VALUE BOXES
                   ========================================================= */
                .bslib-value-box{
                  border-radius: var(--radius) !important;
                  background: rgba(255,255,255,0.06) !important;
                  border: 1px solid var(--border) !important;
                  box-shadow: var(--shadow2);
                }
                .bslib-value-box, .bslib-value-box *{
                  color: rgba(255,255,255,0.95) !important;
                }
                .bslib-value-box .value-box-title{
                  color: rgba(255,255,255,0.80) !important;
                  font-weight: 700 !important;
                }
                .bslib-value-box .value-box-value{
                  font-size: 28px !important;
                  font-weight: 900 !important;
                  letter-spacing: -0.02em;
                }

                /* =========================================================
                   TABLES (general)
                   ========================================================= */
                table{
                  color: rgba(255,255,255,0.90) !important;
                  background: transparent !important;
                }
                thead th{
                  color: rgba(255,255,255,0.90) !important;
                  font-weight: 800;
                  border-bottom: 1px solid var(--border) !important;
                  background: rgba(255,255,255,0.03) !important;
                }
                tbody td{
                  color: rgba(255,255,255,0.85) !important;
                  border-top: 1px solid rgba(255,255,255,0.10) !important;
                }

                /* =========================================================
                   FIX: Top streets table (output_table) white-on-white
                   ========================================================= */
                #top_streets table,
                #top_streets table.table,
                #top_streets .table {
                  width: 100% !important;
                  background: rgba(255,255,255,0.03) !important;
                  color: rgba(255,255,255,0.90) !important;
                  border-collapse: collapse !important;
                }
                #top_streets thead th {
                  background: rgba(255,255,255,0.06) !important;
                  color: rgba(255,255,255,0.92) !important;
                  border-bottom: 1px solid rgba(255,255,255,0.14) !important;
                  font-weight: 800 !important;
                }
                #top_streets tbody td {
                  background: transparent !important;
                  color: rgba(255,255,255,0.86) !important;
                  border-top: 1px solid rgba(255,255,255,0.10) !important;
                }
                #top_streets tbody tr:nth-child(odd) td {
                  background: rgba(255,255,255,0.02) !important;
                }
                #top_streets tbody tr:hover td {
                  background: rgba(255,255,255,0.06) !important;
                }

                /* =========================================================
                   DATE RANGE FIX (visibility + stacked layout)
                   ========================================================= */
                .shiny-date-range-input {
                  display: flex !important;
                  flex-direction: column !important;
                  gap: 6px !important;
                }
                .shiny-date-range-input .form-control {
                  width: 100% !important;
                  min-width: 100% !important;
                }
                .shiny-date-range-input span.input-group-text {
                  background: transparent !important;
                  border: none !important;
                  color: rgba(255,255,255,0.75) !important;
                  font-weight: 600;
                  padding: 0 !important;
                  margin: 2px 0 2px 0 !important;
                  text-align: center;
                  width: 100%;
                }

                }
                .shiny-date-range-input input {
                  background: rgba(0,0,0,0.14) !important;
                  color: rgba(255,255,255,0.92) !important;
                  border: 1px solid rgba(255,255,255,0.18) !important;
                  border-radius: 14px !important;
                  padding: 10px 12px !important;
                }
                .shiny-date-range-input .input-group-addon,
                .shiny-date-range-input .glyphicon {
                  color: rgba(255,255,255,0.85) !important;
                }
                
                
                /* =========================================================
                FIX: DataGrid (Top Dangerous Streets) hover + search boxes
                ========================================================= */

                /* Base DataGrid styling */
                .shiny-data-grid,
                .shiny-data-grid * {
                color: rgba(255,255,255,0.90);
                }

                /* Table background */
                .shiny-data-grid table {
                background: transparent !important;
                }

                /* Header cells */
                .shiny-data-grid thead th {
                background: rgba(255,255,255,0.06) !important;
                color: rgba(255,255,255,0.95) !important;
                font-weight: 800;
                border-bottom: 1px solid rgba(255,255,255,0.14) !important;
                }

                /* Body cells */
                .shiny-data-grid tbody td {
                background: transparent !important;
                color: rgba(255,255,255,0.88) !important;
                border-top: 1px solid rgba(255,255,255,0.10) !important;
                }

                /* 🔥 FIX 1: Row hover (white bg → black text) */
                .shiny-data-grid tbody tr:hover td {
                background: #ffffff !important;
                color: #000000 !important;
                }

                /* Also fix links/text inside hovered rows */
                .shiny-data-grid tbody tr:hover td *,
                .shiny-data-grid tbody tr:hover a {
                color: #000000 !important;
                }

                /* Zebra striping */
                .shiny-data-grid tbody tr:nth-child(odd) td {
                background: rgba(255,255,255,0.02) !important;
                }

                /* =========================================================
                FIX 2: Search / filter input boxes (black → white)
                ========================================================= */

                /* Filter row inputs */
                .shiny-data-grid input,
                .shiny-data-grid select {
                background: rgba(255,255,255,0.95) !important;
                color: #000000 !important;
                border: 1px solid rgba(0,0,0,0.25) !important;
                border-radius: 10px !important;
                padding: 6px 8px !important;
                }

                /* Placeholder text */
                .shiny-data-grid input::placeholder {
                color: rgba(0,0,0,0.55) !important;
                }

                /* Focus state */
                .shiny-data-grid input:focus,
                .shiny-data-grid select:focus {
                outline: none !important;
                box-shadow: 0 0 0 2px rgba(99,102,241,0.35) !important;
                border-color: rgba(99,102,241,0.8) !important;
                }

                /* =========================================================
                DataGrid: make header solid + show Min/Max clearly
                ========================================================= */

                /* Make the whole header area solid so rows don't show through */
                .shiny-data-grid thead,
                .shiny-data-grid thead th {
                position: sticky !important;
                top: 0 !important;
                z-index: 50 !important;
                background: #0b1220 !important;          /* solid */
                backdrop-filter: none !important;
                }

                /* If there is a second header row for filters, keep it solid too */
                .shiny-data-grid thead tr {
                background: #0b1220 !important;
                }

                /* Slight divider below header */
                .shiny-data-grid thead th {
                border-bottom: 1px solid rgba(255,255,255,0.18) !important;
                }

                /* Make filter row background slightly lighter for clarity */
                .shiny-data-grid thead tr:last-child th {
                background: rgba(255,255,255,0.06) !important;
                }

                /* Ensure filter inputs are clearly visible (white inputs + black text) */
                .shiny-data-grid thead input,
                .shiny-data-grid thead select {
                background: rgba(255,255,255,0.96) !important;
                color: #000000 !important;
                border: 1px solid rgba(0,0,0,0.25) !important;
                border-radius: 10px !important;
                padding: 6px 8px !important;
                }

                /* Make placeholder text (often used for Min/Max) visible */
                .shiny-data-grid thead input::placeholder {
                color: rgba(0,0,0,0.65) !important;  /* so "Min"/"Max" shows */
                opacity: 1 !important;
                }

                /* Some grids render "Min"/"Max" as small helper text; ensure it's visible */
                .shiny-data-grid thead small,
                .shiny-data-grid thead .text-muted,
                .shiny-data-grid thead label,
                .shiny-data-grid thead span {
                color: rgba(255,255,255,0.85) !important;
                }

                /* Prevent header overlap issues by giving the grid its own scroll container */
                .shiny-data-grid {
                overflow: auto !important;
                }

                

                /* =========================================================
                   FOOTER
                   ========================================================= */
                .footer-note{
                  color: rgba(255,255,255,0.55) !important;
                  font-size: 12px;
                  margin: 14px 0 18px 0;
                  text-align: center;
                }
                """
            ),
        ),

        ui.div(
            {"class": "hero", "style": "text-align: center;"},
            ui.div(
                {
                    "class": "hero-title",
                    "style": "font-size: 30px; font-weight: 900; justify-content: center; margin: 0;",
                },
                "New York City Road Safety Analytics Dashboard",
            ),
        ),

        ui.layout_sidebar(
            ui.sidebar(
                ui.h4(ui.tags.i(class_="bi bi-sliders"), " Filters"),
                ui.input_date_range(
                    "dates",
                    "Date range",
                    start=(nyc_now() - timedelta(days=183)).date(),
                    end=nyc_now().date(),
                ),
                ui.input_selectize(
                    "borough",
                    "Borough",
                    choices=["All"],
                    selected="All",
                    multiple=False,
                ),
                ui.input_selectize(
                    "severity",
                    "Severity (derived)",
                    choices=["All", "Fatal", "Injury", "No Injury"],
                    selected="All",
                ),
                ui.input_action_button(
                    "refresh",
                    ui.span(
                        ui.tags.i(class_="bi bi-arrow-repeat me-2"),
                        "Apply filters",
                    ),
                    class_="btn-primary",
                ),
                ui.hr(),
                ui.div(
                    {"style": "color: rgba(255,255,255,0.65); font-size: 12px; line-height: 1.4;"},
                    ui.tags.i(class_="bi bi-info-circle"),
                    " Tip: Change dates first — the Apply button activates automatically.",
                ),
            ),

            ui.navset_tab(
                ui.nav_panel(
                    ui.tags.span(ui.tags.i(class_="bi bi-speedometer2"), " Overview"),
                    ui.layout_columns(
                        ui.value_box(
                            "Total crashes",
                            ui.output_text("kpi_total"),
                            showcase=ui.tags.i(class_="bi bi-activity"),
                        ),
                        ui.value_box(
                            "Injury crashes",
                            ui.output_text("kpi_injury"),
                            showcase=ui.tags.i(class_="bi bi-bandaid"),
                        ),
                        ui.value_box(
                            "Fatal crashes",
                            ui.output_text("kpi_fatal"),
                            showcase=ui.tags.i(class_="bi bi-exclamation-triangle"),
                        ),
                        col_widths=(4, 4, 4),
                    ),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-graph-up"), " Crashes over time (daily)"),
                            output_widget("ts_daily"),
                        ),
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-bar-chart"), " Severity distribution"),
                            output_widget("sev_bar"),
                        ),
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-stars"), " Key insights (auto)"),
                            ui.output_ui("insights"),
                        ),

                        col_widths=(7, 5),
                    ),
                ),

                ui.nav_panel(
                    ui.tags.span(ui.tags.i(class_="bi bi-map"), " Hotspots Map"),
                    ui.card(
                        ui.card_header(ui.tags.i(class_="bi bi-geo"), " Crash hotspot areas"),
                        ui.div(
                            {"style": "color: rgba(255,255,255,0.65); font-size: 12px; margin: 6px 0 10px 0;"},
                            "Points are filtered to NYC bounds and sampled for performance.",
                        ),
                        output_widget("map_scatter"),
                    ),
                ),

                ui.nav_panel(
                    ui.tags.span(ui.tags.i(class_="bi bi-clock-history"), " Time Patterns"),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-grid-3x3-gap"), " Hour × Day heatmap"),
                            output_widget("heat_hour_day"),
                        ),
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-clock"), " Hourly trend"),
                            output_widget("hourly_bar"),
                        ),
                        col_widths=(7, 5),
                    ),
                ),

                ui.nav_panel(
                    ui.tags.span(ui.tags.i(class_="bi bi-shield-exclamation"), " Spatial & Borough Analysis"),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-trophy"), " Top 1000 dangerous streets/intersections"),
                            ui.p(
                                {"style": "color: rgba(255,255,255,0.65); font-size: 12px; margin: 6px 0 10px 0;"},
                                "Search, sort, and paginate the results. Ranked by fatalities, then injuries, then total crashes."
                            ),
                            ui.output_data_frame("top_streets_dt"),
                        ),
                        ui.card(
                            ui.card_header(
                                ui.tags.i(class_="bi bi-building"),
                                " Borough × Crash Count"
                            ),
                            output_widget("borough_normalized_bar"),
                        ),

                        

                        col_widths=(7, 5),
                    ),
                ),

                ui.nav_panel(
                    ui.tags.span(ui.tags.i(class_="bi bi-car-front"), " Causes & Vehicles"),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-exclamation-diamond"), " Top contributing factors"),
                            output_widget("top_factors"),
                        ),
                        ui.card(
                            ui.card_header(ui.tags.i(class_="bi bi-truck"), " Top vehicle types"),
                            output_widget("top_vehicles"),
                        ),
                        col_widths=(6, 6),
                    ),
                ),
            ),
        ),

        ui.div(
            {"class": "footer-note"},
            "Data Source: NYC Open Data (Socrata). Dashboard by Ali Sher & Meer Zamanat.",
        ),
    )


app_ui = create_app_ui()
