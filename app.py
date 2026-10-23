"""Interface Streamlit da Cássia IA.

Esta camada não persiste conversas e ainda não chama agente, RAG ou serviços
externos. Ela mantém apenas o estado temporário necessário para a navegação.
"""

from html import escape

import streamlit as st

from agent.llm import GeminiService, GeminiServiceError
from ui.styles import APP_CSS


HOME = "home"
INFO_CHAT = "info_chat"
TALK_CHAT = "talk_chat"
NEUTRAL = "neutral"


def initialize_state() -> None:
    """Cria o estado mínimo de interface sem persistir dados sensíveis."""
    defaults = {
        "screen": HOME,
        "municipality": "",
        "editing_municipality": False,
        "messages": [],
        "chat_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def quick_exit() -> None:
    """Remove o conteúdo transitório e exibe uma tela neutra no app."""
    for key in ("municipality", "editing_municipality", "messages", "chat_error"):
        st.session_state.pop(key, None)
    st.session_state.screen = NEUTRAL


def clear_municipality() -> None:
    """Apaga o município opcional sem alterar as mensagens da conversa."""
    st.session_state.municipality = ""
    st.session_state.editing_municipality = False


def go_to_chat(mode: str) -> None:
    st.session_state.screen = mode
    st.session_state.editing_municipality = False
    st.session_state.chat_error = None
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Posso apresentar informações gerais e fontes oficiais quando "
                "essa etapa estiver integrada. Você não precisa contar nada "
                "pessoal para usar este espaço."
                if mode == INFO_CHAT
                else "Estou aqui para te ouvir no seu tempo. Você decide o que "
                "quer compartilhar; não precisa incluir detalhes que não queira."
            ),
        }
    ]


@st.cache_resource(show_spinner=False)
def get_gemini_service() -> GeminiService:
    """Mantém um cliente reutilizável sem armazenar o histórico fora da sessão."""
    return GeminiService()


def render_header(show_municipality: bool = False) -> None:
    left, middle, right = st.columns([5, 2, 2])
    with left:
        st.markdown(
            '<div class="cassia-brand">Cássia IA<span>assistente de apoio</span></div>',
            unsafe_allow_html=True,
        )
    if show_municipality:
        with middle:
            if st.button("Alterar município", key="change_municipality", use_container_width=True):
                st.session_state.editing_municipality = not st.session_state.editing_municipality
    with right:
        st.button(
            "SAÍDA RÁPIDA ✕",
            key="quick_exit",
            type="secondary",
            use_container_width=True,
            on_click=quick_exit,
        )


def render_emergency_card() -> None:
    st.markdown(
        """
        <section class="cassia-emergency" aria-label="Orientação para emergência">
          <h2>⚠️ Está em perigo imediato?</h2>
          <p>Se você estiver em uma situação de perigo imediato, ligue 190 para acionar a Polícia Militar.</p>
          <p style="margin-top:.45rem">O Ligue 180 oferece orientação sobre os direitos das mulheres e informações sobre serviços de atendimento.</p>
          <div class="cassia-emergency-actions">
            <a class="cassia-emergency-button cassia-emergency-190" href="tel:190">Ligar 190 — Emergência</a>
            <a class="cassia-emergency-button cassia-emergency-180" href="tel:180">Ligar 180 — Orientação</a>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    render_header()
    st.markdown(
        """
        <section class="cassia-hero">
          <div class="cassia-kicker">Um espaço de apoio</div>
          <h1>Cássia IA</h1>
          <p class="cassia-intro">Você pode contar no seu tempo. Sou uma assistente de apoio. Você escolhe como quer usar: posso só informar, ou te ouvir e organizar o que você contar. Você decide o que dizer e o que fazer depois.</p>
          <p class="cassia-gentle">Você está no controle desta conversa. Não há pressão para explicar, decidir ou agir agora.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cassia-section-title">Como você quer começar?</div>', unsafe_allow_html=True)
    first, second = st.columns(2)
    with first:
        st.button(
            "Quero apenas informações",
            key="home_info_button",
            type="primary",
            use_container_width=True,
            on_click=go_to_chat,
            args=(INFO_CHAT,),
        )
    with second:
        st.button(
            "Quero conversar",
            key="home_talk_button",
            type="primary",
            use_container_width=True,
            on_click=go_to_chat,
            args=(TALK_CHAT,),
        )

    st.markdown('<div class="cassia-section-title">Município</div>', unsafe_allow_html=True)
    st.text_input(
        "Município onde você está (opcional)",
        placeholder="Digite seu município",
        key="municipality",
    )
    st.markdown(
        '<p class="cassia-field-note">Essa informação pode ajudar a localizar serviços de atendimento na sua região. Não informe endereço, localização exata ou outros dados pessoais.</p>',
        unsafe_allow_html=True,
    )
    render_emergency_card()


def render_municipality_editor() -> None:
    if not st.session_state.editing_municipality:
        return
    with st.container(border=True):
        st.markdown("#### Município (opcional)")
        st.text_input(
            "Município onde você está (opcional)",
            placeholder="Digite seu município",
            key="municipality",
        )
        save, remove, cancel = st.columns(3)
        with save:
            if st.button("Salvar", key="save_municipality", use_container_width=True):
                st.session_state.editing_municipality = False
                st.rerun()
        with remove:
            st.button(
                "Remover",
                key="remove_municipality",
                type="secondary",
                use_container_width=True,
                on_click=clear_municipality,
            )
        with cancel:
            if st.button("Cancelar", key="cancel_municipality", type="secondary", use_container_width=True):
                st.session_state.editing_municipality = False
                st.rerun()


def render_message(message: dict[str, str]) -> None:
    role = message["role"]
    label = "Cássia IA" if role == "assistant" else "Você"
    kind = "assistant" if role == "assistant" else "user"
    st.markdown(
        f'<div class="cassia-message cassia-message-{kind}"><span class="cassia-message-label">{label}</span>{escape(message["content"])}</div>',
        unsafe_allow_html=True,
    )


def render_chat(mode: str) -> None:
    render_header(show_municipality=True)
    title = "Informações" if mode == INFO_CHAT else "Conversa"
    subtitle = (
        "Espaço preparado para informações fundamentadas em fontes oficiais."
        if mode == INFO_CHAT
        else "Espaço preparado para você escrever no seu ritmo."
    )
    st.markdown(f"## {title}")
    st.markdown(f'<p class="cassia-mode">{subtitle}</p>', unsafe_allow_html=True)
    render_municipality_editor()

    with st.container(height=420, border=False):
        st.markdown('<div class="cassia-chat">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            render_message(message)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.chat_error:
        st.error(st.session_state.chat_error)

    st.markdown(
        '<p class="cassia-disclosure">Compartilhe apenas o que você se sentir confortável em contar.</p>',
        unsafe_allow_html=True,
    )
    text = st.chat_input("Escreva no seu tempo...")
    if text:
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.chat_error = None
        try:
            with st.spinner("A Cássia está preparando uma resposta..."):
                reply = get_gemini_service().generate_reply(
                    st.session_state.messages,
                    mode,
                )
        except GeminiServiceError as error:
            st.session_state.chat_error = str(error)
        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
        st.rerun()


def render_neutral() -> None:
    st.markdown(
        """
        <section class="cassia-neutral">
          <h1>Página inicial</h1>
          <p>O conteúdo anterior não está mais sendo exibido.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Abrir Cássia IA", type="secondary"):
        st.session_state.screen = HOME
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Cássia IA", page_icon="🌷", layout="centered")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    initialize_state()

    screen = st.session_state.screen
    if screen == NEUTRAL:
        render_neutral()
    elif screen == HOME:
        render_home()
    elif screen in (INFO_CHAT, TALK_CHAT):
        render_chat(screen)
    else:
        st.session_state.screen = HOME
        st.rerun()


if __name__ == "__main__":
    main()
