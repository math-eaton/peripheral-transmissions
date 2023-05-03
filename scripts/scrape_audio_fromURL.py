import asyncio
import csv
from pyppeteer import launch
from pydub import AudioSegment
import sounddevice as sd
import os
import re
import numpy as np
import wavio

width = 1280
height = 740

def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

async def process_url(url, id):
    # Launch the browser
    browser = await launch(headless=True, args=[
    '--disable-blink-features=AutomationControlled',
    '--autoplay-policy=no-user-gesture-required',
    '--disable-gpu'])
    page = None

    try:
        # Open the webpage
        page = await browser.newPage()
        print("opening new page")

        # Set the user agent to a common browser user agent
        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

        # Set the viewport size
        await page.setViewport({'width': width, 'height': height})
        # print(page.viewport)

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
            # Set a 30-second timeout for loading the page and wait for the network to be idle
            await asyncio.wait_for(page.goto(url, waitUntil='networkidle0'), timeout=30)
        except asyncio.TimeoutError:
            print(f"Timeout while loading URL {url}")
            if page is not None and not page.isClosed():
                await page.close()
            await browser.close()
            return

        # Refresh the page by navigating to the same URL again
        # await page.goto(url)

        # Wait 15 seconds
        print("waiting 15 seconds...")
        await asyncio.sleep(15)

        # Click in the center of the webpage
        print("clicking in center of page...")
        await page.mouse.move(width/2, height/2)
        await page.mouse.down()
        # await page.mouse.move(width, height + 1)  # Move one pixel in the +y direction
        await page.mouse.up()

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

        # Wait for a network request with a URL that ends with "channel.mp3"
        # await page.waitForRequest(lambda req: req.url.endswith("channel.mp3"))

        # Wait 3 seconds
        print("waiting 3 more secs ...")
        await asyncio.sleep(3)

        # Record 10 seconds of audio from the computer's main output
        print("recording starting ...")
        recording_duration = 10  # seconds
        recording_rate = 44100  # Hz
        recording_channels = 1  # Set number of channels to 1 (mono)
        recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels, dtype='int16', device=6)
        sd.wait()
        print("recording complete!")

        # Save the audio output file with the name of its associated URL in the "audio" subfolder
        sanitized_filename = sanitize_filename(url.split('/')[-1])
        audio_filename = f"audio/{sanitized_filename}.mp3"

        # Save recording to a temporary WAV file
        wav_filename = "temp_recording.wav"
        wavio.write(wav_filename, recording, recording_rate, sampwidth=2)

        # Load the temporary WAV file with pydub and save as mp3
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(audio_filename, format="mp3")
        print(audio_filename)

        # Remove the temporary WAV file
        os.remove(wav_filename)

        # Close the browser window
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        if page is not None and not page.isClosed():
            await page.close()

    # Close the browser
    await browser.close()


async def main():
    # Read the CSV file
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_formatted_NorthAmerica.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['url']
            id = row['id']
            print(f"Processing URL: {url}")
            await process_url(url, id)

    # Create the "audio" subfolder if it doesn't exist
    os.makedirs('audio', exist_ok=True)

    # # Process each URL
    # for url in urls:
    #     await process_url(url)

asyncio.run(main())
