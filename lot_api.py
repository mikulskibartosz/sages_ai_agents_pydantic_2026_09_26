import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("lot_api")

_MOCK_FLIGHTS = {
    ("WAW", "LIS"): [
        {"flight_id": "LO3931", "date": "2026-09-04", "departure": "07:15", "arrival": "10:40",
         "classes": {"economy": {"price": 890, "seats": 12}, "business": {"price": 2400, "seats": 3}}},
        {"flight_id": "LO3933", "date": "2026-09-04", "departure": "14:20", "arrival": "17:45",
         "classes": {"economy": {"price": 950, "seats": 5}, "business": {"price": 2600, "seats": 0}}},
    ],
    ("WAW", "JFK"): [
        {"flight_id": "LO003", "date": "2026-09-04", "departure": "11:00", "arrival": "14:10",
         "classes": {"economy": {"price": 3200, "seats": 20}, "business": {"price": 8900, "seats": 6}}},
    ],
}
_BOOKINGS: dict[str, dict] = {}
_BOOKING_COUNTER = 0


def search_flights(origin: str, destination: str, flight_date: str) -> list[dict]:
    logger.info(f"search_flights: {origin}->{destination} on {flight_date}")
    route = _MOCK_FLIGHTS.get((origin, destination), [])
    return [f for f in route if f["date"] == flight_date]


def check_seat_availability(flight_id: str, seat_class: str) -> dict:
    logger.info(f"check_seat_availability: flight={flight_id}, class={seat_class}")
    for flights in _MOCK_FLIGHTS.values():
        for f in flights:
            if f["flight_id"] == flight_id:
                if seat_class not in f["classes"]:
                    raise ValueError(f"Unknown seat class '{seat_class}'")
                return {"flight_id": flight_id, "seat_class": seat_class, **f["classes"][seat_class]}
    raise KeyError(flight_id)


def hold_booking(flight_id: str, seat_class: str, ffn: str | None = None) -> dict:
    global _BOOKING_COUNTER
    logger.warning(f"hold_booking: flight={flight_id}, class={seat_class}, ffn={ffn}")
    avail = check_seat_availability(flight_id, seat_class)
    if avail["seats"] <= 0:
        raise ValueError(f"No seats available in {seat_class} on {flight_id}")
    _BOOKING_COUNTER += 1
    booking_id = f"BK{_BOOKING_COUNTER:04d}"
    _BOOKINGS[booking_id] = {"flight_id": flight_id, "seat_class": seat_class, "ffn": ffn, "status": "held"}
    return {"booking_id": booking_id, "flight_id": flight_id, "seat_class": seat_class, "status": "held"}