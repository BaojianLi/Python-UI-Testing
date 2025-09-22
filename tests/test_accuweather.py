import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from playwright.sync_api import sync_playwright
from page_objects.accuweather_home_page import AccuWeatherHomePage
from page_objects.accuweather_daily_page import AccuWeatherDailyPage
from page_objects.accuweather_daily_date_page import AccuWeatherDailyDatePage

from util.utils import get_weather_info_from_card, get_day_night_info_from_card
from util.utils import save_to_file, get_current_datetime
from util.utils import load_zipcodes

@pytest.mark.parametrize("zipcode", load_zipcodes())
@pytest.mark.timeout(600)
def test_retrieve_and_validate_daily_weather_information(zipcode: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        home = AccuWeatherHomePage(page)
        daily = AccuWeatherDailyPage(page)
        local_date_page = AccuWeatherDailyDatePage(page)

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        datetime_str = get_current_datetime()
        data_file = os.path.join(output_dir, f"accuweather-data-{zipcode}-{datetime_str}.json")
        summary_file = os.path.join(output_dir, f"accuweather-summary-{zipcode}-{datetime_str}.json")

        home.goto()
        home.search_location(zipcode)
        home.goto_daily()

        date_periods = daily.get_day_date()
        count = daily.get_day_count()
        results = []
        
        print(date_periods)
        print(count)

        for i in range(30):
            home.goto_daily()
            daily.goto_day_date_page(i)

            day_date = local_date_page.get_day_date()
            print(f"Day {i + 1} Date: {day_date}")

            day_locator = local_date_page.get_day_locator()
            day_info = get_day_night_info_from_card(local_date_page, day_locator)

            night_locator = local_date_page.get_night_locator()
            night_info = get_day_night_info_from_card(local_date_page, night_locator)

            info_m = info_a = info_e = info_n = None
            next_section_locator = local_date_page.get_next_section_locator()
            if next_section_locator.is_visible():
                local_date_page.goto_next_section()
                info_m = get_weather_info_from_card(local_date_page)
                local_date_page.goto_next_section()
                info_a = get_weather_info_from_card(local_date_page)
                local_date_page.goto_next_section()
                info_e = get_weather_info_from_card(local_date_page)
                local_date_page.goto_next_section()
                info_n = get_weather_info_from_card(local_date_page)

            results.append({
                "dayDate": day_date,
                "day": day_info,
                "night": night_info,
                "morning": info_m,
                "afternoon": info_a,
                "evening": info_e,
                "overNight": info_n
            })

        save_to_file(data_file, results)

        period_keys = ['day', 'night', 'morning', 'afternoon', 'evening', 'overNight']
        valid_temperature_conversions = 0
        invalid_temperature_conversions = 0

        period_stats = {key: {"tempFSum": 0, "tempFCount": 0, "tempCSum": 0, "tempCCount": 0} for key in period_keys}

        for r in results:
            for key in period_keys:
                period = r.get(key)
                if period and isinstance(period.get("valid"), bool):
                    if period["valid"]:
                        valid_temperature_conversions += 1
                    else:
                        invalid_temperature_conversions += 1
                if period and period.get("tempF"):
                    try:
                        f = int(''.join([c for c in str(period["tempF"]) if c.isdigit() or c == '-']))
                        period_stats[key]["tempFSum"] += f
                        period_stats[key]["tempFCount"] += 1
                    except Exception:
                        pass
                if period and period.get("tempC"):
                    try:
                        c = int(''.join([c for c in str(period["tempC"]) if c.isdigit() or c == '-']))
                        period_stats[key]["tempCSum"] += c
                        period_stats[key]["tempCCount"] += 1
                    except Exception:
                        pass

        average_temps = {}
        for key in period_keys:
            average_temps[key] = {
                "averageTempF": round(period_stats[key]["tempFSum"] / period_stats[key]["tempFCount"], 2) if period_stats[key]["tempFCount"] else None,
                "averageTempC": round(period_stats[key]["tempCSum"] / period_stats[key]["tempCCount"], 2) if period_stats[key]["tempCCount"] else None
            }

        summary = {
            "totalDays": len(results),
            "totalPeriods": len(results) * len(period_keys),
            "validTemperatureConversions": valid_temperature_conversions,
            "invalidTemperatureConversions": invalid_temperature_conversions,
            "averageTemps": {k: average_temps[k] for k in period_keys}
        }
        save_to_file(summary_file, summary)
        assert len(results) > 0
        browser.close()

if __name__ == "__main__":
    pytest.main(["-s", "tests"])
