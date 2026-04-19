import streamlit as st
import os
from audit_chain import generate_document, audit_document
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactLens – Hallucination Audit",
    page_icon="🔬",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0d0d0d;
    color: #f0ede8;
}

.stApp {
    background: #0d0d0d;
}

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f5a623 0%, #e05c2a 50%, #c0392b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    color: #888;
    font-size: 1rem;
    letter-spacing: 0.05em;
    font-family: 'Space Mono', monospace;
    margin-bottom: 2rem;
}

.claim-card {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    border-left: 4px solid;
    background: #1a1a1a;
    font-size: 0.93rem;
}

.claim-verified   { border-color: #27ae60; }
.claim-unverified { border-color: #f39c12; }
.claim-hallucination { border-color: #e74c3c; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    margin-right: 8px;
}
.badge-v  { background: #1a3d2b; color: #2ecc71; }
.badge-u  { background: #3d2f0a; color: #f39c12; }
.badge-h  { background: #3d0a0a; color: #e74c3c; }

.confidence-bar-bg {
    background: #2a2a2a;
    border-radius: 6px;
    height: 6px;
    margin-top: 6px;
}
.confidence-bar-fill {
    height: 6px;
    border-radius: 6px;
}

.doc-box {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    font-size: 0.92rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #ccc;
    max-height: 320px;
    overflow-y: auto;
}

.stat-pill {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    text-align: center;
}

.stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
}

div[data-testid="stTextArea"] textarea {
    background: #161616 !important;
    color: #f0ede8 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
}

div[data-testid="stTextInput"] input {
    background: #161616 !important;
    color: #f0ede8 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #f5a623, #e05c2a) !important;
    color: #0d0d0d !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    color: #888;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    color: #f5a623 !important;
    border-bottom-color: #f5a623 !important;
}

hr { border-color: #222 !important; }

label, .stRadio label { color: #bbb !important; font-size: 0.88rem; }

.source-link {
    color: #f5a623;
    font-size: 0.8rem;
    font-family: 'Space Mono', monospace;
    text-decoration: none;
    word-break: break-all;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🔬 FactLens</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// HALLUCINATION AUDIT TRAIL FOR LLM-GENERATED DOCUMENTS</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Input Mode ────────────────────────────────────────────────────────────────
mode = st.radio(
    "How do you want to provide the document?",
    ["🤖 Generate document from topic (AI writes it, then audits it)",
     "📋 Paste your own LLM-generated text"],
    horizontal=True,
)

document_text = ""

if mode.startswith("🤖"):
    topic = st.text_input("Enter a topic for document generation", placeholder="e.g. The history of the Eiffel Tower")
    if st.button("GENERATE & AUDIT →") and topic.strip():
        with st.spinner("Generating document with AI..."):
            document_text = generate_document(topic)
        st.session_state["doc"] = document_text
        st.session_state["do_audit"] = True

else:
    pasted = st.text_area(
        "Paste LLM-generated text here",
        height=220,
        placeholder="Paste any AI-generated paragraph, report, or research brief..."
    )
    if st.button("AUDIT THIS TEXT →") and pasted.strip():
        document_text = pasted
        st.session_state["doc"] = document_text
        st.session_state["do_audit"] = True

# ── Audit ─────────────────────────────────────────────────────────────────────
if st.session_state.get("do_audit") and st.session_state.get("doc"):
    doc = st.session_state["doc"]
    st.session_state["do_audit"] = False

    st.markdown("### 📄 Document")
    st.markdown(f'<div class="doc-box">{doc}</div>', unsafe_allow_html=True)
    st.markdown("---")

    with st.spinner("Auditing claims... this may take 20–40 seconds ⏳"):
        results = audit_document(doc)

    if not results:
        st.error("Could not extract claims. Try a longer or more factual document.")
        st.stop()

    # ── Stats ──────────────────────────────────────────────────────────────────
    verified      = [r for r in results if r["verdict"] == "VERIFIED"]
    unverified    = [r for r in results if r["verdict"] == "UNVERIFIED"]
    hallucinated  = [r for r in results if r["verdict"] == "HALLUCINATION"]
    total         = len(results)

    st.markdown("### 📊 Audit Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-pill"><div class="stat-num" style="color:#f0ede8">{total}</div><div style="color:#666;font-size:0.8rem">TOTAL CLAIMS</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-pill"><div class="stat-num" style="color:#2ecc71">{len(verified)}</div><div style="color:#666;font-size:0.8rem">VERIFIED ✅</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-pill"><div class="stat-num" style="color:#f39c12">{len(unverified)}</div><div style="color:#666;font-size:0.8rem">UNVERIFIED ⚠️</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-pill"><div class="stat-num" style="color:#e74c3c">{len(hallucinated)}</div><div style="color:#666;font-size:0.8rem">HALLUCINATIONS ❌</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Pie(
        labels=['Verified ✅', 'Unverified ⚠️', 'Hallucination ❌'],
        values=[len(verified), len(unverified), len(hallucinated)],
        hole=0.5,
        marker_colors=['#40916c', '#e9a825', '#d62828'],
        textfont_size=13,
    )])
    fig.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans'),
        legend=dict(orientation='v', x=1, y=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 🧾 Claim-by-Claim Audit Trail")

    tab_all, tab_v, tab_u, tab_h = st.tabs(["All Claims", "✅ Verified", "⚠️ Unverified", "❌ Hallucinations"])

    def render_claim(r, idx):
        v = r["verdict"]
        conf = r.get("confidence", 50)
        cls_map = {"VERIFIED": "claim-verified", "UNVERIFIED": "claim-unverified", "HALLUCINATION": "claim-hallucination"}
        badge_map = {"VERIFIED": "badge-v", "UNVERIFIED": "badge-u", "HALLUCINATION": "badge-h"}
        bar_color = {"VERIFIED": "#27ae60", "UNVERIFIED": "#f39c12", "HALLUCINATION": "#e74c3c"}

        source_html = ""
        if r.get("source"):
            source_html = f'<br><a class="source-link" href="{r["source"]}" target="_blank">🔗 {r["source"][:80]}...</a>'

        st.markdown(f"""
        <div class="claim-card {cls_map[v]}">
            <span class="badge {badge_map[v]}">{v}</span>
            <strong>Claim #{idx+1}</strong><br>
            <span style="color:#ddd">{r['claim']}</span><br>
            <span style="color:#777;font-size:0.82rem;font-family:'Space Mono',monospace">
                {r.get('reasoning','')}</span>
            {source_html}
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill" style="width:{conf}%;background:{bar_color[v]}"></div>
            </div>
            <span style="color:#666;font-size:0.75rem;font-family:'Space Mono',monospace">Confidence: {conf}%</span>
        </div>
        """, unsafe_allow_html=True)

    with tab_all:
        for i, r in enumerate(results):
            render_claim(r, i)

    with tab_v:
        if verified:
            for i, r in enumerate(verified): render_claim(r, i)
        else:
            st.info("No verified claims found.")

    with tab_u:
        if unverified:
            for i, r in enumerate(unverified): render_claim(r, i)
        else:
            st.info("No unverified claims found.")

    with tab_h:
        if hallucinated:
            for i, r in enumerate(hallucinated): render_claim(r, i)
        else:
            st.success("No hallucinations detected! 🎉")

    # ── Download ───────────────────────────────────────────────────────────────
    st.markdown("---")
    report_lines = ["FACTLENS — HALLUCINATION AUDIT REPORT", "="*50, ""]
    report_lines.append(f"Total Claims: {total} | Verified: {len(verified)} | Unverified: {len(unverified)} | Hallucinations: {len(hallucinated)}")
    report_lines.append("")
    for i, r in enumerate(results):
        report_lines.append(f"[{r['verdict']}] Claim #{i+1} (Confidence: {r.get('confidence',0)}%)")
        report_lines.append(f"  Claim     : {r['claim']}")
        report_lines.append(f"  Reasoning : {r.get('reasoning','')}")
        if r.get('source'): report_lines.append(f"  Source    : {r['source']}")
        report_lines.append("")

    st.download_button(
        "⬇ DOWNLOAD AUDIT REPORT (.txt)",
        data="\n".join(report_lines),
        file_name="factlens_audit_report.txt",
        mime="text/plain"
    )
