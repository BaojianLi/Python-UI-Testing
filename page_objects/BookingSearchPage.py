from playwright.sync_api import Page, Locator, expect
from config.config import get_environment

BOOKING_URL = get_environment().get("booking_url", "https://www.booking.com/")

class BookingSearchPage:
  def __init__(self, page: Page):
    self.page = page
    self.homePromo: Locator = page.locator('#indexsearch div').filter(has_text='Find deals for any season')
    self.destinationCombo: Locator = page.get_by_role('combobox', name='Where are you going?')
    self.losAngelesButton: Locator = page.get_by_role('button', name='Los Angeles United States')
    self.datesContainer: Locator = page.get_by_test_id('searchbox-dates-container')
    self.dateStartButton: Locator = page.get_by_role('button', name='Fr 25 July')
    self.dateEndButton: Locator = page.get_by_role('button', name='Sa 2 August')
    self.occupancyConfig: Locator = page.get_by_test_id('occupancy-config')
    self.occupancyTwoButton: Locator = page.locator('div').filter(has_text='2').locator('button').first
    self.doneButton: Locator = page.get_by_role('button', name='Done')
    self.searchButton: Locator = page.get_by_role('button', name='Search')

  def goto(self):
    self.page.goto(BOOKING_URL)
    expect(self.page).to_have_url(BOOKING_URL)

  def click_home_promo(self):
    expect(self.homePromo).to_be_visible()
    self.homePromo.click()

  def click_destination_combo(self):
    self.page.locator('input[name="ss"]').fill('Los Angeles')
    self.page.locator('li[id="autocomplete-result-0"]').click()
    expect(self.destinationCombo).to_be_visible()
    expect(self.destinationCombo).to_have_value('Los Angeles, United States')
    self.destinationCombo.click()

  def click_los_angeles_button(self):
    expect(self.losAngelesButton).to_be_visible()
    self.losAngelesButton.click()

  def click_dates_container(self):
    expect(self.datesContainer).to_be_visible()
    expect(self.datesContainer).to_have_attribute('data-testid', 'searchbox-dates-container')
    self.datesContainer.click()

  def click_date_start_button(self):
    expect(self.dateStartButton).to_be_visible()
    expect(self.dateStartButton).to_have_text('25')
    self.dateStartButton.click()

  def click_date_end_button(self):
    expect(self.dateEndButton).to_be_visible()
    expect(self.dateEndButton).to_have_text('2')
    self.dateEndButton.click()

  def click_occupancy_config(self):
    expect(self.occupancyConfig).to_be_visible()
    expect(self.occupancyConfig).to_have_attribute('data-testid', 'occupancy-config')
    self.occupancyConfig.click()

  def click_occupancy_two_button(self):
    expect(self.occupancyTwoButton).to_be_visible()
    self.occupancyTwoButton.click()

  def click_done_button(self):
    expect(self.doneButton).to_be_visible()
    expect(self.doneButton).to_have_text('Done')
    self.doneButton.click()

  def click_search_button(self):
    expect(self.searchButton).to_be_visible()
    expect(self.searchButton).to_have_text('Search')
    self.searchButton.click()
