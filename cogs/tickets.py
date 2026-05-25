import discord
from discord.ext import commands
from views.ticket_panel import TicketPanel
from views.ticket_controls import TicketControls
from config import EMBED_COLOR

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.author.bot:
            return

        
        if isinstance(message.channel, discord.DMChannel):
            ticket = self.bot.db.cur.execute(
                "SELECT * FROM tickets WHERE user_id=? AND open=1",
                (message.author.id,)
            ).fetchone()

            if not ticket:
                await message.channel.send(
                    "📩 Para abrir um ticket, use o **painel de tickets** no servidor."
                )
                return

            channel = self.bot.get_channel(ticket["channel_id"])
            if not channel:
                await message.channel.send(
                    "⚠️ Não encontrei o canal do seu ticket."
                )
                return

            content = f"**{message.author}**: {message.content or '*Mensagem sem texto*'}"
            files = [await a.to_file() for a in message.attachments]

            await channel.send(content=content, files=files)
            return  

        
        ticket = self.bot.db.cur.execute(
            "SELECT * FROM tickets WHERE channel_id=? AND open=1",
            (message.channel.id,)
        ).fetchone()

        if not ticket:
            return  

        user = self.bot.get_user(ticket["user_id"])
        if not user:
            return

        content = f"**Staff**: {message.content or '*Mensagem sem texto*'}"
        files = [await a.to_file() for a in message.attachments]

        try:
            await user.send(content=content, files=files)
        except discord.Forbidden:
            await message.channel.send(
                "❌ Não foi possível enviar DM para o usuário (DM fechada)."
            )

    @commands.hybrid_command(name="enviar")
    @commands.has_permissions(administrator=True)
    async def enviar(self, ctx, canal: discord.TextChannel):
        embed = discord.Embed(
            title="📩 Suporte",
            description="Clique no botão abaixo para abrir um ticket.",
            color=EMBED_COLOR
        )

        await canal.send(
            embed=embed,
            view=TicketPanel(self.bot)
        )

        await ctx.reply("✅ Painel enviado com sucesso.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))