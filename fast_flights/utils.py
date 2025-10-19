"""Utility functions for round-trip flight support."""

import re
from typing import List, Tuple, Optional
from selectolax.lexbor import LexborHTMLParser


def extract_flight_codes(html_content: str) -> List[Tuple[str, str]]:
    """Extract airline codes and flight numbers from HTML.
    
    Args:
        html_content: Raw HTML response from Google Flights
        
    Returns:
        List of (airline_code, flight_number) tuples
    """
    flight_codes = []
    parser = LexborHTMLParser(html_content)
    
    # Look for flight information in the HTML
    # Google Flights typically shows flight numbers in format like "UA 123" or "UA123"
    for element in parser.css('span.h1fkLb, span.sSHqwe, div.Ir0Voe'):
        text = element.text(strip=True)
        # Match patterns like "UA 123", "UA123", "United 123", etc.
        match = re.match(r'^([A-Z]{2})\s*(\d+)$', text)
        if match:
            airline_code, flight_number = match.groups()
            flight_codes.append((airline_code, flight_number))
    
    return flight_codes


def extract_airlines_from_flight_names(flight_names: List[str]) -> List[str]:
    """Extract airline codes from flight names.
    
    Args:
        flight_names: List of flight names like "United · Delta" or "Emirates"
        
    Returns:
        List of unique airline codes (2-letter IATA codes)
    """
    airlines = set()
    
    # Mapping of common airline names to IATA codes
    airline_map = {
        'united': 'UA',
        'delta': 'DL',
        'american': 'AA',
        'southwest': 'WN',
        'jetblue': 'B6',
        'alaska': 'AS',
        'spirit': 'NK',
        'frontier': 'F9',
        'hawaiian': 'HA',
        'emirates': 'EK',
        'lufthansa': 'LH',
        'british airways': 'BA',
        'air france': 'AF',
        'klm': 'KL',
        'singapore airlines': 'SQ',
        'qantas': 'QF',
        'cathay pacific': 'CX',
        'ana': 'NH',
        'jal': 'JL',
    }
    
    for name in flight_names:
        # Split by common separators
        parts = re.split(r'[·•,\+]', name)
        for part in parts:
            part = part.strip().lower()
            if part in airline_map:
                airlines.add(airline_map[part])
            # Check if it's already a 2-letter code
            elif len(part) == 2 and part.isupper():
                airlines.add(part)
    
    return list(airlines)


def create_return_flight_tfs(
    outbound_tfs: bytes,
    airline_codes: Optional[List[str]] = None
) -> bytes:
    """Create TFS data for return flight search based on outbound flight.
    
    This is a simplified version that modifies the TFS to request return flights.
    In practice, Google Flights handles round-trip differently in their UI.
    
    Args:
        outbound_tfs: Original TFS bytes for outbound flight
        airline_codes: Optional list of airline codes to filter by
        
    Returns:
        Modified TFS bytes for return flight
    """
    # For now, we'll return the original TFS as Google Flights
    # should return both outbound and return in a single request
    # for round-trip searches
    return outbound_tfs
