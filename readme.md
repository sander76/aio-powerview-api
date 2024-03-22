[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![PyPI](https://img.shields.io/pypi/v/aiopvapi)
[![codecov](https://codecov.io/gh/sander76/aio-powerview-api/branch/master/graph/badge.svg?token=83154B19T8)](https://codecov.io/gh/sander76/aio-powerview-api)
![example workflow](https://github.com/sander76/aio-powerview-api/actions/workflows/main.yaml/badge.svg)

# Aio PowerView API

A python async API for PowerView blinds written for Home-Assistant.

Have a look at the examples folder for some guidance how to use it.

## Capabilities

| Description                           | Capabilities | Primary | Secondary | Tilt | Tilt Position | Vertical | DualShade |
| :------------------------------------ | :----------: | :-----: | :-------: | :--: | :-----------: | :------: | :-------: |
| Bottom Up                             |      0       |    X    |           |      |               |          |           |
| Bottom Up Tilt 180°                   |      1*      |    X    |           | 180° | Closed        |          |           |
| Bottom Up Tilt 90°                    |      1       |    X    |           | 90°  | Closed        |          |           |
| Bottom Up Tilt 180°                   |      2       |    X    |           | 180° | Anywhere      |          |           |
| Vertical                              |      3       |    X    |           |      |               |    X     |           |
| Vertical Tilt Anywhere                |      4       |    X    |           | 180° | Anywhere      |    X     |           |
| Tilt Only 180°                        |      5       |         |           | 180° | Anywhere      |          |           |
| Top Down                              |      6       |         |     X     |      |               |          |           |
| Top Down Bottom Up                    |      7       |    X    |     X     |      |               |          |           |
| Dual Shade Overlapped                 |      8       |    X    |     X     |      |               |          |     X     |
| Dual Shade Overlapped Tilt 90°        |      9       |    X    |     X     | 90°  | Closed        |          |     X     |
| Dual Shade Overlapped Tilt 90°        |     10       |    X    |     X     | 180° | Closed        |          |     X     |
| Dual Shade Overlapped Illuminated     |     11^      |    X    |     X     |      |               |          |     X     |

\^ Capability 11 shades have the same functionality as capability 8 shades, plus an inbuild light. Light management not available via aiopvapi at this time

## Shades

Shades that have been directly added to the API are listed below and should function correctly. In **most** cases this is identification is purely aestetic.

Shades not listed will get their features from their **capabilities**, unfortunately the json returned from the shade can sometimes be incorrect and we need to override the features for the API (and Home-Assistant) to read them correctly.

| Name                                  | Type | Capability |
| :------------------------------------ | :--: | :--------: |
| AC Roller                             |  49  |      0     |
| Aura Illuminated, Roller              |  49  |     11     |
| Banded Shades                         |  52  |      0     |
| Bottom Up                             |   5  |      0     |
| Curtain, Left Stack                   |  69  |      3     |
| Curtain, Right Stack                  |  70  |      3     |
| Curtain, Split Stack                  |  71  |      3     |
| Designer Roller                       |   1  |      0     |
| Duette                                |   6  |      0     |
| Duette, Top Down Bottom Up            |   8  |      7     |
| Duette Architella, Top Down Bottom Up |  33  |      7     |
| Duette DuoLite, Top Down Bottom Up    |   9  |      7     |
| Duolite Lift                          |  79  |      9     |
| Facette                               |  43  |      1     |
| M25T Roller Blind                     |  42  |      0     |
| Palm Beach Shutters                   |  66  |      5     |
| Pirouette                             |  18  |      1     |
| Pleated, Top Down Bottom Up           |  47  |      7     |
| Provenance Woven Wood                 |  19  |      0     |
| Roman                                 |   4  |      0     |
| Silhouette                            |  23  |      1     |
| Silhouette Duolite                    |  38  |      9     |
| Sonnette                              |  53  |      0     |
| Skyline Panel, Left Stack             |  26  |      3     |
| Skyline Panel, Right Stack            |  27  |      3     |
| Skyline Panel, Split Stack            |  28  |      3     |
| Top Down                              |   7  |      6     |
| Twist                                 |  44  |      1*    |
| Vignette                              |  31  |      0     |
| Vignette                              |  32  |      0     |
| Vignette                              |  84  |      0     |
| Vignette Duolite                      |  65  |      8     |
| Vertical                              |   3  |      0     |
| Vertical Slats, Left Stack            |  54  |      4     |
| Vertical Slats, Right Stack           |  55  |      4     |
| Vertical Slats, Split Stack           |  56  |      4     |
| Venetian, Tilt Anywhere               |  51  |      2     |
| Venetian, Tilt Anywhere               |  62  |      2     |

\* No other shade are known to have this capability and currently the only way to get this functionality is by hardcoding into this API

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

### v3.0.2

- Add type 19 (Provenance Woven Wood)
- Fix Positioning for ShadeVerticalTiltAnywhere + ShadeTiltOnly (Mid only)  
- Fix logging regression on initial setup
- Fixes for ShadeVerticalTiltAnywhere + ShadeTiltOnly
- Fix tests
- Remove unneeded declerations
- Fix shade position reporting for v2 shades
- Dandle empty hub data being returned

### v3.1.0
- General docstring updates
- Handle kwargs in websessions for management of timeout internally
- Update error handling in tools
- Handle empty values and zeros better
- Add type 53 (Sonnette) and yype 95 (Aura Illuminated, Roller). Note: *Type 95 do not support light control*
- Handle PowerType 11 + 12. Both are fixed and cannot be edited

## Links

---

- https://home-assistant.io/
- https://www.hunterdouglas.com/operating-systems/powerview-motorization
