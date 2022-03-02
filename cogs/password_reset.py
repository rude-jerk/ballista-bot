import asyncio
import re
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
        await context.send('🤖 Hello! I will ask a few questions. Each question must be answered in a single message. '
                           'You can reply as if we were chatting, no leading "!" is necessary! '
                           'I will wait for one minute for a response after a question is asked. '
                           'If you do not have an answer, please say "I don\'t know".\n'
                           'Your information will be sent to one of our administrators to process a password reset. '
                           'This can be quick, but please give them 48 hours to respond before following up.')
        try:
            await context.send('Is this a request for an account recovery or a password reset?')
            response = await self.bot.wait_for('message', timeout=60,
                                               check=lambda message: message.author == context.author)
            recovery_or_reset = response.content.strip()
            await context.send('Please supply the username on the account:')
            response = await self.bot.wait_for('message', timeout=60,
                                               check=lambda message: message.author == context.author)
            user_name = response.content.strip()

            await context.send('Please supply the names of any characters on the account:')
            response = await self.bot.wait_for('message', timeout=60,
                                               check=lambda message: message.author == context.author)
            characters = response.content.strip()

            await context.send('Please supply the email address on the account:')
            response = await self.bot.wait_for('message', timeout=60,
                                               check=lambda message: message.author == context.author)
            email = response.content.strip()

            creation = None
            if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
                await context.send('If you cannot supply a valid email address, '
                                   'please try your best to ballpark your account creation date:')
                response = await self.bot.wait_for('message', timeout=60,
                                                   check=lambda message: message.author == context.author)
                creation = response.content.strip()

            request = discord.Embed(title=f'Password reset request from: '
                                          f'{context.author.name}#{context.author.discriminator} ')
            request.add_field(name="Recovery or Reset", value=recovery_or_reset)
            request.add_field(name='Username', value=user_name)
            request.add_field(name="Character Names", value=characters)
            request.add_field(name="Email Address", value=email)
            if creation:
                request.add_field(name="Creation Date", value=creation)
            await context.send(embed=request)
            await context.send('Would you like to submit this reset request?')
            response = await self.bot.wait_for('message', timeout=60,
                                               check=lambda message: message.author == context.author)
            confirm = response.content.strip()

            if strtobool(confirm):
                await context.send('Password reset request submitted! '
                                   'Please be patient, as these are handled by real people and can take a few days. '
                                   'You may receive a PM from a staff member to check your email to confirm.')
                await self.bot.password_channel.send(embed=request)
            else:
                await context.send('Password reset request canceled.')

        except asyncio.TimeoutError:
            await context.send('Response timeout. Password reset request canceled.')
            return


def setup(bot):
    bot.add_cog(PasswordReset(bot))
