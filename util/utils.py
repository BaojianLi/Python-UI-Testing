import os
import csv
import json
from datetime import datetime
from page_objects.accuweather_daily_date_page import AccuWeatherDailyDatePage

def load_zipcodes():
    zipcodes = []
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'test_data', 'test_data_zip_codes.csv')
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            zipcodes.append(row['zip_code'])
    return zipcodes

def fahrenheit_to_celsius(f: int) -> int:
    return round((f - 32) * 5 / 9)

def save_to_file(file_path: str, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def validate_temp_f(temp_f: str, temp_c: str) -> bool:
    try:
        temp_f_num = int(''.join([c for c in (temp_f or '0') if c.isdigit() or c == '-']))
        temp_c_num = int(''.join([c for c in (temp_c or '0') if c.isdigit() or c == '-']))
        expected_c = fahrenheit_to_celsius(temp_f_num)
        return temp_c_num == expected_c
    except Exception:
        return False

def get_weather_info_from_card(local_date_page: AccuWeatherDailyDatePage):
    info = local_date_page.get_weather_info()
    valid = validate_temp_f(info.get('tempF'), info.get('tempC'))
    info['valid'] = valid
    return info

def get_day_night_info_from_card(local_date_page: AccuWeatherDailyDatePage, locator):
    info = local_date_page.get_day_night_info(locator)
    valid = validate_temp_f(info.get('tempF'), info.get('tempC'))
    info['valid'] = valid
    return info

def get_current_datetime() -> str:
    now = datetime.now()
    return now.strftime('%Y%m%d%H%M%S')

def close_ads(page, retries=5, wait_ms=700):
    print("Attempting to close ads...")
    iframe_selectors = [
        'iframe[id="google_ads_iframe_/6581/web/us/interstitial/weather/local_home_0"]',
        'iframe[id="google_ads_iframe_/6581/web/us/interstitial/weather/extended_0"]',
        'iframe[name="google_ads_iframe_/6581/web/us/interstitial/admin/search_0"]'
    ]
    for attempt in range(retries):
        closed = False
        try:
            found_iframe = False
            for iframe_sel in iframe_selectors:
                iframe = page.query_selector(iframe_sel)
                if iframe:
                    found_iframe = True
                    frame = iframe.content_frame()
                    if frame:
                        for sel in [
                            "button:has-text('×')",
                            "button:has-text('Close')",
                            "button:has-text('Close ad')",
                            "[aria-label='Close']",
                            "#dismiss-button",
                            "svg",
                            "span:has-text('×')",
                            "div:has-text('×')"
                        ]:
                            btns = frame.locator(sel)
                            for i in range(btns.count()):
                                btn = btns.nth(i)
                                if btn.is_visible(timeout=1000):
                                    print(f"Clicking ad close button: {sel} in {iframe_sel}")
                                    btn.click()
                                    page.wait_for_timeout(500)
                                    closed = True
                                    break
                        if closed:
                            break
                if closed:
                    break
            if not found_iframe:
                print("Target ad iframes not found, skipping ad close.")
                break
            if closed:
                return
        except Exception as e:
            print(f"No ads to close or error: {e}")
            pass
        # Try overlay close buttons in main page
        try:
            for sel in [
                "button:has-text('×')",
                "button:has-text('Close')",
                "button:has-text('Close ad')",
                "[aria-label='Close']",
                "#dismiss-button",
                "svg",
                "span:has-text('×')",
                "div:has-text('×')"
            ]:
                btns = page.locator(sel)
                for i in range(btns.count()):
                    btn = btns.nth(i)
                    if btn.is_visible(timeout=1000):
                        print(f"Clicking overlay close button: {sel}")
                        btn.click()
                        page.wait_for_timeout(500)
                        closed = True
                        break
                if closed:
                    break
            if closed:
                return
        except Exception as e:
            print(f"No overlay ads to close or error: {e}")
            pass
        page.wait_for_timeout(wait_ms)
