from .models import AssistantSetting
from .schemas import AssistantSettingResponse

def domain_to_public_schema(domain: AssistantSetting) -> AssistantSettingResponse:
    return AssistantSettingResponse.model_validate(domain, from_attributes=True)
