
# ============================================
# PROJECT 3: EXTERNAL API CLIENT
# Fetches real data from public APIs (Pure Python)
# ============================================

from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import threading
import time


# ============================================
# EXTERNAL API FUNCTIONS (No extra packages!)
# ============================================

def fetch_weather(city="London"):
    """Fetch weather data from free public API"""
    try:
        # Free weather API (no API key needed)
        url = f"https://wttr.in/{city}?format=j1"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            current = data.get("current_condition", [{}])[0]
            return {
                "city": city,
                "temperature": current.get("temp_C", "N/A"),
                "humidity": current.get("humidity", "N/A"),
                "weather": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
                "source": "wttr.in"
            }
    except Exception as e:
        return {"error": f"Could not fetch weather: {str(e)}", "city": city}


def fetch_facts():
    """Fetch random facts from free public API"""
    try:
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            return {
                "fact": data.get("text", "No fact found"),
                "source": "uselessfacts.jsph.pl"
            }
    except Exception as e:
        return {"error": f"Could not fetch fact: {str(e)}"}


def fetch_quote():
    """Fetch random quote from free public API"""
    try:
        url = "https://api.quotable.io/random"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            return {
                "quote": data.get("content", "No quote found"),
                "author": data.get("author", "Unknown"),
                "source": "quotable.io"
            }
    except Exception as e:
        return {"error": f"Could not fetch quote: {str(e)}"}


def fetch_exchange_rate(base="USD", target="EUR"):
    """Fetch exchange rate from free public API"""
    try:
        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            rate = data.get("rates", {}).get(target, "N/A")
            return {
                "base": base,
                "target": target,
                "rate": rate,
                "date": data.get("date", "N/A"),
                "source": "frankfurter.app"
            }
    except Exception as e:
        return {"error": f"Could not fetch exchange rate: {str(e)}"}


# ============================================
# API SERVER
# ============================================

class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_GET(self):
        # Root endpoint
        if self.path == '/':
            self.send_json({
                "message": "Project 3: External API Client is running",
                "project": "Project 3 of 5",
                "description": "Fetches real data from public APIs",
                "endpoints": [
                    "GET /",
                    "GET /health",
                    "GET /weather?city=London",
                    "GET /fact",
                    "GET /quote",
                    "GET /exchange?base=USD&target=EUR"
                ]
            })

        # Health check
        elif self.path == '/health':
            self.send_json({
                "status": "healthy",
                "timestamp": str(datetime.now()),
                "project": "External API Client"
            })

        # Weather endpoint
        elif self.path.startswith('/weather'):
            # Parse city from query string
            city = "London"
            if '?' in self.path and 'city=' in self.path:
                query = self.path.split('?')[1]
                for param in query.split('&'):
                    if param.startswith('city='):
                        city = param.split('=')[1]
                        break
            result = fetch_weather(city)
            self.send_json(result)

        # Random fact endpoint
        elif self.path == '/fact':
            result = fetch_facts()
            self.send_json(result)

        # Random quote endpoint
        elif self.path == '/quote':
            result = fetch_quote()
            self.send_json(result)

        # Exchange rate endpoint
        elif self.path.startswith('/exchange'):
            base = "USD"
            target = "EUR"
            if '?' in self.path:
                query = self.path.split('?')[1]
                for param in query.split('&'):
                    if param.startswith('base='):
                        base = param.split('=')[1].upper()
                    if param.startswith('target='):
                        target = param.split('=')[1].upper()
            result = fetch_exchange_rate(base, target)
            self.send_json(result)

        # 404
        else:
            self.send_json({"error": "Endpoint not found"}, 404)

    def log_message(self, format, *args):
        pass


# ============================================
# RUN THE SERVER
# ============================================

def run_server():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)

    print("=" * 60)
    print("✅ PROJECT 3: EXTERNAL API CLIENT IS RUNNING!")
    print("=" * 60)
    print()
    print(f"🌐 Server: http://localhost:{port}")
    print()
    print("📋 Available endpoints:")
    print("   GET  /                           - API information")
    print("   GET  /health                     - Health check")
    print("   GET  /weather?city=London        - Get weather for any city")
    print("   GET  /fact                       - Get random fact")
    print("   GET  /quote                      - Get random quote")
    print("   GET  /exchange?base=USD&target=EUR - Get exchange rate")
    print()
    print("🌍 This API fetches REAL data from external public APIs!")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    httpd.serve_forever()


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print()
    print("🧪 Testing external APIs...")
    print("-" * 40)

    # Test weather
    print("Testing weather API...")
    weather = fetch_weather("Berlin")
    if "error" not in weather:
        print(f"   ✅ Weather: {weather['temperature']}°C, {weather['weather']}")
    else:
        print(f"   ⚠️  Weather: {weather['error']}")

    # Test fact
    print("Testing facts API...")
    fact = fetch_facts()
    if "error" not in fact:
        print(f"   ✅ Fact: {fact['fact'][:50]}...")
    else:
        print(f"   ⚠️  Fact: {fact['error']}")

    # Test quote
    print("Testing quotes API...")
    quote = fetch_quote()
    if "error" not in quote:
        print(f"   ✅ Quote: '{quote['quote'][:50]}...' - {quote['author']}")
    else:
        print(f"   ⚠️  Quote: {quote['error']}")

    print("-" * 40)
    print()

    run_server()