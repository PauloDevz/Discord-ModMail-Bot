import discord
from discord.ui import View, button
from views.ticket_controls import TicketControls
from config import EMBED_COLOR


class TicketPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label="📩 Abrir Ticket", style=discord.ButtonStyle.primary)
    async def open(self, interaction: discord.Interaction, _):
        guild = interaction.guild
        user = interaction.user

      
        if self.bot.db.get_ticket(user.id, guild.id):
            embed_existente = discord.Embed(
                title="❌ Ticket Já Aberto",
                description="Você já possui um ticket aberto.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed_existente, ephemeral=True)
            return

        
        data = self.bot.db.cur.execute(
            "SELECT * FROM guilds WHERE guild_id=?",
            (guild.id,)
        ).fetchone()

        if not data or not data["category_id"]:
            embed_nao_config = discord.Embed(
                title="⚠️ Sistema Não Configurado",
                description="O sistema de tickets ainda não foi configurado neste servidor.",
                color=0xFFFF00
            )
            await interaction.response.send_message(embed=embed_nao_config, ephemeral=True)
            return

        category = guild.get_channel(data["category_id"])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites
        )

        
        self.bot.db.cur.execute(
            "INSERT INTO tickets VALUES (?, ?, ?, 1)",
            (user.id, guild.id, channel.id)
        )
        self.bot.db.conn.commit()

        
        embed_ticket = discord.Embed(
            title="🎫 Ticket Aberto",
            description=f"Usuário: {user.mention}\nO atendimento será feito por DM.",
            color=EMBED_COLOR
        )
        msg = await channel.send(embed=embed_ticket, view=TicketControls(self.bot, user))
        await msg.pin()

        
        dm_ok = True
        try:
            embed_dm = discord.Embed(
                title="✅ Ticket Criado",
                description="Seu ticket foi aberto com sucesso!\nEnvie sua mensagem respondendo esta DM.\nNossa equipe acompanhará pelo servidor.",
                color=0x00FF00
            )
            await user.send(embed=embed_dm)
        except discord.Forbidden:
            dm_ok = False

        if dm_ok:
            embed_ephemeral = discord.Embed(
                title="📨 Ticket Criado",
                description="Verifique sua DM para continuar o atendimento.",
                color=0x00FF00
            )
        else:
            embed_ephemeral = discord.Embed(
                title="📨 Ticket Criado",
                description="Não consegui enviar DM. Ative suas mensagens diretas e tente novamente.",
                color=0xFF0000
            )

        await interaction.response.send_message(embed=embed_ephemeral, ephemeral=True)