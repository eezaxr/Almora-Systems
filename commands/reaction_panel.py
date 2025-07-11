import discord
from discord.ext import commands
import config
from utils.reaction_panel import REACTION_ROLES, ReactionRoleView, has_staff_permissions

def setup(bot):
    @bot.command(name='reactpanel')
    async def create_reaction_panel(ctx):
        """Create a reaction role panel (Staff only)"""
        
        # Check if user has staff permissions
        if not has_staff_permissions(ctx.author):
            await ctx.send("You don't have permission to use this command.")
            return
        
        # Create embed
        embed = discord.Embed(
            title="<:Group:1393269978031067137> Reaction Roles",
            description="Click the buttons below to get or remove roles.",
            color=0xFFFFFF
        )
        
        # Add field for each role
        for role_data in REACTION_ROLES:
            embed.add_field(
                name=f"{role_data['emoji']} {role_data['name']}",
                value=role_data['description'],
                inline=False
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1393317286248448200/1393317450367369277/image.png?ex=6872bb7e&is=687169fe&hm=679a83259dbb1029cd71ad93e4b74d7979a48365ec7969cebeacfd9905a1d3b4&=&format=webp&quality=lossless")


        # Send the panel
        view = ReactionRoleView()
        await ctx.send(embed=embed, view=view)
        
        # Delete the command message
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass