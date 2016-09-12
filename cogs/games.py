import asyncio
import logging
import bs4
import requests
# import json
import os

from helpers import descriptions as desc, tokens as t  # , time_calculations as tc, simplify as s, settings

# from datetime import datetime

import aiohttp
from discord.ext import commands

from mcstatus import MinecraftServer

loop = asyncio.get_event_loop()
log = logging.getLogger(__name__)


class Games:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mc", description=desc.mc_ip, brief=desc.mc_ip)
    async def minecraft_ip(self, ip: str):
        # TODO add a check to see if the server is modded
        try:
            server = MinecraftServer.lookup(ip)
            status = server.status()
            data = status.raw
            # print(data)
            ver = data['version']['name']
            version = float(ver[2:])
            if version >= 9:
                s_desc = data['description']['text']
            else:
                s_desc = data['description']
            players = ""
            try:
                for player in data['players']['sample']:
                    players += "{}, ".format(player['name'])
                players = players[:-2]  # Remove final comma and the space after it
            except Exception:
                players = "None"

            # TODO formatting
            msg = """ __*Status of {}*__

Version: {}
Online Players: {}
Description: {}
            """.format(ip, ver, players, s_desc)
            await self.bot.say(msg)

        except ValueError as e:
            await self.bot.say("Invalid IP")
            log.warn(e)

        except Exception as e:
            await self.bot.say("An error has occurred.")
            log.warning("Exception in games.py - {}".format(e))

    """
    # TODO decide whether this command is really needed
    @commands.command(name="mcstatus", hidden=True, description=desc.mc_status, brief=desc.mc_status)
    async def minecraft_status(self):

        sessions = "https://sessionserver.mojang.com/"
        website = "https://minecraft.net/en/"
        skins = "http://textures.minecraft.net/texture/a116e69a845e227f7ca1fdde8c357c8c821ebd4ba619382ea4a1f87d4ae94"

        await self.bot.say("http://xpaw.ru/mcstatus/")
    """

    @commands.command(description=desc.csgo, brief=desc.csgo)
    async def csgo(self):
        if not t.web_api == "":
            try:
                link = "https://api.steampowered.com/ICSGOServers_730/GetGameServersStatus/v1/?key={}&format=json" \
                       "".format(t.web_api)

                with aiohttp.ClientSession() as session:
                    async with session.get(link)as resp:
                        data = await resp.json()

                        test = "hi"
                        test.capitalize()

                        scheduler = data['result']['matchmaking']['scheduler']
                        servers = data['result']['matchmaking']['online_servers']
                        players = data['result']['matchmaking']['online_players']
                        searching = data['result']['matchmaking']['searching_players']
                        search_time = data['result']['matchmaking']['search_seconds_avg']

                        # TODO formatting
                        msg = """CSGO Status

Scheduler Status: {}
Online Servers: {}
Online Players: {} ({} searching)
Average Search Time: {} seconds
                        """.format(scheduler.capitalize(), servers, players, searching, search_time)

                        await self.bot.say(msg)

            except Exception as e:
                await self.bot.say("Error getting data - Ask Owner to check WebAPI key is correct")
                log.warn("Invalid WebAPI key")
        else:
            await self.bot.say("This command is disabled currently. Ask the bot owner to add a Steam WebAPI key to "
                               "tokens.py for it to be enabled")

    @commands.group(pass_context=True, description=desc.steam_status, brief=desc.steam_status)
    async def steam(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say(await get_status("short"))

    @steam.command(name="status", description=desc.steam_status, brief=desc.steam_status)
    async def _status(self):
        await self.bot.say(await get_status("long"))

    @steam.command(name="bestsellers", description=desc.steam_bs, brief=desc.steam_bs)
    async def _bs(self):
        future = loop.run_in_executor(None, requests.get,
                                      "http://store.steampowered.com/search/?filter=topsellers&os=win")
        res = await future

        try:
            res.raise_for_status()
        except Exception as e:
            await self.bot.say("**Error with request.\nError: {}".format(str(e)))
            log.exception("Error with request (games.py)")
            return

        doc = bs4.BeautifulSoup(res.text, "html.parser")
        title = doc.select('span[class="title"]')

        msg = """**Best Selling Steam Games**

 1) {}
2) {}
4) {}
3) {}
5) {}
""".format(title[0].getText(), title[1].getText(), title[2].getText(), title[3].getText(), title[4].getText())

        await self.bot.say(msg)

    @steam.command(name="sales", description=desc.steam_sales, brief=desc.steam_sales)
    async def _deals(self):
        await self.bot.say("https://steamdb.info/sales/")

    @commands.command(description=desc.ow, brief=desc.owb)
    async def overwatch(self, region: str, battletag: str):
        msg = await self.bot.say("Fetching Stats for {}".format(battletag))

        user = battletag.replace("#", "-")

        reg_eu = ["eu", "euro", "europe"]
        reg_us = ["australia", "aussie", "aus", "us", "usa", "na", "america", "au"]
        reg_kr = ["asia", "korea", "kr", "as", "china", "japan"]

        if region.lower() in reg_eu:
            reg = "eu"
        elif region.lower() in reg_us:
            reg = "us"
        elif region.lower() in reg_kr:
            reg = "kr"
        else:
            self.bot.edit_message(msg, "Unknown region: {}".format(region))
            return

        future = loop.run_in_executor(
            None, requests.get, "https://playoverwatch.com/en-us/career/pc/{}/{}".format(reg, user))
        res = await future

        try:
            res.raise_for_status()
        except Exception as e:
            await self.bot.edit_message(msg, "**Error with request. Please check for mistakes before trying again.**"
                                             ".\nError: {}".format(str(e)))
            log.exception("Error with request")
            return

        doc = bs4.BeautifulSoup(res.text, "html.parser")
        # page = doc.select('div')

        """
        Games Played seems to have been removed from the page info is pulled from for some reason,
        the code for getting it is commented out in case it makes a return
        """

        most_played = doc.select('div[data-overwatch-progress-percent="1"] div[class="title"]')[0].getText()
        most_games = doc.select('div[data-overwatch-progress-percent="1"] div[class="description"]')[0].getText()

        stats = doc.select('div[class="card-stat-block"] tbody td')

        count = 0

        games_won = 0
        # games_played = 0
        time_played = 0
        medals = 0

        for item in stats:
            # print(item)
            if str(item) == "<td>Games Won</td>" and games_won == 0:
                games_won = doc.select('div[id="quick-play"] div[class="card-stat-block"] tbody td'
                                       '')[count].nextSibling.getText()

            if str(item) == "<td>Medals</td>" and medals == 0:
                medals = doc.select('div[id="quick-play"] div[class="card-stat-block"] tbody td'
                                    '')[count].nextSibling.getText()

            """
            if str(item) == "<td>Games Played</td>" and games_played == 0:
                # print(item)
                # games_played = doc.select('div[class="card-stat-block"] tbody td')[count].nextSibling.getText()
                print(doc.select('div[id="quick-play"] div[class="card-stat-block"] tbody td')[count])
                print(doc.select('div[id="quick-play"] div[class="card-stat-block"] tbody td')[count].nextSibling)
            """

            if str(item) == "<td>Time Played</td>" and time_played == 0:
                time_played = doc.select('div[id="quick-play"] div[class="card-stat-block"] tbody td'
                                         '')[count].nextSibling.getText()
            if not time_played == 0 and games_won is not 0 and medals is not 0:
                # prevent looping unnecessarily
                break
            count += 1

        """
        games_lost = int(games_played) - int(games_won)
        won_lost = "{}/{}".format(games_won, games_lost)

        try:
            win_percent = round(((float(games_won) / float(games_played)) * 100), 1)
        except ZeroDivisionError:
            win_percent = "N/A"
        """
        await self.bot.edit_message(msg, "**Overwatch Stats for {0} - {1}**\n\n"
                                         "Most Played Hero:   *{4}, {5} played*\n"
                                         "Time Played:              *{2}*\n"
                                         "Games Won:             *{3}*\n"
                                         "Medals:                      *{6}*"
                                         "".format(battletag, reg.upper(), time_played,
                                                   games_won, most_played, most_games, medals))


async def get_status(fmt):
    steam_api = 'http://is.steam.rip/api/v1/?request=SteamStatus'
    with aiohttp.ClientSession() as session:
        async with session.get(steam_api)as resp:
            data = await resp.json()
            if str(data["result"]["success"]) == "True":
                login = (data["result"]["SteamStatus"]["services"]["SessionsLogon"]).capitalize()
                community = (data["result"]["SteamStatus"]["services"]["SteamCommunity"]).capitalize()
                economy = (data["result"]["SteamStatus"]["services"]["IEconItems"]).capitalize()
                # leaderboards = (data["result"]["SteamStatus"]["services"]["LeaderBoards"]).capitalize()
                if fmt == "long":
                    reply = """**Steam Server Status**
    ```xl
    Login          {}
    Community      {}
    Economy        {}```""".format(login, community, economy)
                elif fmt == "short":
                    if str(login) != "Normal" and str(community) != "Normal" and str(economy) != "Normal":
                        reply = "Steam might be having some issues, use `!steam status! for more info."
                    # elif login is "normal" and community is "normal" and economy is "normal":
                    #    reply = "Steam is running fine - no issues detected, use `!steam status! for more info."
                    else:
                        reply = "Steam appears to be running fine."
                else:  # if wrong format
                    log.error("Wrong format given for get_status().")
                    reply = "This error has occurred because you entered an incorrect format for get_status()."

            else:
                reply = "Failed to connect to API - Error: {}".format(data["result"]["error"])

    return reply


def setup(bot):
    bot.add_cog(Games(bot))
