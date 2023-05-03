import asyncio
import csv
from pyppeteer import launch
import os
import re

width = 800
height = 600

# def sanitize_filename(filename):
#     return re.sub(r'[\\/:"*?<>|]+', '_', filename)

async def process_url(url, id):
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

        # Wait 5 seconds
        print("waiting 5 seconds...")
        await asyncio.sleep(5)

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
        req = await page.waitForRequest(lambda req: 'channel.mp3' in req.url)
        print("receiving " + req.url)

        # Save the mp3 URL
        mp3_url = req.url

        # Close the browser window
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        if page is not None and not page.isClosed():
            await page.close()

    # Close the browser
    await browser.close()

    return id, mp3_url

async def main():
    # Read the CSV file
    csv_file_path = '/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_formatted_NorthAmerica.csv'
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        radio_data = []
        for row in reader:
            url = row['url']
            id = row['id']
            print(f"Processing URL: {url}")
            id, mp3_url = await process_url(url, id)
            row["radio_URL"] = mp3_url
            radio_data.append(row)

    # Write the modified CSV file
    new_csv_file_path = 'places_formatted_NorthAmerica_with_radio_URL.csv'
    with open(new_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = reader.fieldnames + ['radio_URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in radio_data:
            writer.writerow(row)

asyncio.run(main())