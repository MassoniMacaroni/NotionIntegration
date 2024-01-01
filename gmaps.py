import re
import requests
import json

# Prompt the user for a Google Maps URL
google_maps_url = "https://www.google.com/maps/place/Colosseum/@41.8901534,12.4893873,17z/data=!4m6!3m5!1s0x132f61b6532013ad:0x28f1c82e908503c4!8m2!3d41.8902102!4d12.4922309!16zL20vMGQ1cXg?entry=ttu"
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
    'X-Goog-Api-Key': 'AIzaSyDHlT4doSbP1o_gHmaqrbXTr-PkcpBSr34',  # Replace with your actual API key
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.id,places.primaryType,places.websiteUri,places.nationalPhoneNumber,places.location,places.internationalPhoneNumber,places.nationalPhoneNumber,places.priceLevel,places.regularOpeningHours'
}

# Make the POST request (Uncomment the lines below to actually send the request)
#response = requests.post(url, json=payload, headers=headers)


# Check the response status code and parse the response
""" if response.status_code == 200:
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

# Output for verification
print("Extracted Place Name:", place_name)
print("Extracted Latitude:", latitude)
print("Extracted Longitude:", longitude)
print("Payload for POST Request:", payload)
print("Extracted Address:", formatted_address)
 """
### NOTION INSERTS ###
notion_api_key = 'secret_N6UR0t4kMT7gJTqPKRqDM9OA323eegULmiMBw7ltqBc'

# Headers for Notion API
notion_headers = {
    'Authorization': f'Bearer {notion_api_key}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

# Example payload for Notion API POST request
notion_payload = {
    "query": "Rome",
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

# Check the response
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Failed:", response.status_code, response.text)

database_id = "07cc7511-85a0-49ff-8473-e5470ec595a8"
  
# Notion API URL to create a new page
url = 'https://api.notion.com/v1/pages'

# Headers for the request
headers = {
    'Authorization': f'Bearer {notion_api_key}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# Payload for the new page (activity), incorporating the provided properties
payload = {
    "parent": {"database_id": database_id},
    "properties": {
        "Activity Name": {
            "title": [{"text": {"content": "TESTING ACTIVITIE"}}]
        },
        "Activity Type": {
            "select": {
                "name": "Activity"  # Example, choose appropriate value
            }
        },
        "Priority": {
            "number": 1  # Example value
        },
        "Book/Ticket Req?": {
            "select": {
                "name": "Yes"  # or "No", as appropriate
            }
        },
        "Days Closed": {
            "multi_select": [
                {"name": "Monday"},  # Add other days as needed
            ]
        },
        "Booked": {
            "checkbox": False
        },
        "Price": {
            "number": 25.00  # Example price, adjust as needed
        },
        "Day or Night": {
            "multi_select": [
                {"name": "Day"}  # Or "Night", as appropriate
            ]
        },
        # Add other properties as needed
    },
    # Optional: Add icon, cover, and children (blocks) as needed
}
'''
# Making the POST request to create a new page
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check the response
if response.status_code == 200:
    print("New page created successfully:", response.json())
else:
    print("Failed to create page:", response.status_code, response.text)
    '''