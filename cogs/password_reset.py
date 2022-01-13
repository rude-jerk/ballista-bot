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
                           'I will wait for one minute for a response after a question is asked. '
                           'If you do not have an answer, please say "I don\'t know".')

        await context.send('Please supply the names of any characters on the account:')
        character_names = await self.bot.wait_for('message', timeout=60,
                                                  check=lambda message: message.author == context.author)
        if not character_names:
            await context.send('Password reset request canceled.')
            return

        await context.send('Please supply the email address on the account:')
        email_address = await self.bot.wait_for('message', timeout=60,
                                                check=lambda message: message.author == context.author)
        if not email_address:
            await context.send('Password reset request canceled.')
            return

        await context.send('Please supply the username on the account:')
        user_name = await self.bot.wait_for('message', timeout=60,
                                            check=lambda message: message.author == context.author)
        if not user_name:
            await context.send('Password reset request canceled.')
            return


def setup(bot):
    bot.add_cog(PasswordReset(bot))
