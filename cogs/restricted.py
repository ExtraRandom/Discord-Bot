import os
import logging

import discord
from discord.ext import commands

from helpers import descriptions as desc, checks, settings

log = logging.getLogger(__name__)


class Restricted:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, description=desc.iscream)
    @checks.is_dev()
    async def avatar(self, image: str):
        try:
            with open("cogs/avatar/" + image, "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.edit_profile(avatar=image_bytes)
                # await self.bot.say("New avatar uploaded, how do you like me now?")
                log.info("Avatar updated")

        except Exception as e:
            log.exception("Couldn't change avatar")

    @commands.command(pass_context=True, hidden=True, description=desc.iscream)
    @checks.is_dev()
    async def nick(self, ctx, *, nick: str):
        try:
            await self.bot.change_nickname(ctx.message.server.me, nick)
            # await self.bot.say("I might being having an identity crisis. New name accepted")
            log.info("New name updated")
        except Exception as e:
            log.exception("Couldn't change display name")

    @commands.command(hidden=True, description=desc.idiotech)
    @checks.is_server_owner()
    async def log(self, users: str):
        users = users.split(';')
        messages = []
        admin = self.bot.get_channel(settings.channels['admin'])

        for channel in settings.channels:
            chan = self.bot.get_channel(settings.channels[channel])
            messages.append("======================\n")
            messages.append("MESSAGES FROM {}\n".format(channel))
            messages.append("======================\n")
            for_reversing = []
            async for msg in self.bot.logs_from(chan, limit=500):
                if msg.author.name in users:
                    for_reversing.append("[{}] {}: {}\n".format(msg.timestamp, msg.author.name, msg.clean_content))

            for msg in reversed(for_reversing):
                messages.append(msg)

        messages.append("======================\n")
        messages.append("     END OF FILE")

        w_log = open("log.txt", "w", encoding='utf-8')
        w_log.writelines(messages)
        w_log.close()

        with open("log.txt", "rb") as logfile:
            await self.bot.send_file(admin, logfile, filename="log.txt",
                                     content="Log file for mentioned users from last 500 messages in each channel.")

        os.remove("log.txt")
        log.info("Logging Finished - File sent to admins for review")


def setup(bot):
    bot.add_cog(Restricted(bot))
