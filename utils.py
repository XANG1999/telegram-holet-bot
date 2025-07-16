import gspread
from oauth2client.service_account import ServiceAccountCredentials
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import os
import json

# Google Sheets initialization
def init_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("TelegramHotelBotTracking").sheet1
    return sheet

# Track user interaction
def log_user_interaction(user, action, message=""):
    sheet = init_gsheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([
        now,
        user.id,
        user.username or "",
        user.first_name or "",
        action,
        message
    ])

# Haversine distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return round(6371 * c, 2)

# Placeholder hotel fetcher for now
def fetch_hotels_from_api(lat, lon, radius_km=10, max_results=5):
    hotels = [
        {
            "name": "Budget Stay Goa",
            "price": 799,
            "location": "Near Baga Beach",
            "latitude": lat + 0.01,
            "longitude": lon + 0.01,
            "link": "https://your-affiliate-link"
        },
        {
            "name": "Economy Inn",
            "price": 950,
            "location": "Near Calangute",
            "latitude": lat + 0.02,
            "longitude": lon + 0.02,
            "link": "https://your-affiliate-link"
        },
    ]
    results = []
    for hotel in hotels:
        distance = calculate_distance(lat, lon, hotel["latitude"], hotel["longitude"])
        results.append({
            "name": hotel["name"],
            "price": hotel["price"],
            "location": hotel["location"],
            "distance": distance,
            "link": hotel["link"]
        })
    results.sort(key=lambda x: x["price"])
    return results[:max_results]