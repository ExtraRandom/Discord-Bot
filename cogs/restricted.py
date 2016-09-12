# import os
import logging

# import discord
from discord.ext import commands

from helpers import descriptions as desc, checks, settings

log = logging.getLogger(__name__)


class Restricted:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, description=desc.isdev)
    @checks.is_dev()
    async def avatar(self, image: str):
        try:
            with open("cogs/avatar/" + image, "rb") as avatar:
                f = avatar.read()
                image_bytes = bytearray(f)
                await self.bot.edit_profile(avatar=image_bytes)
                log.info("Avatar updated")

        except Exception as e:
            log.exception("Couldn't change avatar")

    @commands.command(pass_context=True, hidden=True, description=desc.isdev)
    @checks.is_dev()
    async def nick(self, ctx, *, nick: str):
        try:
            await self.bot.change_nickname(ctx.message.server.me, nick)
            log.info("Nickname updated")
        except Exception as e:
            log.exception("Couldn't change nickname")


def setup(bot):
    bot.add_cog(Restricted(bot))
