import discord
from discord.ui import View, button, Modal, TextInput


class CloseModal(Modal):
    motivo = TextInput(
        label="Motivo do fechamento",
        required=True,
        max_length=300
    )

    def __init__(self, bot, channel, ticket_owner: discord.User):
        super().__init__(title="Fechar Ticket")
        self.bot = bot
        self.channel = channel
        self.ticket_owner = ticket_owner

    async def on_submit(self, interaction: discord.Interaction):
        
        self.bot.db.close_ticket(self.channel.id)

        
        try:
            embed_dm = discord.Embed(
                title="🔒 Ticket Fechado",
                description=f"📄 Motivo: {self.motivo.value}",
                color=0xFF0000
            )
            await self.ticket_owner.send(embed=embed_dm)
        except discord.Forbidden:
            pass  

        
        embed_response = discord.Embed(
            title="🔒 Ticket Fechado",
            description="Ticket fechado com sucesso.",
            color=0xFF0000
        )
        await interaction.response.send_message(
            embed=embed_response,
            ephemeral=True
        )

        
        await self.channel.delete()


class TicketControls(View):
    def __init__(self, bot, user: discord.User):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user  

    @button(
        label="🔒 Fechar Ticket",
        style=discord.ButtonStyle.danger
    )
    async def close(self, interaction: discord.Interaction, _):

        
        if (
            interaction.user != self.user
            and not interaction.user.guild_permissions.manage_channels
        ):
            embed_no_perm = discord.Embed(
                title="❌ Sem Permissão",
                description="Você não tem permissão para fechar este ticket.",
                color=0xFF0000
            )
            await interaction.response.send_message(
                embed=embed_no_perm,
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            CloseModal(
                bot=self.bot,
                channel=interaction.channel,
                ticket_owner=self.user
            )
        )