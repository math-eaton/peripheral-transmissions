import asyncio
import csv
from pyppeteer import launch
from pydub import AudioSegment
import sounddevice as sd
import os

async def main():
    # Read the CSV file
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_sample.csv', 'r') as f:
        reader = csv.DictReader(f)
        urls = [row['url'] for row in reader]

    # Launch the browser
    browser = await launch(headless=False)
    for url in urls:
        try:
            # Open the webpage
            page = await browser.newPage()
            await page.setViewport({'width': 800, 'height': 600})
            await page.goto(url)

            # Wait 5 seconds
            await asyncio.sleep(5)

            # Click and drag in the center of the webpage
            await page.mouse.move(400, 300)
            await page.mouse.down()
            await page.mouse.move(400, 295)  # Move 5 pixel in the -y direction
            await page.mouse.up()

            # Wait 3 seconds
            await asyncio.sleep(5)

            # Record 10 seconds of audio from the computer's main output
            recording_duration = 10  # seconds
            recording_rate = 44100  # Hz
            recording_channels = 2
            recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels)
            sd.wait()

            # Save the audio output file with the name of its associated URL
            audio_filename = f"{url.split('/')[-1]}.mp3"
            audio = AudioSegment.from_numpy_array(recording, sample_width=2, channels=recording_channels, frame_rate=recording_rate)
            audio.export(audio_filename, format="mp3")

            # Close the browser window
            await page.close()
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            await page.close()

    # Close the browser
    await browser.close()

asyncio.run(main())
