import httpx
import logging
from src.exceptions import BadRequestException
from src.types import ChatMessage, MessageRole

ghl_channel_map = {
    "whatsapp": "TYPE_WHATSAPP"
}

ghl_message_type = {
    "whatsapp": "WhatsApp"
}

logger = logging.getLogger(__name__)
class GHLConversationsClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        headers: dict[str, str]
    ):
        self._http = http
        self._headers = headers

    async def send_message(
        self,
        channel: str,
        contact_id: str,
        message: str
    ):
    
        body = {
            "type": ghl_message_type[channel],
            "contactId": contact_id,
            "message": message,
            "status": "delivered"
        }

        response = await self._http.post(
            "/conversations/messages",
            headers=self._headers,
            json=body
        )
        response.raise_for_status()
        return response.json()
    

    async def _get_chat_id(self, contact_id: str, location_id: str) -> str:
        params = httpx.QueryParams(
            contactId=contact_id,
            locationId=location_id,
            limit=1
        )

        response = await self._http.get(
            "/conversations/search",
            params=params,
            headers=self._headers,
        )
        response.raise_for_status()

        conversations = response.json().get("conversations")
        if not conversations or not isinstance(conversations, list):
            raise ValueError("Invalid response format from get conversations")

        return conversations[0].get("id")


    async def get_chat_history(
        self,
        contact_id: str,
        location_id: str,
        channel: str,
        limit: int = 5
    ) -> list[ChatMessage]:
        conversation_id = await self._get_chat_id(contact_id=contact_id, location_id=location_id)

        if not conversation_id:
            raise BadRequestException("No conversation found")

        params = httpx.QueryParams(
            limit=limit,
            type=ghl_channel_map[channel]
        )

        response = await self._http.get(
            f"/conversations/{conversation_id}/messages",
            params=params,
            headers=self._headers
        )

        response.raise_for_status()

        data = response.json().get("messages")
        if not data:
            raise ValueError("Message response not valid")

        messages = data.get("messages")

        if not messages or not isinstance(messages, list):
            raise ValueError("invalid response from get messages")

        chat_history = [
            ChatMessage(
                id=message["id"],
                role=MessageRole.AI if message["direction"] == "outbound" else MessageRole.HUMAN,
                content=message["body"]
            )
            for message in messages
        ]

        return chat_history
