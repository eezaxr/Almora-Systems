import discord
from discord.ext import commands
import config
from utils.reaction_panel import GENERAL_ROLES, PRONOUNS_ROLES, GeneralRolesView, PronounsRolesView, has_staff_permissions

def setup(bot):
    @bot.command(name='reactpanel')
    async def create_reaction_panel(ctx):
        """Create a reaction role panel (Staff only)"""
        
        # Check if user has staff permissions
        if not has_staff_permissions(ctx.author):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Create ALMORA RETAIL banner embed
        banner_embed = discord.Embed(color=0x2b2d31)
        banner_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317378938638427/WhiteLogo_1.png?ex=6873642d&is=687212ad&hm=d7128cd50d9b8d1a12b18cd5e27e50b3eb1bcdf5e564efe146c80ff1567f44ee&=&format=webp&quality=lossless")
        
        # Create main description embed
        main_embed = discord.Embed(
            title="**Reaction Roles**",
            description="Welcome to the Reaction Roles channel! Customise your profile by picking from a variety of roles. Connect to a community of members with the same roles, use the buttons below to apply the roles you require.",
            color=0x2b2d31
        )
        main_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6873643e&is=687212be&hm=411e76963bd9f2277315ba7b3047e2eb7ad3b5692d1f9c81b2c553c9fd12e92b&=&format=webp&quality=lossless")

        
        # Create General Roles list embed
        general_roles_embed = discord.Embed(
            title="**General Roles**",
            description="<:ArrowRight:1393269964907090014> Shifts Ping\n<:ArrowRight:1393269964907090014> Engagement Ping\n<:ArrowRight:1393269964907090014> Bored Ping",
            color=0x2b2d31
        )
        general_roles_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6873643e&is=687212be&hm=411e76963bd9f2277315ba7b3047e2eb7ad3b5692d1f9c81b2c553c9fd12e92b&=&format=webp&quality=lossless")
        
        # Create Pronouns embed
        pronouns_embed = discord.Embed(
            title="**Pronouns Roles**",
            description="<:ArrowRight:1393269964907090014> He/Him\n<:ArrowRight:1393269964907090014> She/Her\n<:ArrowRight:1393269964907090014> They/Them\n<:ArrowRight:1393269964907090014> Ask Me",
            color=0x2b2d31
        )
        pronouns_embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6873643e&is=687212be&hm=411e76963bd9f2277315ba7b3047e2eb7ad3b5692d1f9c81b2c553c9fd12e92b&=&format=webp&quality=lossless")
        
        # Create views for each embed
        general_view = GeneralRolesView()
        pronouns_view = PronounsRolesView()
        
        # Send the panels
        await ctx.send(embed=banner_embed)
        await ctx.send(embed=main_embed)
        await ctx.send(embed=general_roles_embed, view=general_view)
        await ctx.send(embed=pronouns_embed, view=pronouns_view)
        
        # Delete the command message
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass