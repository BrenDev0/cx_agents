import httpx
from datetime import datetime, timedelta

class AppointmentsClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        headers: dict[str, str],
        location_id: str
    ):
        self._http = http
        self._headers = headers
        self._location_id = location_id


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

        
    async def check_availability(
        self,
        calendar_id: str,
        start_time: str,
        timezone: str
    ) -> bool:
        requested = datetime.fromisoformat(start_time)
        day_start = requested.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        slots = await self.get_slots(
            calendar_id=calendar_id,
            start_date=int(day_start.timestamp() * 1000),
            end_date=int(day_end.timestamp() * 1000),
            timezone=timezone
        )

        day_slots = slots.get(day_start.strftime("%Y-%m-%d"), {}).get("slots", [])
        return start_time in day_slots


    async def book(
        self,
        calendar_id: str,
        contact_id: str,
        start_time: str,
        title: str | None = None
    ):
        body = {
            "calendarId": calendar_id,
            "locationId": self._location_id,
            "contactId": contact_id,
            "startTime": start_time
        }

        if title:
            body["title"] = title

        response = await self._http.post(
            url="/calendars/events/appointments",
            headers=self._headers,
            json=body
        )
        response.raise_for_status()
        return response.json()


    async def update_appointment(
        self,
        appointment_id: str,
        calendar_id: str,
        start_time: str
    ):
        body = {
            "calendarId": calendar_id,
            "startTime": start_time
        }

        response = await self._http.put(
            url=f"/calendars/events/appointments/{appointment_id}",
            headers=self._headers,
            json=body
        )
        response.raise_for_status()
        return response.json()


    async def cancel_appointment(
        self,
        appointment_id: str
    ):
        body = {"appointmentStatus": "cancelled"}

        response = await self._http.put(
            url=f"/calendars/events/appointments/{appointment_id}",
            headers=self._headers,
            json=body
        )
        response.raise_for_status()
        return response.json()

