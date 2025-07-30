import requests


class WeatherSkill:
    def handle_intent(self, intent: str, slots: dict) -> str:
        if intent == "get_weather":
            city = slots.get("city", "Moscow")
            data = self._fetch_weather(city)
            return f"{data['city']}: {data['temp']}°C, {data['description']}"
        return "Неизвестный интент"

    def _fetch_weather(self, city: str) -> dict:
        """Реальный вызов API (позже можно подменить для оффлайн)"""
        API_KEY = "<тут вставим ключ>"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={API_KEY}"
        resp = requests.get(url, timeout=5)
        r = resp.json()
        return {"city": r["name"], "temp": int(r["main"]["temp"]), "description": r["weather"][0]["description"]}
