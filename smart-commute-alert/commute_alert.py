import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


LOCATION_NAME = "桃園龜山"
LATITUDE = 24.9925
LONGITUDE = 121.3378
TIMEZONE = "Asia/Taipei"

RAIN_THRESHOLD = 60
TEMPERATURE_THRESHOLD = 33
AQI_THRESHOLD = 100
REQUEST_TIMEOUT = 20

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def get_required_env(name: str) -> str:
    """讀取必要的環境變數；若未設定就提供清楚錯誤。"""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少必要環境變數：{name}")
    return value


def get_json(url: str, params: dict) -> dict:
    """呼叫 API 並檢查 HTTP 與 JSON 回應。"""
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(data.get("reason", "API 回傳未知錯誤"))
    return data


def get_weather() -> tuple[str, float, int]:
    """取得今天日期、最高溫與最高降雨機率。"""
    data = get_json(
        WEATHER_API_URL,
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": "temperature_2m_max,precipitation_probability_max",
            "timezone": TIMEZONE,
            "forecast_days": 1,
        },
    )

    daily = data.get("daily", {})
    try:
        date = daily["time"][0]
        max_temperature = daily["temperature_2m_max"][0]
        max_rain_probability = daily["precipitation_probability_max"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("天氣 API 缺少必要資料") from exc

    if max_temperature is None or max_rain_probability is None:
        raise RuntimeError("天氣 API 回傳空值")
    return date, float(max_temperature), int(round(max_rain_probability))


def get_aqi() -> int:
    """取得目前的美國制綜合 AQI。"""
    data = get_json(
        AIR_QUALITY_API_URL,
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "us_aqi",
            "timezone": TIMEZONE,
        },
    )

    aqi = data.get("current", {}).get("us_aqi")
    if aqi is None:
        raise RuntimeError("空氣品質 API 缺少 AQI 資料")
    return int(round(aqi))


def build_advice(max_temperature: float, rain_probability: int, aqi: int) -> list[str]:
    """依門檻建立一項或多項通勤建議。"""
    advice = []
    if rain_probability >= RAIN_THRESHOLD:
        advice.append("☔ 降雨機率偏高，請攜帶雨傘。")
    if max_temperature >= TEMPERATURE_THRESHOLD:
        advice.append("☀️ 天氣炎熱，請做好防曬並補充水分。")
    if aqi >= AQI_THRESHOLD:
        advice.append("😷 空氣品質不佳，建議配戴口罩。")
    if not advice:
        advice.append("✅ 各項條件正常，適合外出通勤。")
    return advice


def build_message(date: str, max_temperature: float, rain_probability: int, aqi: int) -> str:
    advice = build_advice(max_temperature, rain_probability, aqi)
    update_time = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
    return "\n".join(
        [
            "🚦 智慧通勤風險通知",
            f"📍 地點：{LOCATION_NAME}",
            f"📅 預報日期：{date}",
            "",
            f"🌡️ 今日最高溫：{max_temperature:.1f}°C",
            f"🌧️ 今日最高降雨機率：{rain_probability}%",
            f"🌫️ 目前 AQI：{aqi}",
            "",
            "📣 通勤建議：",
            *advice,
            "",
            f"🕒 資料更新：{update_time}",
            "資料來源：Open-Meteo／CAMS",
        ]
    )


def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": message},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram 傳送失敗：{result.get('description', '未知錯誤')}")


def main() -> None:
    token = get_required_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_required_env("TELEGRAM_CHAT_ID")

    date, max_temperature, rain_probability = get_weather()
    aqi = get_aqi()
    message = build_message(date, max_temperature, rain_probability, aqi)
    print(message)
    send_telegram_message(token, chat_id, message)
    print("Telegram 通知已成功傳送。")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"執行失敗：{exc}", file=sys.stderr)
        sys.exit(1)
