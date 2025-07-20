import discord
from discord.ext import commands
import config
from datetime import datetime, timezone

def setup(bot):
    @bot.command(name='members')
    async def server_members(ctx):
        """Display server member statistics"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        guild = ctx.guild
        
        # Calculate member statistics
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        
        # Status counts
        online = len([m for m in guild.members if m.status == discord.Status.online])
        idle = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in guild.members if m.status == discord.Status.dnd])
        offline = len([m for m in guild.members if m.status == discord.Status.offline])
        
        # Role counts (excluding @everyone)
        roles_with_members = {}
        for role in guild.roles:
            if role.name != "@everyone" and len(role.members) > 0:
                roles_with_members[role.name] = len(role.members)
        
        # Sort roles by member count
        top_roles = sorted(roles_with_members.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Create embed
        embed = discord.Embed(
            title="<:Team:1393269975753691276> Server Members",
            color=0xFFFFFF,
            timestamp=discord.utils.utcnow()
        )
        
        # Basic statistics
        embed.add_field(
            name="📊 Member Statistics",
            value=f"**Total Members:** {total_members:,}\n"
                  f"**Humans:** {humans:,}\n"
                  f"**Bots:** {bots:,}",
            inline=True
        )
        
        # Status statistics
        embed.add_field(
            name="🟢 Status Breakdown",
            value=f"**Online:** {online:,}\n"
                  f"**Idle:** {idle:,}\n"
                  f"**Do Not Disturb:** {dnd:,}\n"
                  f"**Offline:** {offline:,}",
            inline=True
        )
        
        # Server info
        embed.add_field(
            name="🏠 Server Info",
            value=f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n"
                  f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
                  f"**Verification:** {guild.verification_level.name.title()}",
            inline=True
        )
        
        # Top roles
        if top_roles:
            role_text = "\n".join([f"**{role}:** {count:,}" for role, count in top_roles[:5]])
            embed.add_field(
                name="👥 Top Roles",
                value=role_text,
                inline=True
            )
        
        # Channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📝 Channels",
            value=f"**Text:** {text_channels}\n"
                  f"**Voice:** {voice_channels}\n"
                  f"**Categories:** {categories}",
            inline=True
        )
        
        # Features
        features = guild.features
        if features:
            feature_list = []
            feature_names = {
                'COMMUNITY': 'Community Server',
                'VERIFIED': 'Verified',
                'PARTNERED': 'Partnered',
                'DISCOVERABLE': 'Discoverable',
                'VANITY_URL': 'Vanity URL',
                'INVITE_SPLASH': 'Invite Splash',
                'BANNER': 'Banner',
                'ANIMATED_ICON': 'Animated Icon'
            }
            
            for feature in features:
                if feature in feature_names:
                    feature_list.append(feature_names[feature])
            
            if feature_list:
                embed.add_field(
                    name="✨ Server Features",
                    value="\n".join([f"• {feature}" for feature in feature_list[:5]]),
                    inline=True
                )
        
        # Server boosts
        if guild.premium_subscription_count:
            embed.add_field(
                name="💎 Nitro Boosts",
                value=f"**Level:** {guild.premium_tier}\n"
                      f"**Boosts:** {guild.premium_subscription_count}\n"
                      f"**Boosters:** {len(guild.premium_subscribers)}",
                inline=True
            )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        
        await ctx.send(embed=embed)

    @bot.command(name='memberinfo', aliases=['userinfo', 'whois'])
    async def member_info(ctx, member: discord.Member = None):
        """Get detailed information about a member"""
        # Check if user has moderation role
        if not any(role.id == config.MODERATION_ROLE_ID for role in ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        
        if member is None:
            member = ctx.author
        
        # Create embed
        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0xFFFFFF,
            timestamp=discord.utils.utcnow()
        )
        
        # Basic info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Username:** {member.name}\n"
                  f"**Discriminator:** #{member.discriminator}\n"
                  f"**ID:** {member.id}\n"
                  f"**Bot:** {'Yes' if member.bot else 'No'}",
            inline=True
        )
        
        # Dates
        embed.add_field(
            name="📅 Dates",
            value=f"**Created:** <t:{int(member.created_at.timestamp())}:R>\n"
                  f"**Joined:** <t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "**Joined:** Unknown",
            inline=True
        )
        
        # Status and activity
        status_emojis = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        
        status_text = f"{status_emojis.get(member.status, '❓')} {member.status.name.title()}"
        
        activity_text = "None"
        if member.activities:
            activity = member.activities[0]
            if activity.type == discord.ActivityType.playing:
                activity_text = f"Playing {activity.name}"
            elif activity.type == discord.ActivityType.listening:
                activity_text = f"Listening to {activity.name}"
            elif activity.type == discord.ActivityType.watching:
                activity_text = f"Watching {activity.name}"
            elif activity.type == discord.ActivityType.streaming:
                activity_text = f"Streaming {activity.name}"
            elif activity.type == discord.ActivityType.custom:
                activity_text = f"{activity.emoji} {activity.name}" if activity.name else str(activity.emoji) if activity.emoji else "Custom Status"
        
        embed.add_field(
            name="💭 Status & Activity",
            value=f"**Status:** {status_text}\n"
                  f"**Activity:** {activity_text}",
            inline=True
        )
        
        # Roles
        if len(member.roles) > 1:  # Exclude @everyone
            roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
            roles.reverse()  # Highest first
            
            if len(roles) <= 10:
                role_text = " ".join(roles)
            else:
                role_text = " ".join(roles[:10]) + f" **+{len(roles) - 10} more**"
            
            embed.add_field(
                name=f"🎭 Roles ({len(roles)})",
                value=role_text,
                inline=False
            )
        
        # Permissions
        if member.guild_permissions.administrator:
            perms_text = "Administrator (All Permissions)"
        else:
            key_perms = []
            perm_checks = {
                'manage_guild': 'Manage Server',
                'manage_channels': 'Manage Channels',
                'manage_roles': 'Manage Roles',
                'manage_messages': 'Manage Messages',
                'kick_members': 'Kick Members',
                'ban_members': 'Ban Members',
                'moderate_members': 'Moderate Members'
            }
            
            for perm, name in perm_checks.items():
                if getattr(member.guild_permissions, perm):
                    key_perms.append(name)
            
            perms_text = ", ".join(key_perms) if key_perms else "No key permissions"
        
        embed.add_field(
            name="🔑 Key Permissions",
            value=perms_text,
            inline=False
        )
        
        # Avatar and banner
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # Additional info for staff
        if member.premium_since:
            embed.add_field(
                name="💎 Nitro Booster",
                value=f"Boosting since <t:{int(member.premium_since.timestamp())}:R>",
                inline=True
            )
        
        embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")
        
        await ctx.send(embed=embed)