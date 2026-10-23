
from pydantic import ValidationError

from case.schemas import CaseSummary


def validate_case_summary(data: dict) -> CaseSummary:
    
    # Valida os dados de saída do agente e retorna um CaseSummary.

    # Levanta ValidationError caso os dados não respeitem 
    # o esquema definido em CaseSummary.
    
    return CaseSummary.model_validate(data)
