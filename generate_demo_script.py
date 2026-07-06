"""
Generates demo_video_script.pdf -- a full narration script for the project demo video.
Run: python generate_demo_script.py
"""

from fpdf import FPDF
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours ────────────────────────────────────────────
NAVY   = (15,  23,  42)
BLUE   = (30,  64, 175)
LBLUE  = (55, 107, 232)
ORANGE = (249,115, 22)
GREEN  = (22, 163, 74)
GREY   = (100,116,139)
LGREY  = (226,232,240)
WHITE  = (255,255,255)
BLACK  = (15,  23,  42)

# ── Helpers ───────────────────────────────────────────────────
class ScriptPDF(FPDF):
    def header(self):
        # Navy header bar
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 14, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 10)
        self.set_xy(8, 3)
        self.cell(80, 8, "BLUESTOCK FINTECH  |  Mutual Fund Analytics", ln=False)
        self.set_font("Helvetica", "", 8)
        self.set_xy(130, 3)
        self.set_text_color(148, 163, 184)
        self.cell(70, 8, "Demo Video Script  |  Capstone Project I", align="R")
        self.ln(14)

    def footer(self):
        self.set_y(-13)
        self.set_fill_color(*LGREY)
        self.rect(0, self.get_y(), 210, 13, "F")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 10,
                  f"Bluestock Fintech  |  Team: asthananeha2015 / bsoham2704 / Bubai Das"
                  f"        Page {self.page_no()}",
                  align="C")

    # ── Utility draw methods ──────────────────────────────────
    def section_header(self, number, title, subtitle="", color=BLUE):
        self.set_fill_color(*color)
        self.rect(8, self.get_y(), 194, 10, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.set_xy(11, self.get_y() + 1)
        self.cell(20, 8, f"SECTION {number}", ln=False)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title.upper())
        self.ln(10)
        if subtitle:
            self.set_text_color(*GREY)
            self.set_font("Helvetica", "I", 9)
            self.set_x(11)
            self.cell(0, 5, subtitle)
            self.ln(5)
        self.set_text_color(*BLACK)

    def timestamp_badge(self, ts):
        y = self.get_y()
        self.set_fill_color(*ORANGE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        self.set_xy(8, y)
        self.cell(26, 6, f"  {ts}", fill=True)
        self.set_xy(37, y)
        self.set_text_color(*BLACK)
        self.ln(7)

    def narration(self, text):
        """Green left-bar narration block -- what presenter says."""
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*GREEN)
        self.rect(8, y, 2, 0, "F")   # placeholder; drawn after height known
        self.set_fill_color(240, 253, 244)
        lines_before = self.get_y()
        self.set_xy(13, y)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(22, 78, 48)
        self.multi_cell(185, 5.5, text)
        height = self.get_y() - lines_before
        self.set_fill_color(*GREEN)
        self.rect(8, lines_before, 2, height, "F")
        self.set_fill_color(240, 253, 244)
        self.rect(10, lines_before, 188, height, "F")
        # re-draw text over fill
        self.set_xy(13, lines_before)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(22, 78, 48)
        self.multi_cell(185, 5.5, text)
        self.ln(2)
        self.set_text_color(*BLACK)

    def action(self, icon, text):
        """Blue action box -- what presenter does on screen."""
        y = self.get_y()
        self.set_fill_color(239, 246, 255)
        self.set_draw_color(*LBLUE)
        self.rect(8, y, 194, 7.5, "FD")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*BLUE)
        self.set_xy(11, y + 1)
        self.cell(8, 5.5, icon, ln=False)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*NAVY)
        self.multi_cell(181, 5.5, text)
        self.ln(1)
        self.set_text_color(*BLACK)

    def tip(self, text):
        """Orange tip / reminder box."""
        y = self.get_y()
        self.set_fill_color(255, 247, 237)
        self.set_fill_color(255, 247, 237)
        self.rect(8, y, 2, 6, "F")
        self.set_fill_color(255, 247, 237)
        h0 = self.get_y()
        self.set_xy(13, y)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(154, 52, 18)
        self.multi_cell(185, 5.5, f"TIP: {text}")
        ht = self.get_y() - h0
        self.set_fill_color(ORANGE[0], ORANGE[1], ORANGE[2])
        self.rect(8, h0, 2, ht, "F")
        self.set_fill_color(255, 247, 237)
        self.rect(10, h0, 188, ht, "F")
        self.set_xy(13, h0)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(154, 52, 18)
        self.multi_cell(185, 5.5, f"TIP: {text}")
        self.ln(2)
        self.set_text_color(*BLACK)

    def kpi_row(self, items):
        """Draw a row of 4 KPI boxes."""
        y = self.get_y()
        bw = 44
        for i, (val, lbl) in enumerate(items):
            x = 8 + i * (bw + 3)
            self.set_fill_color(*BLUE)
            self.rect(x, y, bw, 5, "F")
            self.set_text_color(*WHITE)
            self.set_font("Helvetica", "B", 7)
            self.set_xy(x + 1, y)
            self.cell(bw - 2, 5, lbl, align="C")
            self.set_fill_color(248, 250, 252)
            self.set_draw_color(*LGREY)
            self.rect(x, y + 5, bw, 9, "FD")
            self.set_text_color(*NAVY)
            self.set_font("Helvetica", "B", 11)
            self.set_xy(x + 1, y + 6)
            self.cell(bw - 2, 7, val, align="C")
        self.ln(17)
        self.set_text_color(*BLACK)

    def cmd_block(self, cmd):
        """Monospace command block."""
        y = self.get_y()
        self.set_fill_color(30, 41, 59)
        self.rect(8, y, 194, 9, "F")
        self.set_text_color(134, 239, 172)
        self.set_font("Courier", "B", 9.5)
        self.set_xy(14, y + 1.5)
        self.cell(0, 6, cmd)
        self.ln(11)
        self.set_text_color(*BLACK)

    def bullet(self, text, indent=11):
        self.set_x(indent)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BLACK)
        self.cell(5, 5.5, chr(149))
        self.multi_cell(183 - indent, 5.5, text)

    def gap(self, n=4):
        self.ln(n)

    def h2(self, text, color=NAVY):
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(*color)
        self.set_x(8)
        self.cell(0, 7, text)
        self.ln(7)
        self.set_text_color(*BLACK)


# ── Build PDF ─────────────────────────────────────────────────
pdf = ScriptPDF()
pdf.set_auto_page_break(True, margin=16)
pdf.set_margins(8, 16, 8)

# ═══════════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════════
pdf.add_page()

# Full navy cover background
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, 210, 297, "F")

# Blue accent stripe
pdf.set_fill_color(*BLUE)
pdf.rect(0, 110, 210, 3, "F")
pdf.set_fill_color(*ORANGE)
pdf.rect(0, 113, 210, 1.5, "F")

# Logo text
pdf.set_text_color(147, 197, 253)
pdf.set_font("Helvetica", "B", 28)
pdf.set_xy(0, 55)
pdf.cell(210, 14, "BLUESTOCK FINTECH", align="C")

pdf.set_text_color(*WHITE)
pdf.set_font("Helvetica", "B", 20)
pdf.set_xy(0, 73)
pdf.cell(210, 10, "Mutual Fund Analytics", align="C")
pdf.set_font("Helvetica", "", 13)
pdf.set_xy(0, 86)
pdf.set_text_color(148, 163, 184)
pdf.cell(210, 8, "Capstone Project  I", align="C")

# Title block
pdf.set_text_color(*WHITE)
pdf.set_font("Helvetica", "B", 22)
pdf.set_xy(0, 120)
pdf.cell(210, 12, "DEMO VIDEO SCRIPT", align="C")
pdf.set_font("Helvetica", "", 11)
pdf.set_xy(0, 135)
pdf.set_text_color(148, 163, 184)
pdf.cell(210, 7, "Full narration guide for the 4-5 minute project walkthrough", align="C")

# Meta block
pdf.set_fill_color(30, 41, 59)
pdf.rect(30, 155, 150, 68, "F")
meta = [
    ("Team Members",  "asthananeha2015  /  bsoham2704  /  Bubai Das"),
    ("Project",       "Capstone Project I  --  Mutual Fund Analytics"),
    ("Target Length", "4 to 5 minutes  (screen recording)"),
    ("Tools Covered", "Python  |  Jupyter  |  SQLite  |  PowerPoint"),
    ("Date",          "July 2026"),
]
pdf.set_font("Helvetica", "", 9)
for i, (k, v) in enumerate(meta):
    y = 160 + i * 12
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(35, y)
    pdf.cell(38, 7, k + ":", ln=False)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 7, v)
    pdf.set_font("Helvetica", "", 9)

pdf.set_text_color(148, 163, 184)
pdf.set_font("Helvetica", "I", 8.5)
pdf.set_xy(0, 248)
pdf.cell(210, 7, "Recommended tool: OBS Studio  /  Loom  /  Windows Game Bar (Win + G)", align="C")
pdf.set_xy(0, 256)
pdf.cell(210, 7, "Resolution: 1920 x 1080  |  Format: MP4", align="C")

# ═══════════════════════════════════════════════════════════════
# PAGE 2 -- Overview & Before You Start
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.set_text_color(*BLACK)

pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(*NAVY)
pdf.cell(0, 9, "VIDEO OVERVIEW & PREPARATION CHECKLIST")
pdf.ln(9)
pdf.set_text_color(*BLACK)

# Timeline table
pdf.h2("Timeline at a Glance", BLUE)
segments = [
    ("0:00 - 0:30", "Introduction",              "Greet, state project name, team, and tech stack"),
    ("0:30 - 1:45", "Dashboard Walkthrough",     "Open PPTX, walk 4 pages, explain KPIs & charts"),
    ("1:45 - 3:00", "Jupyter Notebooks",         "EDA, Performance Analytics, Advanced Analytics"),
    ("3:00 - 3:40", "Fund Recommender (CLI)",    "Run recommender.py --risk Moderate in terminal"),
    ("3:40 - 4:20", "SQLite Database",           "DB Browser, run queries, show star schema"),
    ("4:20 - 4:45", "Closing & Summary",         "Recap key findings, thank panel"),
]
pdf.set_font("Helvetica", "B", 8.5)
pdf.set_fill_color(*NAVY)
pdf.set_text_color(*WHITE)
for w, h in [(30,6),(45,6),(119,6)]:
    pass
pdf.set_xy(8, pdf.get_y())
pdf.cell(30, 6, "  Time", fill=True, border=0)
pdf.cell(47, 6, "Section", fill=True, border=0)
pdf.cell(117, 6, "What to Cover", fill=True, border=0)
pdf.ln(6)
pdf.set_font("Helvetica", "", 8.5)
for i, (t, sec, desc) in enumerate(segments):
    bg = (248,250,252) if i%2==0 else WHITE
    pdf.set_fill_color(*bg)
    pdf.set_text_color(*NAVY)
    pdf.cell(30, 6, f"  {t}", fill=True)
    pdf.set_text_color(*BLUE)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.cell(47, 6, sec, fill=True)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.cell(117, 6, desc, fill=True)
    pdf.ln(6)

pdf.gap(6)
pdf.h2("Before You Press Record -- Open These Files", BLUE)
files_to_open = [
    ("PPT_Slides/bluestock_mf_dashboard.pptx", "Open in Microsoft PowerPoint, go to Slide Show view"),
    ("Source_Code/notebooks/EDA_Analysis.ipynb", "Open in Jupyter Notebook (run all cells first)"),
    ("Source_Code/notebooks/Performance_Analytics.ipynb", "Open in Jupyter Notebook (run all cells first)"),
    ("Source_Code/notebooks/Advanced_Analytics.ipynb", "Open in Jupyter Notebook (run all cells first)"),
    ("Datasets/bluestock_mf.db", "Open in DB Browser for SQLite"),
    ("Source_Code/sql/queries.sql", "Open in a text editor beside DB Browser"),
    ("Terminal / Command Prompt", "cd to Source_Code/scripts/ before recording"),
]
for f, note in files_to_open:
    pdf.set_x(8)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*BLUE)
    pdf.cell(6, 5.5, chr(149))
    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(100, 5.5, f, ln=False)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 5.5, f"   <- {note}")
    pdf.ln(5.5)

pdf.gap(5)
pdf.tip("Run all notebook cells BEFORE recording so output is already visible. This saves time and avoids errors on camera.")


# ═══════════════════════════════════════════════════════════════
# PAGE 3 -- Section 1: Introduction
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_header(1, "Introduction", "Duration: 0:00 - 0:30  |  Screen: Desktop or title slide")
pdf.gap(4)
pdf.timestamp_badge("0:00")
pdf.narration(
    "Hello everyone! My name is Neha Asthana, and I am presenting the Bluestock Fintech "
    "Mutual Fund Analytics project -- Capstone Project I. This project was built by our "
    "team: myself, Soham Biswas, and Bubai Das."
)
pdf.gap(3)
pdf.timestamp_badge("0:08")
pdf.narration(
    "In this project, we performed an end-to-end analytics pipeline on 40 Indian mutual fund "
    "schemes across 10 fund houses -- covering data ingestion, cleaning, SQL schema design, "
    "exploratory analysis, performance metrics, advanced risk analytics, and finally a "
    "4-page interactive dashboard."
)
pdf.gap(3)
pdf.timestamp_badge("0:20")
pdf.narration(
    "Our tech stack is entirely Python-based -- using pandas, NumPy, Matplotlib, Seaborn, "
    "Plotly, SQLAlchemy with SQLite, and python-pptx for the dashboard. "
    "All code is version-controlled on GitHub."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Show the GitHub repository briefly OR show the submission folder structure on screen")
pdf.gap(3)
pdf.narration(
    "The submission is organised into five folders: Source Code, Datasets, Documentation, "
    "PPT Slides, and Demo Video. Let me now walk you through the key deliverables."
)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 -- Section 2: Dashboard Walkthrough
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_header(2, "Dashboard Walkthrough",
                   "Duration: 0:30 - 1:45  |  File: PPT_Slides/bluestock_mf_dashboard.pptx", BLUE)
pdf.gap(4)

pdf.timestamp_badge("0:30")
pdf.action(">>", "ACTION: Switch to PowerPoint -- bluestock_mf_dashboard.pptx. Start Slide Show (F5). Go to Slide 1 (Title Slide).")
pdf.narration(
    "Let us start with the dashboard. I have opened our PowerPoint presentation -- "
    "bluestock_mf_dashboard.pptx -- which contains five slides built using python-pptx "
    "with our Bluestock brand theme."
)
pdf.gap(3)

# Slide 2 - Industry Overview
pdf.h2("Slide 2 -- Industry Overview  (0:38)", BLUE)
pdf.action(">>", "ACTION: Advance to Slide 2 (Industry Overview). Highlight the 4 KPI cards at the top.")
pdf.gap(2)
pdf.kpi_row([
    ("Rs.81L Cr", "TOTAL INDUSTRY AUM"),
    ("Rs.31K Cr", "ANNUAL SIP INFLOWS"),
    ("26.12 Cr",  "TOTAL FOLIOS"),
    ("1,908",     "TOTAL SCHEMES"),
])
pdf.narration(
    "Slide 2 is our Industry Overview. At the top, you can see four KPI cards. "
    "Total Industry AUM stands at Rupees 81 Lakh Crore as of March 2026 -- reflecting "
    "the massive scale of Indian mutual fund industry. Annual SIP inflows were Rupees "
    "31,000 Crore for FY2025, showing strong retail investor participation. "
    "There are 26.12 Crore total folios and 1,908 active schemes across all AMCs."
)
pdf.gap(3)
pdf.narration(
    "The line chart below shows the AUM growth trend from 2022 to 2026 for our sample "
    "of 10 fund houses -- you can clearly see a consistent upward trend. "
    "The horizontal bar chart on the right ranks each AMC by their AUM -- "
    "with SBI Mutual Fund leading, followed by HDFC and ICICI Prudential."
)
pdf.gap(3)

# Slide 3 - Fund Performance
pdf.h2("Slide 3 -- Fund Performance  (1:00)", BLUE)
pdf.action(">>", "ACTION: Advance to Slide 3 (Fund Performance). Point to the scatter plot.")
pdf.narration(
    "Slide 3 shows Fund Performance analytics. The scatter plot on the left maps "
    "3-year annualised return on the X-axis against standard deviation -- that is, "
    "risk -- on the Y-axis. Each bubble's size represents the fund's AUM. "
    "The ideal position is the top-left: high return with low risk. "
    "You can see Large Cap and Liquid funds clustered in the lower-left, "
    "while Small Cap funds appear high-right with greater risk and greater return potential."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Point to the scorecard table on the right side.")
pdf.narration(
    "The fund scorecard table ranks the top 10 funds by Sharpe ratio -- "
    "this measures risk-adjusted return. The higher the Sharpe, the better the "
    "return per unit of risk taken. We also show 3-year return, expense ratio, "
    "and the risk grade assigned by SEBI. The NAV chart at the bottom right "
    "shows NAV growth for the top 3 equity funds indexed against the NIFTY 100 benchmark."
)
pdf.gap(3)

# Slide 4 - Investor Analytics
pdf.h2("Slide 4 -- Investor Analytics  (1:18)", BLUE)
pdf.action(">>", "ACTION: Advance to Slide 4 (Investor Analytics).")
pdf.narration(
    "Slide 4 covers Investor Analytics. The top-left bar chart shows transaction volume "
    "by state -- Maharashtra and Karnataka lead, reflecting higher financial literacy "
    "in metro cities. The donut chart breaks down total investment by type: "
    "SIP, Lumpsum, and Redemption. SIP dominates, confirming the systematic "
    "investment culture among Indian retail investors."
)
pdf.gap(3)
pdf.narration(
    "The bottom-left bar shows average SIP ticket size by age group -- "
    "interestingly, the 56-plus age group has the highest average SIP amount, "
    "suggesting retirement-focused wealth building. The bottom-right line chart "
    "tracks monthly transaction volume, showing growth from January 2024 onwards."
)
pdf.gap(3)

# Slide 5 - SIP & Market Trends
pdf.h2("Slide 5 -- SIP & Market Trends  (1:33)", BLUE)
pdf.action(">>", "ACTION: Advance to Slide 5 (SIP & Market Trends).")
pdf.narration(
    "Slide 5 is SIP and Market Trends. The large dual-axis chart at the top "
    "plots monthly SIP inflows as blue bars and the NIFTY 50 index as an orange line "
    "from 2022 to 2026. A key insight here: even during the 2024 market correction "
    "when NIFTY 50 dipped, SIP inflows continued to grow -- showing that systematic "
    "investors stay disciplined during volatility."
)
pdf.gap(3)
pdf.narration(
    "The heatmap shows net category inflows for the last 12 months -- darker orange "
    "means higher inflows. Mid Cap and Flexi Cap funds dominate inflows. "
    "The bar chart on the right shows the top 5 fund categories by net inflows "
    "for FY2025 -- Mid Cap leads with Rupees 22,000-plus Crore."
)


# ═══════════════════════════════════════════════════════════════
# PAGE 5 -- Section 3: Jupyter Notebooks
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_header(3, "Jupyter Notebooks",
                   "Duration: 1:45 - 3:00  |  Source_Code/notebooks/", GREEN)
pdf.gap(4)

pdf.timestamp_badge("1:45")
pdf.action(">>", "ACTION: Switch to browser with Jupyter Notebook. Open EDA_Analysis.ipynb.")
pdf.narration(
    "Now let us look at the Jupyter notebooks which form the analytical core of "
    "this project. I have three key notebooks to show you."
)
pdf.gap(3)

# EDA
pdf.h2("EDA_Analysis.ipynb  (1:48)", GREEN)
pdf.action(">>", "ACTION: Scroll to Cell 1 -- the imports and data loading. Then scroll to the first chart output.")
pdf.narration(
    "EDA Analysis notebook covers 15 charts generated during Day 3. Let me highlight "
    "three key ones. First -- the NAV trend chart for Large Cap funds shows that all "
    "funds trended upward from 2022 to 2026, with a visible correction in early 2024 "
    "followed by recovery."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Scroll to the AUM by AMC bar chart output.")
pdf.narration(
    "Second -- the AUM growth chart by fund house confirms SBI Mutual Fund as "
    "the largest with over 6 Lakh Crore under management. "
    "Third -- the correlation matrix shows NAV returns across funds, "
    "revealing that Large Cap funds are highly correlated with each other "
    "but less so with Small Cap funds -- a useful diversification insight."
)
pdf.gap(3)
pdf.tip("You do not need to explain every chart. Pick the 2 most interesting visuals from each notebook to keep the demo focused.")
pdf.gap(4)

# Performance Analytics
pdf.h2("Performance_Analytics.ipynb  (2:15)", GREEN)
pdf.action(">>", "ACTION: Switch to Performance_Analytics.ipynb. Scroll to the fund scorecard table output.")
pdf.narration(
    "The Performance Analytics notebook computes all standard fund metrics: "
    "CAGR for 1, 3, and 5 years; Sharpe and Sortino ratios; Alpha and Beta "
    "against the NIFTY 100 benchmark; and maximum drawdown."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Scroll to the fund scorecard CSV output cell -- show the top 5 rows.")
pdf.narration(
    "The fund scorecard ranks all 40 funds using a weighted composite score: "
    "30 percent for 3-year return rank, 25 percent for Sharpe rank, 20 percent "
    "for Alpha rank, 15 percent for expense ratio, and 10 percent for max drawdown. "
    "Our top scorer is ICICI Prudential Midcap Fund Regular with a score of 84.5 out of 100. "
    "We also computed Alpha and Beta using OLS regression -- funds with Alpha above "
    "1 percent are generating genuine excess returns beyond what the market explains."
)
pdf.gap(3)

# Advanced Analytics
pdf.h2("Advanced_Analytics.ipynb  (2:38)", GREEN)
pdf.action(">>", "ACTION: Switch to Advanced_Analytics.ipynb. Go to the VaR/CVaR section.")
pdf.narration(
    "The Advanced Analytics notebook covers Day 5 risk metrics. "
    "Section 1 shows Historical VaR and CVaR at 95 percent confidence. "
    "SBI Small Cap Direct has the worst daily VaR of negative 2.69 percent -- "
    "meaning on the worst 5 percent of trading days, investors could lose over "
    "2.69 percent of NAV. ICICI Prudential Liquid Fund shows near-zero VaR, "
    "confirming its capital-preservation role."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Scroll to the Rolling Sharpe chart output.")
pdf.narration(
    "The rolling 90-day Sharpe chart for the top 5 equity funds shows how "
    "risk-adjusted performance evolved over time. The 2024 correction is clearly "
    "visible -- Sharpe ratios dropped to near zero or negative for all funds. "
    "Mirae Asset Large Cap recovered fastest post-correction."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Scroll to SIP Continuity results.")
pdf.narration(
    "Our SIP continuity analysis found that 97.8 percent of investors with "
    "6 or more SIP transactions show average gaps greater than 35 days -- "
    "suggesting a quarterly or bi-monthly SIP pattern in this dataset. "
    "Only 2.2 percent follow strict monthly SIPs."
)


# ═══════════════════════════════════════════════════════════════
# PAGE 6 -- Section 4 & 5: Recommender + Database
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_header(4, "Fund Recommender System",
                   "Duration: 3:00 - 3:40  |  File: Source_Code/scripts/recommender.py", ORANGE)
pdf.gap(4)

pdf.timestamp_badge("3:00")
pdf.action(">>", "ACTION: Switch to terminal / command prompt. Navigate to Source_Code/scripts/")
pdf.narration(
    "Let me now demonstrate the fund recommender system. This is a standalone Python "
    "script that recommends the top 3 funds based on an investor's risk appetite -- "
    "Low, Moderate, or High -- using the Sharpe ratio as the primary ranking metric "
    "filtered by SEBI risk grade."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Type and run the following command in terminal:")
pdf.cmd_block("python recommender.py --risk Low")
pdf.narration(
    "For a Low risk appetite, the recommender returns Liquid and Gilt funds -- "
    "these have near-zero VaR and stable NAV, perfect for capital preservation."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Run again with Moderate risk:")
pdf.cmd_block("python recommender.py --risk Moderate")
pdf.narration(
    "For Moderate risk, we get Large Cap and Flexi Cap funds. "
    "Notice the higher Sharpe ratios -- these funds deliver better risk-adjusted "
    "returns while staying within a manageable volatility range."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Run once more with High risk:")
pdf.cmd_block("python recommender.py --risk High")
pdf.narration(
    "For High risk appetite -- typically younger investors with a longer time horizon -- "
    "the recommender suggests Mid Cap and ELSS funds. These show the highest "
    "3-year CAGR in our universe, though with greater drawdown risk."
)
pdf.gap(3)
pdf.tip("If the terminal is hard to read on screen, increase font size to 14pt before recording.")

pdf.gap(5)
pdf.section_header(5, "SQLite Database",
                   "Duration: 3:40 - 4:20  |  File: Datasets/bluestock_mf.db", NAVY)
pdf.gap(4)

pdf.timestamp_badge("3:40")
pdf.action(">>", "ACTION: Switch to DB Browser for SQLite with bluestock_mf.db already open.")
pdf.narration(
    "Now let us look at the data layer. We designed a star schema in SQLite "
    "with 6 tables: dim_fund, dim_date, fact_nav, fact_transactions, "
    "fact_performance, and fact_aum. This enables efficient time-based joins "
    "and slice-and-dice queries across fund, date, and investor dimensions."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Click 'Browse Data' tab. Show the dim_fund table -- scroll through a few rows.")
pdf.narration(
    "The dim_fund dimension table stores all 40 fund master records including "
    "AMFI code, fund house, scheme name, category, SEBI category code, "
    "expense ratio, benchmark, and risk grade."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Click 'Execute SQL' tab. Paste and run this query from queries.sql:")
pdf.cmd_block("SELECT f.scheme_name, p.sharpe_ratio, p.return_3yr_pct")
pdf.cmd_block("FROM fact_performance p JOIN dim_fund f ON p.amfi_code = f.amfi_code")
pdf.cmd_block("WHERE f.category = 'Equity' ORDER BY p.sharpe_ratio DESC LIMIT 5;")
pdf.narration(
    "This query joins the performance fact table with the fund dimension to show "
    "the top 5 equity funds ranked by Sharpe ratio -- a key analytical query "
    "that would power any fund comparison feature in a production system."
)
pdf.gap(3)
pdf.action(">>", "ACTION: Show one more quick query -- AUM by fund house from fact_aum:")
pdf.cmd_block("SELECT f.fund_house, SUM(a.aum_crore) AS total_aum")
pdf.cmd_block("FROM fact_aum a JOIN dim_fund f ON a.amfi_code = f.amfi_code")
pdf.cmd_block("GROUP BY f.fund_house ORDER BY total_aum DESC;")
pdf.narration(
    "This aggregation query shows total AUM per fund house -- the same data "
    "that powers the AUM by AMC bar chart in our dashboard."
)


# ═══════════════════════════════════════════════════════════════
# PAGE 7 -- Section 6: Closing + Key Findings
# ═══════════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_header(6, "Closing & Key Findings",
                   "Duration: 4:20 - 4:45  |  Screen: Dashboard or Submission Folder", NAVY)
pdf.gap(4)

pdf.timestamp_badge("4:20")
pdf.action(">>", "ACTION: Switch back to the dashboard PPTX or show the submission folder tree.")
pdf.narration(
    "To wrap up, let me summarise the five key findings from this project."
)
pdf.gap(3)

findings = [
    ("Indian MF Industry Growth",
     "Industry AUM grew consistently from 2022 to 2026 despite the 2024 correction. "
     "SIP inflows remained resilient even when NIFTY 50 dipped -- demonstrating the "
     "maturity of Indian retail investors."),
    ("Risk-Return Profile",
     "Small Cap funds offer the highest 3-year CAGR (above 28 percent) but carry "
     "the worst daily VaR of minus 2.69 percent. Liquid funds deliver near-zero risk "
     "with stable 6-7 percent annualised returns -- suitable for emergency funds."),
    ("Fund Scorecard Winner",
     "ICICI Prudential Midcap Fund Regular scored 84.5 out of 100 on our composite "
     "scorecard, balancing strong 3-year returns, a Sharpe ratio above 1.2, "
     "and a competitive expense ratio of 1.4 percent."),
    ("Investor Behaviour Insight",
     "2025 cohort investors bring Rupees 2,500 higher average SIP tickets than 2024 "
     "cohort investors -- suggesting newer investors are entering with greater "
     "financial confidence and awareness."),
    ("Portfolio Concentration Risk",
     "Axis Bluechip has the highest sector HHI of 2,968 -- heavily concentrated in "
     "a single sector. UTI Mid Cap is the most diversified with HHI of 1,241 across "
     "9 sectors. Investors should prefer low-HHI funds for true diversification."),
]

for i, (title, detail) in enumerate(findings):
    y = pdf.get_y()
    pdf.set_fill_color(*BLUE)
    pdf.rect(8, y, 7, 7, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(9, y)
    pdf.cell(6, 7, str(i+1), align="C")
    pdf.set_text_color(*NAVY)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(18, y)
    pdf.cell(0, 7, title)
    pdf.ln(7)
    pdf.set_x(18)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*BLACK)
    pdf.multi_cell(185, 5.5, detail)
    pdf.ln(3)

pdf.gap(4)
pdf.timestamp_badge("4:38")
pdf.narration(
    "This project demonstrates a complete data science pipeline -- from raw CSV ingestion "
    "to a production-ready analytics dashboard -- applied to a real-world financial domain. "
    "All code is open-source and available on our GitHub repository. "
    "Thank you for watching!"
)
pdf.gap(3)
pdf.action(">>", "ACTION: Stop recording. Save the video as MP4 and upload to submission/Demo_Video/ on Google Drive.")
pdf.gap(4)

# Final reminder box
pdf.set_fill_color(239, 246, 255)
pdf.set_draw_color(*BLUE)
pdf.rect(8, pdf.get_y(), 194, 28, "FD")
pdf.set_xy(11, pdf.get_y() + 2)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*BLUE)
pdf.cell(0, 6, "POST-RECORDING CHECKLIST")
pdf.ln(6)
checklist = [
    "Video is 4-5 minutes long and saved as MP4 (1920x1080)",
    "Upload video to submission/Demo_Video/ in Google Drive",
    "Make Google Drive folder public: Anyone with the link -> Viewer",
    "Paste the folder link in the submission form and click Submit",
]
for item in checklist:
    pdf.set_x(13)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(5, 5.5, "[ ]")
    pdf.cell(0, 5.5, item)
    pdf.ln(5.5)

# ── Save ──────────────────────────────────────────────────────
out = os.path.join(BASE, "submission", "Demo_Video", "demo_video_script.pdf")
os.makedirs(os.path.dirname(out), exist_ok=True)
pdf.output(out)
print(f"Saved: {out}")
print(f"Pages: {pdf.page}")
size_kb = os.path.getsize(out) / 1024
print(f"Size:  {size_kb:.0f} KB")
