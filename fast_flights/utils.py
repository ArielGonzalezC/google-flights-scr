"""Utility functions for round-trip flight support."""

import base64
import re
from typing import Any, Dict, List, Tuple

try:
    from . import schema_roundtrip_pb2 as RT_PB
except ImportError:
    RT_PB = None  # type: ignore


def extract_airline_code_and_flight_number(s: str) -> List[Tuple[str, str]]:
    """Extract airline codes and flight numbers from travelimpactmodel URL.
    
    Args:
        s: URL string containing flight information
        
    Returns:
        List of tuples containing (airline_code, flight_number)
    """
    # Pattern matches airline code (2 letters) followed by flight number
    pattern = r'([A-Z]{2})(\d+)'
    matches = re.findall(pattern, s)
    return matches


def is_airport_path(path: str) -> bool:
    """Check if a string represents an airport path.
    
    Args:
        path: String to check
        
    Returns:
        True if path appears to be an airport code/path
    """
    # Airport codes are typically 3 uppercase letters
    return bool(re.match(r'^[A-Z]{3}$', path.strip()))


def create_tfs_for_return_flight(
    outbound_flight: Dict[str, Any],
    from_airport: str,
    to_airport: str,
    return_date: str,
    seat_type: str,
    passenger_types: List[str]
) -> str:
    """Create a TFS (travel flight search) parameter for return flight lookup.
    
    Args:
        outbound_flight: Dictionary containing outbound flight information
        from_airport: Departure airport code for return flight
        to_airport: Arrival airport code for return flight
        return_date: Date of return flight (YYYY-MM-DD)
        seat_type: Seat class (economy, premium-economy, business, first)
        passenger_types: List of passenger types (adult, child, etc.)
        
    Returns:
        Base64-encoded TFS string with '=' stripped
    """
    if RT_PB is None:
        raise ImportError("schema_roundtrip_pb2 module not available. Please compile the proto file.")
    
    # Create RoundTripData message
    round_trip_data = RT_PB.RoundTripData()
    
    # Map seat type to enum
    seat_map = {
        "economy": RT_PB.RT_ECONOMY,
        "premium-economy": RT_PB.RT_PREMIUM_ECONOMY,
        "business": RT_PB.RT_BUSINESS,
        "first": RT_PB.RT_FIRST,
    }
    round_trip_data.seat = seat_map.get(seat_type, RT_PB.RT_ECONOMY)
    
    # Set trip type to round-trip
    round_trip_data.trip = RT_PB.RT_ROUND_TRIP
    
    # Map passenger types to enum
    passenger_map = {
        "adult": RT_PB.RT_ADULT,
        "child": RT_PB.RT_CHILD,
        "infant_in_seat": RT_PB.RT_INFANT_IN_SEAT,
        "infant_on_lap": RT_PB.RT_INFANT_ON_LAP,
    }
    
    for passenger_type in passenger_types:
        passenger_enum = passenger_map.get(passenger_type.lower(), RT_PB.RT_ADULT)
        round_trip_data.passengers.append(passenger_enum)
    
    # Add outbound flight data
    outbound_data = round_trip_data.flights_data.add()
    outbound_data.date = outbound_flight.get('departure_date', '')
    
    # Set airport codes for outbound
    outbound_data.airport_from.path = outbound_flight.get('from_airport', to_airport)
    outbound_data.airport_to.path = outbound_flight.get('to_airport', from_airport)
    
    # Add flight legs if flight_codes are present
    flight_codes = outbound_flight.get('flight_codes', [])
    if flight_codes:
        for airline_code, flight_number in flight_codes:
            flight = outbound_data.flights.add()
            flight.airline = airline_code
            flight.flight_number = flight_number
    
    # Add return flight placeholder
    return_data = round_trip_data.flights_data.add()
    return_data.date = return_date
    return_data.airport_from.path = from_airport
    return_data.airport_to.path = to_airport
    
    # Serialize and encode
    serialized = round_trip_data.SerializeToString()
    encoded = base64.urlsafe_b64encode(serialized).decode('utf-8').rstrip('=')
    
    return encoded
