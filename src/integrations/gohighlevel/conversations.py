import httpx

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
            "type": channel,
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


