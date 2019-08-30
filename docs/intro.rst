.. currentmodule:: gd

Introduction
============

gd.py is a Geometry Dash API, created to simplify interaction with GD servers.

The aim is to create a library following the best aspects of Object-Oriented Programming.

gd.py is async-ready, which means it can be easily run in parallel with other async programs.

For example, you can use it in a Discord bot:

.. code-block:: python3

    from discord.ext import commands
    import discord
    import gd

    bot = commands.Bot(command_prefix='> ')
    client = gd.Client()

    @bot.event
    async def on_ready():
        bot.client = client

        activity = discord.Activity(type=discord.ActivityType.playing, name="Geometry Dash")

        await bot.change_presence(activity=activity, status=discord.Status.online)

    @bot.command(name='daily')
    async def _get_daily(ctx):
        try:
            daily = await bot.client.get_daily()

        except gd.MissingAccess:
            # couldn't fetch a daily level
            return await ctx.send(
                embed=discord.Embed(
                    description='Failed to get a daily level.',
                    title='Error Occured', color=0xde3e35)
            )

        embed = (
            discord.Embed(color=0x7289da).set_author(name='Current Daily')
            .add_field(name='Name', value=daily.name)
            .add_field(name='Difficulty', value=f'{daily.stars} ({daily.difficulty.desc})')
            .add_field(name='ID', value=f'{daily.id}')
            .set_footer(text=f'Creator: {daily.creator.name}')
        )

        await ctx.send(embed=embed)

    bot.run('BOT_TOKEN')

(You can find documentation for ``discord.py`` library `here <https://discordpy.readthedocs.io/>`_)
