const { launch, getStream } = require('puppeteer-stream')
const fs = require('fs')
import Puppeteer from 'puppeteer';
const browser = await Puppeteer.launch(...);
// import * as puppeteer from "puppeteer"


// node arguments are present from the third position going forward.
const args = process.argv.slice(2)
const file = fs.createWriteStream(`./audio/${args[0]}.mp4`)

async function puppeteerStream() {
  const browser = await launch()

  const page = await browser.newPage()
  await page.goto('https://radio.garden/visit/anza-ca/6kWJDkw0')
  await page.waitForSelector('._control_oyndo_11._modPlay_oyndo_53')
  element = await page.querySelector('._control_oyndo_11._modPlay_oyndo_53')
  await element.click()
  console.log("powering on")

  // records audio and video
  const stream = await getStream(page, { audio: true, video: false })
  stream.pipe(file)

  await page.waitForTimeout(8000)
  await stream.destroy()
  await browser.close()
  file.close()
}

puppeteerStream()
