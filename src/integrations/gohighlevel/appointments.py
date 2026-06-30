import httpx

class AppointmentsClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        headers: dict[str, str]
    ):
        self._http = http
        self._headers = headers


    async def check_for_existing_appointment(
        self,
        contact_id: str
    ):
        response = await self._http.get(
            f"/contacts/{contact_id}/appointments",
            headers=self._headers
        )
        response.raise_for_status()
        return response.json()


    async def get_slots(
        self,
        calendar_id: str,
        start_date: int,
        end_date: int,
        timezone: str
    ):
        query_params: dict[str, str | int] = {
            "startDate": start_date,
            "endDate": end_date,
            "timeZone": timezone
        }
        
        response = await self._http.get(
            url=f"/calendars/{calendar_id}/free-slots",
            headers=self._headers,
            params=query_params
        )

        response.raise_for_status()
        return response.json()

        
    async def check_availability(self):
        pass


    async def book(
        self,
        calendar_id: str,
        location_id: str,
        contact_id: str,
        start_time: str
    ):
        body = {
            "calendarId": calendar_id,
            "locationId": location_id,
            "contactId": contact_id,
            "startTime": start_time   
        }

        response = await self._http.post(
            url="/calendars/events/appointments",
            headers=self._headers,
            json=body
        )
        response.raise_for_status()
        return response.json()


    async def update_appointment(self):
        pass


    async def cancel_appointment(self):
        pass

