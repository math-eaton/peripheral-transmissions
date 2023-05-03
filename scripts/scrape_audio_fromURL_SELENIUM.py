import os
import re
import csv
import time
import numpy as np
import sounddevice as sd
import wavio
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random

def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def process_url(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Launch the browser
    browser = webdriver.Chrome(options=chrome_options)

    try:
        # Disable the 'navigator.webdriver' attribute
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Open the webpage
        browser.get(url)

        # Set the viewport size
        browser.set_window_size(800, 600)

        # Wait 15 seconds
        time.sleep(15)

        # Scroll down the page slightly
        body = browser.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.DOWN)

        # Randomize wait times and actions
        time.sleep(random.uniform(1, 3))
        random_scroll = random.randint(1, 10)
        for _ in range(random_scroll):
            body.send_keys(Keys.DOWN)
            time.sleep(random.uniform(0.5, 2))

        # Click and drag in the center of the webpage
        action = ActionChains(browser)
        action.move_by_offset(640, 360)
        action.click_and_hold()
        action.move_by_offset(0, -1)
        action.release()
        action.perform()

        # Wait 5 seconds
        time.sleep(5)

        # Record 10 seconds of audio from the computer's main output
        recording_duration = 10  # seconds
        recording_rate = 44100  # Hz
        recording_channels = 1  # Set number of channels to 1 (mono)
        output_device_index = 6

        recording = sd.rec(int(recording_duration * recording_rate), samplerate=recording_rate, channels=recording_channels, dtype='int16', device=output_device_index)
        sd.wait()

        # Save the audio output file with the name of its associated URL in the "audio" subfolder
        sanitized_filename = sanitize_filename(url.split('/')[-1])
        audio_filename = f"audio/{sanitized_filename}.mp3"
        print(audio_filename)

        # Save recording to a temporary WAV file
        wav_filename = "temp_recording.wav"
        recording = np.frombuffer(b''.join(frames), dtype=np.int16)
        wavio.write(wav_filename, recording, recording_rate, sampwidth=2)
        print(wav_filename)

        # Load the temporary WAV file with pydub and save as mp3
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(audio_filename, format="mp3")

        # Remove the temporary WAV file
        os.remove(wav_filename)

        # Close the browser window
        browser.quit()
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        browser.quit()

def main():
    # Read the CSV file
    with open('/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/csv/places_sample.csv', 'r') as f:
        reader = csv.DictReader(f)
        urls = [row['url'] for row in reader]

    # Create the "audio" subfolder if it doesn't exist
    os.makedirs('audio', exist_ok=True)

    # Process each URL
    for url in urls:
        process_url(url)

if __name__ == "__main__":
    main()
