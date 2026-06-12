from httpx import AsyncClient
from .appointments import AppointmentsClient

class GoHighLevelClient:
    def __int__(
        self,
        pit: str
    ):
        self.http = AsyncClient(
            base_url="https://services.leadconnectorhq.com",
            headers={
                "Authorization": f"Bearer {pit}",
                "Version": "v3",
            },
        )

        self.appointments = AppointmentsClient(http=self.http)