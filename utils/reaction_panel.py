import discord
import config

# Configure your reaction roles here
REACTION_ROLES = [
    {
        "name": "Session Ping",
        "role_id": 1393356313173692518,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "Get pinged when there is a session"
    },
    {
        "name": "Engagement Ping",
        "role_id": 1393356313869942914,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "Get pinged when there is a QOTD or event"
    },
    {
        "name": "Bored Ping",
        "role_id": 1393356314448498759,  # Replace with actual role ID
        "emoji": "<:Person:1393269972888846439>",
        "description": "Get random pings when the server is quiet"
    }
    
]

def has_staff_permissions(member):
    """Check if a member has staff permissions"""
    # Check if user is the specific user ID or has staff role
    if member.id == 790869950076157983:
        return True
    staff_role = discord.utils.get(member.roles, id=config.STAFF_ROLE_ID)
    return staff_role is not None

class ReactionRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add buttons for each reaction role
        for role_data in REACTION_ROLES:
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
                color=0xFFFFFF
            )
        else:
            # Add role
            await member.add_roles(role)
            embed = discord.Embed(
                title="<:Tick:1393269945500045473> Role Added",
                description=f"You have been given the **{role.name}** role!",
                color=0xFFFFFF
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)