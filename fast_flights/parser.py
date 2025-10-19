"""Parser for extracting flight information from HTML content."""

from typing import Any, Dict, List, Union
from selectolax.lexbor import LexborHTMLParser, LexborNode

from .utils import extract_airline_code_and_flight_number


def parse_flight_results(html_content: str) -> Dict[str, Any]:
    """Parse flight results from HTML content.
    
    Args:
        html_content: HTML string to parse
        
    Returns:
        Dictionary containing current_price and list of flights
    """
    class _blank:
        """Helper class for safe node access."""
        def text(self, *_, **__):
            return ""
        
        def iter(self):
            return []
    
    blank = _blank()
    
    def safe(n: Union[LexborNode, None]) -> Union[LexborNode, _blank]:
        """Safely return node or blank object."""
        return n or blank
    
    parser = LexborHTMLParser(html_content)
    flights = []
    
    # Parse flights from the HTML structure
    for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best_flight = i == 0
        
        for item in fl.css("ul.Rk10dc li"):
            # Flight name
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf span")).text(strip=True)
            
            # Get departure & arrival time
            dp_ar_node = item.css("span.mv1WYe div")
            try:
                departure_time = dp_ar_node[0].text(strip=True)
                arrival_time = dp_ar_node[1].text(strip=True)
            except IndexError:
                departure_time = ""
                arrival_time = ""
            
            # Get arrival time ahead
            time_ahead = safe(item.css_first("span.bOzv6")).text()
            
            # Get duration
            duration = safe(item.css_first("li div.Ak5kof div")).text()
            
            # Get flight stops
            stops_text = safe(item.css_first(".BbR8Ec .ogfYpf")).text()
            
            # Get delay
            delay = safe(item.css_first(".GsCCve")).text() or None
            
            # Get prices
            price = safe(item.css_first(".YMlIz.FpEdX")).text() or "0"
            
            # Stops formatting
            try:
                if stops_text == "Nonstop":
                    stops = 0
                else:
                    stops = int(stops_text.split(" ", 1)[0])
            except (ValueError, AttributeError):
                stops = "Unknown"
            
            # Extract flight codes from travelimpactmodel URL
            flight_codes = []
            impact_model_elem = item.css_first(".NZRfve[data-travelimpactmodelwebsiteurl]")
            if impact_model_elem:
                url = impact_model_elem.attributes.get('data-travelimpactmodelwebsiteurl', '')
                if url:
                    flight_codes = extract_airline_code_and_flight_number(url)
            
            flights.append({
                "is_best": is_best_flight,
                "name": name,
                "departure": " ".join(departure_time.split()),
                "arrival": " ".join(arrival_time.split()),
                "arrival_time_ahead": time_ahead,
                "duration": duration,
                "stops": stops,
                "delay": delay,
                "price": price.replace(",", ""),
                "flight_codes": flight_codes,
            })
    
    # Get current price indicator
    current_price = safe(parser.css_first("span.gOatQ")).text()
    
    return {
        "current_price": current_price,
        "flights": flights
    }
