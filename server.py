import os
import logging

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

import lot_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("lot_mcp_server")

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
if not AUTH_TOKEN:
    raise RuntimeError("AUTH_TOKEN environment variable is required")

verifier = StaticTokenVerifier(
    tokens={
        AUTH_TOKEN: {
            "client_id": "lot-client",
            "scopes": ["read:flights", "write:bookings"],
        }
    },
    required_scopes=["read:flights"],
)

mcp = FastMCP(
    name="LOT-Mock-API",
    instructions=(
        "Ten serwer symuluje API rezerwacji lotów LOT. Użyj search_flights, "
        "aby znaleźć loty, check_seat_availability, aby sprawdzić ceny i "
        "dostępność miejsc, a hold_booking, aby zarezerwować lot. Zawsze "
        "sprawdź dostępność miejsc przed próbą rezerwacji."
    ),
    auth=verifier,
)


@mcp.tool(name="search_flights", description="Wyszukuje loty LOT między dwoma lotniskami (kody IATA) na daną datę (YYYY-MM-DD).")
def search_flights(origin: str, destination: str, flight_date: str) -> list[dict]:
    results = lot_api.search_flights(origin, destination, flight_date)
    if not results:
        raise ValueError(f"No flights found for {origin}->{destination} on {flight_date}")
    return results


@mcp.tool(name="check_seat_availability", description="Sprawdza cenę i liczbę wolnych miejsc dla danego lotu i klasy ('economy' lub 'business').")
def check_seat_availability(flight_id: str, seat_class: str) -> dict:
    return lot_api.check_seat_availability(flight_id, seat_class)


@mcp.tool(name="hold_booking", description="Rezerwuje wskazany lot i klasę. Wywołuj TYLKO po potwierdzeniu dostępności miejsc.")
def hold_booking(flight_id: str, seat_class: str, ffn: str | None = None) -> dict:
    return lot_api.hold_booking(flight_id, seat_class, ffn)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=9000,
        log_level="INFO",
    )