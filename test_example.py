from playwright.sync_api import sync_playwright, Playwright, TimeoutError as PlaywrightTimeoutError, expect
from time import sleep
from datetime import datetime, timedelta
import logging

def select_flight_dates(page,outbound_date,inbound_date):
    page.locator("xpath=//input[@id='departureDate']").click()
    for flight_date in [outbound_date,inbound_date]:
        while True:
            try:
                expect(page.locator(f"xpath=//td[contains(@aria-label,'{flight_date}')]")).to_be_visible(timeout=1)
                page.locator(f"xpath=//td[contains(@aria-label,'{flight_date}')]").click()
                break
            except:
                page.locator("xpath=//div[@class='DayPickerNavigation_button DayPickerNavigation_button_1 DayPickerNavigation_button__default DayPickerNavigation_button__default_2 DayPickerNavigation_button__horizontal DayPickerNavigation_button__horizontal_3 DayPickerNavigation_button__horizontalDefault DayPickerNavigation_button__horizontalDefault_4 DayPickerNavigation_rightButton__horizontalDefault DayPickerNavigation_rightButton__horizontalDefault_5']").click()
                continue


def check_for_no_flights_available(page,outbound_date, inbound_date):
    try:
        expect(page.get_by_text("There aren't flights available for this date")).to_be_visible()
        logging.info(f"No flights found for outbound: {outbound_date} inbound: {inbound_date}")
        return False
    except AssertionError as e:
        return True


def travel_dates(outbound_date: datetime, travel_span: int):
    # Define the travel dates
    inbound_date = outbound_date + timedelta(days=travel_span)
    return outbound_date.strftime("%B %d, %Y").replace(" 0", " "), inbound_date.strftime("%B %d, %Y").replace(" 0", " ")


def enter_location(page, field_id, location):
    page.locator(
        f"xpath=//input[@id='{field_id}']").press_sequentially(f"{location}")
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')


def search_prices(playwright: Playwright, outbound_date, inbound_date, headless: bool):
    try:
        start_url = "https://www.latamairlines.com/gb/en"
        chrome = playwright.chromium
        browser = chrome.launch(headless=headless)
        page = browser.new_page()
        response=page.goto(start_url)
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

        # Selects departure and return dates
        select_flight_dates(page,outbound_date,inbound_date)
        

        # Clicks Search buttons
        page.locator("xpath=//button[@id='btnSearchCTA']").click()

        # #Sorts by 'Cheaper' flights
        page.locator("xpath=//button[@class='sc-dUWDJJ eSbJeV']").click()
        page.get_by_test_id("PRICE,asc--menuitem__label-content").click()

        available_flights=check_for_no_flights_available(page,outbound_date, inbound_date)
        if available_flights:
            # Selects outbound and inbound flights from list
            for _ in range(2):
                page.get_by_test_id("flight-info-0").click()
                page.get_by_test_id("bundle-detail-0-flight-select").click()
                sleep(2)
            
            # Gets inbound and outbound flight prices
            prices = page.locator("xpath=//span[@class='sc-aXZVg dxSNap latam-typography latam-typography--heading-06 sc-gEvEer fteAEG']").all_text_contents()
            logging.info(f"{prices}, {outbound_date}, {inbound_date}")

        not_successful = False

    except PlaywrightTimeoutError as e:
        logging.info(e)
        not_successful = True
    finally:
        browser.close()
        return not_successful


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting script")

    with sync_playwright() as playwright:
        start_period_date = datetime(2024, 12, 31)
        finish_period_date = datetime(2025, 12, 15)
        travel_span = 15
        while start_period_date < finish_period_date:
            not_successful = True
            while not_successful:
                start_time = datetime.now()
                outbound_date, inbound_date = travel_dates(
                    start_period_date, travel_span=travel_span)
                not_successful = search_prices(
                    playwright, outbound_date=outbound_date, inbound_date=inbound_date, headless=False)
                finish_time = datetime.now()
                logging.info(f"Script duration: {finish_time-start_time}")

            start_period_date += timedelta(days=1)
            

if __name__ == '__main__':
    main()
