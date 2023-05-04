import asyncio
import csv
import pyppeteer
from pyppeteer import launch
from pydub import AudioSegment
import sounddevice as sd
import os
import re
import numpy as np
import wavio

width = 800
height = 600

def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

async def process_url(url, id):
    # Launch the browser
    browser = await launch(headless=False, args=[
    '--disable-blink-features=AutomationControlled',
    '--autoplay-policy=no-user-gesture-required',
    '--disable-download-extensions'
    '--disable-gpu'])
    page = None

    try:
        # Open the webpage
        page = await browser.newPage()
        print("opening new page")

        page.on('console', lambda msg: print(f'Page log: {msg.text()}'))
        await page.setJavaScriptEnabled(False)

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

        # Create an HTML page containing an audio element with the MP3 URL as its source, and load this HTML page in the browser
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        </head>
        <body>
        <audio controls autoplay>
          <source src="{url}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
        </body>
        </html>
        """
        await page.setContent(html_content)


        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await asyncio.wait_for(page.goto(url, waitUntil='networkidle2'), timeout=30)
                break
            except (asyncio.TimeoutError, pyppeteer.errors.PageError) as e:
                print(f"Attempt {attempt}: Error while loading URL {url}: {e}")
                if attempt == max_retries:
                    print(f"Failed to load URL {url} after {max_retries} attempts")
                    if page is not None and not page.isClosed():
                        await page.close()
                    await browser.close()
                    return
                else:
                    await asyncio.sleep(2)  # Sleep for 2 seconds before retrying

        print("powering on")

        # Wait for the network request with the specified resource type
        # await page.waitForRequest(lambda req: req.resourceType == 'media')

        # Wait 3 seconds
        print("waiting 3 secs ...")
        await asyncio.sleep(3)

        # Record 10 seconds         # Record 10 seconds of audio from the computer's main output
        print("recording starting ... ... ... ")
        recording_duration = 10  # seconds
        recording_rate = 44100  # Hz
        recording_channels = 1  # Set number of channels to 1 (mono)
        recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels, dtype='int16', device=6)
        sd.wait()
        print("recording complete!")

        # Save the audio output file with the name of its associated URL in the "audio" subfolder
        sanitized_filename = sanitize_filename(id.split('/')[-1])
        audio_filename = os.path.join("audio", f"{sanitized_filename}.mp3")

        # Save recording to a temporary WAV file
        wav_filename = "temp_recording.wav"
        wavio.write(wav_filename, recording, recording_rate, sampwidth=2)

        # Convert the temporary WAV file to an MP3 file with a reduced bitrate
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(audio_filename, format="mp3", bitrate='32k')
        print("audio saved as " + audio_filename + " in " + os.path.abspath(audio_filename))

        # Remove the temporary WAV file
        os.remove(wav_filename)


        # Close the browser window
    except Exception as e:
        print(f"An error occurred: {e}")
        # Rest of the code

    # Close the browser window
    if page is not None and not page.isClosed():
        await browser.close()

    # Close the page
    # await page.close()

async def main():
    # Read the CSV file
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/scripts/data/USMX_scraped_channels_final.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # Create the "audio" subfolder if it doesn't exist
        os.makedirs('audio', exist_ok=True)
        for row in reader:
            url = row['mp3_url']
            id = row['url']
            print(f"Processing URL: {url}")
            await process_url(url, id)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())