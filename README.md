# pproteusbot v2
pproteusbot is a wrapper for a discord bot, except it doesn't even need to be a discord bot.

- The bot operates in the form of discrete plugin units. Anything can be a plugin.
- The bot collects plugins at runtime. This means plugins can be added or removed largely without fear of breaking anything.
- Plugins can define their own event loops, or subscribe to events defined by other plugins.

To run: `py -m bot`
