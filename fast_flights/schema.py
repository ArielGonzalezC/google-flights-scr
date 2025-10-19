from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple


@dataclass
class Result:
    current_price: Literal["low", "typical", "high"]
    flights: List[Flight]


@dataclass
class Flight:
    is_best: bool
    name: str
    departure: str
    arrival: str
    arrival_time_ahead: str
    duration: str
    stops: int
    delay: Optional[str]
    price: str
    flight_codes: List[Tuple[str, str]] = None  # type: ignore
    departure_date: Optional[str] = None
    # Round-trip specific fields
    outbound_name: Optional[str] = None
    outbound_departure: Optional[str] = None
    outbound_arrival: Optional[str] = None
    outbound_arrival_time_ahead: Optional[str] = None
    outbound_duration: Optional[str] = None
    outbound_stops: Optional[int] = None
    outbound_delay: Optional[str] = None
    outbound_price: Optional[str] = None
    return_name: Optional[str] = None
    return_departure: Optional[str] = None
    return_arrival: Optional[str] = None
    return_arrival_time_ahead: Optional[str] = None
    return_duration: Optional[str] = None
    return_stops: Optional[int] = None
    return_delay: Optional[str] = None
    return_price: Optional[str] = None
