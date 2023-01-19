import asyncio
import time

import gspread
import httpx

from PIL import Image
from io import BytesIO

from asyncio import Semaphore

from oauth2client.service_account import ServiceAccountCredentials


KEY_OF_SHEET_DATA = "1QX2IhFyYmGDFMvovw2WFz3wAT4piAZ_8hi5Lzp7LjV0"

# use creds to create a client to interact with the Google Drive API
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_key.json", scope
)
cl = gspread.authorize(creds)   # client authorization

gsheet = cl.create("test case 1")

#
gsheet.share("oleksii.bodnarchuk@gmail.com", perm_type="user", role="writer", notify=False)
sheet1_data = gsheet.sheet1

sheet1_data.insert_row(["Image URL", "SIZE"], index=1)

MAX_RETRIES = 10

bad_request_data = []


def take_data_from_sheet(key: str):
    """Retrieves data from a Google Sheets document specified by its key.
    Args:
        key (str): The key of the Google Sheets document.
    Returns:
        list: A list of all records in the document.
    """
    sheet_data = cl.open_by_key(key).get_worksheet(0)
    list_with_data = sheet_data.get_all_records()
    return list_with_data


async def image_size(semaphore: Semaphore(), url: str, client: httpx.AsyncClient(timeout=5)):
    """Retrieves the size of an image from a given URL using a semaphore and a httpx client.
    Args:
        semaphore (Semaphore): A semaphore to limit the number of concurrent requests.
        url (str): The URL of the image.
        client (httpx.AsyncClient): The httpx client used to make the request.
    Returns:
        list: A list containing the URL and size of the image in the format [url, size].
        also catch exception we try few times to reconnect, if not - append to bad request list.
    """
    retries = 0
    await semaphore.acquire()
    while retries <= MAX_RETRIES:
        try:
            response = await client.get(url)
            semaphore.release()
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                retries = 0
                print(img.size)
                return [str(url), str(img.size)]
            if response.status_code != 200:
                print("bad link")
                print(url)
                break
        except:
            print("Received bad request, reconnecting...")
            await asyncio.sleep(3)
            retries += 1
    print("Maximum retries reached")
    bad_request_data.append(url)
    semaphore.release()


async def take_size_from_urls():
    """Retrieves the URLs of images from a Google Sheets document and retrieves their sizes,
    then inserts the URLs and sizes back into created document.
    """
    sheet_data = take_data_from_sheet(KEY_OF_SHEET_DATA)
    semaphore = Semaphore(8)

    async with httpx.AsyncClient(timeout=5) as c:
        data = await asyncio.gather(
            *[image_size(
                semaphore=semaphore,
                url=row["image_url"],
                client=c
            ) for row in sheet_data]
        )
        sheet1_data.append_rows(data)
        print(bad_request_data.__len__())

if __name__ == '__main__':
    start_time = time.perf_counter()
    asyncio.run(take_size_from_urls())
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    print("Execution time:", execution_time)
