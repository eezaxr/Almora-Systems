import discord
import config

# Configure your general roles here
GENERAL_ROLES = [
    {
        "name": "Shifts Ping",
        "role_id": 1393356313173692518,  # Replace with actual role ID
        "emoji": "<:Shifts:1393545049832292482>",
        "description": "Get pinged for shifts"
    },
    {
        "name": "Engagement Ping",
        "role_id": 1393356313869942914,  # Replace with actual role ID
        "emoji": "<:Alert:1393545728923668590>",
        "description": "Get pinged for engagement activities"
    },
    {
        "name": "Bored Ping",
        "role_id": 1393356314448498759,  # Replace with actual role ID
        "emoji": "<:Meh:1393545287477235885>",
        "description": "Get pinged when people are bored"
    }
]

# Configure your pronouns roles here
PRONOUNS_ROLES = [
    {
        "name": "He/Him",
        "role_id": 1393356315245674586,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "He/Him pronouns"
    },
    {
        "name": "She/Her",
        "role_id": 1393356315593801729,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "She/Her pronouns"
    },
    {
        "name": "They/Them",
        "role_id": 1393356316617085018,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "They/Them pronouns"
    },
    {
        "name": "Ask Me",
        "role_id": 1393546048118722602,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "Ask about pronouns"
    }
]

def has_staff_permissions(member):
    """Check if a member has staff permissions"""
    # Check if user is the specific user ID or has staff role
    if member.id == 790869950076157983:
        return True
    staff_role = discord.utils.get(member.roles, id=config.STAFF_ROLE_ID)
    return staff_role is not None

class GeneralRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add buttons for each general role
        for role_data in GENERAL_ROLES:
            button = ReactionRoleButton(
                label=role_data["name"],
                emoji=role_data["emoji"],
                role_id=role_data["role_id"],
                description=role_data["description"]
            )
            self.add_item(button)

class PronounsRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add buttons for each pronouns role
        for role_data in PRONOUNS_ROLES:
            button = ReactionRoleButton(
                label=role_data["name"],
                emoji=role_data["emoji"],
                role_id=role_data["role_id"],
                description=role_data["description"]
            )
            self.add_item(button)

class ReactionRoleButton(discord.ui.Button):
    def __init__(self, label, emoji, role_id, description):
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            custom_id=f"reaction_role_{role_id}"
        )
        self.role_id = role_id
        self.description = description

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        
        if not role:
            await interaction.response.send_message(
                "<:Cross:1393269948700426341> Role not found! Please contact an administrator.",
                ephemeral=True
            )
            return

        member = interaction.user
        
        if role in member.roles:
            # Remove role
            await member.remove_roles(role)
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Role Removed",
                description=f"The **{role.name}** role has been removed from you.",
                color=0xFF0000
            )
        else:
            # Add role
            await member.add_roles(role)
            embed = discord.Embed(
                title="<:Checkmark:1393269948700426340> Role Added",
                description=f"You have been given the **{role.name}** role!",
                color=0x00FF00
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)