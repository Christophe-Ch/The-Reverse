from discord.ext import commands, tasks
import asyncio
from urllib import parse
from discord import Embed

from reverse.core._service import SqliteService, TaskService, loop
from reverse.core._models import Context
from reverse.core import utils

class Debugger(commands.Cog):
	
	def __init__(self, bot):
		self.bot = bot
		try:
			self.config = utils.load_custom_config('config.json', __file__, path='')
		except:
			self.config = None
		self.task = TaskService('Debugger')
		
	@commands.command()
	async def debugdb(self, ctx):
		print('{} asked for debug info on database'.format(ctx.author.name))
		server = SqliteService()
		embed=Embed(title="Debugger Database SQLITE", color=0xe80005)
		embed.set_author(name="The reverse")
		embed.add_field(name="env value", value=server.getEnvSqlite(), inline=False)
		embed.add_field(name="fullpath", value=server.getDBFullpath(), inline=False)
		embed.add_field(name="database name", value=server.getDBName(), inline=False)
		embed.add_field(name="database path", value=server.getDBPath(), inline=False)
		embed.add_field(name="in transaction", value=server.getInstance().in_transaction, inline=False)
		embed.add_field(name="isolation level", value=server.getInstance().in_transaction, inline=False)
		embed.add_field(name="Configuration Debugger", value=self.config, inline=False)
		embed.set_footer(text="Asked by {}".format(ctx.author.name))
		message = await ctx.send(embed=embed)
		self.lastEmbed = message
	
	@commands.command()
	async def updateEmbed(self, ctx):
			if self.lastEmbed is not None:
				embed = self.lastEmbed.embeds[0]
				timestamp = None
				modifier = "Timestamps"
				for index, field in enumerate(embed.fields):
					if modifier == field.name:
						timestamp = index
						break
				import time
				if timestamp is not None:
					embed.set_field_at(timestamp, name=modifier, value=time.time())
				else:
					embed.add_field(name=modifier, value=time.time(), inline=False)
				await self.lastEmbed.edit(embed = embed)
	
	@commands.command()
	async def debugloop(self, ctx, *args):
		_kwargs, _args = utils.parse_args(args)
		data = {
			"index": 0,
			"loop": 5 
		}
		try:
			data["loop"] = _kwargs["loop"]
		except:
			pass
		_loop = self.task.createLoop(self.loop_for_debug, seconds=1.0, count=data["loop"], ctx=Context(ctx), data=data)
		self._debugloop = _loop
		_loop.start(ctx=_loop.ctx, data=_loop.data)
	
	async def testloop(self, ctx):
		await ctx.send(self._debugloop.data)

	async def loop_for_debug(self, **kwargs):
		print(kwargs['data']['index'])
		print(kwargs['ctx'].author)
		kwargs['data']['index'] += 1
		await self.testloop(kwargs['ctx'])
		print("hi loop")

	@commands.command()
	async def testargs(self, ctx, *args):
		_kwargs, _args = utils.parse_args(args)
		embed=Embed(title="Debugger args parser", color=0xe80005)
		embed.set_author(name="The reverse")
		embed.add_field(name="command", value=args, inline=False)
		embed.add_field(name="args", value=_args, inline=False)
		embed.add_field(name="kwargs", value=_kwargs, inline=False)
		embed.set_footer(text="Asked by {}".format(ctx.author.name))
		message = await ctx.send(embed=embed)
		self.lastEmbed = message

def setup(bot):
	bot.add_cog(Debugger(bot))