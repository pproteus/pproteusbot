from base_plugin import PluginWithLoop
import discord
import asyncio
import inspect
import logging

class Discord(PluginWithLoop):
    """This is a wrapper for many parts of discord.py"""
    name = "Discord"

    def __init__(self, mediator):
        super().__init__(mediator)

        #Please be advised that uncaught discord exceptions will end up in the logfile
        # rather than getting caught at the plugin level and printing a traceback.
        logger = logging.getLogger('discord')
        logger.setLevel(logging.INFO)
        logpath = self.fetch_config_filepath("discordlog.txt")
        handler = logging.FileHandler(filename=logpath, encoding='utf-8', mode='w')
        logger.addHandler(handler)
        print(f"Please note: discord errors are logged in {logpath}")

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.client = discord.Client(intents=intents)
        self.tree = discord.app_commands.CommandTree(self.client)

        #note for plugin-writers:
        # calling @self.client.event overwrites, so 
        # using the self.notify system here is mandatory.
        # calling Discord.client.event elsewhere will break things.
        @self.client.event
        async def on_ready():
            await self.notify("ready")
            #assume that all slash-command creation was performed in the above step.
            await self.tree.sync()  
            for g in self.client.guilds:
                await self.tree.sync(guild=g)  
            print("Connected to discord\n")

        @self.client.event
        async def on_message(message):
            if message.author != self.client.user:
                await self.notify("message", message=message)

        @self.client.event
        async def on_raw_reaction_add(payload):
            if payload.user_id != self.client.user.id:
                await self.notify("reaction", payload=payload)
    

    async def main(self):
        token = self.get_key()
        await self.client.start(token)

    def get_key(self):
        filepath  = self.fetch_config_filepath("discord_key_alternate.txt")
        with open(filepath, "r") as f:
            key = f.read()
            if len(key)>2:
                return key
            else:
                raise ValueError(f"Go to {filepath} and provide your own key!!")

    async def send_public_message(self, channel, text, embed=None):
        message = await channel.send(self.encode_text(text, channel.guild), embed=embed)
        return message

    async def send_pm(self, recipient, text, file=None, embed=None):
        if recipient.dm_channel is None:
            await recipient.create_dm()
        if file is not None:
            file = discord.File(file)
        message = await recipient.dm_channel.send(self.encode_text(text, None), file=file, embed=embed)
        return message

    def encode_text(self, text, target_server=None):
        """ Take a literal string and convert it to a form better-suited for discord."""
        text = text.replace("*", "\\*").replace("_", "\\_")
        return text
        #TODO: handle both kinds of emojis, and @s
    
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
                
    async def create_thread(self, root_message, thread_name):
        """Given a message object, create a thread from it."""
        await root_message.create_thread(name=thread_name, auto_archive_duration=60*24*3)
                
    async def create_slash_command(self, funct, description="description goes here", guildlist=None, **param_descriptions):
        """Takes a function that takes an interaction as its first arg, and returns a string.
        Creates a slash command which executes that function.
        This is obviously missing many of the powerful things that discord.py enables,
        but ultimately the benefit is that this endpoint is radically simpler.
        This should be called at "ready", otherwise they won't get registered properly.
        If guildlist is None, then the command is applied to all guilds individually.
        Otherwise, to get a global command, use the empty list.
        To allow enforcement per (one of a limited list of options), it is recommend to use 
         `typing.Literal` or `discord.app_commands.Range` in the annotation.
        Positional arguments are not supported."""

        import functools
        if guildlist is None:
            guildlist = self.client.guilds
        if guildlist:
            print(f"Creating slash command '{funct.__name__}' for {', '.join([i.name for i in guildlist])}")
        else:
            print(f"Creating slash command '{funct.__name__}' as a global command")
        @self.tree.command(name=funct.__name__, description=description, guilds=guildlist)
        @discord.app_commands.describe(**param_descriptions)
        @functools.wraps(funct)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if inspect.ismethod(funct):
                raise TypeError("Cannot make slash command out of a bound method.")
            if asyncio.iscoroutinefunction(funct):
                await interaction.response.defer(thinking=True)
                answer = await funct(interaction, *args, **kwargs)
                await interaction.followup.send(answer)
            else:
                answer = funct(interaction, *args, **kwargs)
                await interaction.response.send_message(f'{answer}')
