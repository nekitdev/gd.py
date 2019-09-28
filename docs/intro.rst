.. currentmodule:: gd

Introduction
============

.. image:: https://img.shields.io/pypi/l/gd.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://img.shields.io/pypi/status/gd.py.svg
    :target: https://github.com/NeKitDS/gd.py/blob/master/gd
    :alt: Project Development Status

.. image:: https://img.shields.io/pypi/dm/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Library Downloads/Month

.. image:: https://img.shields.io/pypi/v/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Required Python Versions

.. image:: https://readthedocs.org/projects/gdpy/badge/?version=latest
    :target: https://gdpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codacy.com/project/badge/Grade/4bd8cfe7a66e4250bc23b21c4e0626b6
    :target: https://app.codacy.com/project/NeKitDS/gd.py/dashboard
    :alt: Code Quality [Codacy]

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
            .add_field(name='Difficulty', value='{0.stars} ({0.difficulty.desc})'.format(daily))
            .add_field(name='ID', value='{0.id}'.format(daily))
            .set_footer(text='Creator: {0.creator.name}'.format(daily))
        )

        await ctx.send(embed=embed)

    bot.run('BOT_TOKEN')

(You can find documentation for ``discord.py`` library `here <https://discordpy.readthedocs.io/>`_)
