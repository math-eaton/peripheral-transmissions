import csv
import os
import requests
from bs4 import BeautifulSoup

def download_and_save_audio(url, output_folder="audio"):
    os.makedirs(output_folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    file_extension = url.split(".")[-1]
    file_name = f"{output_folder}/{url.split('/')[-1]}"
    
    with open(file_name, "wb") as file:
        file.write(response.content)

    return file_name

def find_audio_links(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    audio_links = [link["src"] for link in soup.find_all("source") if link["src"].endswith(".mp3")]

    return audio_links

def main():
    with open("data/places_formatted.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        url_list = [row["url"] for row in csv_reader]

    for url in url_list:
        print(f"Loading URL: {url}")

        audio_links = find_audio_links(url)

        for audio_url in audio_links:
            print(f"Downloading audio: {audio_url}")
            file_name = download_and_save_audio(audio_url)
            print(f"Audio saved as: {file_name}")

if __name__ == "__main__":
    main()
