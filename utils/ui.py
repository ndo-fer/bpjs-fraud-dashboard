from __future__ import annotations

import html
from textwrap import dedent

import streamlit as st

APP_PAGES = [
    {"key": "home", "label": "Home", "path": "app.py", "eyebrow": "Launchpad"},
    {"key": "overview", "label": "Overview", "path": "pages/0_Overview.py", "eyebrow": "Orientation"},
    {"key": "single", "label": "Single Claim", "path": "pages/1_Single_Claim_Scoring.py", "eyebrow": "Manual review"},
    {"key": "batch", "label": "Batch Upload", "path": "pages/2_Batch_Upload.py", "eyebrow": "Operational review"},
    {"key": "artifacts", "label": "Artifacts and Notes", "path": "pages/3_Artifacts_and_Notes.py", "eyebrow": "Trust center"},
    {"key": "history", "label": "History", "path": "pages/4_History.py", "eyebrow": "Audit trail"},
]

THEME_TOKENS = {
    "light": {
        "bg_gradient": "radial-gradient(circle at top left, rgba(255,255,255,0.78), transparent 30%), linear-gradient(180deg, #f7f4ee 0%, #efe9de 100%)",
        "sidebar_bg": "radial-gradient(circle at top, rgba(111, 162, 170, 0.10), transparent 22%), linear-gradient(180deg, #203139 0%, #17262d 58%, #122128 100%)",
        "sidebar_border": "rgba(255,255,255,0.06)",
        "sidebar_text": "#eef3f1",
        "sidebar_text_soft": "rgba(238,243,241,0.72)",
        "sidebar_text_faint": "rgba(238,243,241,0.56)",
        "sidebar_nav_bg": "rgba(255,255,255,0.03)",
        "sidebar_nav_hover": "rgba(255,255,255,0.07)",
        "sidebar_nav_active": "linear-gradient(135deg, rgba(113, 164, 172, 0.34), rgba(255,255,255,0.10))",
        "sidebar_panel_bg": "linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))",
        "sidebar_panel_border": "rgba(255,255,255,0.08)",
        "surface": "rgba(255, 252, 247, 0.92)",
        "surface_soft": "linear-gradient(180deg, rgba(255,252,247,0.76), rgba(248,244,236,0.86))",
        "surface_strong": "linear-gradient(135deg, rgba(255,255,255,0.90), rgba(252,249,244,0.92))",
        "surface_panel": "linear-gradient(180deg, rgba(255,255,255,0.82), rgba(248,244,236,0.88))",
        "surface_plot": "rgba(255,253,249,0.72)",
        "text": "#22313b",
        "text_soft": "#56636d",
        "text_faint": "#7a8790",
        "border": "rgba(68, 92, 104, 0.14)",
        "border_strong": "rgba(39, 69, 82, 0.22)",
        "primary": "#1c6a78",
        "primary_soft": "rgba(28, 106, 120, 0.12)",
        "accent": "#7a9181",
        "danger": "#a14c4f",
        "danger_soft": "rgba(161, 76, 79, 0.12)",
        "warn": "#b88a3b",
        "warn_soft": "rgba(184, 138, 59, 0.14)",
        "success": "#3d7768",
        "success_soft": "rgba(61, 119, 104, 0.12)",
        "shadow": "0 20px 45px rgba(33, 46, 56, 0.06)",
        "button_bg": "linear-gradient(135deg, #1c6a78, #2c7f8d)",
        "button_text": "#ffffff",
        "download_bg": "rgba(255,255,255,0.88)",
    },
    "dark": {
        "bg_gradient": "radial-gradient(circle at top left, rgba(45,74,82,0.22), transparent 28%), linear-gradient(180deg, #10171b 0%, #141e23 100%)",
        "sidebar_bg": "radial-gradient(circle at top, rgba(114, 166, 175, 0.12), transparent 22%), linear-gradient(180deg, #0d1519 0%, #10191d 58%, #0a1115 100%)",
        "sidebar_border": "rgba(255,255,255,0.07)",
        "sidebar_text": "#edf3f2",
        "sidebar_text_soft": "rgba(237,243,242,0.74)",
        "sidebar_text_faint": "rgba(237,243,242,0.56)",
        "sidebar_nav_bg": "rgba(255,255,255,0.02)",
        "sidebar_nav_hover": "rgba(255,255,255,0.08)",
        "sidebar_nav_active": "linear-gradient(135deg, rgba(82, 140, 149, 0.42), rgba(255,255,255,0.08))",
        "sidebar_panel_bg": "linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02))",
        "sidebar_panel_border": "rgba(255,255,255,0.08)",
        "surface": "rgba(23, 33, 39, 0.92)",
        "surface_soft": "linear-gradient(180deg, rgba(24,34,40,0.90), rgba(19,28,33,0.92))",
        "surface_strong": "linear-gradient(135deg, rgba(26,37,44,0.96), rgba(20,30,35,0.94))",
        "surface_panel": "linear-gradient(180deg, rgba(25,35,41,0.94), rgba(20,29,34,0.96))",
        "surface_plot": "rgba(18,26,31,0.72)",
        "text": "#edf3f2",
        "text_soft": "#b6c4c2",
        "text_faint": "#8ca0a5",
        "border": "rgba(167, 190, 196, 0.16)",
        "border_strong": "rgba(205, 222, 226, 0.20)",
        "primary": "#79bec8",
        "primary_soft": "rgba(121, 190, 200, 0.15)",
        "accent": "#93a99d",
        "danger": "#df8187",
        "danger_soft": "rgba(223, 129, 135, 0.14)",
        "warn": "#d3ab5c",
        "warn_soft": "rgba(211, 171, 92, 0.16)",
        "success": "#73b8a4",
        "success_soft": "rgba(115, 184, 164, 0.15)",
        "shadow": "0 18px 42px rgba(2, 6, 8, 0.34)",
        "button_bg": "linear-gradient(135deg, #5aa9b5, #3d7d88)",
        "button_text": "#071014",
        "download_bg": "rgba(26,37,44,0.92)",
    },
}


def get_active_theme() -> str:
    return "dark"


def _tokens() -> dict[str, str]:
    return THEME_TOKENS[get_active_theme()]


def inject_global_styles() -> None:
    theme = _tokens()
    st.markdown(
        dedent(
            f"""
            <style>
            :root {{
              --surface: {theme["surface"]};
              --surface-soft: {theme["surface_soft"]};
              --surface-strong: {theme["surface_strong"]};
              --surface-panel: {theme["surface_panel"]};
              --surface-plot: {theme["surface_plot"]};
              --text: {theme["text"]};
              --text-soft: {theme["text_soft"]};
              --text-faint: {theme["text_faint"]};
              --border: {theme["border"]};
              --border-strong: {theme["border_strong"]};
              --primary: {theme["primary"]};
              --primary-soft: {theme["primary_soft"]};
              --accent: {theme["accent"]};
              --danger: {theme["danger"]};
              --danger-soft: {theme["danger_soft"]};
              --warn: {theme["warn"]};
              --warn-soft: {theme["warn_soft"]};
              --success: {theme["success"]};
              --success-soft: {theme["success_soft"]};
              --shadow: {theme["shadow"]};
              --radius-xl: 28px;
              --radius-lg: 22px;
              --radius-md: 16px;
              --radius-sm: 12px;
            }}

            .stApp {{
              background: {theme["bg_gradient"]};
              color: var(--text);
            }}

            [data-testid="stDecoration"],
            [data-testid="stStatusWidget"],
            .stAppDeployButton,
            div[data-testid="stToolbarActions"] {{
              display: none !important;
              visibility: hidden !important;
              height: 0 !important;
              min-height: 0 !important;
              max-height: 0 !important;
              padding: 0 !important;
              margin: 0 !important;
            }}

            header[data-testid="stHeader"],
            [data-testid="stHeader"] {{
              background: rgba(16, 23, 27, 0.92) !important;
              border-bottom: 1px solid rgba(167, 190, 196, 0.08) !important;
            }}

            [data-testid="stToolbar"] {{
              right: 0.75rem !important;
            }}

            button[kind="header"] {{
              border-radius: 12px !important;
              background: rgba(255,255,255,0.04) !important;
            }}

            [data-testid="stAppViewContainer"] > .main {{
              padding-top: 0.3rem;
            }}

            .block-container {{
              max-width: 1220px;
              padding-top: 1.5rem;
              padding-bottom: 3.6rem;
            }}

            [data-testid="stSidebar"] {{
              background: {theme["sidebar_bg"]};
              border-right: 1px solid {theme["sidebar_border"]};
            }}

            [data-testid="stSidebarNav"] {{
              display: none;
            }}

            [data-testid="stSidebar"] * {{
              color: {theme["sidebar_text"]};
            }}

            .sidebar-theme-label {{
              color: {theme["sidebar_text_faint"]};
              font-size: 0.72rem;
              font-weight: 700;
              letter-spacing: 0.18em;
              text-transform: uppercase;
              margin: 1rem 0 0.4rem 0;
            }}

            .app-shell {{
              margin-top: 0.8rem;
              padding: 1.15rem 1.05rem 1.08rem 1.05rem;
              border: 1px solid {theme["sidebar_panel_border"]};
              border-radius: 24px;
              background: {theme["sidebar_panel_bg"]};
              box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }}

            .app-shell__eyebrow {{
              color: {theme["sidebar_text_faint"]};
              font-size: 0.72rem;
              letter-spacing: 0.18em;
              text-transform: uppercase;
              margin-bottom: 0.5rem;
            }}

            .app-shell__title {{
              font-size: 1.34rem;
              font-weight: 700;
              line-height: 1.08;
              margin-bottom: 0.4rem;
            }}

            .app-shell__body {{
              color: {theme["sidebar_text_soft"]};
              font-size: 0.9rem;
              line-height: 1.6;
            }}

            .app-shell__meta {{
              display: flex;
              flex-wrap: wrap;
              gap: 0.45rem;
              margin-top: 0.78rem;
            }}

            .app-shell__pill {{
              border-radius: 999px;
              padding: 0.32rem 0.62rem;
              font-size: 0.74rem;
              font-weight: 600;
              color: {theme["sidebar_text"]};
              background: rgba(255,255,255,0.06);
              border: 1px solid rgba(255,255,255,0.08);
            }}

            .sidebar-theme-lock {{
              margin-top: 1rem;
              padding: 0.9rem 0.95rem;
              border-radius: 18px;
              border: 1px solid rgba(255,255,255,0.08);
              background: rgba(255,255,255,0.03);
            }}

            .sidebar-theme-lock__title {{
              color: {theme["sidebar_text"]};
              font-size: 0.92rem;
              font-weight: 700;
              margin-bottom: 0.2rem;
            }}

            .sidebar-theme-lock__body {{
              color: {theme["sidebar_text_soft"]};
              font-size: 0.82rem;
              line-height: 1.5;
            }}

            .sidebar-nav {{
              margin-top: 1.15rem;
              display: grid;
              gap: 0.68rem;
            }}

            .sidebar-nav__eyebrow {{
              color: {theme["sidebar_text_faint"]};
              font-size: 0.72rem;
              font-weight: 700;
              letter-spacing: 0.18em;
              text-transform: uppercase;
              margin: 0.15rem 0 0.2rem 0.15rem;
            }}

            .sidebar-nav .stPageLink a {{
              width: 100%;
              text-decoration: none;
              background: {theme["sidebar_nav_bg"]};
              border: 1px solid transparent;
              border-radius: 18px;
              padding: 0.84rem 0.94rem;
              transition: transform 120ms ease, background 120ms ease, border-color 120ms ease;
            }}

            .sidebar-nav .stPageLink a:hover {{
              background: {theme["sidebar_nav_hover"]};
              border-color: rgba(255,255,255,0.08);
              transform: translateX(1px);
            }}

            .sidebar-nav .stPageLink a p,
            .sidebar-nav .stPageLink a span {{
              color: {theme["sidebar_text_soft"]} !important;
              font-weight: 600;
            }}

            .sidebar-nav .stPageLink a[data-current="true"] {{
              background: {theme["sidebar_nav_active"]};
              border-color: rgba(183, 220, 225, 0.22);
              box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.08),
                0 10px 24px rgba(10, 17, 21, 0.22);
            }}

            .sidebar-nav .stPageLink a[data-current="true"] p,
            .sidebar-nav .stPageLink a[data-current="true"] span {{
              color: {theme["sidebar_text"]} !important;
            }}

            .sidebar-nav__active {{
              background: {theme["sidebar_nav_active"]};
              border: 1px solid rgba(183, 220, 225, 0.22);
              border-radius: 18px;
              padding: 0.84rem 0.94rem;
              box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.08),
                0 10px 24px rgba(10, 17, 21, 0.22);
            }}

            .sidebar-nav__active-title {{
              color: {theme["sidebar_text"]};
              font-size: 0.96rem;
              font-weight: 700;
              line-height: 1.25;
            }}

            .sidebar-nav__active-body {{
              color: {theme["sidebar_text_soft"]};
              font-size: 0.8rem;
              line-height: 1.45;
              margin-top: 0.2rem;
            }}

            .page-header {{
              position: relative;
              overflow: hidden;
              background: var(--surface-strong);
              border: 1px solid var(--border);
              border-radius: var(--radius-xl);
              padding: 1.8rem 1.85rem;
              box-shadow: var(--shadow);
              margin-bottom: 1.45rem;
            }}

            .page-header::after {{
              content: "";
              position: absolute;
              top: -30px;
              right: -40px;
              width: 180px;
              height: 180px;
              border-radius: 50%;
              background: radial-gradient(circle, var(--primary-soft), transparent 68%);
              pointer-events: none;
            }}

            .page-header__eyebrow {{
              color: var(--primary);
              font-size: 0.76rem;
              font-weight: 700;
              text-transform: uppercase;
              letter-spacing: 0.18em;
              margin-bottom: 0.5rem;
            }}

            .page-header__title {{
              color: var(--text);
              font-size: 2.35rem;
              font-weight: 760;
              line-height: 1.05;
              letter-spacing: -0.03em;
              margin-bottom: 0.45rem;
            }}

            .page-header__subtitle {{
              max-width: 760px;
              color: var(--text-soft);
              font-size: 1rem;
              line-height: 1.6;
              margin-bottom: 1.15rem;
            }}

            .page-header__meta {{
              display: flex;
              flex-wrap: wrap;
              gap: 0.65rem;
            }}

            .page-pill {{
              display: inline-flex;
              align-items: center;
              border-radius: 999px;
              padding: 0.5rem 0.85rem;
              font-size: 0.85rem;
              font-weight: 600;
              border: 1px solid transparent;
            }}

            .page-pill--primary {{ background: var(--primary-soft); color: var(--primary); border-color: rgba(28,106,120,0.14); }}
            .page-pill--success {{ background: var(--success-soft); color: var(--success); border-color: rgba(61,119,104,0.15); }}
            .page-pill--warn {{ background: var(--warn-soft); color: var(--warn); border-color: rgba(184,138,59,0.18); }}
            .page-pill--danger {{ background: var(--danger-soft); color: var(--danger); border-color: rgba(161,76,79,0.15); }}
            .page-pill--neutral {{ background: rgba(127,145,152,0.10); color: var(--text-soft); border-color: rgba(127,145,152,0.14); }}

            .section-card {{
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: var(--radius-lg);
              padding: 1.28rem 1.28rem 1.22rem 1.28rem;
              box-shadow: var(--shadow);
              margin-bottom: 1.25rem;
            }}

            .section-card--soft {{
              background: var(--surface-soft);
            }}

            .section-title {{
              color: var(--text);
              font-size: 1.02rem;
              font-weight: 700;
              margin-bottom: 0.3rem;
            }}

            .section-kicker {{
              color: var(--primary);
              font-size: 0.76rem;
              font-weight: 700;
              text-transform: uppercase;
              letter-spacing: 0.16em;
              margin-bottom: 0.45rem;
            }}

            .section-copy {{
              color: var(--text-soft);
              font-size: 0.93rem;
              line-height: 1.58;
              margin-bottom: 0.25rem;
            }}

            .page-spacer {{
              width: 100%;
            }}

            .page-spacer--sm {{ height: 0.45rem; }}
            .page-spacer--md {{ height: 0.8rem; }}
            .page-spacer--lg {{ height: 1.2rem; }}

            .metric-card {{
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: var(--radius-md);
              padding: 1.08rem 1.05rem 1rem 1.05rem;
              box-shadow: var(--shadow);
              height: 100%;
            }}

            .metric-card--strong {{
              background: var(--surface-strong);
              border-color: rgba(28,106,120,0.16);
            }}

            .metric-label {{
              color: var(--text-faint);
              font-size: 0.76rem;
              text-transform: uppercase;
              letter-spacing: 0.14em;
              margin-bottom: 0.4rem;
            }}

            .metric-value {{
              color: var(--text);
              font-size: 2rem;
              font-weight: 760;
              line-height: 1;
              letter-spacing: -0.03em;
              margin-bottom: 0.28rem;
            }}

            .metric-note {{
              color: var(--text-soft);
              font-size: 0.88rem;
            }}

            .notice {{
              border-radius: var(--radius-md);
              border: 1px solid var(--border);
              padding: 1.02rem 1.08rem;
              margin-bottom: 1.12rem;
              background: var(--surface);
            }}

            .notice strong {{
              display: block;
              font-size: 0.92rem;
              margin-bottom: 0.25rem;
              color: var(--text);
            }}

            .notice p {{
              margin: 0;
              color: var(--text-soft);
              line-height: 1.55;
            }}

            .notice--info {{ background: color-mix(in srgb, var(--primary-soft) 70%, var(--surface)); border-color: rgba(28,106,120,0.16); }}
            .notice--success {{ background: color-mix(in srgb, var(--success-soft) 70%, var(--surface)); border-color: rgba(61,119,104,0.16); }}
            .notice--warn {{ background: color-mix(in srgb, var(--warn-soft) 70%, var(--surface)); border-color: rgba(184,138,59,0.18); }}
            .notice--danger {{ background: color-mix(in srgb, var(--danger-soft) 70%, var(--surface)); border-color: rgba(161,76,79,0.16); }}

            .hero-result {{
              background: var(--surface-strong);
              border: 1px solid var(--border);
              border-radius: var(--radius-xl);
              padding: 1.38rem 1.45rem;
              box-shadow: var(--shadow);
              margin-bottom: 1.15rem;
            }}

            .hero-result__kicker {{
              font-size: 0.76rem;
              font-weight: 700;
              text-transform: uppercase;
              letter-spacing: 0.16em;
              margin-bottom: 0.6rem;
            }}

            .hero-result__title {{
              color: var(--text);
              font-size: 1.28rem;
              font-weight: 720;
              margin-bottom: 0.45rem;
            }}

            .hero-result__score {{
              font-size: 3.2rem;
              font-weight: 800;
              line-height: 0.95;
              letter-spacing: -0.05em;
              margin-bottom: 0.45rem;
            }}

            .hero-result__body {{
              color: var(--text-soft);
              line-height: 1.6;
              max-width: 760px;
            }}

            .capability-grid {{
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
              gap: 1.12rem;
              margin-bottom: 1.3rem;
            }}

            .capability-card {{
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: var(--radius-lg);
              padding: 1.12rem 1.08rem 1.12rem 1.08rem;
              min-height: 170px;
              box-shadow: var(--shadow);
            }}

            .capability-card__eyebrow {{
              color: var(--primary);
              font-size: 0.76rem;
              font-weight: 700;
              letter-spacing: 0.14em;
              text-transform: uppercase;
              margin-bottom: 0.5rem;
            }}

            .capability-card__title {{
              color: var(--text);
              font-size: 1.1rem;
              font-weight: 700;
              margin-bottom: 0.45rem;
            }}

            .capability-card__body {{
              color: var(--text-soft);
              font-size: 0.93rem;
              line-height: 1.6;
            }}

            .list-panel {{
              display: grid;
              gap: 0.7rem;
            }}

            .list-row {{
              background: var(--surface);
              border: 1px solid var(--border);
              border-radius: var(--radius-md);
              padding: 0.85rem 0.95rem;
            }}

            .list-row__title {{
              color: var(--text);
              font-size: 0.94rem;
              font-weight: 700;
              margin-bottom: 0.2rem;
            }}

            .list-row__body {{
              color: var(--text-soft);
              font-size: 0.9rem;
              line-height: 1.55;
            }}

            .editorial-aside {{
              background: var(--surface-panel);
              border: 1px solid var(--border);
              border-radius: var(--radius-lg);
              padding: 1.14rem 1.18rem;
              box-shadow: var(--shadow);
              margin-bottom: 0.95rem;
            }}

            .editorial-aside__title {{
              color: var(--text);
              font-size: 1rem;
              font-weight: 700;
              margin-bottom: 0.35rem;
            }}

            .editorial-aside__body {{
              color: var(--text-soft);
              font-size: 0.92rem;
              line-height: 1.65;
            }}

            .priority-legend {{
              display: grid;
              gap: 0.55rem;
              margin-top: 1.05rem;
            }}

            .priority-legend__row {{
              display: flex;
              align-items: center;
              gap: 0.65rem;
              color: var(--text-soft);
              font-size: 0.9rem;
            }}

            .priority-dot {{
              width: 0.78rem;
              height: 0.78rem;
              border-radius: 50%;
              flex: 0 0 auto;
            }}

            .priority-dot--high {{ background: var(--danger); }}
            .priority-dot--medium {{ background: var(--warn); }}
            .priority-dot--low {{ background: var(--success); }}

            .upload-surface {{
              background: var(--surface-panel);
              border: 1px solid var(--border);
              border-radius: var(--radius-lg);
              padding: 1.08rem 1.12rem;
              box-shadow: var(--shadow);
              margin-bottom: 0.72rem;
            }}

            .upload-surface__title {{
              color: var(--text);
              font-size: 1rem;
              font-weight: 700;
              margin-bottom: 0.3rem;
            }}

            .upload-surface__body {{
              color: var(--text-soft);
              line-height: 1.6;
              font-size: 0.92rem;
            }}

            [data-testid="stFileUploaderDropzone"] {{
              background: var(--surface) !important;
              border: 1px dashed var(--border-strong) !important;
            }}

            .stFileUploader {{
              margin-bottom: 0.8rem;
            }}

            div[data-testid="stExpander"] {{
              border: 1px solid var(--border) !important;
              background: var(--surface) !important;
              border-radius: var(--radius-md) !important;
              overflow: hidden;
              margin: 0.75rem 0 1.15rem 0;
            }}

            div[data-testid="stExpander"] > details > summary {{
              background: rgba(127,145,152,0.08);
            }}

            div[data-testid="stDataFrame"] {{
              border: 1px solid var(--border);
              border-radius: var(--radius-md);
              overflow: hidden;
            }}

            .stPlotlyChart {{
              margin: 0.65rem 0 1.2rem 0;
            }}

            .stButton > button,
            .stDownloadButton > button {{
              border-radius: 999px;
              border: 1px solid rgba(28,106,120,0.14);
              background: {theme["button_bg"]};
              color: {theme["button_text"]};
              font-weight: 600;
              padding: 0.58rem 1rem;
              box-shadow: var(--shadow);
            }}

            .stDownloadButton > button {{
              background: {theme["download_bg"]};
              color: var(--primary);
              border-color: rgba(28,106,120,0.16);
            }}

            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stRadio label,
            [data-testid="stSidebar"] .stSegmentedControl label {{
              color: {theme["sidebar_text_soft"]};
              font-weight: 600;
            }}

            .stSelectbox label, .stNumberInput label, .stTextInput label, .stFileUploader label {{
              color: var(--text);
              font-weight: 600;
            }}

            .stNumberInput,
            .stSelectbox,
            .stTextInput {{
              margin-bottom: 0.35rem;
            }}

            h1, h2, h3, p, li, div {{
              color: inherit;
            }}

            @media (max-width: 1100px) {{
              .page-header {{
                padding: 1.45rem 1.28rem;
              }}

              .page-header__title {{
                font-size: 2rem;
              }}

              .capability-grid {{
                gap: 0.9rem;
              }}
            }}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_sidebar_brand(
    title: str = "Claim Review Studio",
    eyebrow: str = "BPJS Priority Console",
    body: str = "Prototype decision-support untuk prioritas verifikasi klaim berbasis artifact reguler.",
    current_page: str = "home",
) -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="app-shell">
              <div class="app-shell__eyebrow">{html.escape(eyebrow)}</div>
              <div class="app-shell__title">{html.escape(title)}</div>
              <div class="app-shell__body">{html.escape(body)}</div>
              <div class="app-shell__meta">
                <div class="app-shell__pill">Reguler artifact</div>
                <div class="app-shell__pill">Editorial console</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-theme-lock">
              <div class="sidebar-theme-label">Theme</div>
              <div class="sidebar-theme-lock__title">Dark mode aktif</div>
              <div class="sidebar-theme-lock__body">Tema dashboard sekarang dikunci ke mode gelap agar visual, chart, dan hierarchy tampil konsisten di semua halaman.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-nav__eyebrow">Navigation</div>', unsafe_allow_html=True)
        for page in APP_PAGES:
            if page["key"] == current_page:
                st.markdown(
                    f"""
                    <div class="sidebar-nav__active">
                      <div class="sidebar-nav__active-title">{html.escape(page["label"])}</div>
                      <div class="sidebar-nav__active-body">{html.escape(page["eyebrow"])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.page_link(page["path"], label=page["label"])
        st.markdown("</div>", unsafe_allow_html=True)


def render_page_header(
    eyebrow: str,
    title: str,
    subtitle: str,
    pills: list[tuple[str, str]] | None = None,
) -> None:
    pill_html = ""
    if pills:
        pill_html = '<div class="page-header__meta">' + "".join(
            f'<div class="page-pill page-pill--{html.escape(kind)}">{html.escape(text)}</div>'
            for text, kind in pills
        ) + "</div>"

    st.markdown(
        f"""
        <section class="page-header">
          <div class="page-header__eyebrow">{html.escape(eyebrow)}</div>
          <div class="page-header__title">{html.escape(title)}</div>
          <div class="page-header__subtitle">{html.escape(subtitle)}</div>
          {pill_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, body: str, soft: bool = False) -> None:
    cls = "section-card section-card--soft" if soft else "section-card"
    st.markdown(
        f"""
        <div class="{cls}">
          <div class="section-title">{html.escape(title)}</div>
          <div class="section-copy">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_panel(kicker: str, title: str, body: str, soft: bool = False) -> None:
    cls = "section-card section-card--soft" if soft else "section-card"
    st.markdown(
        f"""
        <div class="{cls}">
          <div class="section-kicker">{html.escape(kicker)}</div>
          <div class="section-title">{html.escape(title)}</div>
          <div class="section-copy">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_notice(kind: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="notice notice--{html.escape(kind)}">
          <strong>{html.escape(title)}</strong>
          <p>{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(metrics: list[dict[str, str]]) -> None:
    columns = st.columns(len(metrics), gap="medium")
    for column, metric in zip(columns, metrics):
        cls = "metric-card metric-card--strong" if metric.get("strong") else "metric-card"
        value = str(metric["value"])
        note = str(metric.get("note", ""))
        with column:
            st.markdown(
                f"""
                <div class="{cls}">
                  <div class="metric-label">{html.escape(metric['label'])}</div>
                  <div class="metric-value">{html.escape(value)}</div>
                  <div class="metric-note">{html.escape(note)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_result_hero(kind: str, title: str, score: str, body: str) -> None:
    kind_map = {
        "high": ("High Priority", "var(--danger)"),
        "medium": ("Medium Priority", "var(--warn)"),
        "low": ("Low Priority", "var(--success)"),
        "neutral": ("Assessment", "var(--primary)"),
    }
    kicker, color = kind_map.get(kind, kind_map["neutral"])
    st.markdown(
        f"""
        <div class="hero-result">
          <div class="hero-result__kicker" style="color:{color};">{html.escape(kicker)}</div>
          <div class="hero-result__title">{html.escape(title)}</div>
          <div class="hero-result__score" style="color:{color};">{html.escape(score)}</div>
          <div class="hero-result__body">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_editorial_aside(title: str, body: str, items: list[tuple[str, str]] | None = None) -> None:
    rows = ""
    if items:
        rows = '<div class="list-panel">' + "".join(
            f'<div class="list-row"><div class="list-row__title">{html.escape(item_title)}</div><div class="list-row__body">{html.escape(item_body)}</div></div>'
            for item_title, item_body in items
        ) + "</div>"
    st.markdown(
        f"""
        <div class="editorial-aside">
          <div class="editorial-aside__title">{html.escape(title)}</div>
          <div class="editorial-aside__body">{html.escape(body)}</div>
          {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_priority_legend() -> None:
    st.markdown(
        """
        <div class="priority-legend">
          <div class="priority-legend__row"><span class="priority-dot priority-dot--high"></span><span><strong>High Priority</strong> untuk klaim yang perlu masuk antrian verifikasi paling depan.</span></div>
          <div class="priority-legend__row"><span class="priority-dot priority-dot--medium"></span><span><strong>Medium Priority</strong> untuk klaim yang perlu perhatian, tetapi belum sekuat sinyal prioritas tinggi.</span></div>
          <div class="priority-legend__row"><span class="priority-dot priority-dot--low"></span><span><strong>Low Priority</strong> untuk klaim dengan indikasi risiko relatif lebih rendah.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_theme(fig, *, horizontal_grid: bool = True, vertical_grid: bool = False):
    theme = _tokens()
    title_text = None
    if getattr(fig.layout, "title", None) is not None:
        title_text = getattr(fig.layout.title, "text", None)
    fig.update_layout(
        font=dict(color=theme["text_soft"], size=14),
        title_text=title_text or "",
        title=dict(font=dict(color=theme["text"], size=20), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=theme["surface_plot"],
        margin=dict(l=8, r=16, t=52, b=16),
    )
    fig.update_xaxes(
        showgrid=horizontal_grid,
        gridcolor=theme["border"],
        zeroline=False,
        linecolor=theme["border_strong"],
        tickfont=dict(color=theme["text_soft"]),
        title_font=dict(color=theme["text_soft"]),
    )
    fig.update_yaxes(
        showgrid=vertical_grid,
        gridcolor=theme["border"],
        zeroline=False,
        linecolor=theme["border_strong"],
        tickfont=dict(color=theme["text_soft"]),
        title_font=dict(color=theme["text_soft"]),
        automargin=True,
    )
    fig.update_traces(textfont=dict(color=theme["text_soft"]))
    return fig
