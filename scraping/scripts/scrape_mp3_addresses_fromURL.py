import asyncio
import csv
from pyppeteer import launch
import os
import re
import json

width = 800
height = 600

# def sanitize_filename(filename):
#     return re.sub(r'[\\/:"*?<>|]+', '_', filename)

async def process_url(url, id):
    max_retries = 3
    retry_delay = 5

    for attempt in range(1, max_retries + 1):
    # Launch the browser
        browser = await launch(headless=True, args=[
        '--disable-blink-features=AutomationControlled',
        '--autoplay-policy=no-user-gesture-required',
        '--disable-gpu'])

    # Initialize variables
    page = None
    mp3_url = ""


    try:
        # Open the webpage
        page = await browser.newPage()
        print("opening new page")

        # Set the user agent to a common browser user agent
        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

        # Set the viewport size
        await page.setViewport({'width': width, 'height': height})

        # Set other options to make the browser appear more like a regular user's browser
        await page.evaluateOnNewDocument('''() => {
            delete navigator.__proto__.webdriver;
            window.navigator.chrome = {
                runtime: {},
            };
            const originalQuery = window.navigator.permissions.query;
            return window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        }''')

        try:
            # Set a 10-second timeout for loading the page and wait for the network to be idle
            await asyncio.wait_for(page.goto(url, waitUntil='domcontentloaded'), timeout=10)
        except asyncio.TimeoutError:
            print(f"Timeout while loading URL {url}")
            if page is not None and not page.isClosed():
                await page.close()
            await browser.close()
            return

        # # Wait 5 seconds
        # print("waiting 5 seconds...")
        # await asyncio.sleep(5)

        # Click on the HTML element with the specified class
        await page.waitForSelector('._control_oyndo_11._modPlay_oyndo_53')
        element = await page.querySelector('._control_oyndo_11._modPlay_oyndo_53')
        await element.click()
        print("powering on")

        # Scroll down the page slightly
        print("scrolling a little ...")
        await page.evaluate("window.scrollBy(0, -250)")

        # Click and drag in the center of the webpage
        print("draagging me ...")
        await page.mouse.move(width/2, height/2)
        await page.mouse.down()
        await page.mouse.move(width/2, height/2 - 1)  # Move one pixel in the -y direction
        await page.mouse.up()

        # Click in the center of the webpage
        print("clicking in center of page...")
        await page.mouse.move(width/2, height/2)
        await page.mouse.down()
        # await page.mouse.move(width, height + 1)  # Move one pixel in the +y direction
        await page.mouse.up()

        # Wait for the network request with the specified initiator
        print("tuning the radio...")
        req = await page.waitForRequest(lambda req: 'channel.mp3' in req.url)
        print("receiving " + req.url)

        # Save the mp3 URL
        mp3_url = req.url

        if mp3_url:
            # Write data directly to CSV and JSON files
            script_dir = os.path.dirname(os.path.abspath(__file__))

            # Write to JSON file
            json_file_path = os.path.join(script_dir, 'data/USMX_scraped_channels.json')
            data = {"id": id, "url": url, "mp3_url": mp3_url}
            with open(json_file_path, 'a', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False)
                json_file.write('\n')
                print(f"Writing to scraped_channels.json: {data}")

            # Write to CSV file
            csv_file_path = os.path.join(script_dir, 'data/USMX_scraped_channels.csv')
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'url', 'mp3_url']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(data)
                print(f"Writing to scraped_channels.csv: {data}")

            return data
        else:
            raise Exception("mp3_url is empty")

    except Exception as e:
        print(f"Error processing URL {url} (attempt {attempt}): {e}")
        if page is not None and not page.isClosed():
            await page.close()
        if attempt < max_retries:
            print(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
        else:
            print("Max retries reached, moving to the next URL.")
            return {"id": id, "url": url, "mp3_url": ""}
    
    # Close the browser
    await browser.close()

async def main():
    # Read the CSV file
    csv_file_path = '/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/USMX_finalStationPoint.csv'
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['url']
            id = row['id']
            print(f"Processing URL: {url}")
            await process_url(url, id)

asyncio.run(main())
