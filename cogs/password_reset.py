import asyncio
from distutils.util import strtobool

import nextcord as discord
from nextcord.ext import commands


class PasswordReset(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(name='pwreset', description='Request a password reset')
    @commands.dm_only()
    async def request_reset(self, context):
        if not self.bot.allow_password_request:
            await context.send(
                'Sorry, the password reset function has been suspended at this time. '
                'Please PM Juul or Rude for a password reset.')
            return
        await context.send('Hello! I will ask a few questions. Each question must be answered in a single message. '
                           'You can reply as if we were chatting, no leading "!" is necessary! '
                           'I will wait for one minute for a response after a question is asked. '
                           'If you do not have an answer, please say "I don\'t know".')
        try:
            await context.send('Please supply the username on the account:')
            user_name = await self.bot.wait_for('message', timeout=60,
                                                check=lambda message: message.author == context.author).content.strip()

            await context.send('Please supply the names of any characters on the account:')
            characters = await self.bot.wait_for('message', timeout=60,
                                                 check=lambda message: message.author == context.author).content.strip()

            await context.send('Please supply the email address on the account:')
            email = await self.bot.wait_for('message', timeout=60,
                                            check=lambda message: message.author == context.author).content.strip()

            request = discord.Embed(title=f'{context.author.name}#{context.author.discriminator} '
                                        f'requests a password reset.')
            request.add_field(name='Username', value=user_name)
            request.add_field(name="Character Names", value=characters)
            request.add_field(name="Email Address", value=email)
            await context.send(embed=request)
            await context.send('Would you like to submit this reset request?')
            confirm = await self.bot.wait_for('message', timeout=60,
                                              check=lambda message: message.author == context.author).content.strip()
            if strtobool(confirm):
                await context.send('Password reset request submitted! '
                                   'Please be patient, as these are handled by real people and can take a few days. '
                                   'You may receive a PM from a staff member to check your email to confirm.')

        except asyncio.TimeoutError:
            await context.send('Response timeout. Password reset request canceled.')
            return


def setup(bot):
    bot.add_cog(PasswordReset(bot))
