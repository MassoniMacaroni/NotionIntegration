import requests
import json
import re
import tkinter as tk
from tkinter import messagebox

url_entry = None

# Replace with your actual Notion API key
notion_api_key = 'secret_N6UR0t4kMT7gJTqPKRqDM9OA323eegULmiMBw7ltqBc'
gmaps_api_key = 'AIzaSyDHlT4doSbP1o_gHmaqrbXTr-PkcpBSr34'

# Function to extract details from a Google Maps link
def extract_details_from_google_maps(google_maps_url):
    # ... your existing code for extracting details ...
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
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.id,places.primaryType,places.websiteUri,places.location,places.regularOpeningHours'
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
                websiteUri = places[0].get('websiteUri')

                # Output the extracted information
                print("Formatted Address:", formatted_address)
                print("Display Name:", display_name)
                print("Primary Type:", primary_type)
            else:
                print("No places found in the response.")

        except requests.exceptions.JSONDecodeError:
            print("JSON Decode Error. Response content:", response.text)
    else:
        print("Request failed with status code:", response.status_code)
        print("Response content:", response.text)

    return place_name, latitude, longitude, regularOpeningHours, websiteUri, primary_type

def get_country_from_lat_long(latitude, longitude):
     # Construct the URL for the Geocoding API
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={gmaps_api_key}&language=en"

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
        print(localities)
        if len(localities) == 1:
            return country, list(localities)[0]
        else:
            return country, list(localities)
    else:
        return f"Error: {response.status_code}", "Error in response"

# Function to search country in Notion and return its page ID
def search_page_in_notion(search_query, database_id):
    # Headers for Notion API
    notion_headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    # Example payload for Notion API POST request
    notion_payload = {
        "query": search_query,
        "filter": {
            "value": "page",
            "property": "object"
        },
        "sort": {
            "direction": "ascending",
            "timestamp": "last_edited_time"
        }
    }

    notion_database_query_url = 'https://api.notion.com/v1/search'

    # Making the POST request
    response = requests.post(notion_database_query_url, json=notion_payload, headers=notion_headers)
    print("Search Query is: " + search_query)
    # Check the response
    if response.status_code == 200:
        search_results = response.json()
        for page in search_results['results']:
            if page.get('parent', {}).get('database_id') == database_id and \
                    any(title['text']['content'] == search_query for title in page.get('properties', {}).get('Name', {}).get('title', [])):
                return page['id']  # Return the first matching page ID

        print("No matching page found.")
        return None
    else:
        print("Failed:", response.status_code, response.text)
        return None
        
def search_localities_in_notion(localities, database_id):
    # Ensure localities is always a list
    if isinstance(localities, str):
        localities = [localities]
    
    # Headers for Notion API
    notion_headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    notion_database_query_url = 'https://api.notion.com/v1/search'

    for search_query in localities:
        print("Searching for:", search_query)

        # Example payload for Notion API POST request
        notion_payload = {
            "query": search_query,
            "filter": {
                "value": "page",
                "property": "object"
            },
            "sort": {
                "direction": "ascending",
                "timestamp": "last_edited_time"
            }
        }

        # Making the POST request
        response = requests.post(notion_database_query_url, json=notion_payload, headers=notion_headers)

        # Check the response
        if response.status_code == 200:
            search_results = response.json()
            for page in search_results['results']:
                if page.get('parent', {}).get('database_id') == database_id and \
                        any(title['text']['content'] == search_query for title in page.get('properties', {}).get('Name', {}).get('title', [])):
                    return page['id']  # Return the first matching page ID

        else:
            print("Failed:", response.status_code, response.text)

    print("No matching page found for any of the localities.")
    return None

def create_page_details(place_name, latitude, longitude, country_page_id, locality_page_id, time_of_day, closed_days, websiteUri, category):
    # Example structure. Modify this according to your Notion database's schema.
    page_details = {
        "parent": {"database_id": "07cc7511-85a0-49ff-8473-e5470ec595a8"},  # Replace with your database ID
        "properties": {
            "Activity Name": {
                "title": [
                    {"text": {"content": place_name}}
                ]
            },
            "Activity Type": {
                "select": {
                    "name": category
                }
            },
            "Days Closed": {
                "multi_select": [
                    {"name": day} for day in closed_days
                ]
            },
            "URL": {
                "url": websiteUri
            },
            "Latitude": {
                "number": latitude
            },
            "Longitude": {
                "number": longitude
            },
            "Country": {
                "relation": [
                    {"id": country_page_id}
                ]
            },
            "City": {
                "relation": [
                    {"id": locality_page_id}
                ]
            },
            "Booked": {
                "checkbox": False
            },
            "Day or Night": {
                "multi_select": [
                    {"name": time} for time in time_of_day 
                ]
            },
            # Add other properties as needed
        },
        # Optional: Add icon, cover, and children (blocks) as needed
    }
    return page_details

def analyze_opening_hours(data):
    # Define the names of the days for reference
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Initialize variables
    closed_days = []
    suitable_for_day = False
    suitable_for_night = False
    open_24_7 = False

    # Check if open 24/7
    if 'open24Hours' in data and data['open24Hours']:
        open_24_7 = True
    else:
        # Create a dictionary to map days to their open/close times
        periods_dict = {period['open']['day']: period for period in data.get('periods', [])}

        for day, day_name in enumerate(days_of_week):
            description = data['weekdayDescriptions'][day]

            # Check if the day is closed
            if 'Closed' in description:
                closed_days.append(day_name)
                continue

            # Check if the day's data is available
            if day in periods_dict:
                period = periods_dict[day]

                # Check if open for day or night or both
                if period['open']['hour'] < 12:
                    suitable_for_day = True
                if 'close' in period and period['close']['hour'] >= 21:
                    suitable_for_night = True

    # Determine suitability
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

def categorise_primary_type(primary_type):
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

# Function to add a page to Notion
def add_page_to_notion(page_details):
    database_id = "07cc7511-85a0-49ff-8473-e5470ec595a8"
  
    # Notion API URL to create a new page
    url = 'https://api.notion.com/v1/pages'

    # Headers for the request
    headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    # Making the POST request to create a new page
    response = requests.post(url, headers=headers, data=json.dumps(page_details))

    # Check the response
    if response.status_code == 200:
        print("New page created successfully:", response.json())
    else:
        print("Failed to create page:", response.status_code, response.text)

def run_script():
    google_maps_url = url_entry.get()
    if google_maps_url:
        main(google_maps_url)
        messagebox.showinfo("Success", "The script has been executed successfully.")
    else:
        messagebox.showwarning("Warning", "Please enter a Google Maps URL.")


# Main script flow
def main(google_maps_url):
    print("URL entered:", google_maps_url)

    # Extract details from Google Maps
    place_name, latitude, longitude, regularOpeningHours, websiteUri, primary_type = extract_details_from_google_maps(google_maps_url)

    # Categorise the primary type
    category = categorise_primary_type(primary_type)

    # Get the country from the latitude and longitude
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    country_name, localities = get_country_from_lat_long(latitude, longitude)
    # Search for the country in Notion and get the page ID
    countries_database = '5270d10c-a5b0-4bbe-9e76-c69e7d2e64c4'
    cities_database = '2fc9cb63-163b-40d5-b41d-c8f17fa4c9e2'
    
    country_page_id = search_page_in_notion(country_name, countries_database)
    print("Country Page ID:", country_page_id)
    locality_page_id = search_localities_in_notion(localities, cities_database)
    print("Locality Page ID:", locality_page_id)
    
    closed_days, time_of_day = analyze_opening_hours(regularOpeningHours)

    if country_page_id:
        # Prepare details for the new Notion page
        page_details = create_page_details(place_name, latitude, longitude, country_page_id, locality_page_id,time_of_day, closed_days, websiteUri, category)

        # Add a new page to Notion
        add_page_to_notion(page_details)
    else:
        print("Unable to find the country page ID in Notion.")

    if locality_page_id:
        print(f"Found matching page ID: {locality_page_id}")
    else:
        # Call or define your function to create a new page here
        print("Proceeding to create a new page...")

    print("Process completed successfully.")

if __name__ == "__main__":
    # GUI Setup
    root = tk.Tk()
    root.title("Google Maps to Notion")

    # URL Entry
    tk.Label(root, text="Enter Google Maps URL:").pack()
    url_entry = tk.Entry(root, width=50)  # Initialize here
    url_entry.pack()

    # Run Button
    run_button = tk.Button(root, text="Run Script", command=run_script)
    run_button.pack()

    # Start the GUI event loop
    root.mainloop()

# Start the GUI event loop
root.mainloop()