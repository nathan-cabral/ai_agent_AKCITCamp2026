from pydantic import BaseModel

# definir o formato dos dados
class CaseSummary(BaseModel):
    summary: str
    missing_information: list[str]
    sources: list[str]
    requires_human_review: bool