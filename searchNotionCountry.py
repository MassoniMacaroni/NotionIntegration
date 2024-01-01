import re
import requests
import json


### NOTION INSERTS ###
notion_api_key = 'secret_N6UR0t4kMT7gJTqPKRqDM9OA323eegULmiMBw7ltqBc'

# Search query
search_query = "Naples"

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

# Check the response
if response.status_code == 200:
    search_results = response.json()
    filtered_results = [page['id'] for page in search_results['results']
                        if page.get('parent', {}).get('database_id') == '2fc9cb63-163b-40d5-b41d-c8f17fa4c9e2'
                        and any(title['text']['content'] == search_query for title in page.get('properties', {}).get('Name', {}).get('title', []))]

    print("Filtered Page IDs:", filtered_results)
else:
    print("Failed:", response.status_code, response.text)


