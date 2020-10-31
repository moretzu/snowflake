#  The MIT License (MIT)
#
#  Copyright (c) 2020 cyber-snowflake
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import asyncio
import random
import sys
from io import BytesIO

from discord import File, PartialEmoji
from discord.ext import commands
from gtts import gTTS
from polyglot.detect import Detector

from bot import BigMommy
from utils.decos import aioify


class Fun(commands.Cog):
    def __init__(self, bot: BigMommy):
        self.bot = bot

    @staticmethod
    @aioify
    def make_tts(text: str, *, language_code: str = None):
        """Generates TTS audio in bytes"""
        fp = BytesIO()

        detected_language = language_code or Detector(text, quiet=True).language.code
        tts = gTTS(text, lang=detected_language)

        tts.write_to_fp(fp)
        fp.seek(0)

        return fp

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tts(self, ctx: commands.Context, *, text: str):
        """Converts text into a speech"""
        await ctx.trigger_typing()

        if len(text) <= 4:
            return await ctx.send(":x: Your text is too short.")

        fp = await self.make_tts(text)
        file = File(fp, filename=f"{ctx.author} Text-To-Speech.mp3")

        if round((sys.getsizeof(fp) / 1048576), 2) > 5:
            return await ctx.send(":x: Resulting file bigger than 5 MB.")

        await ctx.send(f":sparkles: {ctx.author.mention}, here's your tts!", file=file)

    @commands.command(aliases=("rt",))
    @commands.cooldown(1, 3, commands.BucketType.channel)
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True)
    @commands.guild_only()
    async def reactiontest(self, ctx: commands.Context):
        emoji_sequence = tuple(e for e in (*ctx.guild.emojis, PartialEmoji(name="❤")) if e.animated is False)
        emoji = random.choice(emoji_sequence)

        msg = await ctx.send("Be ready! React with the emoji as soon as it appears on this message.")
        await asyncio.sleep(3)
        await msg.add_reaction(emoji)

        def check(r, u):
            return str(r.emoji) == str(emoji) and r.message.id == msg.id and u.id != self.bot.user.id

        try:
            reaction, winner = await self.bot.wait_for("reaction_add", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(content="Nobody has finished my reaction test :(")
        else:
            await msg.edit(content=f"~~{msg.content}~~\n{winner.mention} wins! :tada:")


def setup(bot):
    bot.add_cog(Fun(bot))
