import nextcord, datetime, json, re, httpx, certifi
from nextcord import Interaction, SlashOption, Embed
from nextcord.ext import commands
from nextcord.ui import View, Select, Button
import asyncio
import json
import logging
from utils.embeds import message_delete_embed, messageU, messageUN, channelUN, channelUNSFW, channelUP, channelUT, channelURPU

config = json.load(open('./config.json', 'r', encoding='utf-8'))

intents = nextcord.Intents.all()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(
    command_prefix='!',
    help_command=None,
    intents=nextcord.Intents.all(),
    strip_after_prefix=True,
    case_insensitive=True
)


@bot.event
async def on_ready():
    bot.add_view(SetupView())
    print(f'LOGIN AS {bot.user}')

class SelectMenu(nextcord.ui.Select):
    def __init__(self):
        options = self._get_options()
        super().__init__(
            placeholder='[ เลือกเกมที่คุณต้องการที่จะเติม ]',
            options=options,
            custom_id='select-game'
        )

    def _get_options(self):
        options = []
        with open('./database/embed.json', 'r', encoding='utf-8') as f:
            roleJSON = json.load(f)
        for role_id, role_data in roleJSON.items():
            options.append(nextcord.SelectOption(
                label=role_data['name'],
                description=role_data['description'],
                value=role_id,
                emoji=role_data['emoji']
            ))
        return options

    async def callback(self, interaction: nextcord.Interaction):
        selected = self.values[0]
        with open('./database/embed.json', 'r', encoding='utf-8') as f:
            roleJSON = json.load(f)

        if selected in roleJSON and 'embed' in roleJSON[selected]:
            embed_data = roleJSON[selected]['embed']
            embed = nextcord.Embed(
                title=embed_data['title'],
                description=embed_data['description'],
                color=embed_data['color']
            )

            if 'thumbnail' in embed_data:
                embed.set_thumbnail(url=embed_data['thumbnail'])
            if 'image' in embed_data:
                embed.set_image(url=embed_data['image'])

            button_labels = {f'button_label{i}': roleJSON[selected].get(f'button_label{i}') for i in range(0, 16)}
            view = PurchaseView(role_id=selected, **button_labels)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message(content='Error: Embed not found for the selected option.', ephemeral=True)
    


class PurchaseButton(nextcord.ui.Button):
    def __init__(self, label, role_id, pack_name):
        super().__init__(label=label, style=nextcord.ButtonStyle.primary)
        self.role_id = role_id
        self.pack_name = pack_name

    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed()
        embed.title = '───       Meow - ร้านเติมเกมสุดคุ้ม       ───'
        embed.description = f'''
        »»———   　ยืนยันการสั่งซื้อ　   ——-««
        
        　คุณแน่ใจไหมที่จะซื้อ {self.pack_name}　'''
        embed.color = nextcord.Color.green()

        embed.set_thumbnail(url='https://media.discordapp.net/attachments/1041602377955954718/1041602447967268874/371A4132-5B3D-4A7A-A8DA-5FB9DB40DB0C.png?ex=669f4f5f&is=669dfddf&hm=24d3c35b545b254c1fdffe2d9bf11d588de905904583ed6de449d9b8fe968ac9&=&format=webp&quality=lossless&width=701&height=701')

        view = PurchaseConfirmView(self.role_id, self.pack_name)
        await interaction.response.edit_message(embed=embed, view=view)


class PurchaseConfirmView(nextcord.ui.View):
    def __init__(self, role_id, pack_name):
        super().__init__(timeout=60)
        self.role_id = role_id
        self.pack_name = pack_name

    @nextcord.ui.button(label='ยืนยัน', style=nextcord.ButtonStyle.success)
    async def confirm_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = PurchaseModal(self.role_id, self.pack_name)
        await interaction.response.send_modal(modal)

    @nextcord.ui.button(label='ยกเลิก', style=nextcord.ButtonStyle.danger)
    async def cancel_callback(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # Logic สำหรับการยกเลิกการซื้อ
        await interaction.response.edit_message(content="ยกเลิกการซื้อเรียบร้อยค่ะ", embed=None, view=None)

    
class PurchaseModal(nextcord.ui.Modal):
    def __init__(self, role_id, pack_name):
        self.role_id = role_id
        self.pack_name = pack_name
        super().__init__(title="ฟอร์มการซื้อ")

        self.add_item(nextcord.ui.TextInput(label="เกมที่จะเติม", placeholder="กรอกชื่อเกม", required=True))
        self.add_item(nextcord.ui.TextInput(label="UID หรือ Username", placeholder="กรอก UID หรือ Username ของคุณ", required=True))

    async def callback(self, interaction: nextcord.Interaction):
        game_name = self.children[0].value
        username = self.children[1].value

        interaction.client.form_data[interaction.user.id] = {
            'game_name': game_name,
            'username': username,
            'role_id': self.role_id,
            'pack_name': self.pack_name,
            'interaction': interaction,
            'user': interaction.user  # เพิ่มข้อมูลผู้ใช้
        }

        await interaction.response.send_message("กรุณาส่งรูปสลิปเงินที่นี่ได้เลยค่ะ", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.form_data = {}

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        if message.author.id in self.form_data:
            form_data = self.form_data[message.author.id]
            interaction = form_data['interaction']
            user = form_data['user']

            if message.attachments:
                slip_attachment = message.attachments[0]

                # ส่งรูปไปยังช่อง log ของสลิปเงิน (channel3)
                log_channel = interaction.client.get_channel(1266994307399684238)  # log slip
                if log_channel:
                    log_message = await log_channel.send(file=await slip_attachment.to_file())
                    slip_url = log_message.attachments[0].url

                    # ส่งข้อมูลการสั่งซื้อไปยัง channel1 และ channel2
                    channel1 = interaction.client.get_channel(1266815687750586389)  # log admin
                    channel2 = interaction.client.get_channel(1266815725520289943)  # log user

                    if channel1 and channel2:
                        embed1 = nextcord.Embed(
                            title="การสั่งซื้อใหม่",
                            description="รายละเอียดการสั่งซื้อ",
                            color=nextcord.Color.green()
                        )
                        embed1.add_field(name="เกมที่จะเติม", value=f"```{form_data['game_name']}```", inline=False)
                        embed1.add_field(name="แพ็กที่เลือก", value=f"```{form_data['pack_name']}```", inline=False)
                        embed1.add_field(name="UID หรือ Username", value=f"```{form_data['username']}```", inline=False)
                        embed1.set_image(url=slip_url)
                        embed1.set_footer(text="ขอบคุณที่ใช้บริการของเรา!")
                        embed1.set_author(name=user.display_name, icon_url=user.display_avatar.url)  # ใส่ข้อมูลผู้ใช้

                        embed2 = nextcord.Embed(
                            title="กำลังดำเนินการ",
                            description="รายละเอียดการสั่งซื้อ",
                            color=nextcord.Color.red()
                        )
                        embed2.add_field(name="เกมที่จะเติม", value=f"```{form_data['game_name']}```", inline=False)
                        embed2.add_field(name="แพ็กที่เลือก", value=f"```{form_data['pack_name']}```", inline=False)
                        embed2.add_field(name="UID หรือ Username", value=f"```{form_data['username']}```", inline=False)
                        embed2.set_image(url=slip_url)
                        embed2.set_footer(text="กำลังดำเนินการ โปรดรอสักครู่!")
                        embed2.set_author(name=user.display_name, icon_url=user.display_avatar.url)  # ใส่ข้อมูลผู้ใช้
                        embed2.set_footer(text=f"User ID: {user.id}")  # เก็บ User ID ใน footer

                        try:
                            await channel1.send(f'- รายละเอียดการสั่งซื้อของคุณ {user.mention}', embed=embed1)
                            message2 = await channel2.send(f'- รายละเอียดการสั่งซื้อของคุณ {user.mention}', embed=embed2)
                            await message2.add_reaction("✅")
                            await interaction.followup.send("ข้อมูลของคุณได้รับการส่งเรียบร้อยแล้ว รอแอดมินทำการสักครู่ค่ะ", ephemeral=True)

                            await message.delete()
                            
                            del self.form_data[message.author.id]

                        except Exception as e:
                            print(f"เกิดข้อผิดพลาดขณะส่งข้อความ: {e}")

                    else:
                        await interaction.followup.send("เกิดข้อผิดพลาด ไม่พบช่องทางที่ระบุ กรุณาติดต่อแอดมิน", ephemeral=True)
                else:
                    await interaction.followup.send("เกิดข้อผิดพลาด ไม่พบช่องทางที่ระบุ กรุณาติดต่อแอดมิน", ephemeral=True)

    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.User):
        if user.bot:
            return

        print(f"Reaction added: {reaction.emoji} by {user}")

        if reaction.message.channel.id == 1266815725520289943:
            guild = reaction.message.guild
            if guild is None:
                return

            member = guild.get_member(user.id)
            if member is None:
                print(f"ไม่พบสมาชิก: {user.id}")
                return

            admin_role = nextcord.utils.get(guild.roles, name="ADMIN ONLY")
            if admin_role is None:
                print("ไม่พบบทบาท ADMIN ONLY")
                return

            if admin_role not in member.roles:
                await reaction.message.remove_reaction(reaction.emoji, user)
                await user.send("คุณไม่มีสิทธิ์ในการกด ✅ เฉพาะแอดมินเท่านั้น!")
            else:
                if reaction.emoji == "✅":
                    embed = nextcord.Embed(
                        title="ดำเนินการเสร็จสิ้น",
                        description="รายละเอียดการสั่งซื้อ",
                        color=nextcord.Color.green()
                    )
                    embed.add_field(name="เกมที่จะเติม", value=reaction.message.embeds[0].fields[0].value, inline=False)
                    embed.add_field(name="แพ็กที่เลือก", value=reaction.message.embeds[0].fields[1].value, inline=False)
                    embed.add_field(name="UID หรือ Username", value=reaction.message.embeds[0].fields[2].value, inline=False)
                    embed.set_image(url=reaction.message.embeds[0].image.url)
                    embed.set_footer(text="ดำเนินการเสร็จสิ้น! ขอบคุณที่ใช้บริการของเรา!")

                    try:
                        # ดึง User ID จาก footer ของ embed message
                        user_id = int(reaction.message.embeds[0].footer.text.split(": ")[1])
                        original_user = guild.get_member(user_id)

                        await reaction.message.edit(embed=embed)
                        await reaction.message.channel.send(f"เรียบร้อยง้าบบบ {original_user.mention}")
                    except Exception as e:
                        print(f"เกิดข้อผิดพลาดขณะอัปเดตข้อความ: {e}")


bot = MyBot()

class PurchaseView(nextcord.ui.View):
    def __init__(self, role_id, **kwargs):
        super().__init__()
        self.role_id = role_id
        for i in range(0, 16):
            button_label = kwargs.get(f'button_label{i}')
            pack_name = kwargs.get(f'button_label{i}')
            if button_label and pack_name:
                self.add_item(PurchaseButton(label=button_label, role_id=self.role_id, pack_name=pack_name))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)



class SetupView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SelectMenu())
        self.link_button = nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="เพจ Facebook", url='https://www.facebook.com/Nonn.meoww')
        self.add_item(self.link_button)
        self.link_button1 = nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="เช็คเครดิต", url='https://www.facebook.com/Nonn.meoww/posts/pfbid0X1srDr8VUgiVLGd7SrjCUvBoHgoEkSJRJsaUvNRXUTaWReqfhfWskcwkiAvQDEnil') 
        self.add_item(self.link_button1)


    @nextcord.ui.button(
        label='💳﹒Payment',
        custom_id='link_button',
        style=nextcord.ButtonStyle.primary,
        row=1
    )
    async def link_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # สร้าง Embed ที่จะส่งเมื่อปุ่มถูกกด

        emoji_id = 1263497560321032192  # แทนที่ด้วย ID ของ emoji ที่คุณต้องการใช้
        emoji = nextcord.utils.get(interaction.guild.emojis, id=emoji_id)

        embed = nextcord.Embed(
            title='─────          Payment          ─────',
            description = f'''```
──────────────────────────────────
💳﹒ชำระผ่านวอเลต +10 ค่าธรรมเนียม
✨﹒หากลูกค้าไม่โอนค่าธรรมเนียมร้านจะหักจากราคาที่ลูกค้าโอน
✨﹒มีหน้าเพจ เช็คเครดิตได้เลยย   
💲﹒โอนแล้ว กรอกข้อมูล รอทำการได้เลย
──────────────────────────────────```''',
            color=nextcord.Color.blue()
        )

        embed.set_image(url='https://media.discordapp.net/attachments/821716495296888852/1206295210460577793/donate.png?ex=669f43b6&is=669df236&hm=4ee5a5f82d9accc47512fa3576a1f3d806f7547b2745d058e66983eb28634db1&=&format=webp&quality=lossless&width=701&height=701')

        # แก้ไขข้อความของปุ่มให้เป็น Embed ที่สร้างขึ้น
        await interaction.response.send_message(embed=embed, ephemeral=True)


    async def on_timeout(self):
        # ทำการปิดการใช้งาน view หากหมดเวลา
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


@bot.event
async def on_ready():
    bot.add_view(SetupView())
    print(f'LOGIN AS {bot.user}')

@bot.slash_command(
    name='setup',
    description='setup',
)
async def setup(interaction: nextcord.Interaction):
    if ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้.", ephemeral=True)
        return
    
    embed = nextcord.Embed()
    embed.title = '───       Meow - ร้านเติมเกมสุดคุ้ม       ───'
    embed.description = f'''
```
──────────────────────────────────
🎮﹒บอทเติมเกม 24 ชั่วโมง 💚

💳﹒ชำระผ่านวอเลต +10 ค่าธรรมเนียม
✨﹒หากลูกค้าไม่โอนค่าธรรมเนียมร้านจะหักจากราคาที่ลูกค้าโอน
✨﹒มีหน้าเพจ เช็คเครดิตได้เลยย   
💲﹒โอนแล้วรอทำการได้เลย
──────────────────────────────────```
'''
    embed.color = nextcord.Color.purple()
    embed.set_image(url='https://media.discordapp.net/attachments/1041602377955954718/1041602448982290552/78BA2C87-898E-4505-A1E9-676DA2DA37A7.png?ex=669f4f5f&is=669dfddf&hm=8e7df318030ad5199d4b20af61c8a3d625ecd6d4b52ad0b50fe84701fa1d98c5&=&format=webp&quality=lossless')
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/1041602377955954718/1041602447967268874/371A4132-5B3D-4A7A-A8DA-5FB9DB40DB0C.png?ex=669f4f5f&is=669dfddf&hm=24d3c35b545b254c1fdffe2d9bf11d588de905904583ed6de449d9b8fe968ac9&=&format=webp&quality=lossless&width=701&height=701')
    await interaction.channel.send(embed=embed, view=SetupView())
    await interaction.response.send_message(content='[SUCCESS] Done.', ephemeral=True)

ROLE_ID = 1266849198024818740

@bot.slash_command(name="ลบข้อความตามจำนวน", description="ลบข้อความตามจำนวนที่กำหนด")
@commands.has_permissions(manage_messages=True)
async def purge(interaction: Interaction, amount: int = SlashOption(name="จำนวน", description="จำนวนข้อความที่ต้องการลบ", required=True)):
    # ตรวจสอบว่าผู้ใช้มี role ที่กำหนดหรือไม่
    if ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้.", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("กรุณาระบุจำนวนข้อความที่ต้องการลบให้ถูกต้อง.", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f'ลบ {len(deleted)} ข้อความเรียบร้อยแล้ว.', ephemeral=True)


@bot.slash_command(name="เตะสมาชิก", description="เตะสมาชิกที่เลือก")
@commands.has_permissions(kick_members=True)
async def kick_member(
    interaction: Interaction,
    member: nextcord.Member = SlashOption(
        name="สมาชิก",
        description="สมาชิกที่ต้องการเตะ",
        required=True
    ),
    reason: str = SlashOption(
        name="เหตุผล",
        description="เหตุผลในการเตะสมาชิก",
        required=False
    )
):
    if ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้.", ephemeral=True)
        return

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูกเตะเรียบร้อยแล้ว. เหตุผล: {reason if reason else 'ไม่ได้ระบุ'}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"ไม่สามารถเตะสมาชิกได้: {str(e)}", ephemeral=True)


@bot.slash_command(name="แบนสมาชิก", description="แบนสมาชิกที่เลือก")
@commands.has_guild_permissions(ban_members=True)
async def ban_member(
    interaction: Interaction,
    member: nextcord.Member = SlashOption(
        name="สมาชิก",
        description="สมาชิกที่ต้องการแบน",
        required=True
    ),
    reason: str = SlashOption(
        name="เหตุผล",
        description="เหตุผลในการแบน",
        required=False
    )
):
    if ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้.", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"สมาชิก {member.mention} ถูกแบนเรียบร้อยแล้ว. เหตุผล: {reason if reason else 'ไม่ได้ระบุ'}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"ไม่สามารถแบนสมาชิกได้: {str(e)}", ephemeral=True)

# Log Delete Message

# ตั้งค่าการบันทึก log
logging.basicConfig(level=logging.INFO)

# โหลดการตั้งค่าจากไฟล์ config.json
with open("./config.json") as config_file:
    cfg = json.load(config_file)


guild_ID = 350252371059933187
log_channel_id = 1267011278464094248


#แจ้งเตือนลบข้อความ
@bot.event
async def on_message_delete(message):
    logging.info('on_message_delete event triggered')
    
    if not message.guild or not message.author:
        logging.error('Message, guild, or author is null/undefined')
        return

    logging.info(f'Message from guild ID: {message.guild.id}')

    if message.guild.id != guild_ID:
        logging.info('Message guild ID does not match config guild ID')
        return

    if message.author.bot:
        logging.info('Message author is a bot')
        return

    channel_logs = bot.get_channel(log_channel_id)
    if channel_logs:
        logging.info('Channel found, sending embed')
        embed = message_delete_embed(bot, message)
        await channel_logs.send(embed=embed)
    else:
        logging.error('Channel not found')

#แจ้งเตือนแก้ไขข้อความ
@bot.event
async def on_message_edit(before, after):
    logging.info('on_message_edit event triggered')
    
    if not after.guild or not after.author:
        logging.error('Message, guild, or author is null/undefined')
        return

    logging.info(f'Message from guild ID: {after.guild.id}')

    if after.guild.id != guild_ID:
        logging.info('Message guild ID does not match config guild ID')
        return

    if after.author.bot:
        logging.info('Message author is a bot')
        return

    channel_logs = bot.get_channel(log_channel_id)
    if channel_logs:
        logging.info('Channel found, sending embeds')
        embed_old = messageU(bot, before, after)
        embed_new = messageUN(bot, before, after)
        await channel_logs.send(embeds=[embed_old, embed_new])
    else:
        logging.error('Channel not found')

@bot.event
async def on_guild_channel_update(old_channel, new_channel):
    logging.info('on_guild_channel_update event triggered')

    if not new_channel.guild:
        logging.error('Guild is null/undefined')
        return

    logging.info(f'Channel from guild ID: {new_channel.guild.id}')

    if new_channel.guild.id != guild_ID:
        logging.info('Channel guild ID does not match config guild ID')
        return

    channel_logs = bot.get_channel(log_channel_id)
    if channel_logs:
        logging.info('Channel found, sending embeds')

        if old_channel.name != new_channel.name:
            embed = channelUN(bot, new_channel, old_channel)
            await channel_logs.send(embed=embed)

        if old_channel.is_nsfw() != new_channel.is_nsfw():
            embed = channelUNSFW(bot, new_channel, old_channel)
            await channel_logs.send(embed=embed)

        if old_channel.category_id != new_channel.category_id:
            embed = channelUP(bot, new_channel, old_channel)
            await channel_logs.send(embed=embed)

        if old_channel.topic != new_channel.topic:
            embed = channelUT(bot, new_channel, old_channel)
            await channel_logs.send(embed=embed)

        if old_channel.slowmode_delay != new_channel.slowmode_delay:
            embed = channelURPU(bot, new_channel, old_channel)
            await channel_logs.send(embed=embed)
    else:
        logging.error('Channel not found')


bot.run(config['token'])
