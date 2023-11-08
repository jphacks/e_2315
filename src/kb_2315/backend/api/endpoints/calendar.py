from datetime import UTC, datetime, time, timedelta, timezone

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from icalendar import Calendar, Event

from kb_2315.backend.crud import crud_sensor, crud_session, crud_shoe
from kb_2315.backend.models import Session


router = APIRouter()


@router.get("/")
def get_calendar(shoe_id: int) -> PlainTextResponse:
    JST = timezone(timedelta(hours=+9), "JST")

    shoe_name: str = crud_shoe.search_shoe_by(shoe_id=shoe_id)[0].name
    sessions: list[Session] = crud_session.search_session_by(shoe_id=id)

    cal = Calendar()
    cal["summary"] = f"{shoe_name} の乾燥記録"
    cal["scale"] = "GREGORIAN"
    cal["method"] = "PUBLISH"
    cal["X-WR-CALNAME"] = f"{shoe_name} の乾燥記録"
    cal["X-WR-TIMEZONE"] = "Asia/Tokyo"

    for s in sessions:
        try:
            last_time: datetime = crud_sensor.search_sensor_by(session_id=s.session_id)[0].time

            e = Event(
                SUMMARY=f"{shoe_name} を履いた",
                DTSTART=datetime(
                    last_time.year, last_time.month, last_time.day, time(7, 0).hour, time(7, 0).minute, tzinfo=JST
                )
                .astimezone(UTC)
                .strftime("%Y%m%dT%H%M%SZ"),
                DTEND=last_time.strftime("%Y%m%dT%H%M%SZ"),
            )
            cal.add_component(e)
        except IndexError:
            pass

    ical_data: str = cal.to_ical().decode("utf-8")

    response = PlainTextResponse(content=ical_data, media_type="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=event.ics"

    return response
