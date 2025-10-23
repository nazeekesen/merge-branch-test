import asyncio
import logging
import requests
from pyppeteer import launch
from pyppeteer.chromium_downloader import download_chromium

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def wait_with_retries(page, selector, max_retries=3, initial_delay=5):
    for attempt in range(max_retries):
        try:
            await page.waitForSelector(selector, {'timeout': 30000})
            return
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying after delay...")
            await asyncio.sleep(initial_delay * (2 ** attempt))
    raise Exception(f"Failed to find selector '{selector}' after {max_retries} retries.")

async def export_dash_to_pdf():
    # Ensure Chromium is downloaded
    logging.info("Checking for Chromium installation...")
    try:
        download_chromium()
        logging.info("Chromium is ready.")
    except Exception as e:
        logging.error(f"Failed to download Chromium: {e}")
        raise

    # Wait for Dash server to be ready
    max_attempts = 20
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://127.0.0.1:8050', timeout=5)
            if response.status_code == 200:
                logging.info("Dash server is ready.")
                break
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1}/{max_attempts}: Dash server not ready yet. Error: {e}")
        await asyncio.sleep(3)
    else:
        raise Exception("Dash server did not become ready in time.")

    # Launch Chromium with CI-friendly arguments
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 1024})

    # Load your Dash app
    await page.goto('http://127.0.0.1:8050', {'waitUntil': 'networkidle2'})

    # Wait for Plotly to render with retries
    await wait_with_retries(page, 'g.cartesianlayer')

    # Alternative/more robust check (use one or both)
    await page.waitForFunction('''() => {
        const elem = document.querySelector('g.cartesianlayer');
        return elem && elem.children.length > 0;
    }''', {'timeout': 60000})

    # Buffer time
    await asyncio.sleep(5)

    # Export to PDF
    await page.pdf({
        'path': 'dash_report.pdf',
        'format': 'A4',
        'printBackground': True
    })
    logging.info("✅ PDF saved as dash_report.pdf")
    await browser.close()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(export_dash_to_pdf())
    except Exception as e:
        logging.error(f"Failed to export PDF: {e}")
        raise
