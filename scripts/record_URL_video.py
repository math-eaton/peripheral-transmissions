import asyncio
import os
import csv
from pyppeteer import launch
import sounddevice as sd
import numpy as np

browser = None

async def record_audio_from_page(url):
    global browser
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 720})

    await page.goto(url)
    await asyncio.sleep(3)  # Wait for 5 seconds
    await page.mouse.click(640, 360)  # Click on the center of the viewport
    await asyncio.sleep(3)  # Wait for 5 seconds

    duration = 5  # seconds
    sampling_rate = 44100
    audio_data = np.empty((duration * sampling_rate,), dtype=np.float32)

    with sd.InputStream(callback=lambda indata, frames, time, status: audio_data.put(indata), samplerate=sampling_rate, channels=1):
        await asyncio.sleep(duration)  # Wait for 30 seconds

    output_filename = f"{os.path.basename(url)}.wav"
    sd.write_wav(output_filename, audio_data, sampling_rate)

    await page.close()

async def main():
    global browser
    browser = await launch(headless=False)

    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/places_sample.csv', 'r') as csvfile:
        url_reader = csv.reader(csvfile)
        for row in url_reader:
            url = row[0]
            await record_audio_from_page(url)

async def cleanup():
    global browser
    if browser:
        await browser.close()

tasks = [main(), cleanup()]
asyncio.run(asyncio.gather(*tasks))
