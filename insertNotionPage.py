import requests
import json

notion_api_key = 'secret_N6UR0t4kMT7gJTqPKRqDM9OA323eegULmiMBw7ltqBc'

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

# Making the POST request to create a new page
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check the response
if response.status_code == 200:
    print("New page created successfully:", response.json())
else:
    print("Failed to create page:", response.status_code, response.text)