from .models import Assistant 
from .schemas import AssistantResponse

def domain_to_public_schema(domain: Assistant) -> AssistantResponse:
    return AssistantResponse.model_validate(domain, from_attributes=True)