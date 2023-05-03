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

async def process_url(url):
    # Launch the browser
    browser = await launch(headless=False)

    try:
        # Open the webpage
        page = await browser.newPage()
        await page.setViewport({'width': 800, 'height': 600})
        await page.goto(url)

        # Wait 3 seconds
        await asyncio.sleep(5)

        # Click and drag in the center of the webpage
        await page.mouse.move(400, 300)
        await page.mouse.down()
        await page.mouse.move(400, 299)  # Move one pixel in the -y direction
        await page.mouse.up()

        # Wait 3 seconds
        await asyncio.sleep(5)

        # Record 10 seconds of audio from the computer's main output
        recording_duration = 5  # seconds
        recording_rate = 44100  # Hz
        recording_channels = 1  # Set number of channels to 1 (mono)
        recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels, dtype='int16')
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
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_sample.csv', 'r') as f:
        reader = csv.DictReader(f)
        urls = [row['url'] for row in reader]

    # Create the "audio" subfolder if it doesn't exist
    os.makedirs('audio', exist_ok=True)

    # Process each URL
    for url in urls:
        await process_url(url)

asyncio.run(main())
