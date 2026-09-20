import streamlit as st
import requests
import json
import io
import time
import pandas as pd
import altair as alt

# ─────────────────────────────── Page Setup ───────────────────────────────
st.set_page_config(
    page_title="EduPath AI | Adaptive Learning & Skill Gap Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# ─────────────────────────────── High-End Modern UI Styling ───────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Hero Banner */
    .hero-container {
        background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.25), transparent 45%),
                    linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 15px 35px -10px rgba(79, 70, 229, 0.25);
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Agent Status Badge */
    .agent-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        margin-top: 0.6rem;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34d399;
        box-shadow: 0 0 10px #34d399;
    }

    /* KPI Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 25px -8px rgba(99, 102, 241, 0.25);
    }
    .glass-val {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    .glass-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.35rem;
        font-weight: 600;
    }

    /* Badges */
    .badge-mastered {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-progress {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-struggling {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-missing {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Task Card */
    .task-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .task-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 6px 20px -4px rgba(59,130,246,0.2);
    }
    .task-card.done {
        opacity: 0.55;
        border-color: #064e3b;
        background: #061a14;
    }

    /* Resource Link Button inside task card */
    .resource-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 0.55rem 1rem;
        margin-top: 0.75rem;
        text-decoration: none !important;
        color: #a5b4fc !important;
        font-size: 0.88rem;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .resource-btn:hover {
        background: rgba(99, 102, 241, 0.18);
        border-color: rgba(99, 102, 241, 0.6);
        color: #c7d2fe !important;
        transform: translateX(2px);
        text-decoration: none !important;
    }
    .resource-btn.video {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.3);
        color: #fca5a5 !important;
    }
    .resource-btn.video:hover {
        background: rgba(239, 68, 68, 0.18);
        border-color: rgba(239, 68, 68, 0.6);
        color: #fecaca !important;
    }
    .resource-btn.practice {
        background: rgba(16, 185, 129, 0.08);
        border-color: rgba(16, 185, 129, 0.3);
        color: #6ee7b7 !important;
    }
    .resource-btn.practice:hover {
        background: rgba(16, 185, 129, 0.18);
        border-color: rgba(16, 185, 129, 0.6);
        color: #a7f3d0 !important;
    }
    .resource-btn.book {
        background: rgba(245, 158, 11, 0.08);
        border-color: rgba(245, 158, 11, 0.3);
        color: #fcd34d !important;
    }
    .resource-btn.book:hover {
        background: rgba(245, 158, 11, 0.18);
        border-color: rgba(245, 158, 11, 0.6);
        color: #fde68a !important;
    }
    .resource-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.15rem 0.5rem;
        border-radius: 5px;
        background: rgba(255,255,255,0.07);
    }

    /* Replan Alert */
    .replan-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(185, 28, 28, 0.08));
        border: 1px solid #ef4444;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 8px 20px -5px rgba(239, 68, 68, 0.3);
    }

    /* Focus Timer Box */
    .timer-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }
    .timer-display {
        font-size: 2.8rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #a5b4fc;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────── Helper Functions ───────────────────────────────

def check_backend_alive():
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def get_profile_data():
    pid = st.session_state.get("pid")
    if not pid:
        return None
    try:
        r = requests.get(f"{API_URL}/profile/{pid}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def render_hero(title: str, subtitle: str, badge_text: str = "Autonomous Re-planning Agent Online"):
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
        <div class="agent-status-pill">
            <span class="pulse-dot"></span>
            <span>{badge_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Shared Skill → Code Language map (mirrors backend SKILL_LANGUAGE_MAP) ──
SKILL_LANG = {
    "python": "python",
    "pandas": "python",
    "machine learning fundamentals": "python",
    "ml pipelines": "python",
    "pytorch": "python",
    "statistics": "python",
    "linear algebra": "python",
    "javascript": "javascript",
    "react": "jsx",
    "node.js": "javascript",
    "html/css": "html",
    "rest apis": "javascript",
    "sql": "sql",
    "tableau": "text",
    "docker": "dockerfile",
    "kubernetes": "yaml",
    "ci/cd pipelines": "yaml",
    "cloud architecture (aws)": "yaml",
    "git": "bash",
    "linux": "bash",
    "network security": "bash",
    "siem tools": "text",
    "vulnerability assessment": "text",
}


def skill_language(skill: str) -> str:
    return SKILL_LANG.get((skill or "").lower().strip(), "python")


# ─────────────────────────────── Sidebar Navigation & Demo Personas ───────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 50px; height: 50px; background: linear-gradient(135deg, #6366f1, #4338ca); border-radius: 12px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
        </div>
        <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc; line-height: 1.1;">EduPath AI</div>
            <div style="font-size: 0.75rem; color: #818cf8; font-weight: 600;">Adaptive Learning Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    server_status = check_backend_alive()
    if server_status:
        st.markdown("🟢 **Agent Engine:** Connected")
    else:
        st.markdown("🔴 **Agent Engine:** Offline (`uvicorn main:app`)")

    st.markdown("---")

    # 1-Click Demo Persona Loader for Judges
    st.markdown("##### ⚡ Quick Demo Personas (For Judges)")
    st.caption("Instantly load realistic profiles to demo all features live:")

    demo_p1, demo_p2 = st.columns(2)
    with demo_p1:
        if st.button("🤖 ML Aspirant", help="Python + SQL dev aspiring to be an ML Engineer"):
            with st.spinner("Loading ML Aspirant Profile..."):
                r = requests.post(f"{API_URL}/profile", data={
                    "resume_text": "Experienced Python software developer with 2 years building backend services and SQL queries. Familiar with Git, basic Docker, and introductory data processing. Want to become an ML Engineer.",
                    "target_role": "ml_engineer",
                    "career_goal": "Transition to Production ML Engineer within 4 months",
                    "hours": 8
                })
                if r.status_code == 200:
                    st.session_state["pid"] = r.json()["profile_id"]
                    st.toast("Loaded ML Aspirant Demo Profile!", icon="🚀")
                    st.rerun()

    with demo_p2:
        if st.button("🌐 Fullstack Dev", help="Frontend React dev learning backend APIs & Docker"):
            with st.spinner("Loading Fullstack Dev Profile..."):
                r = requests.post(f"{API_URL}/profile", data={
                    "resume_text": "Frontend engineer with React, JavaScript, HTML/CSS experience. Built responsive user interfaces and consumed REST APIs. Looking to expand into Full-Stack development with Node.js and SQL.",
                    "target_role": "fullstack_dev",
                    "career_goal": "Become a senior Full-Stack Web Developer",
                    "hours": 6
                })
                if r.status_code == 200:
                    st.session_state["pid"] = r.json()["profile_id"]
                    st.toast("Loaded Fullstack Dev Demo Profile!", icon="🚀")
                    st.rerun()

    st.markdown("---")

    nav_options = [
        "1. 👤 Profile & Onboarding",
        "2. 🎯 Skill Gap Radar & DAG",
        "3. 📅 Adaptive Weekly Plan",
        "4. 🧪 Diagnostic Quiz Arena",
        "5. 🛠️ Practice Labs & Projects",
        "6. 📊 Progress Analytics",
        "7. 💬 Ask EduPath Mentor"
    ]
    page = st.radio("Navigation Hub", nav_options, index=0)

    st.markdown("---")
    current_pid = st.session_state.get("pid")
    if current_pid:
        st.caption(f"Active Learner ID: `{current_pid}`")
        if st.button("🔄 Sync Live State"):
            st.rerun()
    else:
        st.info("💡 Load a demo persona or create your profile to start.")


# ─────────────────────────────── Page 1: Profile & Onboarding ───────────────────────────────

if page.startswith("1."):
    render_hero(
        title="Personalized Capability & Career Ingestion",
        subtitle="EduPath parses your prior experience, discovers existing capabilities, and dynamically synthesizes an individualized learning roadmap."
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("🎯 Career Destination")
        role_choices = {
            "ml_engineer": "Machine Learning Engineer",
            "fullstack_dev": "Full-Stack Web Developer",
            "data_analyst": "Data Analyst & BI Specialist",
            "cloud_devops": "Cloud DevOps & SRE Engineer",
            "cybersecurity_analyst": "Cybersecurity & InfoSec Analyst"
        }
        selected_role = st.selectbox(
            "Target Role",
            options=list(role_choices.keys()),
            format_func=lambda k: role_choices[k]
        )

        role_desc_map = {
            "ml_engineer": "Designs and deploys scalable machine learning architectures, training pipelines, and inference servers.",
            "fullstack_dev": "Architects modern full-stack web applications, microservices, REST APIs, and database schemas.",
            "data_analyst": "Transforms raw datasets into business intelligence, predictive metrics, and executive KPI dashboards.",
            "cloud_devops": "Builds resilient infrastructure as code, automated CI/CD pipelines, and cloud orchestration.",
            "cybersecurity_analyst": "Audits security vulnerabilities, analyzes network threat patterns, and monitors SIEM telemetry."
        }
        st.caption(f"💡 **Role Focus:** {role_desc_map[selected_role]}")

        career_goal = st.text_input(
            "Primary Career Milestone / Goal",
            value="Transition to a senior technical role within 4 months",
            placeholder="e.g., Transition to a production ML Engineer role within 4 months"
        )

        hours = st.slider(
            "Available Study Time (Hours per Week)",
            min_value=2, max_value=25, value=8, step=1,
            help="EduPath creates bite-sized weekly plans that strictly respect your time budget."
        )

    with col2:
        st.subheader("📄 Multimodal Resume & Portfolio Ingestion")
        upload_mode = st.radio("Input Source", ["Upload PDF Resume", "Paste Resume / Portfolio / Projects"], horizontal=True)

        uploaded_file = None
        pasted_text = ""

        if upload_mode == "Upload PDF Resume":
            uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
        else:
            pasted_text = st.text_area(
                "Paste Resume, Project Descriptions, or GitHub Links",
                height=165,
                value="Experienced software developer with 2 years of Python scripting, data processing with Pandas, SQL databases, and building basic Flask web apps. Familiar with Git version control.",
                placeholder="Paste your resume summary, tech stack, past projects, certificates (e.g. AWS, Coursera), or GitHub links..."
            )

        st.space(10)
        build_clicked = st.button("🚀 Analyze Capabilities & Generate Adaptive Path", type="primary")

    if build_clicked:
        if not server_status:
            st.error("Backend API is offline. Please launch `uvicorn main:app --port 8000`.")
        else:
            with st.status("🤖 EduPath AI Agent Processing...", expanded=True) as status:
                st.write("1. Parsing resume text and extracting technical capabilities...")
                time.sleep(0.4)
                st.write("2. Evaluating prerequisite Directed Acyclic Graph (DAG)...")
                time.sleep(0.4)
                st.write("3. Querying curated learning vector catalog (ChromaDB)...")
                time.sleep(0.4)
                st.write("4. Synthesizing time-budgeted weekly curriculum and diagnostic quizzes...")

                try:
                    if upload_mode == "Upload PDF Resume" and uploaded_file:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        data = {"target_role": selected_role, "career_goal": career_goal, "hours": hours}
                        res = requests.post(f"{API_URL}/upload_resume", files=files, data=data)
                    else:
                        text_to_send = pasted_text if pasted_text.strip() else "Software practitioner with foundational Python and SQL experience."
                        data = {
                            "resume_text": text_to_send,
                            "target_role": selected_role,
                            "career_goal": career_goal,
                            "hours": hours
                        }
                        res = requests.post(f"{API_URL}/profile", data=data)

                    if res.status_code == 200:
                        payload = res.json()
                        st.session_state["pid"] = payload["profile_id"]
                        status.update(label="✅ Curriculum & Gap Analysis Successfully Generated!", state="complete")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        status.update(label="❌ Profile Generation Failed", state="error")
                        st.error(res.text)
                except Exception as e:
                    status.update(label="❌ Network Request Failed", state="error")
                    st.error(str(e))

    # Existing profile display
    profile = get_profile_data()
    if profile:
        st.markdown("---")
        st.subheader("📋 Detected Capabilities & Mastery Baseline")
        skills_dict = profile.get("skills", {})
        if skills_dict:
            cols = st.columns(4)
            for i, (sk_name, sk_info) in enumerate(skills_dict.items()):
                score_pct = int(sk_info.get("mastery_score", 0) * 100)
                lvl = sk_info.get("current_level") or "beginner"
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 0.75rem; text-align: left; padding: 1rem;">
                        <div style="font-weight: 700; color: #f8fafc; font-size: 1rem;">{sk_name}</div>
                        <div style="margin-top: 0.3rem;">
                            <span class="badge-progress">{lvl.upper()}</span>
                            <span style="color: #94a3b8; font-size: 0.8rem; margin-left: 0.4rem;">{score_pct}% Mastery</span>
                        </div>
                        <div style="margin-top: 0.5rem; background: #334155; border-radius: 999px; height: 5px;">
                            <div style="background: #6366f1; width: {score_pct}%; height: 100%; border-radius: 999px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ─────────────────────────────── Page 2: Skill Gap Radar & DAG ───────────────────────────────

elif page.startswith("2."):
    render_hero(
        title="Deterministic Skill Gap Engine & Prerequisite DAG",
        subtitle="Comparing learner baseline against industry requirements using topological depth sorting and Bloom's learning objectives."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        gaps = profile.get("gaps", [])
        skills_dict = profile.get("skills", {}) or {}
        gap_by_skill = {g.get("skill"): g for g in (gaps or []) if g.get("skill")}
        lvl_val_map = {"beginner": 35, "intermediate": 65, "advanced": 90, None: 0}

        # ── KPI HUD (rendered ONCE) ──
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #818cf8;">{len(gaps)}</div>
            <div class="glass-label">Identified Gaps</div>
        </div>
        """, unsafe_allow_html=True)

        missing_count = sum(1 for g in gaps if g.get("missing"))
        c2.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #fbbf24;">{missing_count}</div>
            <div class="glass-label">Missing From Profile</div>
        </div>
        """, unsafe_allow_html=True)

        below_count = len(gaps) - missing_count
        c3.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #f87171;">{below_count}</div>
            <div class="glass-label">Proficiency Gaps</div>
        </div>
        """, unsafe_allow_html=True)

        struggling = sum(1 for g in gaps if g.get("status") == "Struggling")
        c4.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #fb7185;">{struggling}</div>
            <div class="glass-label">Struggling</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Slide 1: Gap chart + Radar | Slide 2: Prerequisite DAG ──
        slide1, slide2 = st.tabs(["📊 Slide 1 · Skill Gap Chart", "🌲 Slide 2 · Prerequisite DAG"])

        # ═══════════════ SLIDE 1: GAP CHART + RADAR ═══════════════
        with slide1:
            st.subheader("🎯 Skill Gap Overview")
            st.caption("Your mastery vs role requirement. Focus on the biggest gaps first.")

            rows = []
            for sk_name, sk_info in skills_dict.items():
                mastery_pct = int(round((sk_info.get("mastery_score") or 0.0) * 100))
                g = gap_by_skill.get(sk_name, {})
                req_lvl = g.get("required_level") or sk_info.get("current_level") or "intermediate"
                target_pct = lvl_val_map.get(req_lvl, 65) if isinstance(req_lvl, str) else 65
                gap_pts = max(0, target_pct - mastery_pct)
                rows.append({
                    "Skill": sk_name,
                    "Your Level": mastery_pct,
                    "Target": target_pct,
                    "Gap": gap_pts,
                    "Status": g.get("status") or sk_info.get("state") or "—",
                })

            if rows:
                rows_sorted = sorted(rows, key=lambda r: (-r["Gap"], r["Skill"]))
                show = rows_sorted[:14]
                df = pd.DataFrame(show)
                melted = df.melt(
                    id_vars=["Skill", "Gap", "Status"],
                    value_vars=["Your Level", "Target"],
                    var_name="Metric",
                    value_name="Percent",
                )
                chart = (
                    alt.Chart(melted)
                    .mark_bar(cornerRadius=3, height=16)
                    .encode(
                        y=alt.Y(
                            "Skill:N",
                            sort=list(df["Skill"]),
                            title=None,
                            axis=alt.Axis(labelLimit=180, labelFontSize=12),
                        ),
                        x=alt.X("Percent:Q", scale=alt.Scale(domain=[0, 100]), title="Proficiency (%)"),
                        color=alt.Color(
                            "Metric:N",
                            scale=alt.Scale(
                                domain=["Your Level", "Target"],
                                range=["#6366f1", "#34d399"],
                            ),
                            legend=alt.Legend(orient="top", title=None),
                        ),
                        yOffset="Metric:N",
                        tooltip=["Skill", "Metric", "Percent", "Status", "Gap"],
                    )
                    .properties(height=max(360, 32 * len(show) + 50))
                )
                st.altair_chart(chart, use_container_width=True)

                st.markdown("##### Gap details")
                st.dataframe(
                    df[["Skill", "Your Level", "Target", "Gap", "Status"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No skills in profile yet. Create a profile on Page 1.")

            # ── Skill Proficiency Radar ──
            st.markdown("---")
            st.subheader("🎯 Skill Proficiency Radar")
            st.caption("Comparing your baseline capabilities against industry target role requirements.")

            if skills_dict:
                radar_rows = []
                for sk_name, sk_info in skills_dict.items():
                    mastery_pct = int((sk_info.get("mastery_score") or 0.0) * 100)
                    g = gap_by_skill.get(sk_name, {})
                    req_lvl = g.get("required_level") or sk_info.get("current_level") or "intermediate"
                    target_pct = lvl_val_map.get(req_lvl, 65)
                    radar_rows.append({"Skill": sk_name, "Percent": mastery_pct, "Metric": "Current Learner Level"})
                    radar_rows.append({"Skill": sk_name, "Percent": target_pct, "Metric": "Target Role Requirement"})

                df_radar = pd.DataFrame(radar_rows)
                radar_chart = (
                    alt.Chart(df_radar)
                    .mark_bar(opacity=0.85, cornerRadius=3)
                    .encode(
                        x=alt.X(
                            "Skill:N",
                            axis=alt.Axis(labelAngle=-40, labelLimit=160),
                            title=None,
                        ),
                        y=alt.Y(
                            "Percent:Q",
                            scale=alt.Scale(domain=[0, 100]),
                            title="Proficiency (%)",
                        ),
                        color=alt.Color(
                            "Metric:N",
                            scale=alt.Scale(
                                domain=["Current Learner Level", "Target Role Requirement"],
                                range=["#6366f1", "#34d399"],
                            ),
                            legend=alt.Legend(orient="top", title=None),
                        ),
                        xOffset="Metric:N",
                        tooltip=["Skill", "Metric", "Percent"],
                    )
                    .properties(height=360)
                )
                st.altair_chart(radar_chart, use_container_width=True)

        # ═══════════════ SLIDE 2: PREREQUISITE DAG ═══════════════
        with slide2:
            st.subheader("🌲 Prerequisite DAG & Skill Layers")
            st.caption("Skills ordered by dependency — finish lower layers before moving up.")

            edges = []
            nodes = set(skills_dict.keys())
            for g in gaps or []:
                s = g.get("skill")
                if not s:
                    continue
                nodes.add(s)
                for p in g.get("unmet_prereqs") or g.get("prereqs") or []:
                    if p:
                        edges.append((p, s))
                        nodes.add(p)

            if not edges and gaps:
                ordered = [g.get("skill") for g in gaps if g.get("skill")]
                for a, b in zip(ordered, ordered[1:]):
                    edges.append((a, b))

            from collections import defaultdict, deque
            indeg = {n: 0 for n in nodes}
            children = defaultdict(list)
            for a, b in edges:
                if a not in indeg:
                    indeg[a] = 0
                if b not in indeg:
                    indeg[b] = 0
                children[a].append(b)
                indeg[b] = indeg.get(b, 0) + 1

            layers = []
            q = deque([n for n, d in indeg.items() if d == 0])
            seen = set()
            while q:
                layer = []
                for _ in range(len(q)):
                    n = q.popleft()
                    if n in seen:
                        continue
                    seen.add(n)
                    layer.append(n)
                    for c in children.get(n, []):
                        indeg[c] -= 1
                        if indeg[c] == 0:
                            q.append(c)
                if layer:
                    layers.append(sorted(layer))
            rest = sorted(nodes - seen)
            if rest:
                layers.append(rest)

            def _node_style(name: str):
                info = skills_dict.get(name, {})
                score = float(info.get("mastery_score") or 0)
                state = info.get("state") or ""
                g = gap_by_skill.get(name, {})
                status = g.get("status") or state
                if status == "Missing" or (name not in skills_dict):
                    bg, border = "#78350f", "#f59e0b"
                elif status == "Struggling" or state == "struggling":
                    bg, border = "#7f1d1d", "#f87171"
                elif score >= 0.8 or state == "mastered":
                    bg, border = "#064e3b", "#34d399"
                elif score > 0:
                    bg, border = "#312e81", "#818cf8"
                else:
                    bg, border = "#1e293b", "#64748b"
                pct = int(score * 100) if name in skills_dict else 0
                return bg, border, pct, status or "—"

            if layers:
                html = [
                    '<div style="display:flex; gap:1.1rem; overflow-x:auto; padding:0.75rem 0; align-items:flex-start;">'
                ]
                for li, layer in enumerate(layers):
                    html.append(
                        '<div style="min-width:170px; display:flex; flex-direction:column; gap:0.6rem;">'
                        f'<div style="color:#94a3b8; font-size:0.75rem; font-weight:800; letter-spacing:0.08em;">LAYER {li}</div>'
                    )
                    for name in layer:
                        bg, border, pct, status = _node_style(name)
                        short = name if len(name) <= 24 else name[:22] + "…"
                        html.append(
                            f'<div title="{name} — {status}" style="'
                            f'background:{bg}; border:1px solid {border}; border-radius:12px; '
                            f'padding:0.65rem 0.8rem; color:#f8fafc; font-size:0.88rem; font-weight:600;">'
                            f'{short}<div style="font-size:0.75rem; color:#cbd5e1; font-weight:500; margin-top:0.25rem;">'
                            f'{pct}% · {status}</div></div>'
                        )
                    html.append("</div>")
                    if li < len(layers) - 1:
                        html.append(
                            '<div style="align-self:center; color:#64748b; font-size:1.6rem; padding:0 0.2rem;">→</div>'
                        )
                html.append("</div>")
                st.markdown("".join(html), unsafe_allow_html=True)

                st.markdown("##### Legend")
                st.markdown(
                    "🟢 Mastered / strong &nbsp;&nbsp; 🟣 In progress &nbsp;&nbsp; "
                    "🔴 Struggling &nbsp;&nbsp; 🟠 Missing from profile"
                )

                if edges:
                    with st.expander("Dependency arrows (graph view)", expanded=False):
                        dot = [
                            "digraph G {",
                            '  rankdir=LR; bgcolor="transparent";',
                            '  node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10, fontcolor="white"];',
                            '  edge [color="#94a3b8", arrowsize=0.7];',
                        ]
                        for n in nodes:
                            bg, border, pct, status = _node_style(n)
                            dot.append(f'  "{n}" [label="{n}\\n{pct}%", fillcolor="{bg}", color="{border}"];')
                        for a, b in edges:
                            dot.append(f'  "{a}" -> "{b}";')
                        dot.append("}")
                        try:
                            st.graphviz_chart("\n".join(dot), use_container_width=True)
                        except Exception:
                            for a, b in edges[:25]:
                                st.markdown(f"- `{a}` → `{b}`")
            else:
                st.info("No skill nodes to display yet.")

        # ── Roadmap (rendered ONCE, below the tabs) ──
        st.markdown("---")
        st.subheader("🗺️ Prioritized Skill Gap Roadmap (DAG-ordered)")

        if not gaps:
            st.success("🎉 No remaining gaps — you have met all requirements for this role!")
        else:
            for i, g in enumerate(gaps, 1):
                status = g.get("status", "Proficiency Gap")
                if status == "Missing":
                    badge = "badge-missing"
                elif status == "Struggling":
                    badge = "badge-struggling"
                else:
                    badge = "badge-progress"

                prereqs = g.get("unmet_prereqs", [])
                prereq_html = (
                    f"<div style='color:#94a3b8; font-size:0.85rem; margin-top:0.35rem;'>"
                    f"Unmet prereqs: {', '.join(prereqs)}</div>"
                    if prereqs else ""
                )

                st.markdown(f"""
                <div class="task-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; font-size:1.05rem; color:#f8fafc;">
                            #{i} {g.get('skill')}
                        </span>
                        <span class="{badge}">{status}</span>
                    </div>
                    <div style="color:#cbd5e1; margin-top:0.4rem; font-size:0.92rem;">
                        Current: <b>{g.get('current_level') or 'None'}</b> → Required: <b>{g.get('required_level')}</b>
                        &nbsp;|&nbsp; Priority score: {g.get('priority', 0)}
                    </div>
                    <div style="color:#94a3b8; margin-top:0.35rem; font-size:0.88rem;">{g.get('reason', '')}</div>
                    {prereq_html}
                </div>
                """, unsafe_allow_html=True)

                objs = g.get("objectives", [])
                if objs:
                    with st.expander(f"Learning Objectives for {g.get('skill')}"):
                        for o in objs:
                            st.markdown(f"- {o}")


# ─────────────────────────────── Page 3: Adaptive Weekly Plan ───────────────────────────────

elif page.startswith("3."):
    render_hero(
        title="Adaptive Weekly Curriculum",
        subtitle="Time-budgeted plans that automatically replan when diagnostic assessments detect struggle."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        pid = profile["profile_id"]
        current_week = profile.get("current_week", 1)
        plan = profile.get("plan", {})
        tasks = plan.get(str(current_week), [])
        objectives = profile.get("learning_objectives", {}).get(str(current_week), [])

        # Replan banner
        if profile.get("needs_replan"):
            st.markdown("""
            <div class="replan-box">
                <div style="font-weight:700; color:#fca5a5; font-size:1.1rem;">🚨 Struggle Detected — Adaptive Replan Recommended</div>
                <div style="color:#fecaca; margin-top:0.4rem;">One or more skills are flagged as struggling. Click the button below to regenerate this week’s plan with remedial focus.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Trigger Adaptive Replan Now", type="primary"):
                with st.spinner("Replanning curriculum around struggling skills..."):
                    requests.post(f"{API_URL}/replan/{pid}")
                    st.toast("Curriculum replanned!", icon="🔄")
                    st.rerun()

        st.subheader(f"📅 Week {current_week} Plan")
        if objectives:
            st.markdown("**This week’s objectives:**")
            for o in objectives:
                st.markdown(f"- {o}")

        # Quick focus timer
        with st.expander("⏱️ Focus Timer (Pomodoro-style)"):
            st.markdown('<div class="timer-card"><div class="timer-display">25:00</div><div style="color:#94a3b8;">Suggested focus block</div></div>', unsafe_allow_html=True)
            if st.button("Start 25-min Focus"):
                st.info("Timer started conceptually — use your system clock or a Pomodoro app alongside the tasks below.")

        st.markdown("---")
        st.subheader("📝 Weekly Tasks & Checkpoints")

        type_icons = {
            "video": "🎥",
            "reading": "📖",
            "practice": "💻",
            "project": "🚀",
            "quiz": "🧪"
        }

        for t in tasks:
            tid = t["id"]
            icon = type_icons.get(t.get("type"), "📌")
            is_done = t.get("done", False)

            col_check, col_details = st.columns([1, 15])
            with col_check:
                checked = st.checkbox(
                    f"Mark {t['skill']} task as complete",
                    value=is_done,
                    key=f"task_{tid}",
                    label_visibility="collapsed"
                )
                if checked != is_done:
                    requests.post(f"{API_URL}/task/{pid}/{tid}", params={"done": checked})
                    st.rerun()

            with col_details:
                card_class = "task-card done" if is_done else "task-card"
                badge_class = "badge-mastered" if is_done else "badge-progress"
                status_text = "Completed ✓" if is_done else f"{t.get('type', '').upper()} • {t.get('est_hours', 1.0)} hrs"

                t_type = t.get("type", "reading")
                r_url = t.get("resource_url") or ""
                r_title = t.get("resource") or ""

                res_type_map = {
                    "video": ("video", "🎬", "WATCH"),
                    "reading": ("reading", "📖", "READ"),
                    "practice": ("practice", "💻", "CODE"),
                    "project": ("practice", "🚀", "BUILD"),
                    "quiz": ("reading", "🧪", "QUIZ"),
                    "book": ("book", "📚", "READ"),
                    "course": ("reading", "🎓", "ENROLL"),
                }
                btn_class, res_icon, res_label = res_type_map.get(t_type, ("reading", "🔗", "OPEN"))

                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #f8fafc;">
                            {icon} {t['skill']}
                        </span>
                        <span class="{badge_class}">{status_text}</span>
                    </div>
                    <p style="margin: 0.4rem 0 0 0; color: #cbd5e1; font-size: 0.95rem;">{t['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                if r_url and r_url not in ["#", ""]:
                    st.markdown(
                        f'<a href="{r_url}" target="_blank" class="resource-btn {btn_class}">'
                        f'{res_icon} {r_title or r_url}'
                        f'<span class="resource-tag">{res_label} ↗</span>'
                        f'</a>',
                        unsafe_allow_html=True
                    )
                elif t_type == "quiz":
                    st.markdown(
                        '<span class="resource-btn" style="cursor:default;">'
                        '🧪 In-App Diagnostic Quiz '
                        '<span class="resource-tag">GO TO PAGE 4</span>'
                        '</span>',
                        unsafe_allow_html=True
                    )

        st.space(15)
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            if st.button("➡️ Advance to Next Week", help="Advance syllabus and generate next week plan"):
                with st.spinner("Advancing to next week..."):
                    requests.post(f"{API_URL}/next_week/{pid}")
                    st.toast("Advanced to next week!", icon="🚀")
                    st.rerun()
        with act_col2:
            if st.button("⚡ Simulate Conceptual Struggle (Judge Demo)", help="Simulates an assessment failure to showcase dynamic replanning"):
                for sk_name, sk_obj in profile.get("skills", {}).items():
                    requests.post(f"{API_URL}/quiz/{pid}/{sk_name}", json=["I don't know", "Not sure", "Need help"])
                    st.toast("Triggered struggle state for judge demo! Re-plan banner is active.", icon="🚨")
                    st.rerun()
                    break


# ─────────────────────────────── Page 4: Diagnostic Quiz Arena ───────────────────────────────

elif page.startswith("4."):
    render_hero(
        title="Diagnostic Mastery Assessments",
        subtitle="Adaptive evaluations that grade conceptual reasoning in real-time. Failing scores trigger automated replanning."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        pid = profile["profile_id"]
        skills_dict = profile.get("skills", {})

        selected_skill = st.selectbox(
            "Select Skill to Evaluate",
            options=list(skills_dict.keys()) if skills_dict else ["Python"],
            index=0
        )

        curr_skill = skills_dict.get(selected_skill)
        curr_score = curr_skill.get("mastery_score", 0.0) if curr_skill else 0.0
        curr_state = curr_skill.get("state", "not_started") if curr_skill else "not_started"

        k1, k2, k3 = st.columns(3)
        k1.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #60a5fa;">{curr_state.replace('_', ' ').title()}</div>
            <div class="glass-label">Current State</div>
        </div>
        """, unsafe_allow_html=True)

        k2.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #34d399;">{int(curr_score * 100)}%</div>
            <div class="glass-label">Mastery Score</div>
        </div>
        """, unsafe_allow_html=True)

        k3.markdown(f"""
        <div class="glass-card">
            <div class="glass-val" style="color: #f87171;">{curr_skill.get('failed_attempts', 0) if curr_skill else 0}</div>
            <div class="glass-label">Failed Attempts</div>
        </div>
        """, unsafe_allow_html=True)

        st.space(15)

        if st.button(f"🎲 Generate 3-Question Diagnostic Assessment for {selected_skill}", type="primary"):
            with st.spinner(f"Synthesizing diagnostic questions for {selected_skill}..."):
                res = requests.get(f"{API_URL}/quiz/{pid}/{selected_skill}")
                if res.status_code == 200:
                    st.session_state["quiz_questions"] = res.json().get("questions", [])
                    st.session_state["quiz_skill"] = selected_skill

        questions = st.session_state.get("quiz_questions")
        q_skill = st.session_state.get("quiz_skill")

        if questions and q_skill == selected_skill:
            st.markdown(f"### 📋 Assessment: {selected_skill}")
            with st.form("quiz_submission_form"):
                answers = []
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**Question {i}:** {q}")
                    ans = st.text_area(
                        f"Your Answer for Q{i}",
                        key=f"q_ans_{i}",
                        height=90,
                        placeholder="Explain your conceptual reasoning or code solution..."
                    )
                    answers.append(ans)

                submit_btn = st.form_submit_button("📤 Submit for Autonomous AI Grading", type="primary")

            if submit_btn:
                with st.spinner("AI Examiner evaluating comprehension and calculating mastery score..."):
                    resp = requests.post(f"{API_URL}/quiz/{pid}/{selected_skill}", json=answers)
                    if resp.status_code == 200:
                        eval_data = resp.json()
                        st.markdown("### 📊 Evaluation Result")
                        verdict = eval_data.get("verdict")
                        new_m = int(eval_data.get("new_mastery", 0) * 100)

                        if verdict == "mastered":
                            st.success(f"🎉 **Mastery Confirmed!** Score: {new_m}% — Solid comprehension demonstrated!")
                            st.balloons()
                        elif verdict == "struggling":
                            st.error(f"🚨 **Struggling Flagged.** Score: {new_m}%. EduPath has flagged this topic for an adaptive remedial replan.")
                        else:
                            st.info(f"👍 **In Progress.** Score: {new_m}%. On track!")

                        st.markdown(f"**Pedagogical Feedback:** {eval_data.get('feedback')}")
                        if eval_data.get("replan_triggered"):
                            st.warning("⚠️ Autonomous replanning triggered! Check Page 3 to see your adaptive curriculum.")


# ─────────────────────────────── Page 5: Practice Labs & Projects ───────────────────────────────

elif page.startswith("5."):
    render_hero(
        title="Hands-On Practice Labs & Capstone Studio",
        subtitle="Fresh coding problems with starter templates and test cases for every skill — solve them in your own editor."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        pid = profile["profile_id"]

        tab_pract, tab_proj = st.tabs(["💻 Coding Challenges", "🚀 Capstone Project Architecture"])

        with tab_pract:
            st.subheader("Coding Challenges")
            st.caption(
                "Generate a unique problem for any skill. You get a problem statement, starter code, "
                "and test cases. Solve them in VS Code / your local IDE — no in-browser runner."
            )

            skills_dict = profile.get("skills", {})
            skill_options = list(skills_dict.keys()) if skills_dict else [
                "Python", "SQL", "Linear Algebra", "Statistics",
                "Machine Learning Fundamentals", "JavaScript", "Docker"
            ]

            subj_col1, subj_col2 = st.columns([1, 1])
            with subj_col1:
                p_skill = st.selectbox("Select Focus Skill", skill_options, key="practice_skill_select")
            with subj_col2:
                p_lang = skill_language(p_skill)
                st.markdown(f"**Language / format:** `{p_lang}`")

            gen_col1, gen_col2 = st.columns([2, 1])
            with gen_col1:
                generate_clicked = st.button(
                    f"⚡ Generate New Challenge for {p_skill}",
                    type="primary",
                    use_container_width=True
                )
            with gen_col2:
                if st.button("🔄 Clear Challenge", use_container_width=True):
                    st.session_state.pop("practice_data", None)
                    st.rerun()

            if generate_clicked:
                with st.spinner(f"Generating a unique challenge for {p_skill}..."):
                    try:
                        r = requests.get(f"{API_URL}/practice/{pid}/{p_skill}", timeout=30)
                        if r.status_code == 200:
                            st.session_state["practice_data"] = r.json()
                            st.toast(f"New {p_skill} challenge ready!", icon="✨")
                        else:
                            st.error(f"Failed to generate challenge: {r.text}")
                    except Exception as e:
                        st.error(f"Could not reach backend: {e}")

            p_data = st.session_state.get("practice_data")

            if not p_data:
                st.info("👆 Select a skill and click **Generate New Challenge** to get a problem.")
            else:
                st.markdown(f"""
                <div style="background:#0f172a; border:1px solid #334155; border-radius:16px; padding:1.6rem; margin:1rem 0 1.4rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap:wrap; gap:0.5rem;">
                        <h3 style="color:#60a5fa; margin:0;">{p_data.get('title', 'Challenge')}</h3>
                        <span class="badge-progress">{str(p_data.get('difficulty', 'intermediate')).upper()} • {p_data.get('est_hours', 1.5)} hrs</span>
                    </div>
                    <p style="color:#e2e8f0; font-size:1.05rem; line-height:1.65; margin:0;">
                        {p_data.get('problem_statement') or p_data.get('description', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                left, right = st.columns([1.25, 1], gap="large")

                with left:
                    starter = p_data.get("starter_code") or ""
                    if starter.strip():
                        st.markdown("##### 📝 Starter code (copy into your editor)")
                        code_lang = p_data.get("language") or skill_language(p_skill)
                        # Streamlit / Pygments aliases
                        code_lang = {
                            "jsx": "javascript",
                            "tableau": "text",
                            "tsx": "typescript",
                        }.get(code_lang, code_lang)
                        st.code(starter, language=code_lang)
                    else:
                        st.info("No starter template — implement from the problem statement.")

                with right:
                    ac = p_data.get("acceptance_criteria") or []
                    if ac:
                        st.markdown("##### ✅ Acceptance criteria")
                        for a in ac:
                            st.markdown(f"- {a}")

                    tests = p_data.get("test_cases") or []
                    if tests:
                        st.markdown("##### 🧪 Test cases (verify yourself)")
                        for i, tc in enumerate(tests, 1):
                            with st.expander(f"Test {i}: {str(tc.get('explanation', 'Case'))[:55]}", expanded=(i == 1)):
                                st.markdown("**Input**")
                                st.code(str(tc.get("input", "")), language="text")
                                st.markdown("**Expected output**")
                                st.code(str(tc.get("expected_output", "")), language="text")

                    hints = p_data.get("hints") or []
                    if hints:
                        st.markdown("##### 💡 Hints")
                        for i, h in enumerate(hints, 1):
                            with st.expander(f"Hint {i}"):
                                st.write(h)

        with tab_proj:
            st.subheader("Portfolio Capstone Studio")
            st.caption("Every generation produces a different project with architecture and milestones.")

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                fetch_clicked = st.button("💡 Generate New Unique Project", type="primary", use_container_width=True)
            with btn_col2:
                if st.button("🗑️ Clear Capstone View", use_container_width=True):
                    st.session_state.pop("project_data", None)
                    st.rerun()

            if fetch_clicked:
                with st.spinner("Synthesizing project..."):
                    try:
                        r = requests.get(f"{API_URL}/project/{pid}", params={"refresh": True}, timeout=30)
                        if r.status_code == 200:
                            st.session_state["project_data"] = r.json()
                            st.toast("New capstone project generated!", icon="🚀")
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(str(e))

            proj = st.session_state.get("project_data")
            if not proj and profile.get("project_ideas"):
                proj = profile["project_ideas"][0]

            if proj:
                st.markdown(f"### 🚀 {proj.get('title')}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Problem Statement")
                    st.info(proj.get("problem_statement") or proj.get("description") or "—")
                with c2:
                    st.markdown("##### Proposed Solution")
                    st.success(proj.get("proposed_solution") or "Build a modular application.")

                arch = proj.get("architecture") or {}
                if isinstance(arch, dict):
                    st.markdown(f"**Architecture:** {arch.get('overview', '')}")
                    if arch.get("data_flow"):
                        st.markdown(f"**Data flow:** `{arch['data_flow']}`")

                if proj.get("folder_structure"):
                    st.markdown("##### Folder structure")
                    st.code(proj["folder_structure"], language="text")

                stack = proj.get("tech_stack") or proj.get("target_skills") or []
                if stack:
                    st.markdown("##### Tech stack")
                    st.write("  ".join(f"`{t}`" for t in stack))

                for i, m in enumerate(proj.get("milestones") or [], 1):
                    if isinstance(m, dict):
                        with st.expander(m.get("name", f"Milestone {i}"), expanded=(i == 1)):
                            for d in m.get("deliverables") or []:
                                st.markdown(f"- {d}")
                    else:
                        st.markdown(f"{i}. {m}")

                for o in proj.get("learning_outcomes") or []:
                    st.markdown(f"- {o}")
            else:
                st.info("Click **Generate New Unique Project** to create one.")


# ─────────────────────────────── Page 6: Progress Analytics ───────────────────────────────

elif page.startswith("6."):
    render_hero(
        title="Periodic Progress Analytics & Executive Report",
        subtitle="Un-hallucinated quantitative metrics, completion velocity, and exportable learning roadmap."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        pid = profile["profile_id"]

        with st.spinner("Aggregating metrics..."):
            r = requests.get(f"{API_URL}/report/{pid}")
            if r.status_code == 200:
                report_data = r.json()
                stats = report_data.get("stats", {})
                narrative = report_data.get("narrative", "")

                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"""
                <div class="glass-card">
                    <div class="glass-val" style="color: #34d399;">{len(stats.get('skills_acquired', []))}</div>
                    <div class="glass-label">Skills Mastered</div>
                </div>
                """, unsafe_allow_html=True)

                c2.markdown(f"""
                <div class="glass-card">
                    <div class="glass-val" style="color: #60a5fa;">{len(stats.get('skills_in_progress', []))}</div>
                    <div class="glass-label">Skills In Progress</div>
                </div>
                """, unsafe_allow_html=True)

                struggling_count = len(stats.get('struggling', []))
                struggling_color = "#f87171" if struggling_count > 0 else "#94a3b8"
                c3.markdown(f"""
                <div class="glass-card">
                    <div class="glass-val" style="color: {struggling_color};">{struggling_count}</div>
                    <div class="glass-label">Struggling Topics</div>
                </div>
                """, unsafe_allow_html=True)

                c4.markdown(f"""
                <div class="glass-card">
                    <div class="glass-val" style="color: #a78bfa;">{stats.get('completion_rate_percent', 0)}%</div>
                    <div class="glass-label">Curriculum Velocity</div>
                </div>
                """, unsafe_allow_html=True)

                st.space(20)

                col_l, col_r = st.columns([1, 1], gap="large")

                with col_l:
                    st.subheader("📈 Time Allocation & Velocity")
                    st.write(f"**Completed Effort:** {stats.get('hours_completed', 0)} / {stats.get('hours_planned', 0)} planned hours")
                    st.progress(min(1.0, (stats.get('hours_completed', 0) / max(1.0, stats.get('hours_planned', 1)))))

                    st.space(10)
                    st.subheader("🧭 Prescribed Next Steps")
                    for step in stats.get("recommended_next_steps", []):
                        st.markdown(f"- 💡 {step}")

                with col_r:
                    st.subheader("🤖 AI Progress Narrative")
                    st.info(narrative)

                st.markdown("---")
                st.subheader("📥 Export Learning Roadmap (For Hackathon Judges)")

                report_md = f"""# EduPath Personalized Learning Dossier
**Learner ID:** {pid}
**Target Role:** {profile.get('target_role')}
**Career Goal:** {profile.get('career_goal')}
**Weekly Budget:** {profile.get('hours_per_week')} hrs/week

## Progress Summary
- **Skills Mastered:** {', '.join(stats.get('skills_acquired', [])) or 'None yet'}
- **Skills In Progress:** {', '.join(stats.get('skills_in_progress', [])) or 'None'}
- **Struggling Focus Areas:** {', '.join(stats.get('struggling', [])) or 'None'}
- **Completion Velocity:** {stats.get('completion_rate_percent', 0)}%

## Prescribed Actions
{chr(10).join(f"- {s}" for s in stats.get('recommended_next_steps', []))}
"""
                st.download_button(
                    label="📄 Download Executive Roadmap Report (.md)",
                    data=report_md,
                    file_name=f"edupath_roadmap_{pid}.md",
                    mime="text/markdown"
                )


# ─────────────────────────────── Page 7: Ask EduPath Mentor ───────────────────────────────

# ─────────────────────────────── Page 7: Ask EduPath Mentor (Chatbot) ───────────────────────────────

elif page.startswith("7."):
    render_hero(
        title="Ask EduPath: Conversational Learning Mentor",
        subtitle="A context-aware chatbot that already knows your resume, skills, gaps, weekly plan, quizzes, and projects."
    )

    profile = get_profile_data()
    if not profile:
        st.warning("⚠️ Please create or load a profile on Page 1 first!")
    else:
        pid = profile["profile_id"]
        gaps = profile.get("gaps", []) or []
        skills_dict = profile.get("skills", {}) or {}

        # ── Context summary chip (so the learner knows what the bot can see) ──
        with st.expander("🧠 What your mentor can see right now", expanded=False):
            st.markdown(
                f"""
                - **Target role:** `{profile.get('target_role')}`
                - **Career goal:** {profile.get('career_goal') or '—'}
                - **Skills tracked:** {len(skills_dict)}
                - **Open gaps:** {len(gaps)}
                - **Current week:** {profile.get('current_week')}
                - **Resume stored:** {'✅ yes (' + str(len(profile.get('raw_text', ''))) + ' chars)' if profile.get('raw_text') else '❌ no — upload or paste a resume on Page 1'}
                """
            )

        # ── Quick prompt suggestions (grounded in their real data) ──
        st.caption("💡 Suggested questions — grounded in your real profile:")

        top_gap = gaps[0]["skill"] if gaps else (list(skills_dict.keys())[0] if skills_dict else "Python")
        top_gap_prereqs = gaps[0].get("unmet_prereqs", []) if gaps else []

        q1, q2, q3 = st.columns(3)
        sample_q = ""

        with q1:
            if st.button(f"Why is {top_gap} my top gap?", use_container_width=True):
                sample_q = f"Why is {top_gap} my top priority gap, and what should I do first?"

        with q2:
            if st.button("Summarize my resume vs target role", use_container_width=True):
                sample_q = "Based on my uploaded resume, how well do I match my target role? Which skills from my resume count and which are missing?"

        with q3:
            if st.button("What should I study this week?", use_container_width=True):
                sample_q = f"What should I focus on this week, given my current gaps ({', '.join([g['skill'] for g in gaps[:3]])})?"

        q4, q5, q6 = st.columns(3)
        with q4:
            if st.button("How to overcome struggling topics?", use_container_width=True):
                sample_q = "Which topics am I struggling with, and what micro-exercises or resources will help me recover?"

        with q5:
            if st.button("Am I on track for my goal?", use_container_width=True):
                sample_q = "Given my completed hours and mastery scores, am I on track to hit my target career goal?"

        with q6:
            if st.button(f"Explain prereqs for {top_gap}", use_container_width=True):
                sample_q = f"Why do I need {top_gap_prereqs or 'the prerequisites'} before {top_gap}?"

        st.markdown("---")

        # ── Chat history (persisted in session_state) ──
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        colA, colB = st.columns([5, 1])
        with colB:
            if st.button("🗑️ Clear chat", use_container_width=True):
                st.session_state["chat_history"] = []
                st.rerun()

        # Render history
        for msg in st.session_state["chat_history"]:
            avatar = "🧑‍🎓" if msg["role"] == "user" else "🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])
                if msg.get("trace"):
                    with st.expander("🧠 State trace"):
                        st.caption(msg["trace"])

        # ── Chat input ──
        typed = st.chat_input("Ask anything about your roadmap, gaps, resume, or next steps…")
        user_input = typed or sample_q

        if user_input:
            # 1. Add user message
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.write(user_input)

            # 2. Call backend /ask
            with st.chat_message("assistant", avatar="🎓"):
                with st.spinner("EduPath is reasoning over your profile, resume, gaps, and plan…"):
                    try:
                        res = requests.post(
                            f"{API_URL}/ask/{pid}",
                            params={"question": user_input},
                            timeout=45,
                        )
                        if res.status_code == 200:
                            ans = res.json().get("answer", "").strip() or "(empty response)"
                            trace = (
                                f"Role: `{profile.get('target_role')}` · "
                                f"Week: `{profile.get('current_week')}` · "
                                f"Gaps: `{len(gaps)}` · "
                                f"Struggling: `{profile.get('needs_replan')}` · "
                                f"Resume chars: `{len(profile.get('raw_text', ''))}`"
                            )
                            st.write(ans)
                            with st.expander("🧠 State trace"):
                                st.caption(trace)

                            st.session_state["chat_history"].append({"role": "assistant", "content": ans, "trace": trace})
                            st.rerun()
                        else:
                            err = f"Backend returned {res.status_code}: {res.text[:200]}"
                            st.error(err)
                            st.session_state["chat_history"].append({"role": "assistant", "content": f"⚠️ {err}"})
                            st.rerun()

                    except Exception as e:
                        st.error(f"Could not reach backend: {e}")
                        st.session_state["chat_history"].append({"role": "assistant", "content": f"⚠️ Could not reach backend: {e}"})
                        st.rerun()

                        