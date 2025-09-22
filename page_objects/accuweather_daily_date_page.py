from playwright.sync_api import Page, Locator

class AccuWeatherDailyDatePage:
    def __init__(self, page: Page):
        self.page = page
        self.day_date = page.locator("div.page-content.content-module div.subnav-pagination div")
        self.day = page.locator("div.page-content.content-module div.half-day-card.content-module").first
        self.night = page.locator("div.page-content.content-module div.half-day-card.content-module").last
        self.weather = page.locator("div.page-content.content-module div.half-day-card.content-module")

    def goto_daily(self):
        self.page.get_by_role('link', name="DAILY").click()
        self.page.wait_for_timeout(1000)

    def get_day_date(self):
        return self.day_date.text_content()

    def get_day_locator(self) -> Locator:
        return self.day

    def get_night_locator(self) -> Locator:
        return self.night

    def goto_next_day_page(self, index: int):
        self.page.locator('h2.date').nth(index).click()
        self.page.wait_for_timeout(1000)

    def get_next_section_locator(self) -> Locator:
        return self.page.locator('h3 a.quarter-day-cta.spaced-content').first

    def goto_next_section(self):
        self.page.locator('h3 a.quarter-day-cta.spaced-content').first.click()
        self.page.wait_for_timeout(1000)

    def get_day_night_info(self, locator: Locator):
        date_value = locator.locator('span.short-date').text_content()
        if date_value:
            date_value = date_value.replace('\n', '').replace('\t', '').replace("  ", " ")
            import re
            date_value = re.sub(r"^([A-Za-z]{3})(\d)", r"\1 \2", date_value).strip()
        import re
        temp_f_text = locator.locator('div.weather div').text_content()
        temp_f_match = re.search(r'-?\d+', temp_f_text) if temp_f_text else None
        # Fix: use correct regex and handle missing value
        temp_f_match = re.search(r'-?\d+', temp_f_text) if temp_f_text else None
        temp_f = temp_f_match.group() if temp_f_match else ''
        if temp_f:
            temp_f_num = int(temp_f)
            temp_c_num = round((temp_f_num - 32) * 5 / 9)
            temp_c = f"{temp_c_num}°"
        else:
            temp_c = ''
        main_weather = locator.locator('div.phrase').text_content()
        real_feel = locator.locator('div.real-feel div').first.text_content()
        if real_feel:
            real_feel = real_feel.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').strip()
        return {
            'dateValue': date_value,
            'tempF': temp_f,
            'tempC': temp_c,
            'mainWeather': main_weather,
            'realFeel': real_feel
        }

    def get_weather_info(self):
        weather = self.weather
        period = weather.locator('h2.title').first.text_content()
        date_value = weather.locator('span.short-date').text_content()
        if date_value:
            date_value = date_value.replace('\n', '').replace('\t', '').replace("  ", " ")
            import re
            date_value = re.sub(r"^([A-Za-z]{3})(\d)", r"\1 \2", date_value).strip()
        temp_f_text = weather.locator('div.weather div').text_content()
        temp_f = temp_f_text.replace('\n', '').replace('\t', '').replace('°', '').strip() if temp_f_text else ''
        temp_f_num = int(temp_f) if temp_f else 0
        temp_c_num = round((temp_f_num - 32) * 5 / 9)
        temp_c = f"{temp_c_num}°"
        main_weather = weather.locator('div.phrase').text_content()
        real_feel = weather.locator("//div[contains(text(),'RealFeel®')]").text_content()
        if real_feel:
            real_feel = real_feel.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').strip()
        humidity = weather.locator('div.left p.panel-item').nth(2).text_content()
        if humidity:
            humidity = humidity.replace('Humidity', '').strip()
        return {
            'period': period,
            'dateValue': date_value,
            'tempF': temp_f,
            'tempC': temp_c,
            'mainWeather': main_weather,
            'realFeel': real_feel,
            'humidity': humidity
        }
