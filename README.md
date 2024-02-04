## NotionIntegration
My NotionIntegration is a Python application designed to integrate Google Maps data into Notion databases. This tool automates the process of extracting detailed information from Google Maps URLs, including place names, coordinates, opening hours, and other relevant data, and then creates or updates corresponding entries within a Notion database. I use it to streamline my process of travel planning within notion with geolocation-based data.


### Features
Google Maps Extraction: Automatically extracts data from Google Maps URLs, including place names, latitudes, longitudes, opening hours, and website URLs.
Notion Database Integration: Creates or updates Notion database pages with extracted data, organizing information efficiently within your workspace.
GUI Application: Offers a simple and intuitive graphical user interface (GUI) for easy operation by any user, regardless of their technical background.
Flexible Data Handling: Supports handling of various data types and structures from Google Maps, ensuring robust integration with Notion.

### How It Works
* Input Google Maps URL: Users input a Google Maps URL of the location they wish to add to their Notion database.
* Data Extraction: The application uses the Google Maps API to extract detailed information from the provided URL, including the place's name, geographic coordinates, and more.
* Notion Update: Utilizing the Notion API, the application then creates or updates a page within a specified Notion database with the extracted information.
* User Feedback: Through its GUI, the application provides feedback on the operation's success or failure, including any errors encountered.