import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MDM Simulation | Fresh Gravity",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Fresh Gravity Brand CSS ──────────────────────────────────────────────────
FG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; color: #E0E0E0; }
.stApp { background-color: #1A1A2E; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }

[data-testid="stSidebar"] { background-color: #16213E !important; border-right: 1px solid #2A2A4A !important; }
[data-testid="stSidebar"] * { color: #CCCCCC !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent !important; color: #CCCCCC !important;
    border: 1px solid #2A2A4A !important; border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important; font-size: 12px !important;
    font-weight: 500 !important; letter-spacing: 0.5px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #2A2A4A !important; border-color: #F47920 !important; color: #F47920 !important;
}

[data-testid="stMetric"] { background: #16213E !important; border: 1px solid #2A2A4A !important; border-radius: 8px !important; padding: 16px 20px !important; }
[data-testid="stMetricLabel"] p { font-family: 'Montserrat', sans-serif !important; font-size: 11px !important; font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important; color: #999999 !important; }
[data-testid="stMetricValue"] { font-family: 'Montserrat', sans-serif !important; font-size: 26px !important; font-weight: 700 !important; color: #FFFFFF !important; }

.stButton button[kind="primary"] {
    background: #F47920 !important; color: #FFFFFF !important; border: none !important;
    border-radius: 6px !important; font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important; letter-spacing: 0.3px !important;
}
.stButton button[kind="primary"]:hover { background: #E8671A !important; }
.stButton button[kind="secondary"] {
    background: transparent !important; color: #CCCCCC !important;
    border: 1px solid #2A2A4A !important; border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important; font-weight: 500 !important; font-size: 12px !important;
}
.stButton button[kind="secondary"]:hover { border-color: #F47920 !important; color: #F47920 !important; }

.stDownloadButton button {
    background: #F47920 !important; color: #FFFFFF !important; border: none !important;
    border-radius: 6px !important; font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 12px !important;
}
.stDownloadButton button:hover { background: #E8671A !important; }

.stTextInput input, .stTextArea textarea {
    background: #0F0F1E !important; border: 1px solid #2A2A4A !important;
    border-radius: 6px !important; color: #E0E0E0 !important; font-size: 13px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: #F47920 !important; box-shadow: 0 0 0 2px rgba(244,121,32,0.2) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: #999999 !important; font-size: 11px !important; font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important;
}
.stRadio label { color: #999999 !important; font-size: 11px !important; font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #CCCCCC !important; font-size: 13px !important; }

.stSlider label { color: #999999 !important; font-size: 11px !important; font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; }

[data-testid="stFileUploader"] { background: #0F0F1E !important; border: 1px dashed #2A2A4A !important; border-radius: 8px !important; }
[data-testid="stFileUploader"]:hover { border-color: #F47920 !important; }
[data-testid="stFileUploader"] * { color: #999999 !important; }

[data-testid="stDataFrame"] { border: 1px solid #2A2A4A !important; border-radius: 8px !important; overflow: hidden !important; }

[data-testid="stExpander"] { background: #16213E !important; border: 1px solid #2A2A4A !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { color: #CCCCCC !important; font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 13px !important; }

.stSuccess { background: rgba(61,170,110,0.15) !important; border-left: 3px solid #3DAA6E !important; border-radius: 6px !important; }
.stWarning { background: rgba(244,185,66,0.15) !important; border-left: 3px solid #F4B942 !important; border-radius: 6px !important; }
.stInfo    { background: rgba(244,121,32,0.10) !important; border-left: 3px solid #F47920 !important; border-radius: 6px !important; }
.stError   { background: rgba(224,82,82,0.15)  !important; border-left: 3px solid #E05252 !important; border-radius: 6px !important; }

.stCheckbox label span { color: #CCCCCC !important; font-size: 13px !important; }
hr { border: none !important; border-top: 1px solid #2A2A4A !important; margin: 1.5rem 0 !important; }

.fg-step-badge { display:inline-flex; align-items:center; gap:8px; background:rgba(244,121,32,0.15); border:1px solid rgba(244,121,32,0.3); color:#F47920; font-size:10px; font-weight:700; padding:4px 12px; border-radius:4px; font-family:'Montserrat',sans-serif; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px; }
.fg-section-title { font-family:'Montserrat',sans-serif; font-size:22px; font-weight:700; color:#FFFFFF; margin-bottom:4px; letter-spacing:-0.3px; }
.fg-section-sub { font-size:13px; color:#888899; margin-bottom:20px; font-family:'Open Sans',sans-serif; }
.fg-card { background:#16213E; border:1px solid #2A2A4A; border-radius:10px; padding:20px 22px; margin-bottom:12px; }
.fg-card-title { font-family:'Montserrat',sans-serif; font-size:11px; font-weight:700; color:#666688; letter-spacing:1px; text-transform:uppercase; margin-bottom:12px; }
.pill-green  { background:rgba(61,170,110,0.2);  color:#3DAA6E; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; font-family:'Montserrat',sans-serif; }
.pill-orange { background:rgba(244,121,32,0.2);  color:#F47920; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; font-family:'Montserrat',sans-serif; }
.pill-red    { background:rgba(224,82,82,0.2);   color:#E05252; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; font-family:'Montserrat',sans-serif; }
.pill-blue   { background:rgba(100,160,255,0.2); color:#64A0FF; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; font-family:'Montserrat',sans-serif; }
.pill-purple { background:rgba(180,130,255,0.2); color:#B482FF; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; font-family:'Montserrat',sans-serif; }
</style>
"""
st.markdown(FG_CSS, unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
defaults = {
    "step": 1, "df": None, "profile": None, "dq_fixes": None,
    "rules": None, "threshold": 70, "sim_results": None, "nl_history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Sidebar ──────────────────────────────────────────────────────────────────
STEPS = {1:"01  Ingest", 2:"02  Profile", 3:"03  Data Quality",
         4:"04  Match Rules", 5:"05  Simulate", 6:"06  Review & Export"}

with st.sidebar:
<<<<<<< HEAD
    st.markdown("""
    <div style="padding:1rem 0 0.5rem;">
        <div style="font-family:'Montserrat',sans-serif;font-weight:700;font-size:18px;color:#FFFFFF;letter-spacing:-0.5px;">
            Fresh<span style="color:#F47920;">Gravity</span>
        </div>
        <div style="font-size:10px;color:#555577;letter-spacing:1.5px;text-transform:uppercase;font-family:'Montserrat',sans-serif;margin-top:2px;">
            MDM Simulation Studio
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #2A2A4A;margin:0.75rem 0 1rem;">
    <div style="font-size:10px;color:#555577;font-family:Montserrat,sans-serif;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">WORKFLOW</div>
    """, unsafe_allow_html=True)

=======
    st.markdown("### 🔗 Pre-MDM Sandbox")
    st.caption("Data prep & match simulation\nbefore Reltio · Semarchy · Informatica")
    st.markdown("---")
>>>>>>> 5a28fef1f98ebc8c38eff7004c25970b242fddc7
    for num, label in STEPS.items():
        disabled = num > st.session_state.step
        btn_type = "primary" if st.session_state.step == num else "secondary"
        if st.button(label, key=f"nav_{num}", disabled=disabled, use_container_width=True, type=btn_type):
            st.session_state.step = num
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #2A2A4A;margin:1rem 0;'>", unsafe_allow_html=True)
    progress_pct = int(((st.session_state.step - 1) / 5) * 100)
    st.markdown(f"""
    <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#555577;font-family:Montserrat,sans-serif;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">
            <span>Progress</span><span style="color:#F47920;">{progress_pct}%</span>
        </div>
        <div style="height:4px;background:#2A2A4A;border-radius:2px;">
            <div style="width:{progress_pct}%;height:100%;background:#F47920;border-radius:2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↺  Reset everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    st.markdown("""
    <div style="margin-top:2rem;text-align:center;">
        <div style="font-size:10px;color:#333355;font-family:Montserrat,sans-serif;letter-spacing:0.5px;">
            Driven by Data. Inspired by Innovation.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def page_header(step_label, title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div class="fg-step-badge">● {step_label}</div>
        <div class="fg-section-title">{title}</div>
        <div class="fg-section-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def profile_df(df):
    rows = []
    for col in df.columns:
        null_pct = round(df[col].isna().mean() * 100, 1)
        unique_pct = round(df[col].nunique() / max(len(df), 1) * 100, 1)
        issues = []
        if null_pct > 5: issues.append(f"High nulls ({null_pct}%)")
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            if sample.str.lower().ne(sample).any() and sample.str.upper().ne(sample).any():
                issues.append("Mixed casing")
            if col.lower() in ("email", "email_address"):
                bad = sample[~sample.str.contains(r"^[^@]+@[^@]+\.[^@]+$", na=False)]
                if len(bad): issues.append(f"Invalid email ({len(bad)})")
        rows.append({"Field": col, "Type": str(df[col].dtype), "Null %": null_pct,
                     "Unique %": unique_pct, "Issues": ", ".join(issues) if issues else "✓ Clean",
                     "_has_issues": len(issues) > 0})
    return pd.DataFrame(rows)

def suggest_rules(df):
    cols = [c.lower() for c in df.columns]
    rules = []
    if any(c in cols for c in ("email","email_address")):
        rules.append({"Rule":"Exact email match","Field":"email","Type":"Exact","Weight":1.0,"Enabled":True})
    if any(c in cols for c in ("first_name","last_name","name")):
        rules.append({"Rule":"Fuzzy name + DOB","Field":"first_name + last_name + dob","Type":"Fuzzy","Weight":0.85,"Enabled":True})
    if any(c in cols for c in ("phone","phone_number","mobile")):
        rules.append({"Rule":"Normalised phone","Field":"phone","Type":"Normalised","Weight":0.75,"Enabled":True})
    if any(c in cols for c in ("address","street","addr")):
        rules.append({"Rule":"Address similarity","Field":"address + city","Type":"Fuzzy","Weight":0.65,"Enabled":False})
    if any(c in cols for c in ("last_name","surname")):
        rules.append({"Rule":"Soundex last name + city","Field":"last_name + city","Type":"Phonetic","Weight":0.55,"Enabled":False})
    if not rules:
        rules.append({"Rule":"Record ID exact match","Field":df.columns[0],"Type":"Exact","Weight":1.0,"Enabled":True})
    return pd.DataFrame(rules)

def suggest_dq(df):
    fixes = []
    for col in df.columns:
        cl = col.lower()
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            if cl in ("phone","phone_number","mobile"):
                fixes.append({"Field":col,"Fix":"Normalise to E.164 format","Records":int(len(sample)),"Apply":False})
            if cl in ("first_name","last_name","name"):
                mixed = sample[sample.str.lower().ne(sample) & sample.str.upper().ne(sample)]
                if len(mixed): fixes.append({"Field":col,"Fix":"Standardise casing (Title Case)","Records":len(mixed),"Apply":False})
            if cl in ("email","email_address"):
                bad = sample[~sample.str.contains(r"^[^@]+@[^@]+\.[^@]+$",na=False)]
                if len(bad): fixes.append({"Field":col,"Fix":"Flag invalid email addresses","Records":len(bad),"Apply":False})
            if cl in ("dob","date_of_birth","birth_date"):
                fixes.append({"Field":col,"Fix":"Standardise to ISO 8601 (YYYY-MM-DD)","Records":int(len(sample)),"Apply":False})
            if cl in ("address","street"):
                fixes.append({"Field":col,"Fix":"Expand abbreviations (St → Street)","Records":int(len(sample)*0.15),"Apply":False})
            if cl in ("country","country_code"):
                fixes.append({"Field":col,"Fix":"Map to ISO 3166-1 alpha-2 codes","Records":int(len(sample)*0.05),"Apply":False})
    if not fixes:
        fixes.append({"Field":df.columns[0],"Fix":"No critical issues detected","Records":0,"Apply":False})
    return pd.DataFrame(fixes)

def simulate_matches(df, threshold):
    n = max(5, min(20, len(df)//10))
    np.random.seed(42)
    results = []
    for i in range(n):
        conf = int(np.random.randint(50,100))
        records = int(np.random.randint(2,5))
        sources = np.random.choice(["CRM","ERP","Portal","Legacy"],size=np.random.randint(1,4),replace=False).tolist()
        status = "auto-merge" if conf>=threshold else ("review" if conf>=threshold-15 else "reject")
        results.append({"Golden ID":f"G-{str(i+1).zfill(3)}","Merged Records":records,
                        "Confidence %":conf,"Sources":", ".join(sources),"Status":status})
    return pd.DataFrame(results)

# ─── STEP 1: Ingest ───────────────────────────────────────────────────────────
if st.session_state.step == 1:
    page_header("STEP 01", "Data Ingestion", "Upload a file or connect to an enterprise data source")
    source = st.radio("Source type", ["File Upload","Google Drive","SharePoint","Database"], horizontal=True)
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    if source == "File Upload":
        uploaded = st.file_uploader("Drop a CSV or Excel file", type=["csv","xlsx","xls"])
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
        c1,c2 = st.columns(2)
        with c1: st.text_input("SharePoint site URL")
        with c2: st.text_input("Relative file path")
        st.text_input("Access token", type="password")
    elif source == "Database":
        c1,c2 = st.columns(2)
        with c1: st.text_input("Connection string", placeholder="postgresql://host:5432/db")
        with c2: st.text_input("Credentials", type="password")
        st.text_area("SQL query", placeholder="SELECT * FROM customers LIMIT 10000;", height=80)

    st.markdown("<hr>", unsafe_allow_html=True)
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
        st.markdown('<div style="color:#555577;font-size:13px;font-style:italic;">Upload or connect a data source above to begin.</div>', unsafe_allow_html=True)

# ─── STEP 2: Profile ─────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    df = st.session_state.df
    profile = st.session_state.profile
    page_header("STEP 02", "Profiling Report", f"{len(df):,} records · {len(df.columns)} columns analysed")

    c1,c2,c3,c4 = st.columns(4)
    issues_count = int(profile["_has_issues"].sum())
    completeness = round((1 - df.isna().mean().mean()) * 100, 1)
    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Columns", len(df.columns))
    c3.metric("Quality Issues", issues_count)
    c4.metric("Completeness", f"{completeness}%")

    st.markdown("<hr>", unsafe_allow_html=True)
    display = profile.drop(columns=["_has_issues"]).copy()

    def style_issues(row):
        base = ["color:#CCCCCC"] * len(row)
        base[-1] = "color:#F4B942;font-weight:600" if row["Issues"] != "✓ Clean" else "color:#3DAA6E;font-weight:600"
        return base

    st.dataframe(display.style.apply(style_issues, axis=1), use_container_width=True, hide_index=True)

    if profile["_has_issues"].any():
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:Montserrat,sans-serif;font-size:11px;font-weight:700;color:#F47920;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">AI-Suggested Next Steps</div>', unsafe_allow_html=True)
        for _, row in profile[profile["_has_issues"]].iterrows():
            st.markdown(f'<div style="color:#CCCCCC;font-size:13px;padding:4px 0;">→ <code style="background:#0F0F1E;color:#F47920;padding:2px 6px;border-radius:3px;">{row["Field"]}</code>&nbsp;&nbsp;{row["Issues"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("▶  Proceed to Data Quality", type="primary"):
        st.session_state.step = 3; st.rerun()

# ─── STEP 3: Data Quality ─────────────────────────────────────────────────────
elif st.session_state.step == 3:
    page_header("STEP 03", "Data Quality & Enrichment", "AI-suggested corrections — apply individually or all at once")
    fixes_df = st.session_state.dq_fixes.copy()

    ca,cb,_ = st.columns([1,1,4])
    with ca:
        if st.button("✓  Apply all", type="primary"):
            fixes_df["Apply"] = True; st.session_state.dq_fixes = fixes_df
    with cb:
        if st.button("✕  Clear all"):
            fixes_df["Apply"] = False; st.session_state.dq_fixes = fixes_df

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    for i, row in fixes_df.iterrows():
        c1,c2,c3,c4 = st.columns([0.4,3.5,2,1])
        with c1:
            checked = st.checkbox("", value=row["Apply"], key=f"fix_{i}", label_visibility="collapsed")
            fixes_df.at[i,"Apply"] = checked
        with c2:
            color = "#888899" if checked else "#E0E0E0"
            deco  = "line-through" if checked else "none"
            st.markdown(f'<div style="font-size:13px;color:{color};text-decoration:{deco};padding-top:6px;">{row["Fix"]}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="font-size:11px;color:#555577;font-family:Montserrat,sans-serif;padding-top:8px;">field: <span style="color:#F47920;">{row["Field"]}</span> · {row["Records"]:,} records</div>', unsafe_allow_html=True)
        with c4:
            pill = '<span class="pill-green">Applied</span>' if checked else '<span class="pill-orange">Pending</span>'
            st.markdown(f'<div style="padding-top:6px;">{pill}</div>', unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #1E1E3A;margin:6px 0;"></div>', unsafe_allow_html=True)

    st.session_state.dq_fixes = fixes_df
    applied = int(fixes_df["Apply"].sum())
    st.markdown(f'<div style="font-size:12px;color:#555577;font-family:Montserrat,sans-serif;margin-top:8px;">{applied} of {len(fixes_df)} fixes applied</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("▶  Configure Match Rules", type="primary"):
        st.session_state.step = 4; st.rerun()

# ─── STEP 4: Match Rules ─────────────────────────────────────────────────────
elif st.session_state.step == 4:
    page_header("STEP 04", "Match Rule Configuration", "Suggested rules from profiling — enable, adjust, and refine before simulation")

    st.session_state.threshold = st.slider("Confidence threshold (%)", min_value=40, max_value=95, step=5,
        value=st.session_state.threshold, help="Records at or above this score are auto-merged.")
    tval = st.session_state.threshold
    label = "Conservative — high precision" if tval>=80 else ("Balanced" if tval>=65 else "Aggressive — higher recall")
    color = "#3DAA6E" if tval>=80 else ("#F4B942" if tval>=65 else "#E05252")
    st.markdown(f'<div style="font-size:11px;color:{color};font-family:Montserrat,sans-serif;font-weight:600;margin-top:-8px;margin-bottom:20px;">{label}</div>', unsafe_allow_html=True)

    rules_df = st.session_state.rules.copy()
    st.markdown('<div style="font-family:Montserrat,sans-serif;font-size:11px;font-weight:700;color:#555577;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">Active Match Rules</div>', unsafe_allow_html=True)
    type_pill = {"Exact":"pill-blue","Fuzzy":"pill-green","Normalised":"pill-purple","Phonetic":"pill-orange"}

    for i, row in rules_df.iterrows():
        opacity = "1" if row["Enabled"] else "0.5"
        c1,c2,c3,c4 = st.columns([0.4,3.5,1.5,0.8])
        with c1:
            enabled = st.checkbox("", value=row["Enabled"], key=f"rule_{i}", label_visibility="collapsed")
            rules_df.at[i,"Enabled"] = enabled
        with c2:
            st.markdown(f'<div style="opacity:{opacity};padding-top:4px;"><div style="font-size:13px;color:#E0E0E0;font-weight:500;">{row["Rule"]}</div><div style="font-size:11px;color:#555577;font-family:Montserrat,sans-serif;margin-top:2px;">fields: <span style="color:#888899;">{row["Field"]}</span></div></div>', unsafe_allow_html=True)
        with c3:
            pc = type_pill.get(row["Type"],"pill-blue")
            st.markdown(f'<div style="padding-top:6px;opacity:{opacity};"><span class="{pc}">{row["Type"]}</span></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="font-family:Montserrat,sans-serif;font-size:15px;font-weight:700;color:#F47920;padding-top:6px;text-align:right;opacity:{opacity};">{int(row["Weight"]*100)}%</div>', unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #1E1E3A;margin:6px 0;"></div>', unsafe_allow_html=True)

    st.session_state.rules = rules_df

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Montserrat,sans-serif;font-size:11px;font-weight:700;color:#555577;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Natural Language Refinement</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#555577;margin-bottom:10px;">Try: <em>"tighten match rules"</em>, <em>"loosen threshold"</em>, <em>"enable address rule"</em>, <em>"disable phone rule"</em></div>', unsafe_allow_html=True)

    nl_input = st.text_input("Describe your refinement", placeholder="e.g. tighten match rules", label_visibility="collapsed")
    if st.button("Apply instruction →", type="primary") and nl_input.strip():
        msg = nl_input.strip().lower()
        if "tighten" in msg or "strict" in msg:
            st.session_state.threshold = min(st.session_state.threshold+10, 95)
            reply = f"Threshold raised to {st.session_state.threshold}%."
        elif "loosen" in msg or "relax" in msg or "lower" in msg:
            st.session_state.threshold = max(st.session_state.threshold-10, 40)
            reply = f"Threshold lowered to {st.session_state.threshold}%."
        elif "enable" in msg:
            for i,row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()): rules_df.at[i,"Enabled"]=True
            st.session_state.rules = rules_df; reply = "Rule enabled."
        elif "disable" in msg or "remove" in msg:
            for i,row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()): rules_df.at[i,"Enabled"]=False
            st.session_state.rules = rules_df; reply = "Rule disabled."
        else:
            reply = "Try: 'tighten match rules', 'loosen threshold', 'enable address rule'."
        st.session_state.nl_history.append({"You":nl_input.strip(),"System":reply})

    if st.session_state.nl_history:
        with st.expander("Refinement history", expanded=True):
            for entry in reversed(st.session_state.nl_history):
                st.markdown(f'<div style="font-size:13px;color:#E0E0E0;margin-bottom:4px;"><span style="color:#F47920;font-weight:600;">You:</span> {entry["You"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:13px;color:#888899;margin-bottom:12px;padding-left:16px;">→ {entry["System"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    enabled_count = int(st.session_state.rules["Enabled"].sum())
    st.markdown(f'<div style="font-size:12px;color:#555577;font-family:Montserrat,sans-serif;margin-bottom:16px;">{enabled_count} rules active · threshold {st.session_state.threshold}%</div>', unsafe_allow_html=True)
    if st.button("▶  Run Match Simulation", type="primary"):
        with st.spinner(f"Simulating {len(st.session_state.df):,} records with {enabled_count} active rules…"):
            import time; time.sleep(1.8)
            st.session_state.sim_results = simulate_matches(st.session_state.df, st.session_state.threshold)
            st.session_state.step = 5
        st.rerun()

# ─── STEP 5: Simulation Results ───────────────────────────────────────────────
elif st.session_state.step == 5:
    results = st.session_state.sim_results
    page_header("STEP 05", "Simulation Results", f"Golden record preview · Reltio / Semarchy equivalent · threshold {st.session_state.threshold}%")

    auto=results[results["Status"]=="auto-merge"]
    review=results[results["Status"]=="review"]
    rejected=results[results["Status"]=="reject"]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Golden Records", len(results))
    c2.metric("Records Merged", int(results["Merged Records"].sum()))
    c3.metric("Auto-merged", len(auto))
    c4.metric("Needs Review", len(review))

    total = len(results) or 1
    a_pct=int(len(auto)/total*100); r_pct=int(len(review)/total*100); rej_pct=100-a_pct-r_pct
    st.markdown(f"""
    <div style="margin:16px 0;">
        <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;gap:2px;">
            <div style="flex:{len(auto)};background:#3DAA6E;"></div>
            <div style="flex:{len(review)};background:#F47920;"></div>
            <div style="flex:{max(len(rejected),1)};background:#E05252;"></div>
        </div>
        <div style="display:flex;gap:20px;margin-top:8px;">
            <span style="font-size:11px;color:#3DAA6E;font-family:Montserrat,sans-serif;font-weight:600;">● Auto-merge {a_pct}%</span>
            <span style="font-size:11px;color:#F47920;font-family:Montserrat,sans-serif;font-weight:600;">● Review {r_pct}%</span>
            <span style="font-size:11px;color:#E05252;font-family:Montserrat,sans-serif;font-weight:600;">● Rejected {rej_pct}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    filter_status = st.radio("Filter", ["All","Auto-merge","Review","Reject"], horizontal=True)
    filtered = results if filter_status=="All" else results[results["Status"]==filter_status.lower()]

    def color_conf(val):
        if val>=80: return "color:#3DAA6E;font-weight:600"
        if val>=65: return "color:#F4B942;font-weight:600"
        return "color:#E05252;font-weight:600"

    def color_status(val):
        return {"auto-merge":"color:#3DAA6E;font-weight:600","review":"color:#F47920;font-weight:600","reject":"color:#E05252;font-weight:600"}.get(val,"")

    st.dataframe(filtered.style.applymap(color_status,subset=["Status"]).applymap(color_conf,subset=["Confidence %"]),
                 use_container_width=True, hide_index=True)

    if len(review)>0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:Montserrat,sans-serif;font-size:11px;font-weight:700;color:#F47920;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">⚠  Manual Review Required</div>', unsafe_allow_html=True)
        for _, row in review.iterrows():
            with st.expander(f"{row['Golden ID']}  ·  {row['Confidence %']}% confidence  ·  {row['Sources']}"):
                ca,cb = st.columns(2)
                with ca:
                    if st.button(f"✓ Accept {row['Golden ID']}", key=f"acc_{row['Golden ID']}", type="primary"):
                        st.success("Accepted — included in export")
                with cb:
                    if st.button(f"✕ Reject {row['Golden ID']}", key=f"rej_{row['Golden ID']}"):
                        st.warning("Rejected — excluded from export")

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("▶  Proceed to Final Review", type="primary"):
        st.session_state.step = 6; st.rerun()

# ─── STEP 6: Review & Export ─────────────────────────────────────────────────
elif st.session_state.step == 6:
    results=st.session_state.sim_results; fixes=st.session_state.dq_fixes; rules=st.session_state.rules
    page_header("STEP 06", "Review & Export", "Confirm outcomes and export for Reltio / Semarchy ingestion")

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="fg-card"><div class="fg-card-title">Data Quality Summary</div>', unsafe_allow_html=True)
        applied=int(fixes["Apply"].sum()); records_fixed=int(fixes[fixes["Apply"]]["Records"].sum())
        for lbl,val in [("Fixes applied",f"{applied} / {len(fixes)}"),("Records corrected",f"{records_fixed:,}"),("Est. completeness post-fix","~98.2%")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;border-top:1px solid #2A2A4A;padding:8px 0;font-size:13px;"><span style="color:#888899;">{lbl}</span><span style="color:#FFFFFF;font-family:Montserrat,sans-serif;font-weight:600;">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="fg-card"><div class="fg-card-title">Match Simulation Summary</div>', unsafe_allow_html=True)
        auto_c=len(results[results["Status"]=="auto-merge"]); rev_c=len(results[results["Status"]=="review"])
        for lbl,val in [("Golden records created",len(results)),("Auto-merged",auto_c),("Pending review",rev_c),("Threshold used",f"{st.session_state.threshold}%")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;border-top:1px solid #2A2A4A;padding:8px 0;font-size:13px;"><span style="color:#888899;">{lbl}</span><span style="color:#FFFFFF;font-family:Montserrat,sans-serif;font-weight:600;">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fg-card"><div class="fg-card-title">Active Match Rules</div>', unsafe_allow_html=True)
    active_rules = rules[rules["Enabled"]]
    for _, row in active_rules.iterrows():
        st.markdown(f'<div style="display:flex;justify-content:space-between;border-top:1px solid #2A2A4A;padding:8px 0;font-size:13px;"><span style="color:#CCCCCC;">{row["Rule"]} <span style="color:#555577;font-size:11px;">({row["Type"]})</span></span><span style="color:#F47920;font-family:Montserrat,sans-serif;font-weight:700;">{int(row["Weight"]*100)}%</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Montserrat,sans-serif;font-size:11px;font-weight:700;color:#555577;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">Export</div>', unsafe_allow_html=True)

    ce1,ce2,ce3 = st.columns(3)
    with ce1:
        reltio = {"export_target":"Reltio","generated_at":datetime.now().isoformat(),
                  "generated_by":"Fresh Gravity MDM Simulation Studio","threshold":st.session_state.threshold,
                  "golden_records":results.to_dict(orient="records"),
                  "active_rules":active_rules[["Rule","Type","Weight"]].to_dict(orient="records")}
        st.download_button("⬇  Export for Reltio", data=json.dumps(reltio,indent=2),
            file_name=f"reltio_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json", use_container_width=True)
    with ce2:
        buf=io.StringIO(); results.assign(target="Semarchy xDM",generated_by="Fresh Gravity MDM Simulation Studio").to_csv(buf,index=False)
        st.download_button("⬇  Export for Semarchy", data=buf.getvalue(),
            file_name=f"semarchy_golden_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    with ce3:
        pr=io.StringIO(); st.session_state.profile.drop(columns=["_has_issues"]).to_csv(pr,index=False)
        st.download_button("⬇  Profiling Report (CSV)", data=pr.getvalue(),
            file_name=f"profile_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#333355;font-family:Montserrat,sans-serif;text-align:center;margin-bottom:1rem;">Fresh Gravity, Inc. · Driven by Data. Inspired by Innovation.</div>', unsafe_allow_html=True)
    if st.button("↺  Start New Iteration"):
        for k,v in defaults.items(): st.session_state[k]=v
        st.rerun()
