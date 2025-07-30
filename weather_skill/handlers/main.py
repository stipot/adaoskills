from adaos.sdk import speak, http_get


class WeatherSkill:
    def handle(intent: str, entities: dict):

        api_key = "c36f20a73e34677fe737d20b5387f9d4"
        api_entry_point = "https://api.openweathermap.org/data/2.5/weather"
        default_city = "Moscow"

        city = entities.get("city", default_city)
        params = {"q": city, "appid": api_key, "lang": "ru", "units": "metric"}

        response = http_get(api_entry_point, params)
        if not response or "main" not in response:
            speak(f"Не удалось получить погоду для города {city}.")
            return

        temp = response["main"].get("temp")
        description = response["weather"][0].get("description", "")
        speak(f"Сегодня в городе {city} {description}, температура {temp:.1f} градусов.")
