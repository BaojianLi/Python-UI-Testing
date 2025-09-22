from playwright.sync_api import Page, Locator
import re
from util.utils import close_ads

class AccuWeatherDailyPage:
    def __init__(self, page: Page):
        self.page = page
        self.day_cards = page.locator("//div[@class='page-content content-module']//div[@class='daily-wrapper']")
        self.day_date = page.locator("div.page-content.content-module p.module-title")
        self.day_date_link = page.locator("h2.date")

    def get_day_count(self):
        return self.day_cards.count()

    def get_day_date(self):
        return self.day_date.text_content()

    def goto_day_date_page(self, index):
        close_ads(self.page)
        self.day_date_link.nth(index).click()
        self.page.wait_for_timeout(1000)
        close_ads(self.page)

    def get_day_info(self, index: int):
        card = self.day_cards.nth(index)
        day_value = card.locator('h2.date').text_content()
        if day_value:
            day_value = re.sub(r"[\n\t]", '', day_value)
            day_value = re.sub(r"^([A-Za-z]{3})(\d)", r"\1 \2", day_value).strip()
        periods = card.locator('div.precip').all_text_contents()
        periods = [re.sub(r"[\n\t]", '', p).strip() for p in periods]
        temp_h = card.locator('div div.temp span.high').text_content()
        temp_l = card.locator('div div.temp span.low').text_content()
        temp_l = temp_l.replace('/', '').strip() if temp_l else ''
        main_weather = card.locator('div.phrase').text_content()
        real_feel = card.locator('div.left p.panel-item').first.text_content()
        real_feel_s = card.locator('div.left p.panel-item').first.text_content()
        humidity = card.locator('div.left p.panel-item').last.text_content()
        return {
            'dayValue': day_value,
            'periods': periods,
            'tempH': temp_h,
            'tempL': temp_l,
            'mainWeather': main_weather,
            'realFeel': real_feel,
            'realFeelS': real_feel_s,
            'humidity': humidity
        }
