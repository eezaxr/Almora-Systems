import discord
from discord.ext import commands
import config
from typing import Dict, Optional

class InviteTracker:
    def __init__(self, bot):
        self.bot = bot
        self.invites_cache: Dict[int, Dict[str, int]] = {}  # guild_id -> {invite_code: uses}
        self.invite_users: Dict[int, Dict[str, int]] = {}  # guild_id -> {invite_code: inviter_id}
        self.user_invite_counts: Dict[int, Dict[int, int]] = {}  # guild_id -> {user_id: total_invites}
    
    async def update_invite_cache(self, guild: discord.Guild):
        """Update the invite cache for a guild"""
        try:
            invites = await guild.invites()
            if guild.id not in self.invites_cache:
                self.invites_cache[guild.id] = {}
                self.invite_users[guild.id] = {}
                self.user_invite_counts[guild.id] = {}
            
            for invite in invites:
                self.invites_cache[guild.id][invite.code] = invite.uses
                if invite.inviter:
                    self.invite_users[guild.id][invite.code] = invite.inviter.id
                    # Update user's total invite count
                    if invite.inviter.id not in self.user_invite_counts[guild.id]:
                        self.user_invite_counts[guild.id][invite.inviter.id] = 0
                    self.user_invite_counts[guild.id][invite.inviter.id] += invite.uses
            
        except discord.Forbidden:
            print(f"Bot doesn't have permission to view invites in {guild.name}")
        except Exception as e:
            print(f"Error updating invite cache: {e}")
    
    async def find_used_invite(self, guild: discord.Guild):
        """Find which invite was used when someone joined"""
        try:
            current_invites = await guild.invites()
            
            for invite in current_invites:
                cached_uses = self.invites_cache.get(guild.id, {}).get(invite.code, 0)
                if invite.uses > cached_uses:
                    # This invite was used
                    self.invites_cache[guild.id][invite.code] = invite.uses
                    inviter_id = self.invite_users[guild.id].get(invite.code)
                    if inviter_id:
                        # Update inviter's total count
                        if inviter_id not in self.user_invite_counts[guild.id]:
                            self.user_invite_counts[guild.id][inviter_id] = 0
                        self.user_invite_counts[guild.id][inviter_id] += 1
                        return inviter_id
            
            return None
        except Exception as e:
            print(f"Error finding used invite: {e}")
            return None
    
    async def send_invite_notification(self, member: discord.Member, inviter_id: Optional[int]):
        """Send the invite notification"""
        try:
            channel = self.bot.get_channel(config.INVITE_CHANNEL_ID)
            if not channel:
                print(f"Could not find invite channel with ID {config.INVITE_CHANNEL_ID}")
                return
            
            if inviter_id:
                # Found who invited the user
                inviter = member.guild.get_member(inviter_id)
                if not inviter:
                    print("Could not find inviter")
                    # Still send a message that we couldn't determine who invited them
                    message = f"I could not find out how {member.mention} joined the server."
                else:
                    total_invites = self.user_invite_counts.get(member.guild.id, {}).get(inviter_id, 0)
                    message = f"{member.mention} has been invited by {inviter.mention} and has now {total_invites} invites."
            else:
                # Could not determine who invited the user
                message = f"I could not find out how {member.mention} joined the server."
            
            await channel.send(message)
            print(f"Sent invite notification for {member.display_name}")
            
        except Exception as e:
            print(f"Error sending invite notification: {e}")

# Global tracker instance
tracker = None

def setup_invite_tracking(bot):
    """Setup the invite tracking system"""
    global tracker
    tracker = InviteTracker(bot)
    print("Invite tracking setup complete")

async def handle_member_join(member: discord.Member):
    """Handle when a member joins - call this from your existing on_member_join event"""
    if tracker is None:
        print("Invite tracker not initialized")
        return
    
    if member.bot:
        return  # Ignore bots
    
    try:
        # Find who invited this member
        inviter_id = await tracker.find_used_invite(member.guild)
        
        # Always send a notification, whether we found the inviter or not
        await tracker.send_invite_notification(member, inviter_id)
        
        if not inviter_id:
            print(f"Could not determine who invited {member.display_name}")
    
    except Exception as e:
        print(f"Error handling member join for invite tracking: {e}")

async def cache_invites_for_guild(guild: discord.Guild):
    """Cache invites for a guild - call this when bot is ready"""
    if tracker is None:
        print("Invite tracker not initialized")
        return
    
    await tracker.update_invite_cache(guild)
    print(f"Cached invites for {guild.name}")

# Command functions
def setup_invite_commands(bot):
    """Setup invite-related commands"""
    
    @bot.command(name="invites")
    async def check_invites(ctx, member: discord.Member = None):
        """Check how many invites a user has"""
        if member is None:
            member = ctx.author
        
        if tracker is None:
            await ctx.send("Invite tracking is not initialized.")
            return
        
        total_invites = tracker.user_invite_counts.get(ctx.guild.id, {}).get(member.id, 0)
        await ctx.send(f"**{member.display_name}** has **{total_invites}** invites.")
    
    @bot.command(name="refresh_invites")
    async def refresh_invites(ctx):
        """Refresh the invite cache (admin only)"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need Manage Server permission to use this command.")
            return
        
        if tracker is None:
            await ctx.send("Invite tracking is not initialized.")
            return
        
        await tracker.update_invite_cache(ctx.guild)
        await ctx.send("Invite cache refreshed!")
    
    print("Invite commands setup complete")