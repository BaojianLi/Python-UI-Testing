import pytest
from playwright.sync_api import sync_playwright
from page_objects.BookingSearchPage import BookingSearchPage

def test_booking_search():
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    booking_page = BookingSearchPage(page)
    booking_page.goto()
    # booking_page.click_home_promo()
    booking_page.click_destination_combo()
    booking_page.click_los_angeles_button()
    booking_page.click_dates_container()
    booking_page.click_dates_container()
    booking_page.click_date_start_button()
    booking_page.click_date_end_button()
    booking_page.click_occupancy_config()
    booking_page.click_occupancy_two_button()
    booking_page.click_done_button()
    booking_page.click_search_button()
    browser.close()