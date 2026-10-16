# Guncel Girls — @Guncel_Girls_Bot

Free, interactive Turkish/English outfit planner. Choose one of four occasions and four styles, receive clothing/shoe/bag recommendations, switch suggestions, match colours, and save up to 20 favourites. No external redirects, forced joins, payments, AI API keys, or photo uploads.

## Run

Use Python 3.12 or newer. Set `BOT_TOKEN` in your host's secret environment, then run:

```sh
python bot.py
```

`.env.example` documents the variables; the app reads actual environment variables (it does not load .env files). Use only one running instance per bot token. `BOT_TOKEN` must belong to @Guncel_Girls_Bot; startup checks the username.

On startup the code sets the name, bio (`setMyShortDescription`), pre-Start description (`setMyDescription`) and command menu, including default, Turkish and English variants. These changes become visible only after the worker is running with the correct token. Add a suitable fashion/brand profile image through @BotFather before advertising.

For a background worker: build `pip install -r requirements.txt`, start `python bot.py`. No public web port is needed. Set `DB_PATH` to a persistent writable path if saved favourites must survive host replacement; the default `data/girls.db` survives process restarts only when that filesystem is retained. An ephemeral hosting filesystem can lose favourites on redeploy. No database service is required for the core planner.

## Privacy and behaviour

Only private chats are handled. The app stores a Telegram user ID alongside a chosen language and saved looks; it does not build a registration list or send unsolicited broadcasts. `/privacy` explains storage and `/delete_data` removes saved data. Telegram itself handles message delivery and may retain messages under its own policies. Host logs contain operational messages, not token URLs or message contents.

Suggestions are general editorial ideas, not personalised professional advice or live weather recommendations. Two base variations per occasion plus four style adaptations provide 32 combinations per language. Saved looks retain the language in which they were saved.

## Telegram Ads readiness

The visible service, bio, description and ad text must describe this actual outfit planner. Keep ads, destination and targeted channels in matching languages. Do not repurpose it into a redirect-only, dating or adult-content bot, or replace content to evade review. There is no reviewer-specific behaviour. Telegram decides approval; this code cannot guarantee acceptance.

Official rules: https://ads.telegram.org/guidelines and https://ads.telegram.org/tos

## Checks

```sh
python -m unittest discover -s tests -v
python -m py_compile bot.py
```

Live delivery/profile updates need a real bot token and are not covered by offline tests.
