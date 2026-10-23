"""Coordena o processamento inicial de relatos fictícios no MVP."""

from case.schemas import CaseSummary
from case.validation import validate_case_summary


def process_case_report(report: str) -> CaseSummary:
    """Cria um rascunho estruturado para revisão humana.

    Esta primeira versão não interpreta fatos nem oferece orientação. Ela apenas
    preserva o relato informado, registra campos que poderão ser complementados
    e valida o contrato de saída. A etapa de LLM, RAG e ferramentas será incluída
    sobre esta interface em seguida.
    """
    normalized_report = " ".join(report.split())
    if not normalized_report:
        raise ValueError("O relato fictício não pode estar vazio.")

    draft = {
        "summary": normalized_report,
        "missing_information": [
            "Data ou período aproximado dos fatos, se for seguro informar.",
            "Localização aproximada, se for seguro informar.",
            "Forma segura de contato para eventual acompanhamento.",
        ],
        "sources": [],
        "requires_human_review": True,
    }
    return validate_case_summary(draft)
