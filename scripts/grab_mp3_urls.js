const { chromium } = require('playwright');
const fs = require('fs');
const CsvParser = require('csv-parser');
const { createObjectCsvWriter: CsvWriter } = require('csv-writer');

(async () => {
  const inputCSVPath = '/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/places_formatted.csv';
  const outputCSVPath = '/Users/matthewheaton/Documents/GitHub/peripheral-transmissions/data/mp3_urls.csv';

  const rows = [];

  fs.createReadStream(inputCSVPath)
    .pipe(CsvParser())
    .on('data', (row) => rows.push(row))
    .on('end', async () => {
      const outputData = [['Index', 'URL', 'Channel.mp3']];

      // Iterate through the CSV rows
      for (const row of rows) {
        const url = row.URL;
        console.log(url)

        // Open the browser, navigate to the URL, and click on the center of the webpage
        const browser = await chromium.launch();
        const context = await browser.newContext();
        const page = await context.newPage();

        let channelMP3Url = '';

        // Intercept network requests to find "Channel.mp3" initiator
        await page.route('**/*', async (route, request) => {
          if (request.url().includes('Channel.mp3')) {
            channelMP3Url = request.url();
          }
          route.continue();
        });

        await page.goto(url);
        const [width, height] = await page.evaluate(() => [window.innerWidth, window.innerHeight]);
        await page.mouse.click(width / 2, height / 2);

        // Close the browser and save the data to the output array
        await browser.close();
        outputData.push([outputData.length, url, channelMP3Url]);
      }

      // Write the output data to a new CSV file
      const csvWriter = CsvWriter({
        path: outputCSVPath,
        header: outputData.shift().map((title) => ({ id: title, title })),
      });

      await csvWriter.writeRecords(outputData.map((row) => row.reduce((acc, value, index) => {
        acc[outputData[0][index]] = value;
        return acc;
      }, {})));

      console.log(`Data saved to ${outputCSVPath}`);
    });
})();
