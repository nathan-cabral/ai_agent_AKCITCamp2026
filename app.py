"""Interface Streamlit da Cássia IA."""

from html import escape

import streamlit as st

from agent.llm import GeminiService, GeminiServiceError
from ui.location import (
    UF_NAMES,
    LocationDataError,
    format_location,
    load_municipalities,
    search_municipalities,
)
from ui.styles import APP_CSS


HOME = "home"
INFO_CHAT = "info_chat"
TALK_CHAT = "talk_chat"
NEUTRAL = "neutral"
UF_OPTIONS = [""] + list(UF_NAMES)


def initialize_state() -> None:
    defaults = {
        "screen": HOME,
        "municipality_query": "",
        "uf_selection": "",
        "selected_location": None,
        "location_confirmed": False,
        "location_skipped": False,
        "editing_location": False,
        "messages": [],
        "chat_error": None,
        "location_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def quick_exit() -> None:
    """Remove o conteúdo transitório e exibe uma tela neutra."""
    for key in (
        "municipality_query",
        "uf_selection",
        "selected_location",
        "location_confirmed",
        "location_skipped",
        "editing_location",
        "messages",
        "chat_error",
        "location_error",
    ):
        st.session_state.pop(key, None)
    st.session_state.screen = NEUTRAL


def toggle_location_editor() -> None:
    st.session_state.editing_location = not st.session_state.editing_location
    st.session_state.location_error = None


def select_location(location: dict[str, str]) -> None:
    st.session_state.selected_location = location
    st.session_state.municipality_query = location["name"]
    st.session_state.uf_selection = location["uf"]
    st.session_state.location_error = None


def handle_uf_change() -> None:
    selected = st.session_state.get("selected_location")
    current_uf = st.session_state.get("uf_selection", "")
    if selected and selected["uf"] != current_uf:
        st.session_state.selected_location = None
        st.session_state.location_error = (
            "O município selecionado foi limpo porque não pertence ao estado escolhido."
        )


def clear_location() -> None:
    st.session_state.selected_location = None
    st.session_state.municipality_query = ""
    st.session_state.uf_selection = ""
    st.session_state.location_confirmed = False
    st.session_state.location_skipped = True
    st.session_state.editing_location = False
    st.session_state.location_error = None


def enter_chat(mode: str = TALK_CHAT, skipped: bool = False) -> None:
    st.session_state.screen = mode
    st.session_state.editing_location = False
    st.session_state.location_error = None
    st.session_state.location_confirmed = not skipped
    st.session_state.location_skipped = skipped
    st.session_state.chat_error = None
    if not st.session_state.messages:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Posso apresentar informações gerais e fontes oficiais quando "
                    "essa etapa estiver integrada. Você não precisa contar nada "
                    "pessoal para usar este espaço."
                    if mode == INFO_CHAT
                    else "Estou aqui para te ouvir no seu tempo. Você pode pedir "
                    "informações ou compartilhar o que quiser; não precisa incluir "
                    "detalhes que não queira."
                ),
            }
        ]


def confirm_location(mode: str = TALK_CHAT) -> None:
    selected = st.session_state.get("selected_location")
    current_uf = st.session_state.get("uf_selection", "")
    if not selected:
        st.session_state.location_error = (
            "Selecione um município válido nas sugestões ou escolha informar depois."
        )
        return
    if selected["uf"] != current_uf:
        st.session_state.selected_location = None
        st.session_state.location_error = (
            "O município selecionado não corresponde ao estado escolhido."
        )
        return
    enter_chat(mode)


def start_mode(mode: str) -> None:
    """Entra na modalidade escolhida, com ou sem localização."""
    if st.session_state.get("selected_location"):
        confirm_location(mode)
    else:
        enter_chat(mode, skipped=True)


@st.cache_resource(show_spinner=False)
def get_gemini_service() -> GeminiService:
    return GeminiService()


def render_header(show_location: bool = False) -> None:
    left, middle, right = st.columns([5, 2, 2])
    with left:
        st.markdown(
            '<div class="cassia-brand">Cássia IA<span>assistente de apoio</span></div>',
            unsafe_allow_html=True,
        )
    if show_location:
        with middle:
            st.button(
                "Alterar localização",
                key="change_location",
                use_container_width=True,
                on_click=toggle_location_editor,
            )
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


def render_location_screen() -> None:
    render_header()
    st.markdown(
        """
        <section class="cassia-hero">
          <div class="cassia-kicker">Um espaço de apoio</div>
          <h1>Cássia IA</h1>
          <p class="cassia-intro">Você pode contar no seu tempo. Sou uma assistente de apoio. Você decide o que dizer e o que fazer depois.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_location_form(editing=False)
    render_emergency_card()


def format_uf_option(uf: str) -> str:
    return "Selecione o estado" if not uf else f"{uf} — {UF_NAMES[uf]}"


def render_location_form(editing: bool) -> None:
    title = "Alterar localização" if editing else "Onde você procura atendimento?"
    support = (
        "Essa informação ajuda a encontrar serviços na sua região. "
        "Você pode pular esta etapa e informar depois."
    )
    st.markdown(f'<div class="cassia-section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="cassia-field-note">{support}</p>', unsafe_allow_html=True)

    try:
        municipalities = load_municipalities()
    except LocationDataError as error:
        municipalities = ()
        st.warning(f"{error} Você ainda pode continuar sem informar a localização.")

    st.text_input(
        "Município",
        placeholder="Digite o nome do município",
        key="municipality_query",
        help="A seleção precisa ser confirmada nas sugestões para evitar municípios homônimos.",
    )
    query = st.session_state.municipality_query.strip()
    uf = st.session_state.uf_selection
    suggestions = search_municipalities(municipalities, query, uf)

    if query and municipalities and not suggestions:
        st.info("Nenhum município encontrado. Tente outro nome ou altere o estado.")
    elif suggestions:
        st.caption("Selecione o município correto:")
        for index, location in enumerate(suggestions):
            st.button(
                format_location(location),
                key=f"location_suggestion_{location['uf']}_{index}",
                type="secondary",
                use_container_width=True,
                on_click=select_location,
                args=(location,),
            )

    st.selectbox(
        "Estado",
        options=UF_OPTIONS,
        format_func=format_uf_option,
        key="uf_selection",
        on_change=handle_uf_change,
    )

    selected = st.session_state.selected_location
    if selected:
        st.success(f"Município selecionado: {format_location(selected)}")
    if st.session_state.location_error:
        st.warning(st.session_state.location_error)

    if editing:
        confirm, skip, remove = st.columns(3)
        with confirm:
            st.button(
                "Confirmar",
                key="location_confirm_edit",
                type="primary",
                use_container_width=True,
                on_click=confirm_location,
            )
        with skip:
            st.button(
                "Informar depois",
                key="location_skip_edit",
                type="secondary",
                use_container_width=True,
                on_click=lambda: enter_chat(skipped=True),
            )
        with remove:
            st.button(
                "Remover",
                key="location_remove_edit",
                type="secondary",
                use_container_width=True,
                on_click=clear_location,
            )
    else:
        st.markdown(
            '<div class="cassia-section-title">Como você quer continuar?</div>',
            unsafe_allow_html=True,
        )
        info_button, talk_button = st.columns(2)
        with info_button:
            st.button(
                "Quero apenas informações",
                key="home_info_button",
                type="primary",
                use_container_width=True,
                on_click=start_mode,
                args=(INFO_CHAT,),
            )
        with talk_button:
            st.button(
                "Quero conversar",
                key="home_talk_button",
                type="primary",
                use_container_width=True,
                on_click=start_mode,
                args=(TALK_CHAT,),
            )
        st.button(
            "Prefiro informar depois",
            key="location_skip",
            type="secondary",
            use_container_width=True,
            on_click=lambda: enter_chat(TALK_CHAT, skipped=True),
        )


def render_message(message: dict[str, str]) -> None:
    role = message["role"]
    label = "Cássia IA" if role == "assistant" else "Você"
    kind = "assistant" if role == "assistant" else "user"
    st.markdown(
        f'<div class="cassia-message cassia-message-{kind}"><span class="cassia-message-label">{label}</span>{escape(message["content"])}</div>',
        unsafe_allow_html=True,
    )


def render_chat(mode: str) -> None:
    render_header(show_location=True)
    title = "Informações" if mode == INFO_CHAT else "Conversa"
    subtitle = (
        "Espaço para pedir informações gerais com clareza e acolhimento."
        if mode == INFO_CHAT
        else "Espaço para você escrever no seu ritmo."
    )
    st.markdown(f"## {title}")
    st.markdown(f'<p class="cassia-mode">{subtitle}</p>', unsafe_allow_html=True)
    location = st.session_state.selected_location
    if st.session_state.location_confirmed and location:
        st.markdown(
            f'<p class="cassia-mode">Localização selecionada: {escape(format_location(location))}</p>',
            unsafe_allow_html=True,
        )
    elif st.session_state.location_skipped:
        st.markdown(
            '<p class="cassia-mode">Localização não informada. Você pode adicionar depois.</p>',
            unsafe_allow_html=True,
        )

    if st.session_state.editing_location:
        render_location_form(editing=True)

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
                reply = get_gemini_service().generate_reply(st.session_state.messages, mode)
        except GeminiServiceError as error:
            st.session_state.chat_error = str(error)
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
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
    st.button(
        "Abrir Cássia IA",
        type="secondary",
        on_click=lambda: st.session_state.update(screen=HOME),
    )


def main() -> None:
    st.set_page_config(page_title="Cássia IA", page_icon="🌷", layout="centered")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    initialize_state()

    screen = st.session_state.screen
    if screen == NEUTRAL:
        render_neutral()
    elif screen == HOME:
        render_location_screen()
    elif screen in (INFO_CHAT, TALK_CHAT):
        render_chat(screen)
    else:
        st.session_state.screen = HOME
        st.rerun()


if __name__ == "__main__":
    main()
