import requests
from dotenv import load_dotenv
import os
import json
import re
import tkinter as tk
from tkinter import messagebox
import threading

url_entry = None

# Load environment variables from .env file
load_dotenv()

# Access API keys
notion_api_key = os.getenv('NOTION_API_KEY')
gmaps_api_key = os.getenv('GMAPS_API_KEY')

# Function to extract details from a Google Maps link
def extract_details_from_google_maps(google_maps_url):
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

    # Make the POST request 
    response = requests.post(url, json=payload, headers=headers)
    regularOpeningHours = None
    websiteUri = None
    primary_type = None

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
        administrative_areas = set()

        # Iterate through results to find the country, localities, and administrative areas
        for result in results:
            for component in result.get('address_components', []):
                if 'country' in component.get('types', []):
                    country = component.get('long_name')
                if 'locality' in component.get('types', []):
                    localities.add(component.get('long_name'))
                if 'administrative_area_level_2' in component.get('types', []):
                    administrative_areas.add(component.get('long_name'))

        # Determine which value to return based on availability
        print("Localities:", localities)
        print("Administrative Areas:", administrative_areas)
        if localities:
            return country, list(localities)
        elif administrative_areas:
            return country, list(administrative_areas)
        else:
            return country, []
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

    #ayload for Notion API POST request
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

        # payload for Notion API POST request
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

def create_thingsToDo_page_details(place_name, latitude, longitude, country_page_id, locality_page_id, time_of_day, closed_days, websiteUri, category):
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

def create_countries_page_details(country_name):
    page_details = {
        "parent": {"database_id": "5270d10c-a5b0-4bbe-9e76-c69e7d2e64c4"},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": country_name}}
                ]
            },
            # Add other properties as needed
        },
        # Optional: Add icon, cover, and children (blocks) as needed
    }
    return page_details

def create_cities_page_details(city_name, country_page_id):
    page_details = {
        "parent": {"database_id": "2fc9cb63-163b-40d5-b41d-c8f17fa4c9e2"},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": city_name}}
                ]
            },
            "Countries": {
                "relation": [
                    {"id": country_page_id}
                ]
            },
            # Add other properties as needed
        },
        # Optional: Add icon, cover, and children (blocks) as needed
    }
    return page_details
def analyze_opening_hours(data):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    closed_days = []
    open_24_7 = False

    # Check for 24/7 opening
    if data is None or ('open24Hours' in data and data['open24Hours']) or len(data.get('periods', [])) == 1 and data['periods'][0]['open']['day'] == 0 and data['periods'][0]['open']['hour'] == 0:
        open_24_7 = True

    if open_24_7:
        # If open 24/7, no closed days and suitable for both day and night
        time_of_day = ["Day", "Night"]
    else:
        suitable_for_day = False
        suitable_for_night = False

        for day in range(7):  # Check each day of the week
            periods_for_day = [period for period in data.get('periods', []) if period['open']['day'] == day]

            if not periods_for_day:  # If no periods, the day is closed
                closed_days.append(days_of_week[day])
                continue

            for period in periods_for_day:
                open_hour = period['open']['hour']
                close_hour = period.get('close', {}).get('hour', 24)  # Default to 24 if closing time is not specified
                close_day = period.get('close', {}).get('day', day)

                # Check for day and night suitability
                if open_hour < 12:
                    suitable_for_day = True
                if close_hour >= 21 or (close_day != day and close_hour < 6):  # Closing past midnight
                    suitable_for_night = True

        # Determine time of day suitability
        if suitable_for_day and suitable_for_night:
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
    return category_mapping.get(primary_type, "Activity")

# Function to add a page to Notion
def add_page_to_notion(page_details):
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
        response_data = response.json()
        page_id = response_data.get('id')
        print("New page created successfully with ID:", page_id)
        return page_id  # Return the page ID
    else:
        print("Failed to create page:", response.status_code, response.text)


def run_script(status_label):
    google_maps_url = url_entry.get()
    if google_maps_url:
        status_label.config(text="Running script...")
        main(google_maps_url, status_label)
        messagebox.showinfo("Success", "The script has been executed successfully.")
        status_label.config(text="Ready.")
    else:
        messagebox.showwarning("Warning", "Please enter a Google Maps URL.")
        status_label.config(text="Please enter a valid URL.")

def run_script_threaded(status_label):
    google_maps_url = url_entry.get()
    if google_maps_url:
        status_label.config(text="Running script...")
        # Start a new thread for the main task
        threading.Thread(target=main, args=(google_maps_url, status_label), daemon=True).start()
    else:
        messagebox.showwarning("Warning", "Please enter a Google Maps URL.")
        status_label.config(text="Please enter a valid URL.")

# Main script flow
def main(google_maps_url, status_label):
    try:
        print("URL entered:", google_maps_url)
        status_label.config(text="Extracting details from Google Maps...")
        # Extract details from Google Maps
        place_name, latitude, longitude, regularOpeningHours, websiteUri, primary_type = extract_details_from_google_maps(google_maps_url)
        category = categorise_primary_type(primary_type)

        print("Latitude:", latitude)
        print("Longitude:", longitude)
        country_name, localities = get_country_from_lat_long(latitude, longitude)

        countries_database = '5270d10c-a5b0-4bbe-9e76-c69e7d2e64c4'
        cities_database = '2fc9cb63-163b-40d5-b41d-c8f17fa4c9e2'

        # Search for the country in Notion, create if not found
        country_page_id = search_page_in_notion(country_name, countries_database)
        if not country_page_id:
            print("Creating new Country Page:", country_name)
            page_details = create_countries_page_details(country_name)
            country_page_id = add_page_to_notion(page_details)

        # Check and handle localities (cities)
        locality_page_id = None
        for locality in localities:
            locality_page_id = search_page_in_notion(locality, cities_database)
            if locality_page_id:
                break

        if not locality_page_id and localities:
            print("Creating new City Page:", localities[0])
            country_page_id = search_page_in_notion(country_name, countries_database)
            page_details = create_cities_page_details(localities[0], country_page_id)
            locality_page_id = add_page_to_notion(page_details)

        closed_days, time_of_day = analyze_opening_hours(regularOpeningHours)

        # Prepare and add the thingsToDo page
        if country_page_id and locality_page_id:
            page_details = create_thingsToDo_page_details(place_name, latitude, longitude, country_page_id, locality_page_id, time_of_day, closed_days, websiteUri, category)
            add_page_to_notion(page_details)
        else:
            print("Failed to find or create necessary pages in Notion.")

        status_label.config(text="Process completed successfully.")
        messagebox.showinfo("Success", "The script has been executed successfully.")
        url_entry.delete(0, tk.END)  # Clear the entry box
        print("Process completed successfully.")
    except Exception as e:
            messagebox.showerror("Error", str(e))
            status_label.config(text="An error occurred.")
    
if __name__ == "__main__":
    # GUI Setup
    root = tk.Tk()
    root.title("Google Maps to Notion")

    # URL Entry
    tk.Label(root, text="Enter Google Maps URL:").pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.pack()

    # Run Button
    run_button = tk.Button(root, text="Run Script", command=lambda: run_script_threaded(status_label))
    run_button.pack()

    # Status Label
    status_label = tk.Label(root, text="Ready.", fg="green")
    status_label.pack()

    # Start the GUI event loop
    root.mainloop()