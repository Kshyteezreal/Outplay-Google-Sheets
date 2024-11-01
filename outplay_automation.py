# Step 1: Mount Google Drive
from google.colab import drive
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
import asyncio
import aiohttp  # Asynchronous HTTP requests for faster API calls
import time  # To add delay between batch writes
from datetime import timedelta, date

# Step 1: Mount Google Drive
drive.mount('/content/drive')

# Step 2: Google Sheets API Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/content/drive/My Drive/credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1kur479WhaPe7_z_9JFI5CjXp5Qzu38-JdIXCNoUJFE8/edit?usp=sharing")
worksheet = spreadsheet.sheet1

# Step 3: Optimized Async API Calls
async def fetch_data(session, url, headers, payload):
    async with session.post(url, headers=headers, json=payload) as response:
        if response.status == 200:
            return await response.json()
        else:
            return None

async def main():
    url = "https://us4-api.outplayhq.com/api/v1/call/search?client_id=RokT6dTXOVyf7J35mNkLwXFPfe8V3DCi"
    headers = {
        'X-CLIENT-SECRET': 'VdYOfkjSU5WhPv7YppVpWMaPLUFxBXCXiIeoGQCuVjU6CwpHft3BTF3AsqnmnONB',
        'Content-Type': 'application/json'
    }
    today = date.today()
    from_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    tasks = []
    async with aiohttp.ClientSession() as session:
        for pageindex in range(1, 121):  # Looping from pageindex 1 to 50
            payload = {
                "calldirection": "both",
                "fromdate": from_date,
                "todate": to_date,
                "pageindex": pageindex
            }
            task = asyncio.ensure_future(fetch_data(session, url, headers, payload))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    # Step 4: Extract Individual Fields, Batch Rows, and Append in Batches
    batch_size = 50  # Number of rows to append in each batch
    row_batch = []  # To collect rows for batch insertion

    for result in results:
        if result:
            for item in result.get('data', []):  # Adjust this according to actual response structure
                # Extract individual fields from each record in the JSON response
                calldate = item.get('calldate')  # Date of the call
                calloutcome = item.get('calloutcome')  # Outcome of the call
                callsid = item.get('callsid')  # Call SID
                callstatus = item.get('callstatus')  # Call Status
                calltype = item.get('calltype')  # Type of call
                duration = item.get('duration')  # Call duration
                firstname = item.get('firstname')  # First name of the prospect
                lastname = item.get('lastname')  # Last name of the prospect
                phonenumber = item.get('phonenumber')  # Phone number
                sequencename = item.get('sequencename')  # Sequence name
                prospectid = item.get('prospectid')  # Prospect ID
                userid = item.get('userid')  # User ID
                callstate = item.get('callstate')  # Call state
                prospectcallid = str(item.get('prospectcallid'))  # Prospect call ID
                recordingurl = item.get('recordingurl')  # Recording URL

                # Create a row with the extracted fields
                row = [
                    calldate, calloutcome, callsid, callstatus, calltype, duration, firstname,
                    lastname, phonenumber, sequencename, prospectid, userid, callstate, str(prospectcallid), recordingurl
                ]

                # Add row to batch
                row_batch.append(row)

                # If batch size is reached, append the rows to Google Sheets
                if len(row_batch) >= batch_size:
                    worksheet.append_rows(row_batch)
                    row_batch.clear()  # Clear the batch
                    time.sleep(0.5)  # Add a 0.5-second delay between batches

    # Step 5: Append any remaining rows in the batch
    if row_batch:
        worksheet.append_rows(row_batch)

    print("All rows successfully uploaded to Google Sheets in batches!")

# Step 6: Execute the Async Main Function
await main()
