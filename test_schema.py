from case.schemas import CaseSummary

caso = CaseSummary(
    summary="Relato fictício para teste.",
    missing_information=["Data do ocorrido"],
    sources=["manual_ficticio.pdf"],
    requires_human_review=True,
)

print(caso)
print(caso.model_dump())
