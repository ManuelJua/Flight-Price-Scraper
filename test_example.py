from playwright.sync_api import sync_playwright, Playwright, TimeoutError as PlaywrightTimeoutError, expect
from time import sleep
from datetime import datetime, timedelta
import logging
import pandas as pd

# Checks if flight data already exists in the CSV file


def data_already_exists(outbound_date, inbound_date):
    df = pd.read_csv('flights_info.csv')
    existent_data = df[(df['outbound_date'] == outbound_date)
                       & (df['inbound_date'] == inbound_date)]
    if len(existent_data) > 0:
        return True
    else:
        return False

# Checks if flights available on these dates
def check_for_flights(page,outbound_date,inbound_date):
    try:
        sleep(5)
        expect(page.locator(
            "//html/body/div[1]/div[1]/main/div/div/div[1]/img")).to_be_hidden(timeout=10)
        logging.info(f"No available flights for dates {outbound_date} and {inbound_date}")
        return False
    except Exception as e:
        logging.info("Flights available")
        return True
    

# Selects flights on the page
def select_flights(page,outbound_date,inbound_date):
    # available_flights = check_for_flights(page,outbound_date,inbound_date)
    # if available_flights:
    # Sorts by 'Cheaper' flights
    try:
        page.get_by_test_id("sort-by-dropdown-dropdown-select").click()
        page.get_by_test_id("PRICE,asc--menuitem__label-content").click()

        #Select flight time
        for _ in range(2):
            page.get_by_test_id("flight-info-0").click()
            page.get_by_test_id("bundle-detail-0-flight-select").click()
            sleep(2)
        return True
    except Exception as e:
        logging.info(e)
        return False

# Determines whether to run the browser in headless mode based on the number of tries


def check_number_of_tries(try_count):
    if try_count >= 4:
        headless = False
    else:
        headless = True
    return headless

# Writes flight information to a CSV file


def info_to_csv(new_flight_info):
    try:
        flights_df = pd.read_csv('flights_info.csv')
        updated_flights_df = pd.concat(
            [flights_df, pd.DataFrame(new_flight_info)])
        logging.info(updated_flights_df)
        updated_flights_df.to_csv('flights_info.csv', index=False)
        return updated_flights_df
    except FileNotFoundError as e:
        print(e)
        flights_df = pd.DataFrame(new_flight_info)
        flights_df.to_csv('flights_info.csv', index=False)
        logging.info(flights_df)
        return flights_df

# Selects flight dates on the page


def select_flight_dates(page, outbound_date, inbound_date):
    page.locator("xpath=//input[@id='departureDate']").click()
    for flight_date in [outbound_date, inbound_date]:
        while True:
            try:
                expect(page.locator(
                    f"xpath=//td[contains(@aria-label,'{flight_date}')]")).to_be_visible(timeout=1)
                page.locator(
                    f"xpath=//td[contains(@aria-label,'{flight_date}')]").click()
                break
            except:
                page.locator("xpath=//div[@class='DayPickerNavigation_button DayPickerNavigation_button_1 DayPickerNavigation_button__default DayPickerNavigation_button__default_2 DayPickerNavigation_button__horizontal DayPickerNavigation_button__horizontal_3 DayPickerNavigation_button__horizontalDefault DayPickerNavigation_button__horizontalDefault_4 DayPickerNavigation_rightButton__horizontalDefault DayPickerNavigation_rightButton__horizontalDefault_5']").click()
                continue


# Calculates inbound travel date based on outbound date and travel span
def travel_dates(outbound_date: datetime, travel_span: int):
    inbound_date = outbound_date + timedelta(days=travel_span)
    return outbound_date.strftime("%B %d, %Y").replace(" 0", " "), inbound_date.strftime("%B %d, %Y").replace(" 0", " ")


# Enters location information on the page
def enter_location(page, field_id, location):
    page.locator(
        f"xpath=//input[@id='{field_id}']").press_sequentially(f"{location}")
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')


# Searches for flight prices
def search_prices(playwright: Playwright, outbound_date, inbound_date, headless: bool):
    logging.info(f"Looking prices for dates {outbound_date} and {inbound_date}")
    try:
        start_url = "https://www.latamairlines.com/gb/en"
        chrome = playwright.chromium
        browser = chrome.launch(headless=headless)
        page = browser.new_page()
        response = page.goto(start_url)
        assert response.ok

        # Rejects cookies
        page.get_by_test_id("cookies-politics-reject-button--button").click()

        # Clicks on Origin field and types info
        page.locator("xpath=//input[@id='txtInputOrigin_field']").click()
        enter_location(page, 'txtInputOrigin_field',
                       'London, LON - United Kingdom')
        # Clicks on Destination field and types info
        enter_location(page, 'txtInputDestination_field',
                       'Cordoba, COR - Argentina')

        # Selects departure and return dates (not shown in snippet)

        # Selects departure and return flights
        select_flight_dates(page, outbound_date, inbound_date)

        # Clicks Search buttons
        page.locator("xpath=//button[@id='btnSearchCTA']").click()

        # Selects outbound and inbound flights from list
        flights_found=select_flights(page,outbound_date=outbound_date,inbound_date=inbound_date)
        
        if flights_found:
        # Gets inbound and outbound flight prices
            outbound_price, inbound_price = page.locator(
                "xpath=//span[@class='sc-aXZVg dxSNap latam-typography latam-typography--heading-06 sc-gEvEer fteAEG']").all_text_contents()
            new_flights_info = {
                'outbound_date': [outbound_date],
                'inbound_date': [inbound_date],
                'outbound_price': [outbound_price],
                'inbound_price': [inbound_price]
            }
            info_to_csv(new_flight_info=new_flights_info)
            logging.info(
                f"outbound price: {outbound_price}, outbound date: {outbound_date}")
            logging.info(
                f"inbound price: {inbound_price}, inbound date: {inbound_date}")

    except PlaywrightTimeoutError as e:
        logging.info(e)

    finally:
        browser.close()


def main():
    # Set up logging to display INFO-level messages
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting script")

    # Initialize Playwright
    with sync_playwright() as playwright:
        # Define a list of travel spans (number of days)
        travel_span_days = range(22,12,-1)

        for travel_span in travel_span_days:
            # Calculate start and finish dates based on today's date and booking availability
            start_period_date = datetime.today().date()+timedelta(days=1)
            finish_period_date = datetime.today().date() + timedelta(days=329 - travel_span - 1)

            while start_period_date < finish_period_date:
                start_time = datetime.now()
                # Calculate outbound and inbound travel dates
                outbound_date, inbound_date = travel_dates(
                    start_period_date, travel_span=travel_span)
                
                if not data_already_exists(outbound_date=outbound_date, inbound_date=inbound_date):
                    # Search for flight prices
                    search_prices(
                        playwright, outbound_date=outbound_date, inbound_date=inbound_date, headless=True)
                    finish_time = datetime.now()
                    logging.info(
                        f"Script duration: {finish_time - start_time}")
                else:
                    logging.info(
                        f"Data for dates: {outbound_date} and {inbound_date} already exists")
                    not_successful = False

                start_period_date += timedelta(days=1)


if __name__ == '__main__':
    main()
