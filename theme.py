
import streamlit as st

INK = "#1B1E24"
INK_SOFT = "#5B6270"
NAVY = "#1E3A5F"
GOLD = "#AD8A3E"
RULE = "#E5E1D8"
PAPER = "#FFFFFF"
PAPER_SUBTLE = "#F8F7F3"

CHART_PALETTE = ["#1E3A5F", "#AD8A3E", "#2F6F62", "#B5533C", "#6B5B7B", "#4E7A94"]


def inject_css():
    """Apply the dashboard's scholarly-ledger CSS theme. Call once, near the top of streamlit_app.py."""
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

html, body {{
    font-family: 'Inter', -apple-system, sans-serif;
}}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: {PAPER} !important;
    color: {INK} !important;
}}

[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stCaptionContainer"] {{
    color: {INK} !important;
}}

section[data-testid="stSidebar"] {{
    background-color: {PAPER_SUBTLE} !important;
    border-right: 1px solid {RULE};
}}
section[data-testid="stSidebar"] * {{
    color: {INK} !important;
}}
section[data-testid="stSidebar"] [data-testid="stHeader"],
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {NAVY} !important;
}}

/* Inputs - force light backgrounds so they don't inherit a dark theme's
   black fill when the app theme isn't being applied. */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] input {{
    background-color: {PAPER} !important;
    color: {INK} !important;
}}
div[data-testid="stNumberInput"] button {{
    background-color: {PAPER_SUBTLE} !important;
    color: {INK} !important;
}}


h1, h2, h3 {{
    font-family: 'Source Serif 4', Georgia, serif !important;
    color: {NAVY} !important;
    letter-spacing: -0.01em;
}}

h1 {{ font-weight: 700 !important; }}
h2, h3 {{ font-weight: 600 !important; }}

/* Masthead */
.masthead-title {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 700;
    font-size: 2.6rem;
    text-align: center;
    color: {NAVY};
    margin-bottom: 0.15rem;
    line-height: 1.15;
}}
.masthead-rule {{
    width: 64px;
    height: 3px;
    background: {GOLD};
    margin: 0.6rem auto 0.9rem auto;
}}
.masthead-sub {{
    text-align: center;
    color: {INK_SOFT};
    font-size: 1rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 2.2rem;
}}

/* Section eyebrow used before subheaders */
.eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {GOLD};
    margin-bottom: -0.4rem;
}}

/* Metrics */
div[data-testid="stMetric"] {{
    background-color: {PAPER_SUBTLE};
    border: 1px solid {RULE};
    border-bottom: 2px solid {GOLD};
    border-radius: 4px;
    padding: 0.9rem 1rem 0.7rem 1rem;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace;
    color: {NAVY};
    font-weight: 600;
    font-size: 1.5rem;
}}
div[data-testid="stMetricLabel"] {{
    color: {INK_SOFT};
    font-size: 0.8rem;
    letter-spacing: 0.03em;
}}
label[data-testid="stWidgetLabel"] p {{
    color: {INK_SOFT};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.03em;
}}

/* Tabs styled like index-card dividers */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid {RULE};
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.02em;
    color: {INK_SOFT};
    background-color: transparent;
    border-radius: 4px 4px 0 0;
    padding: 0.5rem 1rem;
}}
.stTabs [aria-selected="true"] {{
    color: {NAVY} !important;
    background-color: {PAPER_SUBTLE} !important;
    border-bottom: 2px solid {GOLD} !important;
    font-weight: 600;
}}

/* Buttons / inputs */
.stButton > button, .stDownloadButton > button {{
    font-family: 'Inter', sans-serif;
    background-color: {GOLD};
    color: {PAPER};
    border: none;
    border-radius: 3px;
}}
.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: {INK_SOFT};
}}
div[data-baseweb="select"] > div, .stTextInput input {{
    border-color: {RULE} !important;
    border-radius: 3px !important;
}}

/* Dividers */
hr {{
    border: none;
    border-top: 1px solid {RULE};
    margin: 1.4rem 0;
}}

/* Expanders */
.streamlit-expanderHeader {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: {NAVY};
    background-color: {PAPER_SUBTLE};
    border: 1px solid {RULE};
    border-radius: 4px;
}}

/* Dataframe framing only - no color overrides, see note above */
div[data-testid="stDataFrame"] {{
    border: 1px solid {RULE};
    border-radius: 4px;
    overflow: hidden;
}}

/* Footer */
.dashboard-footer {{
    text-align: center;
    color: {INK_SOFT};
    font-size: 0.82rem;
    padding: 1.4rem 0 0.6rem 0;
    border-top: 1px solid {RULE};
    margin-top: 1rem;
}}
.dashboard-footer strong {{
    color: {NAVY};
    font-family: 'Source Serif 4', Georgia, serif;
}}

/* Tab content */
.stTabs [data-baseweb="tab-panel"] {{
    background-color: {PAPER} !important;
    color: {INK} !important;
}}

.stTabs .stMarkdown {{
    color: {INK} !important;
}}

.stTabs .stMarkdown strong {{
    color: {INK} !important;
}}

#MainMenu, footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


apply = inject_css


def masthead(title, subtitle=None):
    """Render the report-style masthead heading used at the top of the page."""
    st.markdown(f'<div class="masthead-title">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="masthead-rule"></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="masthead-sub">{subtitle}</div>', unsafe_allow_html=True)


def eyebrow(text):
    """Small uppercase mono label placed just above a subheader."""
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def footer(text):
    """Centered, ruled-off footer line at the bottom of the page."""
    st.markdown(f'<div class="dashboard-footer">{text}</div>', unsafe_allow_html=True)


def style_chart(fig, ax):
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.set_prop_cycle(color=CHART_PALETTE)

    if ax.get_title():
        ax.title.set_fontfamily("serif")
        ax.title.set_fontweight("bold")
        ax.title.set_color(NAVY)
        ax.title.set_fontsize(13)

    ax.xaxis.label.set_color(INK_SOFT)
    ax.yaxis.label.set_color(INK_SOFT)
    ax.tick_params(colors=INK_SOFT, labelsize=9)

    for spine in ax.spines.values():
        spine.set_color(RULE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(True, color=RULE, linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)

    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor(PAPER_SUBTLE)
        legend.get_frame().set_edgecolor(RULE)
        for text in legend.get_texts():
            text.set_color(INK)

    return fig