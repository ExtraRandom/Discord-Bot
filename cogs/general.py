# import calendar
from datetime import datetime

# import aiohttp
from discord.ext import commands
from pytz import timezone

# import helpers.tokens as t
from helpers import descriptions as desc  # , time_calculations as tc, settings


class General:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, description=desc.time, brief=desc.time)
    async def time(self, ctx):
        # Group for !time command, set subcommands by wrapping them in @time.command(name='subcommand_name)
        # We use function get_time() to get all the times over the world.
        # To add a city, edit get_time() and add it into dictionary

        if ctx.invoked_subcommand is None:
            time = get_time()
            await self.bot.say("**San Francisco**: {} | **New York**: {} | **London**: {} | **Sydney** {}".format(
                time["sf"], time["ny"], time["london"], time["sydney"]))

        # TODO Squish timezones into one command (here)

    @time.command(name='advanced', description=desc.time_advanced, brief=desc.time_advanced)
    async def _advanced(self):
        time = get_time()
        await self.bot.say(
            "**San Francisco** {} (UTC-7) "
            "| **New York**: {} (UTC-4) "
            "| **London**: {} (UTC+1) "
            "| **Sydney**: {} (UTC+10) "
            "".format(time["sf"], time["ny"], time["london"], time["sydney"]))

    @time.command(name='sydney', description=desc.time_sydney, brief=desc.time_sydney)
    async def _sydney(self):
        time = get_time()
        await self.bot.say("**Sydney**: {} (UTC+10)".format(time["sydney"]))

    @time.command(name='london', description=desc.time_london, brief=desc.time_london)
    async def _london(self):
        time = get_time()
        await self.bot.say("**London**: {} (UTC+1)".format(time["london"]))

    @time.command(name='ny', description=desc.time_ny, brief=desc.time_ny)
    async def _ny(self):
        time = get_time()
        await self.bot.say("**New York**: {} (UTC-4)".format(time["ny"]))

    @time.command(name='sf', description=desc.time_sf, brief=desc.time_sf)
    async def _sf(self):
        time = get_time()
        await self.bot.say("**San Francisco**: {} (UTC-7)".format(time["sf"]))

    @time.command(name='perth', description=desc.time_perth, brief=desc.time_perth)
    async def _perth(self):
        time = get_time()
        await self.bot.say("**Perth**: {} (UTC+8)".format(time["perth"]))


def get_time() -> dict:
    """
    Function to get local time in cities
    :return: Dictionary with {"city":"%H:%M"}
    """
    places = {'sf': 'US/Pacific', 'london': 'Europe/London', 'sydney': 'Australia/Sydney', 'perth': 'Australia/Perth',
              'ny': 'US/Eastern'}
    output = {}

    now_utc = datetime.now(timezone('UTC'))

    for i in places:
        time = now_utc.astimezone(timezone(places[i]))
        fmttime = time.strftime('%H:%M')
        output[i] = fmttime

    return output


def setup(bot):
    bot.add_cog(General(bot))
