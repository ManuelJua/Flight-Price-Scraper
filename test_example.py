from playwright.sync_api import sync_playwright, Playwright, TimeoutError as PlaywrightTimeoutError
from time import sleep


def run(playwright: Playwright):
    start_url = "https://www.latamairlines.com/gb/en"
    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url)

    #Rejects cookies
    page.get_by_test_id("cookies-politics-reject-button--button").click()

    #Clicks on Origin field and types info
    page.locator("xpath=//input[@id='txtInputOrigin_field']").click()
    page.locator("xpath=//input[@id='txtInputOrigin_field']").press_sequentially(
        'London, LON - United Kingdom')
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')

    #Clicks on Destination field and types info
    page.locator(
        "xpath=//input[@id='txtInputDestination_field']").press_sequentially('Cordoba, COR - Argentina')
    page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')

    #Clicks Search button
    page.locator("xpath=//input[@id='departureDate']").click()

    #Selects departure and return dates
    page.locator("xpath=//td[@class='CalendarDay CalendarDay_1 CalendarDay__default CalendarDay__default_2' and @aria-label='Choose Thursday, September 12, 2024 as your departure date. It’s available.']").click()
    page.locator("xpath=//td[@class='CalendarDay CalendarDay_1 CalendarDay__default CalendarDay__default_2' and @aria-label='Choose Thursday, September 26, 2024 as your return flight date. It’s available.']").click()
    
    #Sorts by 'Cheaper' flights
    page.locator("xpath=//button[@id='btnSearchCTA']").click()
    page.locator("xpath=//button[@class='sc-dUWDJJ eSbJeV']").click()

    #Selects outbound flights from list
    page.get_by_test_id("PRICE,asc--menuitem__label-content").click()
    page.get_by_test_id("flight-info-0").click()
    page.get_by_test_id("bundle-detail-1-flight-select").click()

    #sleep is necesary to allow the next step
    sleep(2) 

    #Selects inbound flights from list
    page.get_by_test_id("flight-info-0").click()
    page.get_by_test_id("bundle-detail-1-flight-select").click()
    sleep(1200)

with sync_playwright() as playwright:
    not_succesfull = True
    while not_succesfull:
        try:
            run(playwright)
            not_succesfull = False
        except PlaywrightTimeoutError as e:
            print(e)
            continue
