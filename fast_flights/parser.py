"""Enhanced HTML parser for extracting flight information."""

import re
from typing import Dict, List, Optional, Any
from selectolax.lexbor import LexborHTMLParser, LexborNode


class FlightHTMLParser:
    """Parser for Google Flights HTML response."""
    
    def __init__(self, html_content: str):
        self.parser = LexborHTMLParser(html_content)
        self.html_content = html_content
    
    def _safe_node(self, node: Optional[LexborNode]) -> LexborNode:
        """Return node or blank node if None."""
        class _blank:
            def text(self, *_, **__):
                return ""
            def iter(self):
                return []
        
        return node or _blank()
    
    def extract_flight_data(
        self,
        dangerously_allow_looping_last_item: bool = False
    ) -> List[Dict[str, Any]]:
        """Extract flight data from HTML.
        
        Args:
            dangerously_allow_looping_last_item: Whether to include last item in non-best flights
            
        Returns:
            List of flight dictionaries with extracted data
        """
        flights = []
        
        for i, fl in enumerate(self.parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
            is_best_flight = i == 0
            
            for item in fl.css("ul.Rk10dc li")[
                : (None if dangerously_allow_looping_last_item or i == 0 else -1)
            ]:
                flight_data = self._extract_single_flight(item, is_best_flight)
                if flight_data:
                    flights.append(flight_data)
        
        return flights
    
    def _extract_single_flight(
        self,
        item: LexborNode,
        is_best: bool
    ) -> Optional[Dict[str, Any]]:
        """Extract data from a single flight element.
        
        Args:
            item: HTML node containing flight information
            is_best: Whether this is from the best flights section
            
        Returns:
            Dictionary with flight data or None if extraction failed
        """
        # Flight name
        name = self._safe_node(item.css_first("div.sSHqwe.tPgKwe.ogfYpf span")).text(strip=True)
        
        # Get departure & arrival time
        dp_ar_node = item.css("span.mv1WYe div")
        try:
            departure_time = dp_ar_node[0].text(strip=True)
            arrival_time = dp_ar_node[1].text(strip=True)
        except IndexError:
            departure_time = ""
            arrival_time = ""
        
        # Get arrival time ahead
        time_ahead = self._safe_node(item.css_first("span.bOzv6")).text()
        
        # Get duration
        duration = self._safe_node(item.css_first("li div.Ak5kof div")).text()
        
        # Get flight stops
        stops = self._safe_node(item.css_first(".BbR8Ec .ogfYpf")).text()
        
        # Get delay
        delay = self._safe_node(item.css_first(".GsCCve")).text() or None
        
        # Get prices
        price = self._safe_node(item.css_first(".YMlIz.FpEdX")).text() or "0"
        
        # Extract flight codes (airline + flight number)
        flight_codes = self._extract_flight_codes_from_element(item)
        
        # Stops formatting
        try:
            stops_fmt = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])
        except ValueError:
            stops_fmt = "Unknown"
        
        return {
            "is_best": is_best,
            "name": name,
            "departure": " ".join(departure_time.split()),
            "arrival": " ".join(arrival_time.split()),
            "arrival_time_ahead": time_ahead,
            "duration": duration,
            "stops": stops_fmt,
            "delay": delay,
            "price": price.replace(",", ""),
            "flight_codes": flight_codes,
        }
    
    def _extract_flight_codes_from_element(self, element: LexborNode) -> List[str]:
        """Extract flight codes from a flight element.
        
        Args:
            element: HTML node containing flight information
            
        Returns:
            List of flight codes (e.g., ["UA123", "DL456"])
        """
        codes = []
        
        # Look for flight numbers in various possible locations
        for span in element.css("span.h1fkLb, span.sSHqwe, div.Ir0Voe"):
            text = span.text(strip=True)
            # Match patterns like "UA 123" or "UA123"
            match = re.match(r'^([A-Z]{2})\s*(\d+)$', text)
            if match:
                airline, number = match.groups()
                codes.append(f"{airline}{number}")
        
        return codes
    
    def get_current_price(self) -> str:
        """Extract current price indicator.
        
        Returns:
            Price indicator string ("low", "typical", "high", or empty)
        """
        current_price = self._safe_node(self.parser.css_first("span.gOatQ")).text()
        return current_price
