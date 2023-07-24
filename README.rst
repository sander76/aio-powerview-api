AioPvApi
========

A python asyncio API for PowerView blinds.
Written for Home-Assistant. Adding features as I go...

Have a look at the examples folder for some guidance how to use it.

Links
-----
- https://home-assistant.io/
- https://www.hunterdouglas.com/operating-systems/powerview-motorization

Changelog
---------

**v1.6.19**

- Add endpoints and handle 423 response
- Remove loop as argument

**v2.0.0**

- Add support for all known shade types
- Fallback to shade recognition based on capability
- Clamping to prevent MIN_POSITION or MAX_POSITION being exceeded
- Code refactoring

**v2.0.1**

- Invert type 3 & 4 to match api documentation from hunter douglas
- Add type 10

**v2.0.2**

- Bug Fix to handle shades with unexpected json responses

**v2.0.3**

- Add Type 26, 27 & 28 - Skyline Panels
- Force capability 1 for Type 44 - Twist
- Align class name standard

**v2.0.4**

- Add Type 10 - SkyLift
- Handle calls to update shade position during maintenance
- Raise error directly on hub calls instead of logger

**v3.0.0**

- Major overhaul to incorporate gateway version 3 API.  Version can be automatically detected or manually specified.
- UserData class is deprecated and replaced with Hub.
- ShadePosition class now replaces the raw json management of shades in support of cross generational management.
- Schedules / Automations are now supported by the API
- New get_*objecttype* methods available to returned structured data objects for consistent management