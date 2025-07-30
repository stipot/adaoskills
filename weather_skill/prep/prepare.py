import json
import datetime
import requests
from pathlib import Path


def run_prep(skill_path: Path):
    log_dir = skill_path / "logs"
    prep_dir = skill_path / "prep"
    log_dir.mkdir(exist_ok=True)
    prep_dir.mkdir(exist_ok=True)

    logs = []
    result = {"status": "failed", "reason": None, "timestamp": datetime.datetime.utcnow().isoformat()}
    resources = {}

    def log(message):
        logs.append(message)
        print(message)

    log("[cyan]Подготовка навыка 'Погода'[/cyan]")

    # 1. Проверка интернета
    try:
        requests.get("https://api.openweathermap.org", timeout=3)
        log("[green]✓ Интернет доступен[/green]")
        resources["internet"] = True
    except:
        resources["internet"] = False
        result["reason"] = "Нет доступа в интернет"
        _finalize(skill_path, logs, result, resources)
        return result

    # 2. Сбор данных
    api_key = input("Введите API-ключ OpenWeather (или пусто для теста): ").strip() or "demo_key"
    city = input("Введите город по умолчанию: ").strip() or "Moscow"

    resources["api_key"] = api_key
    resources["default_city"] = city

    # 3. Проверка API
    entry_point = "https://api.openweathermap.org/data/2.5/weather"
    try:
        resp = requests.get(entry_point, params={"q": city, "appid": api_key, "units": "metric"}, timeout=5)
        if "main" in resp.json():
            log(f"[green]✓ API работает для города {city}[/green]")
            resources["api_entry_point"] = entry_point
            result["status"] = "ok"
        else:
            result["reason"] = "API не вернул погоду"
    except Exception as e:
        result["reason"] = f"Ошибка API: {e}"

    _finalize(skill_path, logs, result, resources)
    return result


def _finalize(skill_path, logs, result, resources):
    # Сохраняем лог
    with open(skill_path / "logs" / "prep.log", "w", encoding="utf-8") as f:
        f.write("\n".join(logs))

    # Сохраняем JSON с результатами
    result["resources"] = resources
    with open(skill_path / "prep" / "prep_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Сохраняем шаблон prompt
    if result["status"] == "ok":
        prompt = f"""
Задача: написать навык "{skill_path.name}".
Результаты подготовки:
{json.dumps(resources, ensure_ascii=False, indent=2)}
"""
        with open(skill_path / "prep" / "prep_prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
