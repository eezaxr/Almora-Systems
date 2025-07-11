import discord
from discord.ext import commands
import config
from utils.ticket_utils import create_ticket_channel

def setup(bot):

    @bot.command(name='panel')
    async def setup_ticket_panel(ctx):
        """Set up the ticket panel with buttons"""

        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:Cross:1393269948700426341> Permission Denied",
                description="You don't have permission to use this command!",
                color=0xFFFFFF
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="<:Team:1393269975753691276> Almora Support",
            description="At Almora, we want to cater to all of our members by offering a wide variety of support. If you need to speak to a member of our Support Team, please open a ticket below.",
            color=0xFFFFFF
        )
        embed.add_field(
            name="**Before opening a ticket, be aware of these things**;",
            value="<:ArrowRight:1393269964907090014>Abusing the system will result into being moderated.\n<:ArrowRight:1393269964907090014>Please allow 24-48 hours for our team to process your enquiry.\n<:ArrowRight:1393269964907090014>Failure to respond to the ticket after a certain time will result in closure.",
            inline=False
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267553077301298/Banner1.png?ex=68728d06&is=68713b86&hm=faae5dcd1923d5285ef234b09e47fafd84793088bfac7bc364cbc536032e1901&=&format=webp&quality=lossless&width=1318&height=326")
        
        view = TicketPanelView()
        await ctx.send(embed=embed, view=view)

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Create Ticket', 
        style=discord.ButtonStyle.gray, 
        emoji='<:Team:1393269975753691276>',
        custom_id='create_ticket_button'
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        existing_ticket = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name.lower()}")

        if existing_ticket:
            embed = discord.Embed(
                title="<:Warning:1393269985031487528> Ticket Already Exists",
                description=f"You already have an open ticket: {existing_ticket.mention}",
                color=0x5C3BB9
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        modal = TicketReasonModal()
        await interaction.response.send_modal(modal)

class TicketReasonModal(discord.ui.Modal, title='Create Support Ticket'):
    def __init__(self):
        super().__init__()

    reason = discord.ui.TextInput(
        label='Reason for ticket',
        placeholder='Please describe your issue or question.',
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):

        ticket_channel = await create_ticket_channel(interaction.guild, interaction.user, self.reason.value)

        if ticket_channel:

            success_embed = discord.Embed(
                title="<:Tick:1393269945500045473> Ticket Created Successfully",
                description=f"Your ticket has been created: {ticket_channel.mention}",
                color=0x5C3BB9
            )

            await interaction.response.send_message(embed=success_embed, ephemeral=True)

            support_role = interaction.guild.get_role(config.STAFF_ROLE_ID)
            if support_role:
                ping_message = await ticket_channel.send(f"{support_role.mention} - New ticket created!")
                await ping_message.delete()

            embed = discord.Embed(
                title="<:Team:1393269975753691276> Support Ticket",
                description=f"**Created by:** {interaction.user.mention}\n**Reason:** {self.reason.value}\n\nA staff member will be with you shortly.",
                color=0x5C3BB9
            )
            embed.set_footer(text="Use !close to close this ticket")

            embed.set_image(url="https://media.discordapp.net/attachments/1301667213131907170/1393267567925137478/Banner2.png?ex=68728d09&is=68713b89&hm=3848c521166c97401f3eaac93d3ed9b0901279cab8ae433b4a7a48600d1a000e&=&format=webp&quality=lossless&width=1318&height=63")
            await ticket_channel.send(embed=embed)
        else:
            
            error_embed = discord.Embed(
                title="<:Cross:1393269948700426341> Ticket Creation Failed",
                description="Failed to create ticket. Please contact the Network Administrator.",
                color=0x5C3BB9
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)