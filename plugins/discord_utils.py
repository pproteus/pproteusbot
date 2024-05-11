from base_plugin import PluginWithLoop
import discord

class Discord(PluginWithLoop):
    name = "Discord"

    def __init__(self, mediator):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print("Connected to discord")
            await self.notify("ready")

        @self.client.event
        async def on_message(message):
            await self.notify("message", message=message)
    

    async def main(self):
        token = self.get_key()
        await self.client.start(token)

    def get_key(self):
        #filename = "plugins/config/discord/discord_key.txt"
        filename  = "plugins/config/discord/discord_key_alternate.txt"
        with open(filename, "r") as f:
            return f.read()
            #provide your own key!!

    async def send_public_message(self, channel, text, embed=None):
        await channel.send(self.encode_text(text, channel.guild), embed=embed)

    async def send_pm(self, recipient, text, file=None, embed=None):
        if recipient.dm_channel is None:
            await recipient.create_dm()
        if file is not None:
            file = discord.File(file)
        await recipient.dm_channel.send(self.encode_text(text, None), file=file, embed=embed)

    def encode_text(self, text, target_server=None):
        """ Take a literal string and convert it to a form better-suited for discord."""
        return text.replace("*", "\\*").replace("_", "\\_") 
        #TODO: both kinds of emojis, and @s
    
    def fetch_server_from_string(self, server_string):
        for i in self.client.guilds:
            if i.name == server_string:
                return i

    def fetch_channel_from_string(self, channel_string, server):
        for i in server.channels:
            if i.name == channel_string:
                return i

    def fetch_member_from_string(self, member_string, server=None):
        if server is None:
            for guild in self.client.guilds:
                for member in guild.members:
                    if member.name == member_string:
                        return member
        else:
            for member in server.members:
                if member.name == member_string:
                    return member