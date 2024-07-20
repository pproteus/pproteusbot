import json
from datetime import datetime, timedelta
from base_plugin import Plugin

import re
EMOJI_PATTERN = r'<:([^\s:]+):(\d+)>'
DATEFORMAT = "%Y-%m-%d"


class Reactiontracker(Plugin):
    """This plugin tracks use of discord server emojis."""
    name = "ReactionTracker"
    requirements = ["Discord"]

    def __init__(self, mediator, discord):
        super().__init__(mediator)

        self.filename = self.fetch_config_filepath("reactioncounts.json")
        with open(self.filename, "r") as f:
            try:
                self.emojidict = json.load(f)
            except json.decoder.JSONDecodeError:
                self.emojidict = dict() #new file

        discord.attach_subscriber("message", self.register_message_reactions)
        discord.attach_subscriber("reaction", self.register_raw_reaction)

    def register_message_reactions(self, message):
        server_id = message.guild.id
        author_id = message.author.id
        author_name = message.author.display_name.encode('ascii','replace').decode('ascii')
        text = message.content.encode('ascii','replace').decode('ascii')
        for e in re.finditer(EMOJI_PATTERN, text):
            self.update_file(server_id, e.group(2), e.group(1), author_id, author_name)

    def register_raw_reaction(self, payload):
        if payload.emoji.id: #otherwise it's a builtin emoji, ignore those
            server_id = payload.guild_id
            author_id = payload.user_id
            author_name = payload.member.display_name.encode('ascii','replace').decode('ascii')
            self.update_file(server_id, payload.emoji.id, payload.emoji.name, author_id, author_name)

    def save_file(self):
        with open(self.filename,"w") as f:
            json.dump(self.emojidict, f)

    def update_file(self, server_id, emoji_id, emoji_name, user_id, user_name):
        emoji_id = str(emoji_id)
        user_id = str(user_id)
        date = datetime.now().strftime(DATEFORMAT)
        if server_id not in self.emojidict:
            self.emojidict[server_id] = {}
        if emoji_id not in self.emojidict[server_id].keys():
            self.emojidict[server_id][emoji_id] = {"name": emoji_name, "users": {user_id: 
                                                    {"name": user_name, "time":date}} }
        else:
            self.emojidict[server_id][emoji_id]["name"] = emoji_name
            self.emojidict[server_id][emoji_id]["users"][user_id]["name"] = user_name
            self.emojidict[server_id][emoji_id]["users"][user_id]["time"] = date
        self.save_file()

    def get_summary(self, server, date=None):
        """Given a server, find all the emojis for that server, and return sorted by # of users.
            Filtered by only uses after a certain date if the date arg is not None."""
        pass
        #TODO
        #handle cases whether server is an actual server, a name, or an id