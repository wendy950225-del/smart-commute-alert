# 智慧通勤風險通知系統

GitHub Actions 於台灣時間每週一至週五上午 7:00 自動執行，也能手動執行。程式取得桃園龜山今日最高溫、最高降雨機率與目前 AQI，再透過 Telegram Bot 傳送通勤建議。

## 判斷規則

- 最高降雨機率 ≥ 60%：提醒攜帶雨傘。
- 今日最高溫 ≥ 33°C：提醒防曬與補充水分。
- AQI ≥ 100：提醒配戴口罩。
- 三項都未達門檻：顯示適合外出通勤。
- 多項超標時，會同時顯示多項提醒。

## 檔案

- `commute_alert.py`：主程式
- `requirements.txt`：Python 套件
- `.github/workflows/commute-alert.yml`：自動排程
- `tests/test_commute_alert.py`：條件判斷測試

## GitHub Secrets

到 Repository 的 `Settings` → `Secrets and variables` → `Actions` → `New repository secret`，建立：

1. `TELEGRAM_BOT_TOKEN`
2. `TELEGRAM_CHAT_ID`

Token 與 Chat ID 不可寫入程式或上傳到 Repository。

## 手動測試

到 Repository 的 `Actions` → `Smart Commute Alert` → `Run workflow` → `Run workflow`。

## 本機測試條件判斷

```bash
python -m unittest discover -s tests -v
```

資料來源：[Open-Meteo](https://open-meteo.com/) 與 CAMS。
