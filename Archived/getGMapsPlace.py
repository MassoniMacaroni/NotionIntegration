# This was separated just for testing but is no longer in use as I have not updated recently.
import os
import re
from dotenv import load_dotenv
import requests


# Load environment variables from .env file
load_dotenv()

# Access API keys
notion_api_key = os.getenv('NOTION_API_KEY')
gmaps_api_key = os.getenv('GMAPS_API_KEY')

# Prompt the user for a Google Maps URL
google_maps_url = "https://www.google.com/maps/place/Mama+Eat/@40.8366911,14.2131827,15z/data=!4m6!3m5!1s0x133b09205fc705bd:0xb27f043e82c18803!8m2!3d40.8366911!4d14.2131827!16s%2Fg%2F1tqd2_zv?entry=ttu"
#input("Please enter a Google Maps URL: ")

#Endpoint
url = 'https://places.googleapis.com/v1/places:searchText'

# Regular expression patterns to extract the place name, latitude and longitude
name_pattern = re.compile(r"maps/place/([^/@]+)")
lat_long_pattern = re.compile(r"@([0-9.-]+),([0-9.-]+)")

# Extracting the place name
name_match = name_pattern.search(google_maps_url)
place_name = name_match.group(1).replace('+', ' ') if name_match else None

# Extracting the latitude and longitude
lat_long_match = lat_long_pattern.search(google_maps_url)
latitude = float(lat_long_match.group(1)) if lat_long_match else None
longitude = float(lat_long_match.group(2)) if lat_long_match else None

# Preparing the POST request payload
payload = {
    "textQuery": place_name,
    "maxResultCount": 1,
    "locationBias": {
        "circle": {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius": 1.0
        }
    },
}
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': gmaps_api_key,  
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.types,places.primaryType,places.websiteUri,places.nationalPhoneNumber,places.location,places.internationalPhoneNumber,places.nationalPhoneNumber,places.priceLevel,places.regularOpeningHours'
}

# Make the POST request (Uncomment the lines below to actually send the request)
response = requests.post(url, json=payload, headers=headers)


# Check the response status code and parse the response
if response.status_code == 200:
    try:
        response_data = response.json()
        places = response_data.get('places', [])

        # Check if there is at least one place in the response
        if places:
            print(response.json())
            # Extract formattedAddress and displayName from the first place
            formatted_address = places[0].get('formattedAddress')
            display_name = places[0]['displayName'].get('text')
            primary_type = places[0].get('primaryType')
            regularOpeningHours = places[0].get('regularOpeningHours')

            # Output the extracted information
            print("Formatted Address:", formatted_address)
            print("Display Name:", display_name)
            print("Primary Type:", primary_type)
            print("Regular Opening Hours:", regularOpeningHours)
        else:
            print("No places found in the response.")

    except requests.exceptions.JSONDecodeError:
        print("JSON Decode Error. Response content:", response.text)
else:
    print("Request failed with status code:", response.status_code)
    print("Response content:", response.text)

# Output for verification
print("Extracted Place Name:", place_name)
print("Extracted Latitude:", latitude)
print("Extracted Longitude:", longitude)
print("Payload for POST Request:", payload)
print("Extracted Address:", formatted_address)


def get_location_details_from_lat_long(latitude, longitude, api_key):
    # Construct the URL for the Geocoding API
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}&language=en"

    # Make the request
    response = requests.get(url)

    if response.status_code == 200:
        results = response.json().get('results', [])
        country = None
        localities = set()

        # Iterate through results to find the country and localities
        for result in results:
            for component in result.get('address_components', []):
                if 'country' in component.get('types', []):
                    country = component.get('long_name')
                if 'locality' in component.get('types', []):
                    localities.add(component.get('long_name'))

        # Check if only one unique locality is found
        if len(localities) == 1:
            return country, list(localities)[0]
        else:
            return country, list(localities)
    else:
        return f"Error: {response.status_code}", "Error in response"


def analyze_opening_hours(data):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    closed_days = []
    suitable_for_day = False
    suitable_for_night = False
    open_24_7 = False

    if data is None or 'open24Hours' in data and data['open24Hours']:
        open_24_7 = True
    else:
        # Check each period for each day
        for day in range(7):  # 0 to 6 for each day of the week
            periods_for_day = [period for period in data.get('periods', []) if period['open']['day'] == day]

            if not periods_for_day:  # If no periods, the day is closed
                closed_days.append(days_of_week[day])
                continue

            for period in periods_for_day:
                open_hour = period['open']['hour']
                close_hour = period.get('close', {}).get('hour', 24)  # Default to 24 if closing time is not specified

                # Check for day and night suitability
                if open_hour < 12:
                    suitable_for_day = True
                if close_hour >= 21 or close_hour == 0:  # Midnight closing is represented as 0
                    suitable_for_night = True

    # Determine time of day suitability
    if open_24_7:
        time_of_day = ["Day", "Night"]
    elif suitable_for_day and suitable_for_night:
        time_of_day = ["Day", "Night"]
    elif suitable_for_day:
        time_of_day = ["Day"]
    elif suitable_for_night:
        time_of_day = ["Night"]
    else:
        time_of_day = []

    return closed_days, time_of_day


def categorize_primary_type(primary_type):
    # Mapping of primary types to categories
    category_mapping = {
        # Automotive
        **{key: "Transport" for key in [
            "car_dealer", "car_rental", "car_repair", "car_wash",
            "electric_vehicle_charging_station", "gas_station", "parking", "rest_stop"
        ]},
        
        # Business
        "farm": "Activity",

        # Culture
        **{key: "Activity" for key in ["art_gallery", "museum", "performing_arts_theater"]},

        # Education
        **{key: "Activity" for key in [
            "library", "preschool", "primary_school", "school", "secondary_school", "university"
        ]},

        # Entertainment and Recreation
        **{key: "Activity" for key in [
            "amusement_center", "amusement_park", "aquarium", "banquet_hall", "bowling_alley",
            "casino", "community_center", "convention_center", "cultural_center", "dog_park",
            "event_venue", "hiking_area", "historical_landmark", "marina", "movie_rental",
            "movie_theater", "national_park", "night_club", "park", "tourist_attraction",
            "visitor_center", "wedding_venue", "zoo"
        ]},

        # Food and Drink
        **{key: "Food" for key in [
            "american_restaurant", "bakery", "bar", "barbecue_restaurant", "brazilian_restaurant",
            "breakfast_restaurant", "brunch_restaurant", "cafe", "chinese_restaurant",
            "coffee_shop", "fast_food_restaurant", "french_restaurant", "greek_restaurant",
            "hamburger_restaurant", "ice_cream_shop", "indian_restaurant", "indonesian_restaurant",
            "italian_restaurant", "japanese_restaurant", "korean_restaurant", "lebanese_restaurant",
            "meal_delivery", "meal_takeaway", "mediterranean_restaurant", "mexican_restaurant",
            "middle_eastern_restaurant", "pizza_restaurant", "ramen_restaurant", "restaurant",
            "sandwich_shop", "seafood_restaurant", "spanish_restaurant", "steak_house",
            "sushi_restaurant", "thai_restaurant", "turkish_restaurant", "vegan_restaurant",
            "vegetarian_restaurant", "supermarket", "vietnamese_restaurant",
            "liquor_store", "grocery_store", "convenience_store"
        ]},

        # Lodging
        **{key: "Accommodation" for key in [
            "bed_and_breakfast", "campground", "camping_cabin", "cottage", "extended_stay_hotel",
            "farmstay", "guest_house", "hostel", "hotel", "lodging", "motel", "private_guest_room",
            "resort_hotel", "rv_park"
        ]},

        # Transportation
        **{key: "Transport" for key in [
            "airport", "bus_station", "bus_stop", "ferry_terminal", "heliport",
            "light_rail_station", "park_and_ride", "subway_station", "taxi_stand",
            "train_station", "transit_depot", "transit_station", "truck_stop"
        ]},

        # Sports
        **{key: "Activity" for key in [
            "athletic_field", "fitness_center", "golf_course", "gym", "playground",
            "ski_resort", "sports_club", "sports_complex", "stadium", "swimming_pool"
        ]},

        # Shopping
        **{key: "Activity" for key in [
            "auto_parts_store", "bicycle_store", "book_store", "cell_phone_store",
            "clothing_store", "department_store", "discount_store",
            "electronics_store", "furniture_store", "gift_shop",
            "hardware_store", "home_goods_store", "home_improvement_store", "jewelry_store", 
            "market", "pet_store", "shoe_store", "shopping_mall",
            "sporting_goods_store", "store", "wholesaler"
        ]},


    }

    # Return the category for the given primary type
    return category_mapping.get(primary_type, "TypeNotFound")

closed_days, time_of_day = analyze_opening_hours(regularOpeningHours)
print("Closed on:", closed_days)
print("Time of Day Suitability:", time_of_day)

print(categorize_primary_type(primary_type))


country, localities = get_location_details_from_lat_long(latitude, longitude, gmaps_api_key)
print(f"Country: {country}, Localities: {localities}")