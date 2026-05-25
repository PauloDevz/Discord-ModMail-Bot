import discord
from discord.ui import View, Button, Modal, TextInput

class CategoryModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Categoria dos Tickets")
        self.bot = bot

        self.category = TextInput(
            label="ID da categoria",
            placeholder="Cole o ID da categoria",
            required=True
        )
        self.add_item(self.category)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cat_id = int(self.category.value)
            category = interaction.guild.get_channel(cat_id)
            if not isinstance(category, discord.CategoryChannel):
                raise ValueError
        except:
            return await interaction.response.send_message(
                "❌ Categoria inválida.", ephemeral=True
            )

        self.bot.db.cur.execute(
            """
            INSERT INTO guilds (guild_id, category_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET category_id=excluded.category_id
            """,
            (interaction.guild.id, cat_id)
        )
        self.bot.db.conn.commit()

        await interaction.response.send_message(
            "✅ Categoria configurada com sucesso.", ephemeral=True
        )


class SupportRolesModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Cargos de Suporte")
        self.bot = bot

        self.roles = TextInput(
            label="IDs dos cargos (separados por vírgula)",
            required=True
        )
        self.add_item(self.roles)

    async def on_submit(self, interaction: discord.Interaction):
        ids = []
        for r in self.roles.value.split(","):
            role = interaction.guild.get_role(int(r.strip())) if r.strip().isdigit() else None
            if role:
                ids.append(str(role.id))

        if not ids:
            return await interaction.response.send_message(
                "❌ Nenhum cargo válido.", ephemeral=True
            )

        self.bot.db.cur.execute(
            "UPDATE guilds SET support_roles=? WHERE guild_id=?",
            (",".join(ids), interaction.guild.id)
        )
        self.bot.db.conn.commit()

        await interaction.response.send_message(
            "✅ Cargos de suporte configurados.", ephemeral=True
        )


class LogChannelModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Canal de Logs")
        self.bot = bot

        self.channel = TextInput(
            label="ID do canal",
            required=True
        )
        self.add_item(self.channel)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            ch_id = int(self.channel.value)
            channel = interaction.guild.get_channel(ch_id)
            if not isinstance(channel, discord.TextChannel):
                raise ValueError
        except:
            return await interaction.response.send_message(
                "❌ Canal inválido.", ephemeral=True
            )

        self.bot.db.cur.execute(
            "UPDATE guilds SET log_channel=? WHERE guild_id=?",
            (ch_id, interaction.guild.id)
        )
        self.bot.db.conn.commit()

        await interaction.response.send_message(
            "✅ Canal de logs configurado.", ephemeral=True
        )


class CategoryButton(Button):
    def __init__(self, bot):
        super().__init__(label="Categoria", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CategoryModal(self.bot))


class RolesButton(Button):
    def __init__(self, bot):
        super().__init__(label="Cargo Suporte", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SupportRolesModal(self.bot))


class LogsButton(Button):
    def __init__(self, bot):
        super().__init__(label="Canal de Logs", style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(LogChannelModal(self.bot))


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            MessageModal(self.bot, self.field, self.title)
        )


class ConfigPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)

        self.add_item(CategoryButton(bot))
        self.add_item(RolesButton(bot))
        self.add_item(LogsButton(bot))

        
    async def interaction_check(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores.", ephemeral=True
            )
            return False
        return True