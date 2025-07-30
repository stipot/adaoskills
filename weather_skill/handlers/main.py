class WeatherSkill:
    def handle_intent(self, intent: str, slots: dict) -> str:
        if intent == "get_weather":
            return "Погода на сегодня: 20°C, ясно (заглушка)"
        return "Неизвестный интент"
