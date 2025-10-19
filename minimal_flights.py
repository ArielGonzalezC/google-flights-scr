"""
Minimal Google Flights Scraper
================================
A simple, well-commented implementation for scraping Google Flights using protobuf encoding.

This module provides a minimalist interface to:
- Search for one-way and round-trip flights
- Parse flight results from Google Flights HTML
- Handle different seat classes and passenger configurations
"""

import base64
import re
import json
from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Dict, Any

# Import required dependencies
from selectolax.lexbor import LexborHTMLParser, LexborNode

# Import protobuf definitions (generated from flights.proto)
try:
    from fast_flights import flights_pb2 as PB
except ImportError:
    print("Warning: flights_pb2 not available. Protobuf encoding will not work.")
    PB = None


# ============================================================================
# Data Models - Simple classes to represent flights and results
# ============================================================================

@dataclass
class Flight:
    """Represents a single flight option.
    
    Attributes:
        is_best: Whether Google marks this as the best option
        name: Airline name(s)
        departure: Departure time
        arrival: Arrival time
        arrival_time_ahead: Time difference (e.g., "+1 day")
        duration: Flight duration
        stops: Number of stops
        delay: Delay information (if any)
        price: Price as string (e.g., "$500")
        flight_codes: List of (airline_code, flight_number) tuples
        
    Round-trip specific attributes:
        outbound_*: Details of the outbound flight
        return_*: Details of the return flight
    """
    is_best: bool
    name: str
    departure: str
    arrival: str
    arrival_time_ahead: str
    duration: str
    stops: int
    delay: Optional[str]
    price: str
    flight_codes: List[tuple] = None
    
    # For round-trip flights - outbound leg
    outbound_name: Optional[str] = None
    outbound_departure: Optional[str] = None
    outbound_arrival: Optional[str] = None
    outbound_duration: Optional[str] = None
    outbound_stops: Optional[int] = None
    outbound_price: Optional[str] = None
    
    # For round-trip flights - return leg
    return_name: Optional[str] = None
    return_departure: Optional[str] = None
    return_arrival: Optional[str] = None
    return_duration: Optional[str] = None
    return_stops: Optional[int] = None
    return_price: Optional[str] = None


@dataclass
class SearchResult:
    """Result of a flight search.
    
    Attributes:
        current_price: Price indicator ("low", "typical", "high")
        flights: List of flight options
    """
    current_price: str
    flights: List[Flight]


@dataclass
class FlightQuery:
    """Defines a flight search query.
    
    Attributes:
        date: Departure date (YYYY-MM-DD)
        from_airport: Origin airport code (e.g., "JFK")
        to_airport: Destination airport code (e.g., "LAX")
        max_stops: Maximum number of stops (optional)
    """
    date: str
    from_airport: str
    to_airport: str
    max_stops: Optional[int] = None


@dataclass
class PassengerConfig:
    """Passenger configuration for a flight search.
    
    Attributes:
        adults: Number of adults
        children: Number of children
        infants_in_seat: Number of infants with seat
        infants_on_lap: Number of infants on lap
    """
    adults: int = 1
    children: int = 0
    infants_in_seat: int = 0
    infants_on_lap: int = 0
    
    def validate(self):
        """Validate passenger configuration."""
        total = self.adults + self.children + self.infants_in_seat + self.infants_on_lap
        if total > 9:
            raise ValueError(f"Too many passengers ({total}). Maximum is 9.")
        if self.infants_on_lap > self.adults:
            raise ValueError("Each infant on lap requires an adult.")
        return self


# ============================================================================
# Protobuf Encoding - Convert search parameters to Google Flights format
# ============================================================================

def create_search_filter(
    queries: List[FlightQuery],
    trip_type: Literal["one-way", "round-trip", "multi-city"],
    passengers: PassengerConfig,
    seat_class: Literal["economy", "premium-economy", "business", "first"],
) -> str:
    """Create a base64-encoded protobuf filter for Google Flights.
    
    This function encodes search parameters into Google's proprietary protobuf format
    used in the ?tfs= URL parameter.
    
    Args:
        queries: List of flight queries (1 for one-way, 2 for round-trip)
        trip_type: Type of trip
        passengers: Passenger configuration
        seat_class: Seat class preference
        
    Returns:
        Base64-encoded protobuf string
    """
    if PB is None:
        raise ImportError("flights_pb2 module not available")
    
    # Validate input
    passengers.validate()
    if trip_type == "round-trip" and len(queries) != 2:
        raise ValueError("Round-trip requires exactly 2 flight queries")
    elif trip_type == "one-way" and len(queries) != 1:
        raise ValueError("One-way requires exactly 1 flight query")
    
    # Create protobuf message
    info = PB.Info()
    
    # Set seat class
    seat_map = {
        "economy": PB.Seat.ECONOMY,
        "premium-economy": PB.Seat.PREMIUM_ECONOMY,
        "business": PB.Seat.BUSINESS,
        "first": PB.Seat.FIRST,
    }
    info.seat = seat_map[seat_class]
    
    # Set trip type
    trip_map = {
        "one-way": PB.Trip.ONE_WAY,
        "round-trip": PB.Trip.ROUND_TRIP,
        "multi-city": PB.Trip.MULTI_CITY,
    }
    info.trip = trip_map[trip_type]
    
    # Add passengers
    passenger_map = [
        (passengers.adults, PB.Passenger.ADULT),
        (passengers.children, PB.Passenger.CHILD),
        (passengers.infants_in_seat, PB.Passenger.INFANT_IN_SEAT),
        (passengers.infants_on_lap, PB.Passenger.INFANT_ON_LAP),
    ]
    for count, passenger_type in passenger_map:
        for _ in range(count):
            info.passengers.append(passenger_type)
    
    # Add flight data
    for query in queries:
        data = info.data.add()
        data.date = query.date
        data.from_flight.airport = query.from_airport
        data.to_flight.airport = query.to_airport
        if query.max_stops is not None:
            data.max_stops = query.max_stops
    
    # Serialize and encode
    serialized = info.SerializeToString()
    return base64.b64encode(serialized).decode('utf-8')


# ============================================================================
# HTML Parsing - Extract flight information from Google Flights pages
# ============================================================================

def parse_flights_from_html(html_content: str) -> SearchResult:
    """Parse flight results from Google Flights HTML.
    
    Args:
        html_content: Raw HTML from Google Flights search page
        
    Returns:
        SearchResult with parsed flights
    """
    # Helper class for safe node access
    class SafeNode:
        def text(self, *args, **kwargs):
            return ""
        def iter(self):
            return []
    
    safe_node = SafeNode()
    
    def safe(node: Optional[LexborNode]) -> Union[LexborNode, SafeNode]:
        """Return node or safe placeholder."""
        return node or safe_node
    
    parser = LexborHTMLParser(html_content)
    flights = []
    
    # Parse each flight card
    for idx, flight_card in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best = (idx == 0)  # First flight is marked as "best"
        
        # Parse each flight option within the card
        for item in flight_card.css("ul.Rk10dc li"):
            # Extract airline name
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf span")).text(strip=True)
            
            # Extract departure and arrival times
            time_nodes = item.css("span.mv1WYe div")
            try:
                departure = time_nodes[0].text(strip=True)
                arrival = time_nodes[1].text(strip=True)
            except IndexError:
                departure = ""
                arrival = ""
            
            # Extract additional details
            time_ahead = safe(item.css_first("span.bOzv6")).text()
            duration = safe(item.css_first("li div.Ak5kof div")).text()
            stops_text = safe(item.css_first(".BbR8Ec .ogfYpf")).text()
            delay = safe(item.css_first(".GsCCve")).text() or None
            price = safe(item.css_first(".YMlIz.FpEdX")).text() or "0"
            
            # Parse stops count
            try:
                stops = 0 if stops_text == "Nonstop" else int(stops_text.split()[0])
            except (ValueError, IndexError):
                stops = 0
            
            # Extract flight codes from data attribute
            flight_codes = []
            impact_elem = item.css_first(".NZRfve[data-travelimpactmodelwebsiteurl]")
            if impact_elem:
                url = impact_elem.attributes.get('data-travelimpactmodelwebsiteurl', '')
                if url:
                    # Extract airline code and flight number (e.g., "UA123")
                    matches = re.findall(r'([A-Z]{2})(\d+)', url)
                    flight_codes = matches
            
            flights.append(Flight(
                is_best=is_best,
                name=name,
                departure=" ".join(departure.split()),
                arrival=" ".join(arrival.split()),
                arrival_time_ahead=time_ahead,
                duration=duration,
                stops=stops,
                delay=delay,
                price=price.replace(",", ""),
                flight_codes=flight_codes,
            ))
    
    # Extract price indicator
    current_price = safe(parser.css_first("span.gOatQ")).text()
    
    if not flights:
        raise RuntimeError("No flights found in HTML content")
    
    return SearchResult(current_price=current_price, flights=flights)


# ============================================================================
# Round-Trip Support - Pair outbound and return flights
# ============================================================================

def combine_round_trip_flights(outbound: Flight, return_flight: Flight) -> Flight:
    """Combine outbound and return flights into a single round-trip flight.
    
    Args:
        outbound: Outbound flight
        return_flight: Return flight
        
    Returns:
        Combined Flight object with both legs
    """
    # Calculate combined price
    try:
        outbound_price = float(outbound.price.replace('$', '').replace(',', ''))
        return_price = float(return_flight.price.replace('$', '').replace(',', ''))
        combined_price = f"${outbound_price + return_price:.2f}"
    except (ValueError, AttributeError):
        combined_price = f"{outbound.price} + {return_flight.price}"
    
    return Flight(
        is_best=outbound.is_best and return_flight.is_best,
        name=f"{outbound.name} + {return_flight.name}",
        departure=outbound.departure,
        arrival=return_flight.arrival,
        arrival_time_ahead="",
        duration=f"Outbound: {outbound.duration}, Return: {return_flight.duration}",
        stops=outbound.stops + return_flight.stops,
        delay=outbound.delay or return_flight.delay,
        price=combined_price,
        flight_codes=(outbound.flight_codes or []) + (return_flight.flight_codes or []),
        # Outbound details
        outbound_name=outbound.name,
        outbound_departure=outbound.departure,
        outbound_arrival=outbound.arrival,
        outbound_duration=outbound.duration,
        outbound_stops=outbound.stops,
        outbound_price=outbound.price,
        # Return details
        return_name=return_flight.name,
        return_departure=return_flight.departure,
        return_arrival=return_flight.arrival,
        return_duration=return_flight.duration,
        return_stops=return_flight.stops,
        return_price=return_flight.price,
    )


# ============================================================================
# Main Search Function - High-level interface
# ============================================================================

def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: Optional[PassengerConfig] = None,
    seat_class: Literal["economy", "premium-economy", "business", "first"] = "economy",
    max_stops: Optional[int] = None,
) -> str:
    """Search for flights and return the Google Flights URL.
    
    This is the main entry point for searching flights. It generates
    the properly formatted URL for Google Flights.
    
    Args:
        origin: Origin airport code (e.g., "JFK")
        destination: Destination airport code (e.g., "LAX")
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round-trip (optional)
        passengers: Passenger configuration (default: 1 adult)
        seat_class: Seat class preference
        max_stops: Maximum number of stops (optional)
        
    Returns:
        Google Flights URL for the search
        
    Example:
        >>> url = search_flights("JFK", "LAX", "2025-07-01", "2025-07-10")
        >>> print(url)
        https://www.google.com/travel/flights?tfs=...
    """
    # Set defaults
    if passengers is None:
        passengers = PassengerConfig(adults=1)
    
    # Build queries
    queries = [FlightQuery(departure_date, origin, destination, max_stops)]
    trip_type = "one-way"
    
    if return_date:
        queries.append(FlightQuery(return_date, destination, origin, max_stops))
        trip_type = "round-trip"
    
    # Create filter
    tfs = create_search_filter(queries, trip_type, passengers, seat_class)
    
    # Build URL
    url = f"https://www.google.com/travel/flights?tfs={tfs}&hl=en"
    
    return url


# ============================================================================
# Helper Functions
# ============================================================================

def format_flight_for_display(flight: Flight) -> Dict[str, Any]:
    """Convert Flight object to a readable dictionary.
    
    Args:
        flight: Flight object to format
        
    Returns:
        Dictionary with formatted flight information
    """
    result = {
        "airline": flight.name,
        "departure": flight.departure,
        "arrival": flight.arrival,
        "duration": flight.duration,
        "stops": flight.stops,
        "price": flight.price,
        "is_best": flight.is_best,
    }
    
    # Add round-trip details if present
    if flight.outbound_name:
        result["outbound"] = {
            "airline": flight.outbound_name,
            "departure": flight.outbound_departure,
            "arrival": flight.outbound_arrival,
            "duration": flight.outbound_duration,
            "stops": flight.outbound_stops,
            "price": flight.outbound_price,
        }
    
    if flight.return_name:
        result["return"] = {
            "airline": flight.return_name,
            "departure": flight.return_departure,
            "arrival": flight.return_arrival,
            "duration": flight.return_duration,
            "stops": flight.return_stops,
            "price": flight.return_price,
        }
    
    return result


if __name__ == "__main__":
    # Example usage
    print("Minimal Google Flights Scraper")
    print("=" * 50)
    
    # One-way flight example
    url = search_flights(
        origin="JFK",
        destination="LAX",
        departure_date="2025-07-01",
        passengers=PassengerConfig(adults=1),
        seat_class="economy"
    )
    print(f"\nOne-way flight URL:\n{url}")
    
    # Round-trip flight example
    url = search_flights(
        origin="JFK",
        destination="LAX",
        departure_date="2025-07-01",
        return_date="2025-07-10",
        passengers=PassengerConfig(adults=2, children=1),
        seat_class="economy"
    )
    print(f"\nRound-trip flight URL:\n{url}")
