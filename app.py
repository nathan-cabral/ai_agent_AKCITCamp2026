import streamlit as st

from agent.orchestrator import process_case_report
from agent.tools import save_draft_for_human_review


st.set_page_config(
    page_title="CASSIA IA",
    page_icon="🟣",
)

st.title("CASSIA IA")

st.write(
    "Protótipo de acolhimento e organização "
    "de informações para revisão humana."
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

    st.subheader("Informações que podem ser complementadas")
    for item in case_summary.missing_information:
        st.markdown(f"- {item}")

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
