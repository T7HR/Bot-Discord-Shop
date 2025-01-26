import nextcord
from nextcord import Embed

def message_delete_embed(client, message):
    date = int(message.created_at.timestamp())
    
    embed = Embed(
        title="ข้อความที่ถูกลบไปแล้ว",
        description=f"### Message content\n```{message.content}```",
        color=nextcord.Color.blue()
    )
    embed.set_author(
        name="ข้อความที่ถูกลบไปแล้ว",
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/830790543659368448.webp?size=96&quality=lossless"
    )
    embed.add_field(name="Message ID", value=f"{message.id}", inline=False)
    embed.add_field(name="ข้อความของ", value=f"<@{message.author.id}>", inline=False)
    embed.add_field(name="ข้อมูลผู้เขียน", value=f"{message.author.name}**/**{message.author.id}", inline=False)
    embed.add_field(name="Channel", value=f"<#{message.channel.id}>", inline=False)
    embed.add_field(name="Timestamp", value=f"<t:{date}:R>", inline=True)

    return embed

def messageU(client, old_message, new_message):
    date = int(new_message.created_at.timestamp())
    
    embed = Embed(
        title="ก่อนแก้ไขข้อความ (1/2)",
        description=f"### ข้อความเก่า\n```{old_message.content}```",
        color=nextcord.Color.orange()
    )
    embed.set_author(
        name="ก่อนแก้ไขข้อความ (1/2)",
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1142475983396536451/1181689429723717682/pencil.png?ex=6581f90a&is=656f840a&hm=e37d6a9945fa953a8dc8b9e3ff22965f28c203b5b2c5dd6f4c101a5e2c380938&"
    )

    return embed

def messageUN(client, old_message, new_message):
    date = int(new_message.created_at.timestamp())
    
    embed = Embed(
        title="หลังแก้ไขข้อความ (2/2)",
        description=f"### ข้อความใหม่\n```{new_message.content}```",
        color=nextcord.Color.green()
    )
    embed.set_author(
        name="หลังแก้ไขข้อความ (2/2)",
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1142475983396536451/1181689429723717682/pencil.png?ex=6581f90a&is=656f840a&hm=e37d6a9945fa953a8dc8b9e3ff22965f28c203b5b2c5dd6f4c101a5e2c380938&"
    )
    embed.add_field(name="Message ID", value=f"{new_message.id}", inline=False)
    embed.add_field(name="ผู้เขียน", value=f"<@{new_message.author.id}>", inline=False)
    embed.add_field(name="ข้อมูลผู้เขียน", value=f"{new_message.author.name}**/**{new_message.author.id}", inline=False)
    embed.add_field(name="Channel", value=f"<#{new_message.channel.id}>", inline=False)
    embed.add_field(name="Timestamp", value=f"<t:{date}:R>", inline=True)

    return embed

def channelUN(client, new_channel, old_channel):
    date = nextcord.utils.utcnow().timestamp()
    embed = Embed(
        color=nextcord.Color.orange()
    )
    embed.set_author(
        name=f'{client.user.name} | เปลี่ยนชื่อ Channel',
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        "https://cdn.discordapp.com/emojis/1138482145673871400.webp?size=96&quality=lossless"
    )
    embed.description = (
        f"### Channel Information:\n"
        f"Name: **{new_channel.name}**\n"
        f"Tag: <#{new_channel.id}>\n"
        f"ID: **{new_channel.id}**"
    )
    embed.add_field(name="ชื่อเก่า", value=f"{old_channel.name}", inline=True)
    embed.add_field(name="ชื่อใหม่", value=f"{new_channel.name}", inline=True)
    embed.add_field(name="Time", value=f"<t:{int(date)}:R>", inline=True)
    return embed

def channelUNSFW(client, new_channel, old_channel):
    embed = Embed(
        color=nextcord.Color.green()
    )
    embed.set_author(
        name=f'{client.user.name} | อัปเดตการจำกัดอายุของช่องแล้ว',
        icon_url=client.user.display_avatar.url
    )
    embed.description = (
        f"### Channel Information:\n"
        f"Name: **{new_channel.name}**\n"
        f"Tag: <#{new_channel.id}>\n"
        f"ID: **{new_channel.id}**"
    )
    embed.add_field(
        name="Old Restriction", 
        value="Enabled :white_check_mark:" if old_channel.is_nsfw() else "Disabled :x:", 
        inline=True
    )
    embed.add_field(
        name="New Restriction", 
        value="Enabled :white_check_mark:" if new_channel.is_nsfw() else "Disabled :x:", 
        inline=True
    )
    embed.timestamp = nextcord.utils.utcnow()
    return embed

def channelUP(client, new_channel, old_channel):
    date = nextcord.utils.utcnow().timestamp()
    embed = Embed(
        color=nextcord.Color.green()
    )
    embed.set_author(
        name=f'{client.user.name} | หมวดหมู่ช่องมีการเปลี่ยนแปลง',
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        "https://cdn.discordapp.com/emojis/1138488289846890557.webp?size=96&quality=lossless"
    )
    embed.description = (
        f"### Channel Information:\n"
        f"Name: **{new_channel.name}**\n"
        f"Tag: <#{new_channel.id}>\n"
        f"ID: **{new_channel.id}**"
    )
    embed.add_field(name="หมวดเก่า", value=f"{old_channel.category or 'None :x:'}", inline=True)
    embed.add_field(name="หมวดใหม่", value=f"{new_channel.category or 'None :x:'}", inline=True)
    embed.add_field(name="Time", value=f"<t:{int(date)}:R>", inline=True)
    return embed

def channelUT(client, new_channel, old_channel):
    date = nextcord.utils.utcnow().timestamp()
    embed = Embed(
        color=nextcord.Color.green()
    )
    embed.set_author(
        name=f'{client.user.name} | หัวข้อช่องมีการเปลี่ยนแปลง',
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        "https://cdn.discordapp.com/emojis/1138482145673871400.webp?size=96&quality=lossless"
    )
    embed.description = (
        f"### Channel Information:\n"
        f"Name: **{new_channel.name}**\n"
        f"Mention: <#{new_channel.id}>\n"
        f"ID: **{new_channel.id}**"
    )
    embed.add_field(name="อันเก่า", value=f"{old_channel.topic or 'None :x:'}", inline=True)
    embed.add_field(name="อันใหม่", value=f"{new_channel.topic or 'None :x:'}", inline=True)
    embed.add_field(name="Time", value=f"<t:{int(date)}:R>", inline=True)
    return embed

def channelURPU(client, new_channel, old_channel):
    date = nextcord.utils.utcnow().timestamp()
    embed = Embed(
        color=nextcord.Color.green()
    )
    embed.set_author(
        name=f'{client.user.name} | Delay Message Changed',
        icon_url=client.user.display_avatar.url
    )
    embed.set_thumbnail(
        "https://cdn.discordapp.com/emojis/785483969453883432.webp?size=96&quality=lossless"
    )
    embed.description = (
        f"### Channel Information:\n"
        f"Name: **{new_channel.name}**\n"
        f"Tag: <#{new_channel.id}>\n"
        f"ID: **{new_channel.id}**"
    )
    embed.add_field(name="ก่อนปรับ", value=f"{old_channel.slowmode_delay or 'None :x:'}", inline=True)
    embed.add_field(name="หลังปรับ", value=f"{new_channel.slowmode_delay or 'None :x:'}", inline=True)
    embed.add_field(name="Time", value=f"<t:{int(date)}:R>", inline=True)
    return embed