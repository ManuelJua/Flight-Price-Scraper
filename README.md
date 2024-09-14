# Flight Price Scraper

This Python script scrapes flight prices from the LATAM Airlines website for specific travel dates. It utilizes the Playwright library to automate browser interactions. Here's a brief overview of its functionality:

1. **Data Check:**
   - The script first checks if flight data already exists in a CSV file named `flights_info.csv`. This prevents duplicate entries.

2. **Browser Interaction:**
   - It launches a headless Chromium browser.
   - Navigates to the LATAM Airlines website.
   - Rejects cookies (if prompted).
   - Enters the origin (London, UK) and destination (Cordoba, Argentina).

3. **Flight Selection:**
   - The script sorts available flights by price (cheapest first).
   - It selects two flights (outbound and inbound) for further details.

4. **Price Extraction:**
   - The outbound and inbound flight prices are retrieved from the page.

5. **CSV Update:**
   - If new data is found, the script appends flight information (dates and prices) to the CSV file.
   - If data already exists, it skips the entry.

6. **Disclaimer:**
   - **Important:** This script is intended for educational purposes only. It may not comply with webpage scraping policies or terms of use. Use it responsibly and respect website guidelines.

Feel free to customize the script parameters (such as origin, destination, or other settings) as needed. Remember to adhere to website terms and conditions when scraping data.

Happy learning and safe travels! ✈️🌎

