
import discord
from discord.ext import commands
from discord import app_commands
from views.config_panel import ConfigPanel
from config import EMBED_COLOR

class Panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="painel", description="Painel de configuração do ModMail")
    @app_commands.checks.has_permissions(administrator=True)
    async def painel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Painel do ModMail",
            description=(
                "Configure todo o sistema usando os botões abaixo.\n\n"
                "Categoria dos tickets\n"
                "Cargos da equipe\n"
                "Canal de logs\n"
                "Powered By Hosta Cloud"
            ),
            color=EMBED_COLOR
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfigPanel(self.bot),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Panel(bot))