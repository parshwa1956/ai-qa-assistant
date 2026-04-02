import streamlit as st

st.set_page_config(
    page_title="Kaldi One",
    page_icon="🧪",
    layout="wide",
)

# ------------------------------
# Config
# ------------------------------
STRIPE_SUBSCRIBE_URL = "https://buy.stripe.com/your-link-here"
PRO_PRICE_TEXT = "$19 / Month"

# ------------------------------
# Query params
# ------------------------------
view = st.query_params.get("view", "")

# ------------------------------
# Styling
# ------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    margin: 0 auto;
    padding-top: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.hero-card {
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    background: #ffffff;
    padding: 2rem 2rem 1.6rem 2rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.04);
    margin-bottom: 1.5rem;
}

.clean-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    background: #ffffff;
    padding: 1.2rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.03);
    margin-bottom: 1rem;
    height: 100%;
}

.highlight-card {
    border: 2px solid #2563eb;
    border-radius: 18px;
    background: #f8fbff;
    padding: 1.35rem;
    box-shadow: 0 6px 22px rgba(37,99,235,0.08);
    margin-bottom: 1rem;
    height: 100%;
}

.k-muted {
    color: #6b7280;
    font-size: 0.98rem;
}

.feature-pill {
    display: inline-block;
    padding: 0.42rem 0.78rem;
    margin: 0.25rem 0.35rem 0.25rem 0;
    border-radius: 999px;
    background: #eff6ff;
    border: 1px solid #dbeafe;
    color: #1d4ed8;
    font-size: 0.9rem;
    font-weight: 500;
}

.section-space {
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
}

.pricing-badge-free {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    color: #334155;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
}

.pricing-badge-pro {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
}

.pricing-focus-banner {
    border: 1px solid #bfdbfe;
    background: #eff6ff;
    color: #1e3a8a;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 1rem;
    font-weight: 600;
}

.price-text {
    font-size: 1.95rem;
    font-weight: 700;
    color: #1d4ed8;
    margin: 0.8rem 0 1rem 0;
}

.pricing-subscribe-wrap .stLinkButton a {
    background: #4da3ff !important;
    color: white !important;
    border: 1px solid #4da3ff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    box-shadow: 0 4px 12px rgba(77, 163, 255, 0.22) !important;
}

.pricing-subscribe-wrap .stLinkButton a:hover {
    background: #4da3ff !important;
    border-color: #4da3ff !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Helper
# ------------------------------
def render_pricing_section():
    st.markdown("## Pricing & Subscription")

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("""
        <div class="clean-card" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div class="pricing-badge-free">Free Plan</div>
                <h3 style="margin-top:0; color:#1f2937;">Try the Platform</h3>
                <p class="k-muted">Good for individual users who want to explore the core workflow.</p>
                <ul style="line-height:1.9; color:#374151;">
                    <li>1 project</li>
                    <li>Core QA generation</li>
                    <li>Basic workflow</li>
                    <li>Limited usage</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="highlight-card" style="min-height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div class="pricing-badge-pro">Pro Plan</div>
                <h3 style="margin-top:0; color:#1f2937;">Built for active users and teams</h3>
                <p class="k-muted">Best for users who want unlimited project access and integrations.</p>
                <div class="price-text">{PRO_PRICE_TEXT}</div>
                <ul style="line-height:1.9; color:#374151;">
                    <li>Unlimited projects</li>
                    <li>JIRA integration</li>
                    <li>Azure DevOps integration</li>
                    <li>Premium workflow features</li>
                    <li>Expanded generation limits</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="pricing-subscribe-wrap">', unsafe_allow_html=True)
        st.link_button("🚀 Subscribe to Pro", STRIPE_SUBSCRIBE_URL, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Header
# ------------------------------
st.markdown("""
<div class="hero-card">
    <h1 style="margin-bottom:0.35rem; color:#1f2937;">Kaldi One</h1>
    <p class="k-muted" style="margin-top:0;">
        AI-powered workspace for QA, BA, and Development teams.
    </p>
    <p style="font-size:1.02rem; color:#374151; margin-top:1rem;">
        Generate bug reports, test cases, test scenarios, flow-based requirements,
        user stories, acceptance criteria, and technical task breakdowns in one clean workspace.
    </p>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Quick actions
# ------------------------------
st.markdown("## Get Started")
c1, c2, c3 = st.columns(3)

with c1:
    st.page_link("pages/1_Login_and_Start.py", label="Open Workspace", icon="🚀")

with c2:
    st.page_link("pages/10_History.py", label="View History", icon="🕘")

with c3:
    st.page_link("pages/11_Settings.py", label="Open Settings", icon="⚙️")

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# Pricing section first if requested
# ------------------------------
if view == "pricing":
    st.markdown("""
    <div class="pricing-focus-banner">
        Upgrade to Pro to unlock unlimited projects, integrations, and premium workflow features.
    </div>
    """, unsafe_allow_html=True)

    render_pricing_section()
    st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# Platform overview
# ------------------------------
st.markdown("## Platform Overview")
o1, o2 = st.columns(2)

with o1:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">Workspaces</h3>
        <p class="k-muted">Organized into focused work areas so users can generate exactly what they need.</p>
        <div class="feature-pill">QA Workspace</div>
        <div class="feature-pill">BA Workspace</div>
        <div class="feature-pill">Dev Workspace</div>
        <div class="feature-pill">Flow to Requirement</div>
    </div>
    """, unsafe_allow_html=True)

with o2:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">Integrations & Output</h3>
        <p class="k-muted">Keep integrations in Settings while the workspace stays clean and focused.</p>
        <div class="feature-pill">JIRA Integration</div>
        <div class="feature-pill">Azure DevOps</div>
        <div class="feature-pill">Download TXT / CSV / Excel</div>
        <div class="feature-pill">Saved History</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# Workspace details
# ------------------------------
st.markdown("## Workspace Details")
w1, w2, w3, w4 = st.columns(4)

with w1:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">QA Workspace</h3>
        <p class="k-muted">Generate bug reports, test cases, and test scenarios from requirement details and screenshots.</p>
    </div>
    """, unsafe_allow_html=True)

with w2:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">BA Workspace</h3>
        <p class="k-muted">Convert requirements into user stories, acceptance criteria, and requirement breakdowns.</p>
    </div>
    """, unsafe_allow_html=True)

with w3:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">Dev Workspace</h3>
        <p class="k-muted">Create technical task breakdowns, API tasks, and developer checklists.</p>
    </div>
    """, unsafe_allow_html=True)

with w4:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">Flow to Requirement</h3>
        <p class="k-muted">Upload a flow diagram and turn it into structured business requirements.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# Pricing section in normal view too
# ------------------------------
if view != "pricing":
    render_pricing_section()
    st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# How it works
# ------------------------------
st.markdown("## How It Works")
h1, h2, h3 = st.columns(3)

with h1:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">1. Choose a workspace</h3>
        <p class="k-muted">Select QA, BA, Dev, or Flow to Requirement depending on the work you need done.</p>
    </div>
    """, unsafe_allow_html=True)

with h2:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">2. Add context</h3>
        <p class="k-muted">Enter requirement details, screenshots, flow diagrams, or technical notes.</p>
    </div>
    """, unsafe_allow_html=True)

with h3:
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top:0; color:#1f2937;">3. Generate and manage</h3>
        <p class="k-muted">Review outputs, download files, save history, and create issues through integrations.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

# ------------------------------
# Privacy Policy
# ------------------------------
st.markdown("## Privacy Policy")
st.markdown("""
<div class="clean-card">
    Kaldi One stores only the information necessary to support account access, saved history,
    project-based organization, and integrations. Users should avoid entering sensitive
    production data unless it is appropriate for their environment and security controls.
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Terms of Service
# ------------------------------
st.markdown("## Terms of Service")
st.markdown("""
<div class="clean-card">
    By using Kaldi One, users agree to use the platform responsibly for QA, BA, and development
    workflow support. Generated outputs should be reviewed by a human before production use.
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Support
# ------------------------------
st.markdown("## Contact Support")
st.markdown("""
<div class="clean-card">
    Need help with the platform, subscription, or integrations?<br><br>
    <b>Email:</b> kaldiglobal1008@gmail.com
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ------------------------------
# Final CTA
# ------------------------------
c1, c2 = st.columns(2)

with c1:
    st.page_link("pages/1_Login_and_Start.py", label="Launch Kaldi One Workspace", icon="🧪")

with c2:
    st.page_link("pages/11_Settings.py", label="Manage Integrations", icon="🔗")
