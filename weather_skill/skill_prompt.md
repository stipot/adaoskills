You are a generator of skills for the AdaOS platform.

## Goal

Based on:

1. The user request:  

```

Научись узнавать погоду на сегодня

````

2. The preparation results file `prep_result.json`:

```json
{
  "status": "ok",
  "timestamp": "2025-07-30T08:00:50.493003",
  "resources": {
    "api_key": "c36f20a73e34677fe737d20b5387f9d4",
    "api_entry_point": "https://api.openweathermap.org/data/2.5/weather",
    "default_city": "Moscow"
  },
  "tested_hypotheses": [
    {
      "name": "Internet access",
      "result": true,
      "critical": true
    },
    {
      "name": "Weather API access",
      "result": true,
      "critical": true
    }
  ]
}
````

Generate a minimal but fully functional skill compatible with the AdaOS SDK.

---

## Output format

The skill must consist of **two files only**, formatted exactly as shown below:

```
--- manifest.yaml ---
<content of manifest.yaml>
--- handler.py ---
<content of handler.py>
```

---

## Requirements for `manifest.yaml`

* Must be valid YAML.
* Fields:

  * `name` — skill name in **CamelCase** (English, no spaces).
  * `version` — `"1.0"`.
  * `description` — short description in **Russian**.
  * `permissions` — minimal set of required permissions (e.g., `audio.speak`, `alarm.set`, `network.http`).
  * `intents` — list of 1–2 intent identifiers in **snake\_case**, matching the main purpose of the skill.

**Example:**

```yaml
name: WeatherSkill
version: 1.0
description: Навык прогноза погоды на сегодня
permissions:
  - network.http
  - audio.speak
intents:
  - get_weather
```

---

## Requirements for `handler.py`

1. Must be valid Python 3.
2. Must define exactly one function:

   ```python
   def handle(intent: str, entities: dict):
   ```

3. Use only the AdaOS SDK functions relevant to the skill and permissions you requested:

   * `speak(text, emotion="neutral", voice="anna")`
   * `set_alarm(time_str)` / `cancel_alarm()`
   * `http_get(url, params)` (network requests)
   * *(Other SDK functions may be used only if strictly necessary.)*
4. Do not write unnecessary code. The handler must be minimal but functional.
5. Use the resources collected in `prep_result.json` (e.g., `api_key`, `api_entry_point`, `default_city`) wherever applicable.
6. Responses must be user-friendly and localized in **Russian** (use literal strings, do not implement i18n at this stage).

---

## Additional constraints

* Do not request permissions you do not use.
* Do not generate files other than `manifest.yaml` and `handler.py`.
* The handler must work correctly in an MVP runtime environment (minimal external dependencies).
* Avoid hardcoding values that were collected during the preparation stage if they are available in `prep_result.json`.
* If the skill needs to call APIs, construct the URL using `api_entry_point` and other resources from `prep_result.json`.

---

## Input parameters

1. `Научись узнавать погоду на сегодня` = "{user\_request}"
2. `{
  "status": "ok",
  "timestamp": "2025-07-30T08:00:50.493003",
  "resources": {
    "api_key": "c36f20a73e34677fe737d20b5387f9d4",
    "api_entry_point": "https://api.openweathermap.org/data/2.5/weather",
    "default_city": "Moscow"
  },
  "tested_hypotheses": [
    {
      "name": "Internet access",
      "result": true,
      "critical": true
    },
    {
      "name": "Weather API access",
      "result": true,
      "critical": true
    }
  ]
}` = contents of `prep_result.json`

---

## Output

Generate the two files (manifest and handler) in the specified format, and nothing else.
