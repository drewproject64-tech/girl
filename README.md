# Guncel Girls — @Guncel_Girls_Bot

Simple free Turkish/English outfit and colour suggestion bot. No database, saved users, favourites, admin panel, broadcasts, external redirects or forced channel joins. Python 3.12 standard library only; no paid APIs.

## Run

Set `BOT_TOKEN` in your hosting environment and run `python bot.py`.
Use one worker only. The token is checked against @Guncel_Girls_Bot at startup. Never commit a token. `.env.example` is a reference; the app does not load .env files.

Build command: `pip install -r requirements.txt`
Start command: `python bot.py`

On startup the worker sets the bot name, bio, description visible before Start, and command menu in Turkish and English. These updates only happen once the worker runs with the correct token. Add a suitable brand/fashion profile image using @BotFather before submitting ads.

## Functions

- Occasion → style → outfit recommendation, with another variation button.
- Quick outfit suggestion.
- Colour matching.
- Turkish/English menu switch; language travels in button callbacks, with no saved user preferences.
- `/start`, `/help`, `/privacy`.

The app processes Telegram messages to reply but does not save user IDs or message history. Telegram may retain messages under its own policies. Operational logs exclude message text and token URLs.

## Ads

The bot provides the same service to all users and moderators. Keep the ad text, target channel language and actual service consistent. No approval guarantee: Telegram reviews the ad, profile, imagery and destination.

https://ads.telegram.org/guidelines
https://ads.telegram.org/tos

## Validation

`python -m unittest discover -s tests -v`

`python -m py_compile bot.py`

Offline checks do not confirm live Telegram delivery. A bot token and running host are required for live verification.
