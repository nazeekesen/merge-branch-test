import asyncio
from pyppeteer import launch

async def export_dash_to_pdf():
    browser = await launch()
    page = await browser.newPage()

    # Load your Dash app
    await page.goto('http://127.0.0.1:8050', {'waitUntil': 'networkidle2'})

    # Wait for Plotly to fully render bars (wait for at least one graph SVG node)
    await page.waitForSelector('g.cartesianlayer')

    # Give it a little buffer just in case (helps with animations)
    await asyncio.sleep(2)

    # Export to PDF
    await page.pdf({
        'path': 'dash_report.pdf',
        'format': 'A4',
        'printBackground': True
    })

    print("✅ PDF saved as dash_report.pdf")
    await browser.close()

asyncio.get_event_loop().run_until_complete(export_dash_to_pdf())
