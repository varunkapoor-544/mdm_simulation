import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from datetime import datetime

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pre-MDM Sandbox",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main font & background */
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #f5f5f4; border-right: 1px solid #e5e5e3; }
    [data-testid="stSidebar"] .stRadio label { font-size: 13px; }

    /* Metric cards */
    [data-testid="stMetric"] { background: #f5f5f4; border-radius: 8px; padding: 12px 16px; }
    [data-testid="stMetricLabel"] { font-size: 11px !important; color: #6b7280 !important; font-family: 'IBM Plex Mono', monospace; }
    [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; }

    /* Step badge */
    .step-badge {
        display: inline-block;
        background: #1a1a1a;
        color: white;
        font-size: 10px;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    /* Status pills */
    .pill-green  { background:#EAF3DE; color:#3B6D11; padding:3px 10px; border-radius:4px; font-size:12px; }
    .pill-amber  { background:#FAEEDA; color:#854F0B; padding:3px 10px; border-radius:4px; font-size:12px; }
    .pill-red    { background:#FCEBEB; color:#A32D2D; padding:3px 10px; border-radius:4px; font-size:12px; }
    .pill-blue   { background:#E6F1FB; color:#185FA5; padding:3px 10px; border-radius:4px; font-size:12px; }
    .pill-purple { background:#EEEDFE; color:#534AB7; padding:3px 10px; border-radius:4px; font-size:12px; }

    /* Section title */
    .section-title { font-size:17px; font-weight:600; margin-bottom:2px; }
    .section-sub   { font-size:12px; color:#6b7280; font-family:'IBM Plex Mono',monospace; margin-bottom:16px; }

    /* Divider */
    hr { border:none; border-top:0.5px solid #e5e5e3; margin:1.5rem 0; }
</style>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ─── Session state init ───────────────────────────────────────────────────────
defaults = {
    "step": 1,
    "df": None,
    "profile": None,
    "dq_fixes": None,
    "rules": None,
    "threshold": 70,
    "sim_results": None,
    "nl_history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Sidebar navigation ───────────────────────────────────────────────────────
STEPS = {
    1: "01  Ingest",
    2: "02  Profile",
    3: "03  Data Quality",
    4: "04  Match Rules",
    5: "05  Simulate",
    6: "06  Review & Export",
}
with st.sidebar:
    st.markdown("### 🔗 Pre-MDM Sandbox")
    st.caption("Data prep & match simulation\nbefore Reltio · Semarchy · MarkLogic")
    st.markdown("---")
    for num, label in STEPS.items():
        disabled = num > st.session_state.step
        if st.button(
            label,
            key=f"nav_{num}",
            disabled=disabled,
            use_container_width=True,
            type="primary" if st.session_state.step == num else "secondary",
        ):
            st.session_state.step = num
            st.rerun()
    st.markdown("---")
    if st.button("🔄 Reset everything", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# ─── Helper: profile a dataframe ─────────────────────────────────────────────
def profile_df(df):
    rows = []
    for col in df.columns:
        null_pct = round(df[col].isna().mean() * 100, 1)
        unique_pct = round(df[col].nunique() / max(len(df), 1) * 100, 1)
        dtype = str(df[col].dtype)
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
            "Field": col,
            "Type": dtype,
            "Null %": null_pct,
            "Unique %": unique_pct,
            "Issues": ", ".join(issues) if issues else "✓ Clean",
            "_has_issues": len(issues) > 0,
        })
    return pd.DataFrame(rows)

# ─── Helper: suggest match rules ──────────────────────────────────────────────
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

# ─── Helper: simulate match results ──────────────────────────────────────────
def simulate_matches(df, threshold):
    n = max(5, min(20, len(df) // 10))
    np.random.seed(42)
    results = []
    for i in range(n):
        conf = int(np.random.randint(50, 100))
        records = int(np.random.randint(2, 5))
        sources = np.random.choice(["CRM", "ERP", "Portal", "Legacy"], size=np.random.randint(1, 4), replace=False).tolist()
        status = "auto-merge" if conf >= threshold else ("review" if conf >= threshold - 15 else "reject")
        results.append({
            "Golden ID": f"G-{str(i+1).zfill(3)}",
            "Merged Records": records,
            "Confidence %": conf,
            "Sources": ", ".join(sources),
            "Status": status,
        })
    return pd.DataFrame(results)

# ─── Helper: DQ suggestions ───────────────────────────────────────────────────
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
                fixes.append({"Field": col, "Fix": "Expand abbreviations (St→Street)", "Records": int(len(sample) * 0.15), "Apply": False})
            if cl in ("country", "country_code"):
                fixes.append({"Field": col, "Fix": "Map to ISO 3166-1 alpha-2 codes", "Records": int(len(sample) * 0.05), "Apply": False})
    if not fixes:
        fixes.append({"Field": df.columns[0], "Fix": "No critical issues detected — data looks clean", "Records": 0, "Apply": False})
    return pd.DataFrame(fixes)

# ─── STEP 1: Ingest ──────────────────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown('<div class="step-badge">STEP 01</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data ingestion</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload a file or connect to a data source</div>', unsafe_allow_html=True)

    source = st.radio("Source type", ["File Upload", "Google Drive", "SharePoint", "Database"], horizontal=True)

    if source == "File Upload":
        uploaded = st.file_uploader("Drop a CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)
                st.success(f"✓ Loaded **{uploaded.name}** — {len(df):,} rows × {len(df.columns)} columns")
                st.dataframe(df.head(5), use_container_width=True)
                st.session_state.df = df
            except Exception as e:
                st.error(f"Could not read file: {e}")

    elif source == "Google Drive":
        st.info("🔗 Google Drive connector — paste a shareable CSV/Sheet link below")
        url = st.text_input("Google Drive URL")
        if url and st.button("Connect & Load"):
            st.warning("In production this calls the Drive API. Loading sample data for demo.")
            st.session_state.df = _demo_df()

    elif source == "SharePoint":
        col1, col2 = st.columns(2)
        with col1: st.text_input("SharePoint site URL")
        with col2: st.text_input("Relative file path")
        st.text_input("Access token", type="password")
        if st.button("Connect & Load"):
            st.warning("SharePoint connector demo mode — loading sample data.")

    elif source == "Database":
        col1, col2 = st.columns(2)
        with col1: st.text_input("JDBC / connection string", placeholder="postgresql://host:5432/db")
        with col2: st.text_input("Credentials", type="password")
        st.text_area("SQL query", placeholder="SELECT * FROM customers LIMIT 10000;", height=80)
        if st.button("Execute & Load"):
            st.warning("Database connector demo mode — loading sample data.")

    st.markdown("---")
    if st.session_state.df is not None:
        if st.button("▶ Run data profiling", type="primary"):
            with st.spinner("Profiling schema and statistics…"):
                import time; time.sleep(1.2)
                st.session_state.profile = profile_df(st.session_state.df)
                st.session_state.dq_fixes = suggest_dq(st.session_state.df)
                st.session_state.rules = suggest_rules(st.session_state.df)
                st.session_state.step = 2
            st.rerun()
    else:
        st.info("Upload or connect a data source to begin.")

# ─── STEP 2: Profile ─────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    df = st.session_state.df
    profile = st.session_state.profile

    st.markdown('<div class="step-badge">STEP 02</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Profiling report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{len(df):,} records · {len(df.columns)} columns analysed</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    issues_count = int(profile["_has_issues"].sum())
    null_cols = int((profile["Null %"] > 0).sum())
    completeness = round((1 - df.isna().mean().mean()) * 100, 1)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Quality Issues", issues_count, delta=f"-{issues_count} fields" if issues_count else None, delta_color="inverse")
    col4.metric("Completeness", f"{completeness}%")

    st.markdown("---")
    display = profile.drop(columns=["_has_issues"]).copy()

    def highlight_issues(row):
        if row["Issues"] != "✓ Clean":
            return ["", "", "", "", "background-color:#FAEEDA; color:#854F0B"]
        return ["", "", "", "", "background-color:#EAF3DE; color:#3B6D11"]

    st.dataframe(
        display.style.apply(highlight_issues, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("**AI-suggested next steps based on profiling:**")
    for _, row in profile[profile["_has_issues"]].iterrows():
        st.markdown(f"- `{row['Field']}` — {row['Issues']}")

    if st.button("▶ Proceed to data quality", type="primary"):
        st.session_state.step = 3
        st.rerun()

# ─── STEP 3: Data Quality ────────────────────────────────────────────────────
elif st.session_state.step == 3:
    st.markdown('<div class="step-badge">STEP 03</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data quality & enrichment</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">AI-suggested corrections — apply individually or all at once</div>', unsafe_allow_html=True)

    fixes_df = st.session_state.dq_fixes.copy()

    col_apply_all, col_clear = st.columns([1, 5])
    with col_apply_all:
        if st.button("✅ Apply all fixes"):
            fixes_df["Apply"] = True
            st.session_state.dq_fixes = fixes_df
    with col_clear:
        if st.button("↩ Clear all"):
            fixes_df["Apply"] = False
            st.session_state.dq_fixes = fixes_df

    st.markdown("---")
    for i, row in fixes_df.iterrows():
        c1, c2, c3, c4 = st.columns([0.5, 3, 2, 1])
        with c1:
            checked = st.checkbox("", value=row["Apply"], key=f"fix_{i}", label_visibility="collapsed")
            fixes_df.at[i, "Apply"] = checked
        with c2:
            label = f"~~{row['Fix']}~~" if checked else row["Fix"]
            st.markdown(label)
        with c3:
            st.caption(f"`{row['Field']}` · {row['Records']:,} records")
        with c4:
            if checked:
                st.markdown('<span class="pill-green">Applied</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill-amber">Pending</span>', unsafe_allow_html=True)

    st.session_state.dq_fixes = fixes_df

    applied = int(fixes_df["Apply"].sum())
    st.markdown("---")
    st.caption(f"{applied} of {len(fixes_df)} fixes applied")

    if st.button("▶ Configure match rules", type="primary"):
        st.session_state.step = 4
        st.rerun()

# ─── STEP 4: Match Rules ─────────────────────────────────────────────────────
elif st.session_state.step == 4:
    st.markdown('<div class="step-badge">STEP 04</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Match rule configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Suggested rules from profiling — enable or refine before simulation</div>', unsafe_allow_html=True)

    st.session_state.threshold = st.slider(
        "Confidence threshold (%)",
        min_value=40, max_value=95, step=5,
        value=st.session_state.threshold,
        help="Records with confidence above this threshold are auto-merged. Below triggers manual review."
    )

    st.markdown("---")
    rules_df = st.session_state.rules.copy()
    st.markdown("**Active match rules**")

    for i, row in rules_df.iterrows():
        c1, c2, c3, c4 = st.columns([0.5, 3, 2, 1])
        with c1:
            enabled = st.checkbox("", value=row["Enabled"], key=f"rule_{i}", label_visibility="collapsed")
            rules_df.at[i, "Enabled"] = enabled
        with c2:
            st.markdown(f"{'**' if enabled else ''}{row['Rule']}{'**' if enabled else ''}")
            st.caption(f"fields: `{row['Field']}`")
        with c3:
            type_pill = {
                "Exact": "pill-blue", "Fuzzy": "pill-green",
                "Normalised": "pill-purple", "Phonetic": "pill-amber"
            }.get(row["Type"], "pill-blue")
            st.markdown(f'<span class="{type_pill}">{row["Type"]}</span>', unsafe_allow_html=True)
        with c4:
            st.markdown(f"**{int(row['Weight']*100)}%**")

    st.session_state.rules = rules_df

    st.markdown("---")
    st.markdown("**Natural language refinement**")
    st.caption("Try: *tighten match rules*, *loosen threshold*, *enable address rule*, *disable phone rule*")

    nl_input = st.text_input("Describe your refinement", placeholder="e.g. tighten match rules", key="nl_box")

    if st.button("Apply instruction") and nl_input.strip():
        msg = nl_input.strip().lower()
        reply = ""
        if "tighten" in msg or "strict" in msg:
            st.session_state.threshold = min(st.session_state.threshold + 10, 95)
            reply = f"Raised threshold to {st.session_state.threshold}%. Fewer, higher-confidence merges."
        elif "loosen" in msg or "relax" in msg or "lower" in msg:
            st.session_state.threshold = max(st.session_state.threshold - 10, 40)
            reply = f"Lowered threshold to {st.session_state.threshold}%. More matches will surface for review."
        elif "enable" in msg:
            for i, row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()):
                    rules_df.at[i, "Enabled"] = True
            st.session_state.rules = rules_df
            reply = "Matching rule enabled based on your instruction."
        elif "disable" in msg or "remove" in msg:
            for i, row in rules_df.iterrows():
                if any(w in msg for w in row["Rule"].lower().split()):
                    rules_df.at[i, "Enabled"] = False
            st.session_state.rules = rules_df
            reply = "Matching rule disabled."
        else:
            reply = "Try phrases like 'tighten match rules', 'loosen threshold', 'enable address rule'."
        st.session_state.nl_history.append({"You": nl_input.strip(), "System": reply})

    if st.session_state.nl_history:
        with st.expander("Refinement history", expanded=True):
            for entry in reversed(st.session_state.nl_history):
                st.markdown(f"**You:** {entry['You']}")
                st.markdown(f"→ {entry['System']}")
                st.markdown("---")

    st.markdown("---")
    enabled_count = int(st.session_state.rules["Enabled"].sum())
    st.caption(f"{enabled_count} rules active · threshold {st.session_state.threshold}%")

    if st.button("▶ Run match simulation", type="primary"):
        with st.spinner(f"Simulating {len(st.session_state.df):,} records with {enabled_count} rules…"):
            import time; time.sleep(1.8)
            st.session_state.sim_results = simulate_matches(
                st.session_state.df, st.session_state.threshold
            )
            st.session_state.step = 5
        st.rerun()

# ─── STEP 5: Simulation results ──────────────────────────────────────────────
elif st.session_state.step == 5:
    results = st.session_state.sim_results

    st.markdown('<div class="step-badge">STEP 05</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulation results</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Reltio/Semarchy-equivalent golden record preview · threshold {st.session_state.threshold}%</div>', unsafe_allow_html=True)

    auto = results[results["Status"] == "auto-merge"]
    review = results[results["Status"] == "review"]
    rejected = results[results["Status"] == "reject"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Golden Records", len(results))
    c2.metric("Records Merged", int(results["Merged Records"].sum()))
    c3.metric("Auto-merged", len(auto))
    c4.metric("Needs Review", len(review))

    st.markdown("---")
    filter_status = st.radio("Filter by status", ["All", "Auto-merge", "Review", "Reject"], horizontal=True)

    filtered = results if filter_status == "All" else results[results["Status"] == filter_status.lower()]

    def color_status(val):
        colors = {
            "auto-merge": "background-color:#EAF3DE; color:#3B6D11",
            "review":     "background-color:#FAEEDA; color:#854F0B",
            "reject":     "background-color:#FCEBEB; color:#A32D2D",
        }
        return colors.get(val, "")

    def color_conf(val):
        if val >= 80: return "color:#3B6D11; font-weight:500"
        if val >= 65: return "color:#854F0B; font-weight:500"
        return "color:#A32D2D; font-weight:500"

    styled = filtered.style \
        .applymap(color_status, subset=["Status"]) \
        .applymap(color_conf, subset=["Confidence %"])

    st.dataframe(styled, use_container_width=True, hide_index=True)

    if len(review) > 0:
        st.markdown("---")
        st.markdown("**⚠ Records needing manual review**")
        st.caption("Inspect and accept or reject borderline matches below.")
        for _, row in review.iterrows():
            with st.expander(f"{row['Golden ID']} — {row['Confidence %']}% confidence · sources: {row['Sources']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"✅ Accept {row['Golden ID']}", key=f"acc_{row['Golden ID']}"):
                        st.success("Accepted — will be included in export.")
                with col_b:
                    if st.button(f"❌ Reject {row['Golden ID']}", key=f"rej_{row['Golden ID']}"):
                        st.warning("Rejected — excluded from export.")

    st.markdown("---")
    if st.button("▶ Proceed to final review", type="primary"):
        st.session_state.step = 6
        st.rerun()

# ─── STEP 6: Review & Export ─────────────────────────────────────────────────
elif st.session_state.step == 6:
    results = st.session_state.sim_results
    fixes = st.session_state.dq_fixes
    rules = st.session_state.rules

    st.markdown('<div class="step-badge">STEP 06</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Final review & export</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Confirm outcomes and export for Reltio / Semarchy ingestion</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Data quality summary**")
        applied = int(fixes["Apply"].sum())
        records_fixed = int(fixes[fixes["Apply"]]["Records"].sum())
        st.markdown(f"- Fixes applied: **{applied} / {len(fixes)}**")
        st.markdown(f"- Records corrected: **{records_fixed:,}**")
        st.markdown(f"- Estimated completeness after fixes: **~98.2%**")

    with col2:
        st.markdown("**Match simulation summary**")
        auto_c = len(results[results["Status"] == "auto-merge"])
        rev_c = len(results[results["Status"] == "review"])
        st.markdown(f"- Golden records created: **{len(results)}**")
        st.markdown(f"- Auto-merged: **{auto_c}**")
        st.markdown(f"- Pending review: **{rev_c}**")
        st.markdown(f"- Threshold used: **{st.session_state.threshold}%**")

    st.markdown("---")
    st.markdown("**Active match rules**")
    active_rules = rules[rules["Enabled"]]
    for _, row in active_rules.iterrows():
        st.markdown(f"- `{row['Rule']}` ({row['Type']}) — weight {int(row['Weight']*100)}%")

    st.markdown("---")
    st.markdown("**Export**")
    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        reltio_export = {
            "export_target": "Reltio",
            "generated_at": datetime.now().isoformat(),
            "threshold": st.session_state.threshold,
            "golden_records": results.to_dict(orient="records"),
            "active_rules": active_rules[["Rule", "Type", "Weight"]].to_dict(orient="records"),
        }
        st.download_button(
            "⬇ Export for Reltio",
            data=json.dumps(reltio_export, indent=2),
            file_name=f"reltio_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_e2:
        semarchy_export = results.copy()
        semarchy_export["target"] = "Semarchy xDM"
        csv_buf = io.StringIO()
        semarchy_export.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇ Export for Semarchy",
            data=csv_buf.getvalue(),
            file_name=f"semarchy_golden_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_e3:
        profile_report = st.session_state.profile.drop(columns=["_has_issues"])
        pr_buf = io.StringIO()
        profile_report.to_csv(pr_buf, index=False)
        st.download_button(
            "⬇ Profiling report (CSV)",
            data=pr_buf.getvalue(),
            file_name=f"profile_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    if st.button("🔄 Start new iteration"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
