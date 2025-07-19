import discord
import config

async def create_ticket_channel(guild, user, reason):
    """Create a new ticket channel for a user"""
    try:
        # Get category
        category = guild.get_channel(config.TICKET_CATEGORY_ID)
        
        # Set up permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            )
        }
        
        # Add staff role permissions if configured
        if config.STAFF_ROLE_ID:
            staff_role = guild.get_role(config.STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    attach_files=True,
                    embed_links=True
                )
        
        # Create channel
        channel_name = f"ticket-{user.name.lower()}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket created by {user} - {reason}"
        )
        
        return channel
        
    except Exception as e:
        print(f"Error creating ticket channel: {e}")
        return None

def is_ticket_channel(channel):
    """Check if a channel is a ticket channel by checking if it's in the ticket category"""
    return channel.category_id == config.TICKET_CATEGORY_ID

def has_staff_permissions(member):
    """Check if a member has staff permissions"""
    if config.STAFF_ROLE_ID:
        staff_role = member.guild.get_role(config.STAFF_ROLE_ID)
        return staff_role in member.roles
    return member.guild_permissions.manage_channels