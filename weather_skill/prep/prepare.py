from pathlib import Path
import json
import requests
from datetime import datetime, timezone
import logging
from adaos.i18n.translator import _


def run_prep(skill_path: Path):
    """
    Run the preparation stage for the weather skill.
    """
    logs_path = skill_path / "logs"
    logs_path.mkdir(parents=True, exist_ok=True)
    log_file = logs_path / "prep.log"

    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(message)s")

    prep_result = {
        "status": "ok",
        "reason": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resources": {"api_key": "", "api_entry_point": "https://api.openweathermap.org/data/2.5/weather", "default_city": ""},
        "tested_hypotheses": [],
    }

    try:
        # Collect required inputs
        default_city = input(_("prep.ask_default_city"))
        api_key = input(_("prep.ask_api_key"))

        prep_result["resources"]["default_city"] = default_city
        prep_result["resources"]["api_key"] = api_key

        # Test hypotheses

        # 1. Internet access
        logging.info(_("prep.test_internet_access"))
        try:
            requests.get("https://www.google.com", timeout=5)
            prep_result["tested_hypotheses"].append({"name": "Internet access", "result": True, "critical": True})
        except Exception:
            prep_result["tested_hypotheses"].append({"name": "Internet access", "result": False, "critical": True})
            prep_result["status"] = "failed"
            prep_result["reason"] = _("prep.fail_internet")

        # 2. Weather API access
        if prep_result["status"] == "ok":
            logging.info(_("prep.test_weather_api"))
            try:
                url = f"{prep_result['resources']['api_entry_point']}?q={default_city}&appid={api_key}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    prep_result["tested_hypotheses"].append({"name": "Weather API access", "result": True, "critical": True})
                else:
                    prep_result["tested_hypotheses"].append({"name": "Weather API access", "result": False, "critical": True})
                    prep_result["status"] = "failed"
                    prep_result["reason"] = _("prep.fail_weather_api")
            except Exception:
                prep_result["tested_hypotheses"].append({"name": "Weather API access", "result": False, "critical": True})
                prep_result["status"] = "failed"
                prep_result["reason"] = _("prep.fail_weather_api")

    except Exception:
        prep_result["status"] = "failed"
        prep_result["reason"] = _("prep.unexpected_error")

    # Write prep_result.json
    prep_result_path = skill_path / "prep_result.json"
    with prep_result_path.open("w", encoding="utf-8") as f:
        json.dump(prep_result, f, indent=2, ensure_ascii=False)

    # Write prep_prompt.md
    prep_prompt_path = skill_path / "prep_prompt.md"
    with prep_prompt_path.open("w", encoding="utf-8") as f:
        if prep_result["status"] == "ok":
            f.write(f"# { _('prep.summary_header') }\n\n")
            f.write(f"## { _('prep.collected_resources') }\n")
            for key, value in prep_result["resources"].items():
                f.write(f"- **{key}**: {value}\n")
            f.write(f"\n## { _('prep.tested_hypotheses') }\n")
            for hypo in prep_result["tested_hypotheses"]:
                symbol = "✅" if hypo["result"] else "❌"
                f.write(f"- {symbol} {hypo['name']}\n")
        else:
            f.write(f"# { _('prep.failed_header') }\n\n")
            f.write(f"**{ _('prep.reason') }**: {prep_result['reason']}\n")

    return prep_result


def lang_res():
    return {
        "prep.ask_default_city": "Enter default city for weather forecast: ",
        "prep.ask_api_key": "Enter API key for OpenWeatherMap: ",
        "prep.ask_api_entry_point": "Enter API entry point: ",
        "prep.test_internet_access": "Testing internet access...",
        "prep.fail_internet": "Internet access failed",
        "prep.test_weather_api": "Testing weather API...",
        "prep.fail_weather_api": "Weather API access failed",
        "prep.unexpected_error": "Unexpected error occurred",
        "prep.summary_header": "Preparation Summary",
        "prep.collected_resources": "Collected Resources",
        "prep.tested_hypotheses": "Tested Hypotheses",
        "prep.failed_header": "Preparation Failed",
        "prep.reason": "Reason",
    }
