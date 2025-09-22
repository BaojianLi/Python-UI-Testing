
from playwright.sync_api import Page
from util.utils import close_ads
from config.config import get_environment

class AccuWeatherHomePage:
    def __init__(self, page: Page):
        self.page = page
        self.env = get_environment()
        self.weather_url = self.env["weather_url"]

    def goto(self):
        self.page.goto(self.weather_url, wait_until='domcontentloaded')

    def search_location(self, zip_code: str):
        self.page.get_by_role('textbox', name='search').fill(zip_code)
        self.page.wait_for_timeout(1000)
        self.page.locator("//div[@class='featured-locations']//a[1]").click()
        self.page.wait_for_timeout(1000)

    def goto_daily(self):
        close_ads(self.page)
        self.page.locator("//div[@class='page-subnav']//a[@data-qa='daily']").click()
        self.page.wait_for_timeout(1000)
        close_ads(self.page)
