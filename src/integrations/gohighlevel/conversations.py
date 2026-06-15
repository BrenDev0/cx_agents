import httpx

class ConversationsClient:
    def __init__(
        self,
        http: httpx.AsyncClient
    ):
        self.http = http

    async def send_message(
        self,
        type: str,
        contact_id: str,
        message: str
    ):
        body = {
            "type": type,
            "contactId": contact_id,
            "message": message,
            "status": "delivered"
        }

        response = await self.http.post(
            "/conversations/messages",
            json=body
        )
        response.raise_for_status()
        return response.json()
    

    async def get_conversation_by_contact_id(
        self,
        contact_id: str
    ) -> str:
        query_parameters = {
            contact_id: contact_id
        }
        response = await self.http.get(
            "/conversations/search",
            params=query_parameters
        )

        response.raise_for_status()
        return response.json()


