import requests


def run_prep():
    print("[cyan]Подготовка к разработке навыка 'Погода'[/cyan]")

    # 1. Проверка доступа в интернет
    try:
        requests.get("https://api.openweathermap.org", timeout=3)
        print("[green]✓ Интернет доступен[/green]")
    except:
        print("[red]✗ Нет доступа в интернет[/red]")
        return

    # 2. Проверка API-ключа
    api_key = input("Введите API-ключ OpenWeather (или пусто для теста): ").strip() or "demo_key"
    city = input("Введите город по умолчанию: ").strip() or "Moscow"

    try:
        resp = requests.get(f"https://api.openweathermap.org/data/2.5/weather", params={"q": city, "appid": api_key, "units": "metric", "lang": "ru"}, timeout=5)
        data = resp.json()
        if "main" in data:
            print(f"[green]✓ API работает. Температура в {city}: {data['main']['temp']}°C[/green]")
        else:
            print(f"[yellow]API вернул ошибку: {data}[/yellow]")
    except Exception as e:
        print(f"[red]✗ Ошибка API: {e}[/red]")

    print("[cyan]Подготовка завершена[/cyan]")


run_prep()
