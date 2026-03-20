import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MDM Simulation Studio | FreshGravity",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── QAForge-matched CSS ──────────────────────────────────────────────────────
# Design tokens extracted from screenshots:
#   BG main:        #111827  (dark navy, main content)
#   BG sidebar:     #1B2237  (slightly blue-navy sidebar)
#   BG card:        #1E2A3A  (card surfaces)
#   BG card light:  #FFFFFF  (white cards for data tables)
#   Accent:         #F47920  (FG orange — active nav, badges)
#   Teal gradient:  #17B8A6 → #6DC94E (login button / border style)
#   Text primary:   #FFFFFF
#   Text secondary: #94A3B8
#   Text muted:     #475569
#   Border:         #2D3F55
#   Input bg:       #0F172A

QA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── CRITICAL: force dark background on main content area ── */
.stApp {
    background-color: #111827 !important;
}
.stApp > header {
    background-color: #111827 !important;
}
[data-testid="stAppViewContainer"] {
    background-color: #111827 !important;
}
[data-testid="stMain"] {
    background-color: #111827 !important;
}
.main .block-container {
    background-color: #111827 !important;
    color: #E2E8F0 !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}
/* catch any white panel Streamlit injects */
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
section[data-testid="stSidebar"] + div,
.css-1d391kg, .css-18e3th9, .css-1y4p8pa {
    background-color: #111827 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1B2237 !important;
    border-right: 1px solid #2D3F55 !important;
    min-width: 240px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: #1B2237 !important;
    padding-top: 1.5rem !important;
}
[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}

/* Sidebar nav buttons — default (inactive) */
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: #CBD5E1 !important;
    border: 1px solid #2D3F55 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    text-align: left !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #243049 !important;
    border-color: #F47920 !important;
    color: #FFFFFF !important;
}
/* Active nav button — orange fill like screenshot */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: #F47920 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
    background: #E8671A !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #1E2A3A !important;
    border: 1px solid #2D3F55 !important;
    border-radius: 10px !important;
    padding: 18px 20px !important;
}
[data-testid="stMetricLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
}

/* ── Primary buttons — orange ── */
.stButton button[kind="primary"] {
    background: #F47920 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: background 0.15s !important;
}
.stButton button[kind="primary"]:hover {
    background: #E8671A !important;
}

/* ── Secondary buttons ── */
.stButton button[kind="secondary"] {
    background: transparent !important;
    color: #94A3B8 !important;
    border: 1px solid #2D3F55 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
.stButton button[kind="secondary"]:hover {
    border-color: #F47920 !important;
    color: #F47920 !important;
}

/* ── Download buttons — teal→green gradient (matching QAForge CTA) ── */
.stDownloadButton button {
    background: linear-gradient(90deg, #17B8A6, #6DC94E) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stDownloadButton button:hover {
    opacity: 0.9 !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: #0F172A !important;
    border: 1px solid #2D3F55 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #17B8A6 !important;
    box-shadow: 0 0 0 2px rgba(23,184,166,0.2) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: #64748B !important;
    font-size: 11px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}

/* ── Radio ── */
.stRadio label {
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    color: #CBD5E1 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ── Slider ── */
.stSlider label {
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #1E2A3A !important;
    border: 1px dashed #2D3F55 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #17B8A6 !important;
}
[data-testid="stFileUploader"] * { color: #64748B !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #2D3F55 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #1E2A3A !important;
    border: 1px solid #2D3F55 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── Alerts ── */
.stSuccess { background: rgba(109,201,78,0.12) !important; border-left: 3px solid #6DC94E !important; border-radius: 8px !important; }
.stWarning { background: rgba(244,185,66,0.12) !important; border-left: 3px solid #F4B942 !important; border-radius: 8px !important; }
.stInfo    { background: rgba(23,184,166,0.10) !important; border-left: 3px solid #17B8A6 !important; border-radius: 8px !important; }
.stError   { background: rgba(239,68,68,0.12)  !important; border-left: 3px solid #EF4444 !important; border-radius: 8px !important; }

/* ── Checkbox ── */
.stCheckbox label span { color: #CBD5E1 !important; font-size: 13px !important; }

/* ── HR ── */
hr { border: none !important; border-top: 1px solid #2D3F55 !important; margin: 1.5rem 0 !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #17B8A6 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1B2237; }
::-webkit-scrollbar-thumb { background: #2D3F55; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #F47920; }

/* ── Custom component classes ── */
.qa-step-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(23,184,166,0.12);
    border: 1px solid rgba(23,184,166,0.3);
    color: #17B8A6;
    font-size: 10px; font-weight: 700;
    padding: 3px 10px; border-radius: 4px;
    font-family: 'Inter', sans-serif;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 6px;
}
.qa-title {
    font-family: 'Inter', sans-serif;
    font-size: 24px; font-weight: 700;
    color: #FFFFFF; margin-bottom: 4px;
    letter-spacing: -0.5px;
}
.qa-sub {
    font-size: 13px; color: #64748B;
    margin-bottom: 1.5rem;
    font-family: 'Inter', sans-serif;
}
.qa-card {
    background: #1E2A3A;
    border: 1px solid #2D3F55;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.qa-card-title {
    font-family: 'Inter', sans-serif;
    font-size: 10px; font-weight: 700;
    color: #475569; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 12px;
}
.qa-row {
    display: flex; justify-content: space-between; align-items: center;
    border-top: 1px solid #1E3A52; padding: 9px 0; font-size: 13px;
}
.qa-row-label { color: #64748B; }
.qa-row-value { color: #FFFFFF; font-family: 'Inter', sans-serif; font-weight: 600; }

/* Status pills */
.pill-green  { background: rgba(109,201,78,0.15);  color: #6DC94E; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.pill-teal   { background: rgba(23,184,166,0.15);  color: #17B8A6; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.pill-orange { background: rgba(244,121,32,0.15);  color: #F47920; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.pill-red    { background: rgba(239,68,68,0.15);   color: #EF4444; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.pill-blue   { background: rgba(59,130,246,0.15);  color: #60A5FA; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.pill-purple { background: rgba(139,92,246,0.15);  color: #A78BFA; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
</style>
"""
st.markdown(QA_CSS, unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
defaults = {
    "step": 1, "df": None, "profile": None, "dq_fixes": None,
    "rules": None, "threshold": 70, "sim_results": None, "nl_history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Sidebar ──────────────────────────────────────────────────────────────────
STEPS = {
    1: "01  Ingest",
    2: "02  Profile",
    3: "03  Data Quality",
    4: "04  Match Rules",
    5: "05  Simulate",
    6: "06  Review & Export",
}

with st.sidebar:
    # Logo block — matches QAForge sidebar style
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem;">
        <div style="font-family:'Inter',sans-serif; font-weight:800; font-size:20px; color:#FFFFFF; letter-spacing:-0.5px;">
            FreshGravity
        </div>
        <div style="font-size:10px; color:#475569; letter-spacing:2px; text-transform:uppercase;
                    font-family:'Inter',sans-serif; font-weight:600; margin-top:3px;">
            MDM Simulation Studio
        </div>
    </div>
    <div style="border-top: 1px solid #2D3F55; margin-bottom: 1.25rem;"></div>
    <div style="font-size:10px; color:#475569; font-family:Inter,sans-serif; font-weight:700;
                letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
        WORKFLOW
    </div>
    """, unsafe_allow_html=True)

    for num, label in STEPS.items():
        disabled = num > st.session_state.step
        is_active = st.session_state.step == num
        if st.button(
            label,
            key=f"nav_{num}",
            disabled=disabled,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.step = num
            st.rerun()

    # Progress bar
    st.markdown("<div style='border-top:1px solid #2D3F55; margin:1.25rem 0;'></div>", unsafe_allow_html=True)
    pct = int(((st.session_state.step - 1) / 5) * 100)
    st.markdown(f"""
    <div>
        <div style="display:flex; justify-content:space-between; font-size:10px; color:#475569;
                    font-family:Inter,sans-serif; font-weight:600; letter-spacing:1px;
                    text-transform:uppercase; margin-bottom:6px;">
            <span>Progress</span>
            <span style="color:#17B8A6;">{pct}%</span>
        </div>
        <div style="height:4px; background:#2D3F55; border-radius:2px;">
            <div style="width:{pct}%; height:100%;
                        background: linear-gradient(90deg, #17B8A6, #6DC94E);
                        border-radius:2px; transition:width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    if st.button("↺  Reset", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    # Footer
    st.markdown("""
    <div style="position:fixed; bottom:1.5rem; font-size:10px; color:#2D3F55;
                font-family:Inter,sans-serif; letter-spacing:0.3px;">
        FreshGravity · MDM Simulation Studio
    </div>
    """, unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def page_header(step_label, title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom: 1.75rem;">
        <div class="qa-step-badge">● {step_label}</div>
        <div class="qa-title">{title}</div>
        <div class="qa-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def profile_df(df):
    rows = []
    for col in df.columns:
        null_pct = round(df[col].isna().mean() * 100, 1)
        unique_pct = round(df[col].nunique() / max(len(df), 1) * 100, 1)
        issues = []
        if null_pct > 5:
            issues.append(f"High nulls ({null_pct}%)")
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            if sample.str.lower().ne(sample).any() and sample.str.upper().ne(sample).any():
                issues.append("Mixed casing")
            if col.lower() in ("email", "email_address"):
                bad = sample[~sample.str.contains(r"^[^@]+@[^@]+\.[^@]+$", na=False)]
                if len(bad):
                    issues.append(f"Invalid email ({len(bad)})")
        rows.append({
            "Field": col, "Type": str(df[col].dtype),
            "Null %": null_pct, "Unique %": unique_pct,
            "Issues": ", ".join(issues) if issues else "✓ Clean",
            "_has_issues": len(issues) > 0,
        })
    return pd.DataFrame(rows)


def suggest_rules(df):
    cols = [c.lower() for c in df.columns]
    rules = []
    if any(c in cols for c in ("email", "email_address")):
        rules.append({"Rule": "Exact email match", "Field": "email", "Type": "Exact", "Weight": 1.0, "Enabled": True})
    if any(c in cols for c in ("first_name", "last_name", "name")):
        rules.append({"Rule": "Fuzzy name + DOB", "Field": "first_name + last_name + dob", "Type": "Fuzzy", "Weight": 0.85, "Enabled": True})
    if any(c in cols for c in ("phone", "phone_number", "mobile")):
        rules.append({"Rule": "Normalised phone", "Field": "phone", "Type": "Normalised", "Weight": 0.75, "Enabled": True})
    if any(c in cols for c in ("address", "street", "addr")):
        rules.append({"Rule": "Address similarity", "Field": "address + city", "Type": "Fuzzy", "Weight": 0.65, "Enabled": False})
    if any(c in cols for c in ("last_name", "surname")):
        rules.append({"Rule": "Soundex last name + city", "Field": "last_name + city", "Type": "Phonetic", "Weight": 0.55, "Enabled": False})
    if not rules:
        rules.append({"Rule": "Record ID exact match", "Field": df.columns[0], "Type": "Exact", "Weight": 1.0, "Enabled": True})
    return pd.DataFrame(rules)


def suggest_dq(df):
    fixes = []
    for col in df.columns:
        cl = col.lower()
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            if cl in ("phone", "phone_number", "mobile"):
                fixes.append({"Field": col, "Fix": "Normalise to E.164 format", "Records": int(len(sample)), "Apply": False})
            if cl in ("first_name", "last_name", "name"):
                mixed = sample[sample.str.lower().ne(sample) & sample.str.upper().ne(sample)]
                if len(mixed):
                    fixes.append({"Field": col, "Fix": "Standardise casing (Title Case)", "Records": len(mixed), "Apply": False})
            if cl in ("email", "email_address"):
                bad = sample[~sample.str.contains(r"^[^@]+@[^@]+\.[^@]+$", na=False)]
                if len(bad):
                    fixes.append({"Field": col, "Fix": "Flag invalid email addresses", "Records": len(bad), "Apply": False})
            if cl in ("dob", "date_of_birth", "birth_date"):
                fixes.append({"Field": col, "Fix": "Standardise to ISO 8601 (YYYY-MM-DD)", "Records": int(len(sample)), "Apply": False})
            if cl in ("address", "street"):
                fixes.append({"Field": col, "Fix": "Expand abbreviations (St → Street)", "Records": int(len(sample) * 0.15), "Apply": False})
            if cl in ("country", "country_code"):
                fixes.append({"Field": col, "Fix": "Map to ISO 3166-1 alpha-2 codes", "Records": int(len(sample) * 0.05), "Apply": False})
    if not fixes:
        fixes.append({"Field": df.columns[0], "Fix": "No critical issues detected", "Records": 0, "Apply": False})
    return pd.DataFrame(fixes)


def simulate_matches(df, threshold):
    n = max(5, min(20, len(df) // 10))
    np.random.seed(42)
    results = []
    for i in range(n):
        conf = int(np.random.randint(50, 100))
        records = int(np.random.randint(2, 5))
        sources = np.random.choice(["CRM", "ERP", "Portal", "Legacy"],
                                   size=np.random.randint(1, 4), replace=False).tolist()
        status = "auto-merge" if conf >= threshold else ("review" if conf >= threshold - 15 else "reject")
        results.append({
            "Golden ID": f"G-{str(i+1).zfill(3)}",
            "Merged Records": records,
            "Confidence %": conf,
            "Sources": ", ".join(sources),
            "Status": status,
        })
    return pd.DataFrame(results)


def divider():
    st.markdown("<hr>", unsafe_allow_html=True)


# ─── STEP 1: Ingest ───────────────────────────────────────────────────────────
if st.session_state.step == 1:
    page_header("STEP 01", "Data Ingestion",
                "Upload a file or connect to an enterprise data source")

    source = st.radio("Source type",
                      ["File Upload", "Google Drive", "SharePoint", "Database"],
                      horizontal=True)
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    if source == "File Upload":
        uploaded = st.file_uploader("Drop a CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.success(f"✓  **{uploaded.name}** loaded — {len(df):,} rows × {len(df.columns)} columns")
                st.dataframe(df.head(5), use_container_width=True)
                st.session_state.df = df
            except Exception as e:
                st.error(f"Could not read file: {e}")

    elif source == "Google Drive":
        st.info("Connect via a shareable CSV / Sheet link")
        st.text_input("Google Drive URL", placeholder="https://drive.google.com/...")

    elif source == "SharePoint":
        c1, c2 = st.columns(2)
        with c1: st.text_input("SharePoint site URL")
        with c2: st.text_input("Relative file path")
        st.text_input("Access token", type="password")

    elif source == "Database":
        c1, c2 = st.columns(2)
        with c1: st.text_input("Connection string", placeholder="postgresql://host:5432/db")
        with c2: st.text_input("Credentials", type="password")
        st.text_area("SQL query", placeholder="SELECT * FROM customers LIMIT 10000;", height=80)

    divider()

    if st.session_state.df is not None:
        if st.button("▶  Run Data Profiling", type="primary"):
            with st.spinner("Analysing schema and statistics…"):
                import time; time.sleep(1.2)
                st.session_state.profile  = profile_df(st.session_state.df)
                st.session_state.dq_fixes = suggest_dq(st.session_state.df)
                st.session_state.rules    = suggest_rules(st.session_state.df)
                st.session_state.step     = 2
            st.rerun()
    else:
        st.markdown(
            '<div style="color:#475569;font-size:13px;font-style:italic;">'
            'Upload or connect a data source above to begin.</div>',
            unsafe_allow_html=True,
        )


# ─── STEP 2: Profile ─────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    df = st.session_state.df
    profile = st.session_state.profile
    page_header("STEP 02", "Profiling Report",
                f"{len(df):,} records · {len(df.columns)} columns analysed")

    issues_count = int(profile["_has_issues"].sum())
    completeness = round((1 - df.isna().mean().mean()) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Columns", len(df.columns))
    c3.metric("Quality Issues", issues_count)
    c4.metric("Completeness", f"{completeness}%")

    divider()

    display = profile.drop(columns=["_has_issues"]).copy()

    def style_issues(row):
        base = ["color:#CBD5E1"] * len(row)
        base[-1] = ("color:#F4B942;font-weight:600" if row["Issues"] != "✓ Clean"
                    else "color:#6DC94E;font-weight:600")
        return base

    st.dataframe(
        display.style.apply(style_issues, axis=1),
        use_container_width=True, hide_index=True,
    )

    if profile["_has_issues"].any():
        divider()
        st.markdown(
            '<div style="font-family:Inter,sans-serif;font-size:10px;font-weight:700;'
            'color:#17B8A6;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">'
            'AI-Suggested Next Steps</div>',
            unsafe_allow_html=True,
        )
        for _, row in profile[profile["_has_issues"]].iterrows():
            st.markdown(
                f'<div style="color:#94A3B8;font-size:13px;padding:5px 0;">'
                f'→ <code style="background:#0F172A;color:#17B8A6;padding:2px 8px;'
                f'border-radius:4px;">{row["Field"]}</code>&nbsp;&nbsp;{row["Issues"]}</div>',
                unsafe_allow_html=True,
            )

    divider()
    if st.button("▶  Proceed to Data Quality", type="primary"):
        st.session_state.step = 3; st.rerun()


# ─── STEP 3: Data Quality ────────────────────────────────────────────────────
elif st.session_state.step == 3:
    page_header("STEP 03", "Data Quality & Enrichment",
                "AI-suggested corrections — apply individually or all at once")

    fixes_df = st.session_state.dq_fixes.copy()

    ca, cb, _ = st.columns([1, 1, 4])
    with ca:
        if st.button("✓  Apply all", type="primary"):
            fixes_df["Apply"] = True
            st.session_state.dq_fixes = fixes_df
    with cb:
        if st.button("✕  Clear all"):
            fixes_df["Apply"] = False
            st.session_state.dq_fixes = fixes_df

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    for i, row in fixes_df.iterrows():
        c1, c2, c3, c4 = st.columns([0.4, 3.5, 2, 1])
        with c1:
            checked = st.checkbox("", value=row["Apply"], key=f"fix_{i}",
                                  label_visibility="collapsed")
            fixes_df.at[i, "Apply"] = checked
        with c2:
            color = "#475569" if checked else "#E2E8F0"
            deco  = "line-through" if checked else "none"
            st.markdown(
                f'<div style="font-size:13px;color:{color};text-decoration:{deco};padding-top:6px;">'
                f'{row["Fix"]}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(
                f'<div style="font-size:11px;color:#475569;padding-top:8px;">'
                f'field: <span style="color:#17B8A6;">{row["Field"]}</span>'
                f' · {row["Records"]:,} records</div>', unsafe_allow_html=True)
        with c4:
            pill = ('<span class="pill-green">Applied</span>' if checked
                    else '<span class="pill-orange">Pending</span>')
            st.markdown(f'<div style="padding-top:6px;">{pill}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="border-bottom:1px solid #1E3A52;margin:5px 0;"></div>',
            unsafe_allow_html=True)

    st.session_state.dq_fixes = fixes_df
    applied = int(fixes_df["Apply"].sum())
    st.markdown(
        f'<div style="font-size:12px;color:#475569;margin-top:10px;">'
        f'{applied} of {len(fixes_df)} fixes applied</div>',
        unsafe_allow_html=True)

    divider()
    if st.button("▶  Configure Match Rules", type="primary"):
        st.session_state.step = 4; st.rerun()


# ─── STEP 4: Match Rules ─────────────────────────────────────────────────────
elif st.session_state.step == 4:
    page_header("STEP 04", "Match Rule Configuration",
                "Suggested rules from profiling — enable, adjust, and refine before simulation")

    # Threshold slider
    st.session_state.threshold = st.slider(
        "Confidence threshold (%)",
        min_value=40, max_value=95, step=5,
        value=st.session_state.threshold,
        help="Records at or above this score are auto-merged. Below triggers manual review.",
    )
    tval = st.session_state.threshold
    if tval >= 80:
        lbl, col = "Conservative — high precision", "#6DC94E"
    elif tval >= 65:
        lbl, col = "Balanced", "#F4B942"
    else:
        lbl, col = "Aggressive — higher recall", "#EF4444"
    st.markdown(
        f'<div style="font-size:11px;color:{col};font-weight:600;margin-top:-6px;margin-bottom:20px;">'
        f'{lbl}</div>', unsafe_allow_html=True)

    # Rules list
    rules_df = st.session_state.rules.copy()
    st.markdown(
        '<div style="font-size:10px;font-weight:700;color:#475569;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:12px;">Active Match Rules</div>',
        unsafe_allow_html=True)

    type_pill = {
        "Exact": "pill-blue", "Fuzzy": "pill-green",
        "Normalised": "pill-purple", "Phonetic": "pill-orange",
    }

    for i, row in rules_df.iterrows():
        op = "1" if row["Enabled"] else "0.45"
        c1, c2, c3, c4 = st.columns([0.4, 3.5, 1.5, 0.8])
        with c1:
            enabled = st.checkbox("", value=row["Enabled"], key=f"rule_{i}",
                                  label_visibility="collapsed")
            rules_df.at[i, "Enabled"] = enabled
        with c2:
            st.markdown(
                f'<div style="opacity:{op};padding-top:4px;">'
                f'<div style="font-size:13px;color:#E2E8F0;font-weight:500;">{row["Rule"]}</div>'
                f'<div style="font-size:11px;color:#475569;margin-top:2px;">'
                f'fields: <span style="color:#64748B;">{row["Field"]}</span></div></div>',
                unsafe_allow_html=True)
        with c3:
            pc = type_pill.get(row["Type"], "pill-blue")
            st.markdown(
                f'<div style="padding-top:6px;opacity:{op};">'
                f'<span class="{pc}">{row["Type"]}</span></div>',
                unsafe_allow_html=True)
        with c4:
            st.markdown(
                f'<div style="font-size:15px;font-weight:700;color:#17B8A6;'
                f'padding-top:6px;text-align:right;opacity:{op};">'
                f'{int(row["Weight"]*100)}%</div>',
                unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #1E3A52;margin:5px 0;"></div>',
                    unsafe_allow_html=True)

    st.session_state.rules = rules_df

    # NL refinement
    divider()
    st.markdown(
        '<div style="font-size:10px;font-weight:700;color:#475569;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:6px;">Natural Language Refinement</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:12px;color:#475569;margin-bottom:10px;">'
        'Try: <em>"tighten match rules"</em>, <em>"loosen threshold"</em>, '
        '<em>"enable address rule"</em>, <em>"disable phone rule"</em></div>',
        unsafe_allow_html=True)

    nl_input = st.text_input("Refine rules", placeholder="e.g. tighten match rules",
                              label_visibility="collapsed")
    if st.button("Apply instruction →", type="primary") and nl_input.strip():
        msg = nl_input.strip().lower()
        if "tighten" in msg or "strict" in msg:
            st.session_state.threshold = min(st.session_state.threshold + 10, 95)
            reply = f"Threshold raised to {st.session_state.threshold}%."
        elif "loosen" in msg or "relax" in msg or "lower" in msg:
            st.session_state.threshold = max(st.session_state.threshold - 10, 40)
            reply = f"Threshold lowered to {st.session_state.threshold}%."
        elif "enable" in msg:
            for i, row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()):
                    rules_df.at[i, "Enabled"] = True
            st.session_state.rules = rules_df
            reply = "Rule enabled."
        elif "disable" in msg or "remove" in msg:
            for i, row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()):
                    rules_df.at[i, "Enabled"] = False
            st.session_state.rules = rules_df
            reply = "Rule disabled."
        else:
            reply = "Try: 'tighten match rules', 'loosen threshold', 'enable address rule'."
        st.session_state.nl_history.append({"You": nl_input.strip(), "System": reply})

    if st.session_state.nl_history:
        with st.expander("Refinement history", expanded=True):
            for entry in reversed(st.session_state.nl_history):
                st.markdown(
                    f'<div style="font-size:13px;color:#E2E8F0;margin-bottom:4px;">'
                    f'<span style="color:#17B8A6;font-weight:600;">You:</span> {entry["You"]}</div>',
                    unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:13px;color:#64748B;margin-bottom:12px;padding-left:16px;">'
                    f'→ {entry["System"]}</div>',
                    unsafe_allow_html=True)

    divider()
    enabled_count = int(st.session_state.rules["Enabled"].sum())
    st.markdown(
        f'<div style="font-size:12px;color:#475569;margin-bottom:16px;">'
        f'{enabled_count} rules active · threshold {st.session_state.threshold}%</div>',
        unsafe_allow_html=True)

    if st.button("▶  Run Match Simulation", type="primary"):
        with st.spinner(f"Simulating {len(st.session_state.df):,} records…"):
            import time; time.sleep(1.8)
            st.session_state.sim_results = simulate_matches(
                st.session_state.df, st.session_state.threshold)
            st.session_state.step = 5
        st.rerun()


# ─── STEP 5: Simulation Results ───────────────────────────────────────────────
elif st.session_state.step == 5:
    results = st.session_state.sim_results
    page_header("STEP 05", "Simulation Results",
                f"Golden record preview · Reltio / Semarchy equivalent · threshold {st.session_state.threshold}%")

    auto     = results[results["Status"] == "auto-merge"]
    review   = results[results["Status"] == "review"]
    rejected = results[results["Status"] == "reject"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Golden Records", len(results))
    c2.metric("Records Merged", int(results["Merged Records"].sum()))
    c3.metric("Auto-merged", len(auto))
    c4.metric("Needs Review", len(review))

    # Status bar — teal/orange/red gradient strip
    total = len(results) or 1
    a_pct   = int(len(auto)     / total * 100)
    r_pct   = int(len(review)   / total * 100)
    rej_pct = 100 - a_pct - r_pct
    st.markdown(f"""
    <div style="margin: 18px 0 10px;">
        <div style="display:flex; height:8px; border-radius:4px; overflow:hidden; gap:2px;">
            <div style="flex:{max(len(auto),1)};
                        background:linear-gradient(90deg,#17B8A6,#6DC94E);"></div>
            <div style="flex:{max(len(review),1)};   background:#F47920;"></div>
            <div style="flex:{max(len(rejected),1)}; background:#EF4444;"></div>
        </div>
        <div style="display:flex; gap:20px; margin-top:8px;">
            <span style="font-size:11px;color:#6DC94E;font-weight:600;">● Auto-merge {a_pct}%</span>
            <span style="font-size:11px;color:#F47920;font-weight:600;">● Review {r_pct}%</span>
            <span style="font-size:11px;color:#EF4444;font-weight:600;">● Rejected {rej_pct}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    filter_opt = st.radio("Filter", ["All", "Auto-merge", "Review", "Reject"], horizontal=True)
    filtered = results if filter_opt == "All" else results[results["Status"] == filter_opt.lower()]

    def color_conf(val):
        if val >= 80: return "color:#6DC94E;font-weight:600"
        if val >= 65: return "color:#F4B942;font-weight:600"
        return "color:#EF4444;font-weight:600"

    def color_status(val):
        return {
            "auto-merge": "color:#6DC94E;font-weight:600",
            "review":     "color:#F47920;font-weight:600",
            "reject":     "color:#EF4444;font-weight:600",
        }.get(val, "")

    st.dataframe(
        filtered.style
            .applymap(color_status, subset=["Status"])
            .applymap(color_conf,   subset=["Confidence %"]),
        use_container_width=True, hide_index=True,
    )

    if len(review) > 0:
        divider()
        st.markdown(
            '<div style="font-size:10px;font-weight:700;color:#F47920;letter-spacing:1px;'
            'text-transform:uppercase;margin-bottom:10px;">⚠  Manual Review Required</div>',
            unsafe_allow_html=True)
        for _, row in review.iterrows():
            with st.expander(
                f"{row['Golden ID']}  ·  {row['Confidence %']}% confidence  ·  {row['Sources']}"
            ):
                ca, cb = st.columns(2)
                with ca:
                    if st.button(f"✓ Accept {row['Golden ID']}",
                                 key=f"acc_{row['Golden ID']}", type="primary"):
                        st.success("Accepted — included in export")
                with cb:
                    if st.button(f"✕ Reject {row['Golden ID']}",
                                 key=f"rej_{row['Golden ID']}"):
                        st.warning("Rejected — excluded from export")

    divider()
    if st.button("▶  Proceed to Final Review", type="primary"):
        st.session_state.step = 6; st.rerun()


# ─── STEP 6: Review & Export ─────────────────────────────────────────────────
elif st.session_state.step == 6:
    results = st.session_state.sim_results
    fixes   = st.session_state.dq_fixes
    rules   = st.session_state.rules
    page_header("STEP 06", "Review & Export",
                "Confirm outcomes and export for Reltio / Semarchy ingestion")

    c1, c2 = st.columns(2)

    with c1:
        applied       = int(fixes["Apply"].sum())
        records_fixed = int(fixes[fixes["Apply"]]["Records"].sum())
        st.markdown('<div class="qa-card"><div class="qa-card-title">Data Quality Summary</div>',
                    unsafe_allow_html=True)
        for lbl, val in [
            ("Fixes applied",            f"{applied} / {len(fixes)}"),
            ("Records corrected",        f"{records_fixed:,}"),
            ("Est. completeness",        "~98.2%"),
        ]:
            st.markdown(
                f'<div class="qa-row"><span class="qa-row-label">{lbl}</span>'
                f'<span class="qa-row-value">{val}</span></div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        auto_c = len(results[results["Status"] == "auto-merge"])
        rev_c  = len(results[results["Status"] == "review"])
        st.markdown('<div class="qa-card"><div class="qa-card-title">Match Simulation Summary</div>',
                    unsafe_allow_html=True)
        for lbl, val in [
            ("Golden records",    len(results)),
            ("Auto-merged",       auto_c),
            ("Pending review",    rev_c),
            ("Threshold used",    f"{st.session_state.threshold}%"),
        ]:
            st.markdown(
                f'<div class="qa-row"><span class="qa-row-label">{lbl}</span>'
                f'<span class="qa-row-value">{val}</span></div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    active_rules = rules[rules["Enabled"]]
    st.markdown('<div class="qa-card"><div class="qa-card-title">Active Match Rules</div>',
                unsafe_allow_html=True)
    for _, row in active_rules.iterrows():
        st.markdown(
            f'<div class="qa-row">'
            f'<span class="qa-row-label">{row["Rule"]} '
            f'<span style="color:#2D3F55;font-size:11px;">({row["Type"]})</span></span>'
            f'<span style="color:#17B8A6;font-weight:700;">{int(row["Weight"]*100)}%</span>'
            f'</div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    divider()
    st.markdown(
        '<div style="font-size:10px;font-weight:700;color:#475569;letter-spacing:1px;'
        'text-transform:uppercase;margin-bottom:14px;">Export</div>',
        unsafe_allow_html=True)

    ce1, ce2, ce3 = st.columns(3)

    with ce1:
        reltio = {
            "export_target": "Reltio",
            "generated_at":  datetime.now().isoformat(),
            "generated_by":  "FreshGravity MDM Simulation Studio",
            "threshold":     st.session_state.threshold,
            "golden_records": results.to_dict(orient="records"),
            "active_rules":   active_rules[["Rule","Type","Weight"]].to_dict(orient="records"),
        }
        st.download_button(
            "⬇  Export for Reltio",
            data=json.dumps(reltio, indent=2),
            file_name=f"reltio_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json", use_container_width=True,
        )

    with ce2:
        buf = io.StringIO()
        results.assign(target="Semarchy xDM",
                       generated_by="FreshGravity MDM Simulation Studio").to_csv(buf, index=False)
        st.download_button(
            "⬇  Export for Semarchy",
            data=buf.getvalue(),
            file_name=f"semarchy_golden_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True,
        )

    with ce3:
        pr = io.StringIO()
        st.session_state.profile.drop(columns=["_has_issues"]).to_csv(pr, index=False)
        st.download_button(
            "⬇  Profiling Report",
            data=pr.getvalue(),
            file_name=f"profile_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True,
        )

    divider()
    st.markdown(
        '<div style="font-size:11px;color:#2D3F55;text-align:center;margin-bottom:1rem;">'
        'FreshGravity · MDM Simulation Studio · Driven by Data. Inspired by Innovation.</div>',
        unsafe_allow_html=True)

    if st.button("↺  Start New Iteration"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
