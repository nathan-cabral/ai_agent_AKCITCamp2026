import streamlit as st

from agent.orchestrator import process_case_report
from agent.tools import save_draft_for_human_review


st.set_page_config(
    page_title="CASSIA IA",
    page_icon="🟣",
    layout="centered",
)

st.markdown(
    """
    <style>
        .stApp {
            background: #ead9e5;
            color: #352b38;
        }

        .block-container {
            max-width: 880px;
            padding-top: 3.5rem;
            padding-bottom: 3rem;
        }

        .cassia-eyebrow {
            color: #806687;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
        }

        h1 {
            color: #4a354f;
            font-size: 2.7rem !important;
            letter-spacing: -0.04em;
            margin-bottom: 0.35rem;
        }

        [data-testid="stForm"] {
            background: rgba(255, 250, 253, 0.76);
            border: 1px solid rgba(120, 91, 126, 0.2);
            border-radius: 16px;
            padding: 1.35rem;
            box-shadow: 0 10px 28px rgba(74, 53, 79, 0.09);
        }

        [data-testid="stTextArea"] textarea {
            background: #fff0f6;
            border: 1px solid #deb6ca;
            border-radius: 10px;
        }

        [data-testid="stTextArea"] label,
        [data-testid="stTextArea"] label p {
            color: #745b7a !important;
            font-weight: 600;
        }

        [data-testid="stTextArea"] textarea:focus {
            border-color: #86678e;
            box-shadow: 0 0 0 1px #86678e;
        }

        div.stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background: #745b7a;
            border: 1px solid #745b7a;
            border-radius: 9px;
            color: #ffffff;
            font-weight: 600;
            padding: 0.5rem 1rem;
        }

        div.stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background: #5d4664;
            border-color: #5d4664;
            color: #ffffff;
        }

        [data-testid="stAlert"] {
            background: rgba(255, 248, 252, 0.82);
            border: 1px solid rgba(91, 65, 98, 0.28);
            border-radius: 10px;
            color: #352b38;
        }

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] span,
        [data-testid="stAlert"] div {
            color: #352b38 !important;
        }

        [data-testid="stCaptionContainer"] {
            color: #6d6070;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="cassia-eyebrow">estou aqui para te ouvir e te ajudar</p>', unsafe_allow_html=True)
st.title("CASSIA IA")

st.write(
    "Um espaço de demonstração para organizar relatos fictícios "
    "com cuidado e encaminhá-los para revisão humana."
)

st.info(
    "Demonstração com dados fictícios. "
    "Este protótipo não substitui atendimento "
    "profissional nem registra uma ocorrência oficial."
)

st.caption(
    "Modo atual: processamento local e estruturado. "
    "A integração com IA e RAG será adicionada nas próximas etapas."
)

st.divider()

with st.form("case_report_form"):
    report = st.text_area(
        "Relato fictício",
        placeholder="Exemplo fictício: recebi mensagens ameaçadoras durante a última semana.",
        help="Use somente dados fictícios. Não inclua nomes, contatos ou informações pessoais reais.",
        height=180,
    )
    submitted = st.form_submit_button("Processar relato fictício", type="primary")

if submitted:
    st.session_state.pop("case_summary", None)
    try:
        st.session_state.case_summary = process_case_report(report)
    except ValueError as error:
        st.error(str(error))

if "case_summary" in st.session_state:
    case_summary = st.session_state.case_summary
    st.success("Rascunho estruturado criado para revisão humana.")

    st.subheader("Resumo do relato")
    st.write(case_summary.summary)

    st.subheader("Fontes consultadas")
    if case_summary.sources:
        for source in case_summary.sources:
            st.markdown(f"- {source}")
    else:
        st.write("Nenhuma fonte foi consultada nesta etapa.")

    if case_summary.requires_human_review:
        st.warning("Este rascunho exige revisão humana antes de qualquer uso.")

    if st.button("Salvar rascunho para revisão", type="secondary"):
        saved_path = save_draft_for_human_review(case_summary)
        st.success(f"Rascunho salvo localmente como {saved_path.name}.")
