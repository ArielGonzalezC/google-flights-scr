# Frequently Asked Questions (FAQ)

## General Questions

### What is this project?

This is a minimalist Google Flights scraper that generates valid Google Flights URLs and can parse flight results. It uses Protocol Buffers (the same format Google uses internally) to encode search parameters.

### Is this legal?

Web scraping is a gray area. This tool generates URLs and parses publicly available HTML. Always:
- Respect Google's Terms of Service
- Implement rate limiting
- Don't overload their servers
- Check your local laws regarding web scraping

### Does this work with all airports?

Yes! It works with any valid IATA airport code (3-letter codes like "JFK", "LAX", "LHR", etc.).

## Technical Questions

### Why two implementations (minimal and full)?

- **Minimal (`minimal_flights.py`)**: Simple, educational, easy to understand and modify
- **Full (`fast_flights/`)**: More features, more robust, better for production use

Use minimal if you want to learn or customize. Use full if you need advanced features.

### What are the dependencies?

Only 3 core dependencies:
- `protobuf` - For encoding search parameters
- `selectolax` - Fast HTML parsing
- `primp` - HTTP client (optional, for making requests)

### How does the protobuf encoding work?

Google Flights uses Protocol Buffers to encode search parameters in the `?tfs=` URL parameter. We:
1. Define the protobuf schema (see `fast_flights/flights.proto`)
2. Create a protobuf message with search parameters
3. Serialize and base64-encode it
4. Add it to the URL

### Can I make actual HTTP requests with this?

The minimal implementation focuses on URL generation and HTML parsing. To make requests:

```python
import requests
from minimal_flights import search_flights, PassengerConfig

url = search_flights("JFK", "LAX", "2025-07-01")
response = requests.get(url)
# Then parse response.text with parse_flights_from_html()
```

**Important**: Add delays between requests to avoid being blocked!

## Usage Questions

### How do I search for round-trip flights?

Simply provide a `return_date`:

```python
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    return_date="2025-07-10"  # Add this for round-trip
)
```

### How do I search for flights with multiple passengers?

Use `PassengerConfig`:

```python
from minimal_flights import PassengerConfig

passengers = PassengerConfig(
    adults=2,
    children=1,
    infants_in_seat=0,
    infants_on_lap=0
)

url = search_flights("JFK", "LAX", "2025-07-01", passengers=passengers)
```

### How do I limit the number of stops?

Use the `max_stops` parameter:

```python
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    max_stops=0  # Non-stop flights only (0, 1, or 2)
)
```

### What seat classes are available?

Four options:
- `"economy"` - Standard economy
- `"premium-economy"` - Premium economy
- `"business"` - Business class
- `"first"` - First class

```python
url = search_flights(..., seat_class="business")
```

### Can I search for multi-city flights?

The minimal implementation focuses on one-way and round-trip. For multi-city:

1. Use the full implementation (`fast_flights/`)
2. Or create multiple queries manually:

```python
from minimal_flights import FlightQuery, create_search_filter, PassengerConfig

queries = [
    FlightQuery("2025-07-01", "JFK", "LAX"),
    FlightQuery("2025-07-05", "LAX", "SFO"),
    FlightQuery("2025-07-10", "SFO", "JFK"),
]

tfs = create_search_filter(queries, "multi-city", PassengerConfig(adults=1), "economy")
url = f"https://www.google.com/travel/flights?tfs={tfs}&hl=en"
```

### How do I parse flight results?

```python
from minimal_flights import parse_flights_from_html
import requests

# Get HTML (you need to implement this)
url = search_flights("JFK", "LAX", "2025-07-01")
response = requests.get(url)

# Parse results
results = parse_flights_from_html(response.text)

# Access flights
for flight in results.flights:
    print(f"{flight.name}: {flight.price}")
    print(f"  {flight.departure} → {flight.arrival}")
    print(f"  Duration: {flight.duration}, Stops: {flight.stops}")
```

## Troubleshooting

### Import Error: "No module named 'google'"

Install protobuf:
```bash
pip install protobuf
```

### Import Error: "cannot import name 'flights_pb2'"

Make sure you have the `fast_flights/` directory with `flights_pb2.py`.

### ValueError: "Too many passengers"

Google Flights limits total passengers to 9. Reduce your passenger count.

### ValueError: "Each infant on lap requires an adult"

You can't have more infants on lap than adults. Adjust your passenger configuration.

### RuntimeError: "No flights found in HTML content"

The HTML structure might have changed, or:
- You're getting blocked (add delays between requests)
- The page didn't load completely
- Google's HTML structure changed (parser needs updating)

### The generated URL doesn't work in my browser

Check:
1. Dates are in YYYY-MM-DD format
2. Airport codes are valid 3-letter IATA codes
3. Departure date is in the future
4. Return date is after departure date (for round-trip)

## Examples

### Complete workflow example

```python
from minimal_flights import search_flights, PassengerConfig
import requests
import time

# 1. Generate URL
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    return_date="2025-07-10",
    passengers=PassengerConfig(adults=2),
    seat_class="economy"
)

print(f"Search URL: {url}")

# 2. Make request (with delay for politeness)
time.sleep(2)  # Be nice to Google's servers
response = requests.get(url)

# 3. Parse results
if response.status_code == 200:
    results = parse_flights_from_html(response.text)
    
    print(f"\nPrice indicator: {results.current_price}")
    print(f"Found {len(results.flights)} flights\n")
    
    # Show first 5 flights
    for i, flight in enumerate(results.flights[:5], 1):
        print(f"{i}. {flight.name} - {flight.price}")
        print(f"   {flight.departure} → {flight.arrival}")
        print(f"   {flight.duration}, {flight.stops} stop(s)")
        if flight.is_best:
            print("   ⭐ Best flight")
        print()
else:
    print(f"Error: {response.status_code}")
```

## Contributing

### How can I contribute?

1. Report bugs via GitHub Issues
2. Suggest improvements
3. Submit pull requests
4. Improve documentation
5. Share your use cases

### I found a bug. What should I do?

1. Check if it's already reported in Issues
2. Create a new issue with:
   - Clear description
   - Code to reproduce
   - Expected vs actual behavior
   - Error messages (if any)

### Can I use this in my project?

Yes! This is MIT licensed. You can:
- Use it commercially
- Modify it
- Distribute it
- Use it privately

Just keep the license notice.

## Advanced Topics

### How can I customize the parser?

Edit the `parse_flights_from_html()` function in `minimal_flights.py`. The parser uses CSS selectors to extract data from Google Flights HTML.

### Can I add support for airline preferences?

Yes! See the `FlightData` class in `fast_flights/flights_impl.py` for the airlines parameter. You'd need to extend the protobuf schema and minimal implementation.

### How do I debug protobuf encoding?

Decode the base64 string:

```python
import base64
from minimal_flights import search_flights

url = search_flights("JFK", "LAX", "2025-07-01")
tfs = url.split("tfs=")[1].split("&")[0]
decoded = base64.b64decode(tfs)
print(decoded)  # Raw protobuf bytes
```

Use an online protobuf decoder like [protobuf-decoder.netlify.app](https://protobuf-decoder.netlify.app) to inspect the structure.

## More Help

Still have questions? 

1. Check the examples: `example.py`, `example_roundtrip.py`
2. Read the code - it's well commented!
3. Look at `STRUCTURE.md` for project organization
4. Open an issue on GitHub

---

**Last updated**: October 2025
