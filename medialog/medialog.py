from datetime import datetime; import discord; from discord.ext import commands; from core import checks; from core.models import PermissionLevel

class MediaLogger2(commands.Cog):
    """Logs all media to a specified channel"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)

    async def log_channel(self):
        config = await self.db.find_one({'_id': 'config'}) or {}
        channel_id = config.get('log_channel')
        if channel_id:
            return self.bot.get_channel(int(channel_id))

    async def in_ticket_category(self, channel):
        return not isinstance(channel, discord.DMChannel) and str(channel.category_id) == '1127651667073048747'

    @commands.Cog.listener()
    async def on_message(self, m):
        if not await self.in_ticket_category(m.channel):
            return

        em = discord.Embed(
            description=f'[Jump to Message]({m.jump_url})',
            color=self.bot.main_color,
            timestamp=datetime.utcnow()
        )
        em.set_author(name=m.author.name, icon_url=m.author.display_avatar)
        em.set_footer(text=f'U: {m.author.id} | C: {m.channel.id} | M: {m.id}')
        for a in m.attachments:
            if a.filename.endswith('.png') or a.filename.endswith('.jpeg') or a.filename.endswith('.gif') or a.filename.endswith('.jpg'):
                file = await a.to_file()
                channel = await self.log_channel()
                if channel:
                    await channel.send(file=file, embed=em)

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def setmedialogchannel(self, ctx, channel: discord.TextChannel):
        """Sets the media log channel"""
        await self.db.find_one_and_update({'_id': 'config'}, {'$set': {'log_channel': str(channel.id), 'ignored_channels': []}}, upsert=True)
        await ctx.send('Success')

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def medialogignore(self, ctx, channel: discord.TextChannel):
        """Sets the media log channel"""
        if not await self.in_ticket_category(channel):
            await self.db.find_one_and_update({'_id': 'config'}, {'$pull': {'ignored_channels': str(channel.id)}}, upsert=True)
        else:
            await self.db.find_one_and_update({'_id': 'config'}, {'$addToSet': {'ignored_channels': str(channel.id)}}, upsert=True)
        await ctx.send('Success')


async def setup(bot):
    await bot.add_cog(MediaLogger2(bot))
