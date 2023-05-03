import asyncio
import csv
from pyppeteer import launch
from pydub import AudioSegment
import sounddevice as sd
import os
import re
import numpy as np
import wavio

def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

async def process_url(url, id):
    # Launch the browser
    browser = await launch(headless=False, args=['--disable-blink-features=AutomationControlled'])

    try:
        # Open the webpage
        page = await browser.newPage()

        # Set the user agent to a common browser user agent
        await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

        # Set the viewport size
        await page.setViewport({'width': 800, 'height': 600})

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

        await page.goto(url)


        # Refresh the page by navigating to the same URL again
        # await page.goto(url)

        # Wait 3 seconds
        await asyncio.sleep(15)

        # Scroll down the page slightly
        await page.evaluate("window.scrollBy(0, 50)")

        # Click and drag in the center of the webpage
        await page.mouse.move(640, 360)
        await page.mouse.down()
        await page.mouse.move(640, 359)  # Move one pixel in the -y direction
        await page.mouse.up()

        # Wait for a network request with a URL that ends with "channel.mp3"
        # await page.waitForRequest(lambda req: req.url.endswith("channel.mp3"))

        # Wait 3 seconds
        await asyncio.sleep(5)

        # Record 10 seconds of audio from the computer's main output
        recording_duration = 10  # seconds
        recording_rate = 44100  # Hz
        recording_channels = 1  # Set number of channels to 1 (mono)
        recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels, dtype='int16', device=6)
        sd.wait()

        # Save the audio output file with the name of its associated URL in the "audio" subfolder
        sanitized_filename = sanitize_filename(url.split('/')[-1])
        audio_filename = f"audio/{sanitized_filename}.mp3"
        print(audio_filename)

        # Save recording to a temporary WAV file
        wav_filename = "temp_recording.wav"
        wavio.write(wav_filename, recording, recording_rate, sampwidth=2)
        print(wav_filename)

        # Load the temporary WAV file with pydub and save as mp3
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(audio_filename, format="mp3")

        # Remove the temporary WAV file
        os.remove(wav_filename)

        # Close the browser window
        await page.close()
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        await page.close()

    # Close the browser
    await browser.close()

async def main():
    # Read the CSV file
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_sample.csv', newline='', encoding='utf-8') as csvfile:
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
