import json
from typing import Dict
import requests

from adaos.sdk.skills.i18n import _
from adaos.sdk.context import get_current_skill
from adaos.sdk.output import output
from adaos.sdk.decorators import subscribe, tool
from adaos.sdk.bus import emit
from adaos.sdk.skill_env import get_env, set_env
from adaos.sdk.skill_memory import get, set


def handle(intent: str, entities: dict):
    # Ensure environment settings are loaded
    api_key = get_env("api_key")
    api_entry_point = get_env("api_entry_point")
    default_city = get_env("default_city")

    if not api_key or not api_entry_point or not default_city:
        prep_file = get_current_skill().path / "prep" / "prep_result.json"
        if prep_file.exists():
            with open(prep_file, "r", encoding="utf-8") as f:
                prep_data = json.load(f)
                resources = prep_data.get("resources", {})
                api_key = resources.get("api_key")
                api_entry_point = resources.get("api_entry_point")
                default_city = resources.get("default_city")
                if api_key:
                    set_env("api_key", api_key)
                if api_entry_point:
                    set_env("api_entry_point", api_entry_point)
                if default_city:
                    set_env("default_city", default_city)

    if not api_key:
        output(_("prep.weather.missing_key"))
        return

    # Determine the city
    city = entities.get("city") or get("last_city") or get_env("default_city")
    set("last_city", city)

    # Make the API request
    try:
        response = requests.get(
            api_entry_point,
            params={"q": city, "appid": api_key, "units": "metric", "lang": "en"},
            timeout=5,
        )
        if response.status_code != 200:
            output(_("prep.weather.api_error", city=city))
            return

        data = response.json()
        temp = data.get("main", {}).get("temp")
        description = data.get("weather", [{}])[0].get("description", "")

        if temp is None:
            output(_("prep.weather.invalid_response"))
            return

        output(_("prep.weather.success", city=city, temp=temp, description=description))
    except Exception:
        output(_("prep.weather.api_error", city=city))


# инструмент для LLM (/api/tools/call)
@tool("get_weather")
def get_weather(city: str) -> dict:
    api_key = get_env("api_key")
    api_entry_point = get_env("api_entry_point")

    if not api_key or not api_entry_point or not city:
        prep_file = get_current_skill().path / "prep" / "prep_result.json"
        if prep_file.exists():
            try:
                data = json.loads(prep_file.read_text(encoding="utf-8"))
                res = data.get("resources", {}) or {}
                api_key = api_key or res.get("api_key")
                api_entry_point = api_entry_point or res.get("api_entry_point")
                city = city or res.get("default_city")
                if api_key:
                    set_env("api_key", api_key)
                if api_entry_point:
                    set_env("api_entry_point", api_entry_point)
                if city:
                    set_env("default_city", city)
            except Exception:
                pass

    if not api_key or not api_entry_point:
        return {"ok": False, "error": "missing api config"}

    if not city:
        return {"ok": False, "error": "missing city"}

    try:
        r = requests.get(
            api_entry_point,
            params={"q": city, "appid": api_key, "units": "metric", "lang": "en"},
            timeout=5,
        )
        if r.status_code != 200:
            return {"ok": False, "error": f"api status {r.status_code}"}
        d = r.json()
        temp = d.get("main", {}).get("temp")
        desc = d.get("weather", [{}])[0].get("description", "")
        if temp is None:
            return {"ok": False, "error": "invalid response"}
        return {"ok": True, "city": city, "temp": temp, "description": desc}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# подписка на событие: nlp.intent.weather.get
@subscribe("nlp.intent.weather.get")
async def on_weather_intent(evt):
    city = evt.payload.get("city") or get("last_city") or get_env("default_city")
    if not city:
        await emit("ui.notify", {"text": _("prep.weather.missing_key")}, actor=evt.actor, source="weather_skill", trace_id=evt.trace_id)
        return
    res = get_weather(city)
    if res.get("ok"):
        msg = _("prep.weather.success", city=res["city"], temp=res["temp"], description=res["description"])
        await emit("ui.notify", {"text": msg}, actor=evt.actor, source="weather_skill", trace_id=evt.trace_id)
    else:
        await emit("ui.notify", {"text": _("prep.weather.api_error", city=city)}, actor=evt.actor, source="weather_skill", trace_id=evt.trace_id)


def lang_res() -> Dict[str, str]:
    return {
        "prep.weather.api_error": "Could not get weather for {city}",
        "prep.weather.success": "Current weather in {city}: {temp}°C, {description}",
        "prep.weather.missing_key": "API key is missing",
        "prep.weather.invalid_response": "Invalid response from weather service",
    }
