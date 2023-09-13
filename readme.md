[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![PyPI](https://img.shields.io/pypi/v/aiopvapi)
[![codecov](https://codecov.io/gh/sander76/aio-powerview-api/branch/master/graph/badge.svg?token=83154B19T8)](https://codecov.io/gh/sander76/aio-powerview-api)
![example workflow](https://github.com/sander76/aio-powerview-api/actions/workflows/main.yaml/badge.svg)

# Aio PowerView API

A python async API for PowerView blinds.
Written for Home-Assistant. Adding features as I go...

Have a look at the examples folder for some guidance how to use it.

## Development

- Install dev requirements.
- Testing is done using NOX
- Build a package: `python .\setup.py bdist bdist_wheel --universal`
- upload a package `twine upload dist/*.*`

## Changelog

### 1.6.15

- Constrain aiohttp package versions.

### v1.6.19

- Add endpoints and handle 423 response
- Remove loop as argument

### v2.0.0

- Add support for all known shade types
- Fallback to shade recognition based on capability
- Clamping to prevent MIN_POSITION or MAX_POSITION being exceeded
- Code refactoring

### v2.0.1

- Invert type 3 & 4 to match api documentation from hunter douglas
- Add type 10

### v2.0.2

- Bug Fix to handle shades with unexpected json responses

### v2.0.3

- Add Type 26, 27 & 28 - Skyline Panels
- Force capability 1 for Type 44 - Twist
- Align class name standard

### v2.0.4

- Add Type 10 - SkyLift
- Handle calls to update shade position during maintenance
- Raise error directly on hub calls instead of logger

### v3.0.0

- Major overhaul to incorporate gateway version 3 API.  Version can be automatically detected or manually specified.
- UserData class is deprecated and replaced with Hub.
- ShadePosition class now replaces the raw json management of shades in support of cross generational management.
- Schedules / Automations are now supported by the API
- New get_*objecttype* methods available to returned structured data objects for consistent management

### v3.0.1

- Raw hub data updates made via defined function (`request_raw_data`, `request_home_data`, `request_raw_firware`, `detect_api_version`)
- Parse Gen 3 hub name based on serial + mac
- Find API version based on firmware revision
- Remove async_timeout and move to asyncio

## Links

---

- https://home-assistant.io/
- https://www.hunterdouglas.com/operating-systems/powerview-motorization
