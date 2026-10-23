"""Estilos centralizados da interface Streamlit."""

APP_CSS = """
<style>
    :root {
        --cassia-bg: #fff5f8;
        --cassia-surface: #ffffff;
        --cassia-text: #2f2434;
        --cassia-muted: #6b5a70;
        --cassia-purple: #684278;
        --cassia-purple-dark: #4f2d5e;
        --cassia-lilac: #f0e4f4;
        --cassia-border: #e8d6e7;
        --cassia-danger: #a61b32;
        --cassia-danger-dark: #7e1022;
    }

    .stApp { background: var(--cassia-bg); color: var(--cassia-text); }
    /* Reserva espaço para a barra fixa nativa do Streamlit, clara ou escura. */
    [data-testid="stMainBlockContainer"],
    .main .block-container,
    .block-container {
        max-width: 980px;
        padding: calc(5rem + env(safe-area-inset-top)) 1.35rem 2.5rem !important;
    }
    h1, h2, h3, p, span, label { color: var(--cassia-text); }

    .cassia-header { align-items: center; border-bottom: 1px solid var(--cassia-border); display: flex; justify-content: space-between; margin-bottom: 1.65rem; padding-bottom: 1rem; }
    .cassia-brand { color: var(--cassia-purple-dark); font-size: 1.38rem; font-weight: 800; letter-spacing: -.03em; }
    .cassia-brand span { color: var(--cassia-muted); display: block; font-size: .78rem; font-weight: 500; letter-spacing: 0; margin-top: .1rem; }
    .cassia-kicker { color: var(--cassia-purple); font-size: .8rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
    .cassia-hero { background: var(--cassia-surface); border: 1px solid var(--cassia-border); border-radius: 20px; box-shadow: 0 10px 30px rgba(77, 43, 84, .08); margin: .7rem 0 1.25rem; padding: 1.6rem; }
    .cassia-hero h1 { color: var(--cassia-purple-dark); font-size: clamp(2.35rem, 7vw, 3.7rem); letter-spacing: -.055em; line-height: 1; margin: .4rem 0 1.1rem; }
    .cassia-intro { color: #45354b; font-size: 1.09rem; line-height: 1.65; margin: 0; max-width: 760px; }
    .cassia-gentle { color: var(--cassia-muted); font-size: .96rem; line-height: 1.55; margin: 1.15rem 0 0; }
    .cassia-section-title { color: var(--cassia-purple-dark); font-size: 1.1rem; font-weight: 800; margin: 1.5rem 0 .25rem; }
    .cassia-field-note { color: var(--cassia-muted); font-size: .87rem; line-height: 1.45; margin: .1rem 0 .7rem; }

    .cassia-emergency { background: #fff0f1; border: 1px solid #e9a8b1; border-left: 6px solid var(--cassia-danger); border-radius: 16px; margin: 1.5rem 0; padding: 1.15rem 1.2rem; }
    .cassia-emergency h2 { color: #741227; font-size: 1.15rem; margin: 0 0 .5rem; }
    .cassia-emergency p { color: #4c2730; line-height: 1.55; margin: 0; }
    .cassia-emergency-actions { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 1rem; }
    .cassia-emergency-button { border-radius: 9px; color: white !important; display: inline-block; font-weight: 750; padding: .67rem 1rem; text-decoration: none !important; }
    .cassia-emergency-190 { background: var(--cassia-danger); }
    .cassia-emergency-180 { background: var(--cassia-danger-dark); }
    .cassia-emergency-button:hover { filter: brightness(.92); color: white !important; }

    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { background: var(--cassia-purple); border: 1px solid var(--cassia-purple); border-radius: 10px; color: white; font-weight: 700; min-height: 2.75rem; padding: .5rem .85rem; transition: background .15s ease, transform .15s ease; }
    /* Somente os dois caminhos principais da tela inicial usam texto branco. */
    .st-key-home_info_button button,
    .st-key-home_info_button button *,
    .st-key-home_talk_button button,
    .st-key-home_talk_button button * { color: white !important; }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background: var(--cassia-purple-dark); border-color: var(--cassia-purple-dark); color: white; transform: translateY(-1px); }
    div.stButton > button:focus-visible, div[data-testid="stFormSubmitButton"] > button:focus-visible { box-shadow: 0 0 0 3px #cfb6d9; }
    button[kind="secondary"] { background: var(--cassia-lilac) !important; border-color: #c7aacd !important; color: var(--cassia-purple-dark) !important; }
    button[kind="secondary"]:hover { background: #e5d1eb !important; }
    [data-testid="stTextInput"] input, [data-testid="stChatInput"] textarea { background: #fffafd; border-color: #d8bfda; border-radius: 10px; color: var(--cassia-text); }
    [data-testid="stTextInput"] input:focus, [data-testid="stChatInput"] textarea:focus { border-color: var(--cassia-purple); box-shadow: 0 0 0 2px #e6d5ea; }
    [data-testid="stChatInput"] { border-top: 1px solid var(--cassia-border); padding-top: .65rem; }
    [data-testid="stChatInputSubmitButton"] { background: var(--cassia-purple) !important; color: white !important; }

    .cassia-chat { background: rgba(255,255,255,.6); border: 1px solid var(--cassia-border); border-radius: 18px; padding: .55rem .3rem; }
    .cassia-message { border-radius: 15px; line-height: 1.52; margin: .55rem .55rem; max-width: 78%; padding: .75rem .9rem; white-space: pre-wrap; }
    .cassia-message-assistant { background: #f0e4f4; border: 1px solid #e1cce7; color: #3f2948; margin-right: auto; }
    .cassia-message-user { background: var(--cassia-purple); color: white; margin-left: auto; }
    .cassia-message-label { display: block; font-size: .72rem; font-weight: 800; margin-bottom: .2rem; opacity: .78; }
    .cassia-disclosure { color: var(--cassia-muted); font-size: .82rem; margin: .45rem .15rem .6rem; }
    .cassia-mode { color: var(--cassia-muted); font-size: .88rem; margin-top: -.5rem; }
    .cassia-neutral { background: white; border: 1px solid var(--cassia-border); border-radius: 18px; margin: 14vh auto; max-width: 540px; padding: 2rem; text-align: center; }
    .cassia-neutral h1 { color: var(--cassia-purple-dark); font-size: 1.65rem; }
    .cassia-neutral p { color: var(--cassia-muted); line-height: 1.55; }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"], .main .block-container, .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        .cassia-hero { padding: 1.25rem; }
        .cassia-message { max-width: 90%; }
        .cassia-emergency-actions { display: grid; grid-template-columns: 1fr; }
        .cassia-emergency-button { text-align: center; }
    }
</style>
"""
