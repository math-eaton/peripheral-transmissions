import asyncio
import os
import csv
from pyppeteer import launch

async def record_audio_video_from_page(url):
    global browser
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 720})

    await page.goto(url)
    await asyncio.sleep(3)  # Wait for 3 seconds
    await page.mouse.click(640, 360)  # Click on the center of the viewport
    await asyncio.sleep(3)  # Wait for 3 seconds

    output_filename = f"{os.path.basename(url)}.webm"
    await page.evaluate('''async () => {
        const mimeType = 'video/webm; codecs="vp8, opus"';
        const mediaRecorder = new MediaRecorder(document.querySelector('video, audio').captureStream(), { mimeType });
        const chunks = [];
        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.start();
        await new Promise((resolve) => setTimeout(resolve, 30 * 1000));
        mediaRecorder.stop();
        const blob = new Blob(chunks, { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'output.webm';
        a.click();
    }''')

    await asyncio.sleep(10)  # Wait for 35 seconds to ensure the download is completed
    await page.close()

async def main():
    global browser
    browser = await launch(headless=False)

    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/places_sample.csv', 'r') as csvfile:
        url_reader = csv.reader(csvfile)
        for row in url_reader:
            url = row[0]
            await record_audio_video_from_page(url)

async def cleanup():
    global browser
    if browser:
        await browser.close()

asyncio.run(main())
asyncio.run(cleanup())