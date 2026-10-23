"""Ferramentas locais que podem ser acionadas no fluxo do agente."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from case.schemas import CaseSummary


DEFAULT_DRAFTS_DIRECTORY = Path(__file__).resolve().parent.parent / "reports" / "drafts"


def save_draft_for_human_review(
    case_summary: CaseSummary, output_directory: Path | None = None
) -> Path:
    """Salva um rascunho estruturado local para posterior revisão humana.

    O arquivo é destinado exclusivamente aos relatos fictícios usados na
    demonstração. Nenhum envio externo é realizado por esta ferramenta.
    """
    drafts_directory = output_directory or DEFAULT_DRAFTS_DIRECTORY
    drafts_directory.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc)
    filename = f"draft_{created_at.strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}.json"
    draft_path = drafts_directory / filename
    draft = {
        "created_at": created_at.isoformat(),
        "status": "pending_human_review",
        "case_summary": case_summary.model_dump(),
    }

    with draft_path.open("w", encoding="utf-8") as file:
        json.dump(draft, file, ensure_ascii=False, indent=2)

    return draft_path
