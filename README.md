# Image Size Retriever
### Description
The Image Size Retriever is a Python script that retrieves image URLs from a Google Sheets document, retrieves the sizes of the images from the URLs, and inserts the URLs and sizes back into the Google Sheets document. The script uses the gspread and httpx libraries to interact with the Google Sheets API and make HTTP requests, respectively. It also uses the asyncio library to make the requests asynchronously and the PIL library to open the images.

### Dependencies
- gspread
- httpx
- asyncio
- PIL
- oauth2client
## Usage
- Set the KEY_OF_SHEET_DATA variable to the key of the Google Sheets document containing the image URLs.
- Run the script with python3 image_size_retriever.py.
- The script will retrieve the image URLs and sizes, and insert them back into the new created Google Sheets document.
## Configuration
- The script is configured to create a new google sheet with name "test case 1" and share it with your email
- Also the script is using the "service_key.json" file to authorize the client

## Additional info
The script uses semaphore to limit the number of concurrent requests.

The script also uses retry mechanism for bad requests, if the image url is bad or not available it will retry for maximum of 10 times and if still not able to get image it will append the url to bad_request_data list.

Note
Please ensure that the Google Sheets document has a header row with columns named "image_url"also you can change it to your case

_You need to have the **credentials** for the google sheets API._

Please ensure that you have the necessary permissions to access the Google Sheets document and insert data into it.
