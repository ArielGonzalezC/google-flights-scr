import re
import json
from dataclasses import asdict
from typing import List, Literal, Optional, Union, overload

from selectolax.lexbor import LexborHTMLParser, LexborNode

from .decoder import DecodedResult, ResultDecoder
from .schema import Flight, Result
from .flights_impl import FlightData, Passengers
from .filter import TFSData
from .fallback_playwright import fallback_playwright_fetch
from .bright_data_fetch import bright_data_fetch
from .primp import Client, Response
from .utils import create_tfs_for_return_flight
from .parser import parse_flight_results


DataSource = Literal['html', 'js']

def fetch(params: dict) -> Response:
    client = Client(impersonate="chrome_126", verify=False)
    res = client.get("https://www.google.com/travel/flights", params=params)
    assert res.status_code == 200, f"{res.status_code} Result: {res.text_markdown}"
    return res

@overload
def get_flights_from_filter(
    filter: TFSData,
    currency: str = "",
    *,
    mode: Literal["common", "fallback", "force-fallback", "local", "bright-data"] = "common",
    data_source: Literal['js'] = ...,
) -> Union[DecodedResult, None]: ...

@overload
def get_flights_from_filter(
    filter: TFSData,
    currency: str = "",
    *,
    mode: Literal["common", "fallback", "force-fallback", "local", "bright-data"] = "common",
    data_source: Literal['html'],
) -> Result: ...

def get_flights_from_filter(
    filter: TFSData,
    currency: str = "",
    *,
    mode: Literal["common", "fallback", "force-fallback", "local", "bright-data"] = "common",
    data_source: DataSource = 'html',
) -> Union[Result, DecodedResult, None]:
    data = filter.as_b64()

    params = {
        "tfs": data.decode("utf-8"),
        "hl": "en",
        "tfu": "EgQIABABIgA",
        "curr": currency,
    }

    if mode in {"common", "fallback"}:
        try:
            res = fetch(params)
        except AssertionError as e:
            if mode == "fallback":
                res = fallback_playwright_fetch(params)
            else:
                raise e

    elif mode == "local":
        from .local_playwright import local_playwright_fetch

        res = local_playwright_fetch(params)

    elif mode == "bright-data":
        res = bright_data_fetch(params)

    else:
        res = fallback_playwright_fetch(params)

    try:
        return parse_response(res, data_source)
    except RuntimeError as e:
        if mode == "fallback":
            return get_flights_from_filter(filter, mode="force-fallback")
        raise e


def get_flights(
    *,
    flight_data: List[FlightData],
    trip: Literal["round-trip", "one-way", "multi-city"],
    passengers: Passengers,
    seat: Literal["economy", "premium-economy", "business", "first"],
    fetch_mode: Literal["common", "fallback", "force-fallback", "local", "bright-data"] = "common",
    max_stops: Optional[int] = None,
    data_source: DataSource = 'html',
) -> Union[Result, DecodedResult, None]:
    # For non-html data sources or non-round-trip, use the existing logic
    if data_source != 'html' or trip != 'round-trip':
        return get_flights_from_filter(
            TFSData.from_interface(
                flight_data=flight_data,
                trip=trip,
                passengers=passengers,
                seat=seat,
                max_stops=max_stops,
            ),
            mode=fetch_mode,
            data_source=data_source,
        )
    
    # Validate inputs for round-trip
    if trip == 'round-trip' and len(flight_data) != 2:
        raise ValueError("Round-trip requires exactly 2 FlightData entries (outbound and return)")
    
    # Get outbound flights first
    outbound_result = get_flights_from_filter(
        TFSData.from_interface(
            flight_data=flight_data,
            trip=trip,
            passengers=passengers,
            seat=seat,
            max_stops=max_stops,
        ),
        mode=fetch_mode,
        data_source=data_source,
    )
    
    # If not round-trip or failed to get outbound, return as-is
    if trip != 'round-trip' or not outbound_result or not hasattr(outbound_result, 'flights'):
        return outbound_result
    
    # Try to fetch and pair return flights
    try:
        # Prepare passenger types list
        passenger_types = []
        for p_type in passengers.pb:
            if p_type == 1:
                passenger_types.append('adult')
            elif p_type == 2:
                passenger_types.append('child')
            elif p_type == 3:
                passenger_types.append('infant_in_seat')
            elif p_type == 4:
                passenger_types.append('infant_on_lap')
        
        # Get return flight data
        return_flight_data = flight_data[1]
        from_airport = return_flight_data.from_airport
        to_airport = return_flight_data.to_airport
        return_date = return_flight_data.date
        
        # Try to get return flights for each outbound flight that has flight_codes
        paired_flights = []
        
        for outbound_flight in outbound_result.flights:
            # Check if outbound flight has flight_codes
            if not hasattr(outbound_flight, 'flight_codes') or not outbound_flight.flight_codes:
                continue
            
            try:
                # Create outbound flight dict
                outbound_dict = asdict(outbound_flight)
                outbound_dict['departure_date'] = flight_data[0].date
                outbound_dict['from_airport'] = flight_data[0].from_airport
                outbound_dict['to_airport'] = flight_data[0].to_airport
                
                # Create TFS for return flight
                tfs = create_tfs_for_return_flight(
                    outbound_flight=outbound_dict,
                    from_airport=from_airport,
                    to_airport=to_airport,
                    return_date=return_date,
                    seat_type=seat,
                    passenger_types=passenger_types
                )
                
                # Fetch return flights
                return_url = f"https://www.google.com/travel/flights/search?tfs={tfs}&hl=en&curr=USD"
                params = {'tfs': tfs, 'hl': 'en', 'curr': 'USD'}
                
                if fetch_mode in {"common", "fallback"}:
                    try:
                        res = fetch(params)
                    except AssertionError as e:
                        if fetch_mode == "fallback":
                            res = fallback_playwright_fetch(params)
                        else:
                            raise e
                elif fetch_mode == "local":
                    from .local_playwright import local_playwright_fetch
                    res = local_playwright_fetch(params)
                elif fetch_mode == "bright-data":
                    res = bright_data_fetch(params)
                else:
                    res = fallback_playwright_fetch(params)
                
                # Parse return flights
                return_parsed = parse_flight_results(res.text)
                
                # Create Flight objects for return flights and pair them
                for return_flight_data in return_parsed.get('flights', []):
                    return_flight = Flight(
                        is_best=return_flight_data.get('is_best', False),
                        name=return_flight_data.get('name', ''),
                        departure=return_flight_data.get('departure', ''),
                        arrival=return_flight_data.get('arrival', ''),
                        arrival_time_ahead=return_flight_data.get('arrival_time_ahead', ''),
                        duration=return_flight_data.get('duration', ''),
                        stops=return_flight_data.get('stops', 0),
                        delay=return_flight_data.get('delay'),
                        price=return_flight_data.get('price', '0'),
                        flight_codes=return_flight_data.get('flight_codes', []),
                        departure_date=return_date
                    )
                    
                    # Create paired round-trip flight
                    paired_flight = create_round_trip_flight(outbound_flight, return_flight)
                    paired_flights.append(paired_flight)
                
            except Exception as e:
                # If fetching return flights fails for this outbound, continue
                print(f"Warning: Failed to fetch return flights for {outbound_flight.name}: {e}")
                continue
        
        # If we got paired flights, return them instead
        if paired_flights:
            return Result(
                current_price=outbound_result.current_price,
                flights=paired_flights
            )
    
    except Exception as e:
        print(f"Warning: Round-trip pairing failed, returning outbound only: {e}")
    
    # Fall back to outbound flights only
    return outbound_result


def create_round_trip_flight(outbound: Flight, return_flight: Flight) -> Flight:
    """Create a combined round-trip flight from outbound and return flights.
    
    Args:
        outbound: Outbound flight
        return_flight: Return flight
        
    Returns:
        Flight object with combined information
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
        duration=f"{outbound.duration} / {return_flight.duration}",
        stops=outbound.stops + return_flight.stops if isinstance(outbound.stops, int) and isinstance(return_flight.stops, int) else 0,
        delay=outbound.delay or return_flight.delay,
        price=combined_price,
        flight_codes=getattr(outbound, 'flight_codes', []) + getattr(return_flight, 'flight_codes', []),
        departure_date=getattr(outbound, 'departure_date', None),
        # Outbound info
        outbound_name=outbound.name,
        outbound_departure=outbound.departure,
        outbound_arrival=outbound.arrival,
        outbound_arrival_time_ahead=outbound.arrival_time_ahead,
        outbound_duration=outbound.duration,
        outbound_stops=outbound.stops,
        outbound_delay=outbound.delay,
        outbound_price=outbound.price,
        # Return info
        return_name=return_flight.name,
        return_departure=return_flight.departure,
        return_arrival=return_flight.arrival,
        return_arrival_time_ahead=return_flight.arrival_time_ahead,
        return_duration=return_flight.duration,
        return_stops=return_flight.stops,
        return_delay=return_flight.delay,
        return_price=return_flight.price,
    )


def parse_response(
    r: Response,
    data_source: DataSource,
    *,
    dangerously_allow_looping_last_item: bool = False,
) -> Union[Result, DecodedResult, None]:
    class _blank:
        def text(self, *_, **__):
            return ""

        def iter(self):
            return []

    blank = _blank()

    def safe(n: Optional[LexborNode]):
        return n or blank

    parser = LexborHTMLParser(r.text)

    if data_source == 'js':
        script = parser.css_first(r'script.ds\:1').text()

        match = re.search(r'^.*?\{.*?data:(\[.*\]).*\}', script)
        assert match, 'Malformed js data, cannot find script data'
        data = json.loads(match.group(1))
        return ResultDecoder.decode(data) if data is not None else None

    flights = []

    for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
        is_best_flight = i == 0

        for item in fl.css("ul.Rk10dc li")[
            : (None if dangerously_allow_looping_last_item or i == 0 else -1)
        ]:
            # Flight name
            name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf span")).text(
                strip=True
            )

            # Get departure & arrival time
            dp_ar_node = item.css("span.mv1WYe div")
            try:
                departure_time = dp_ar_node[0].text(strip=True)
                arrival_time = dp_ar_node[1].text(strip=True)
            except IndexError:
                # sometimes this is not present
                departure_time = ""
                arrival_time = ""

            # Get arrival time ahead
            time_ahead = safe(item.css_first("span.bOzv6")).text()

            # Get duration
            duration = safe(item.css_first("li div.Ak5kof div")).text()

            # Get flight stops
            stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()

            # Get delay
            delay = safe(item.css_first(".GsCCve")).text() or None

            # Get prices
            price = safe(item.css_first(".YMlIz.FpEdX")).text() or "0"

            # Stops formatting
            try:
                stops_fmt = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])
            except ValueError:
                stops_fmt = "Unknown"

            # Extract flight codes from travelimpactmodel URL
            flight_codes = []
            impact_model_elem = item.css_first(".NZRfve[data-travelimpactmodelwebsiteurl]")
            if impact_model_elem:
                url = impact_model_elem.attributes.get('data-travelimpactmodelwebsiteurl', '')
                if url:
                    from .utils import extract_airline_code_and_flight_number
                    flight_codes = extract_airline_code_and_flight_number(url)

            flights.append(
                {
                    "is_best": is_best_flight,
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
            )

    current_price = safe(parser.css_first("span.gOatQ")).text()
    if not flights:
        raise RuntimeError("No flights found:\n{}".format(r.text_markdown))

    return Result(current_price=current_price, flights=[Flight(**fl) for fl in flights])  # type: ignore
