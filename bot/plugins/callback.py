import re
import time
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from bot.__init__ import ADMIN_USERNAME, GROUP_USERNAME, BOT_NAME
from bot import start_uptime, Translation, VERIFY # pylint: disable=import-error
from bot.plugins.auto_filter import ( # pylint: disable=import-error
    FIND, 
    INVITE_LINK, 
    ACTIVE_CHATS,
    recacher,
    gen_invite_links
    )
from bot.plugins.settings import( # pylint: disable=import-error
    remove_emoji
)
from bot.database import Database # pylint: disable=import-error

db = Database()


@Client.on_callback_query(filters.regex(r"navigate\((.+)\)"), group=2)
async def cb_navg(bot, update: CallbackQuery):
    """
    A Callback Funtion For The Next Button Appearing In Results
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, btn, query = re.findall(r"navigate\((.+)\)", query_data)[0].split("|", 2)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        print(e)
        ruser_id = None
    
    admin_list = VERIFY.get(str(chat_id))
    if admin_list == None: # Make Admin's ID List
        
        admin_list = []
        
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
            
        admin_list.append(None) # Just For Anonymous Admin....
        VERIFY[str(chat_id)] = admin_list
    
    if not ((user_id == ruser_id) or (user_id in admin_list)): # Checks if user is same as requested user or is admin
        await update.answer("ආව් ආව් 😂 ඒක ඔයාගෙ request එකක් නෙමේ නෙ 😂😂",show_alert=True)
        return


    if btn == "next":
        index_val = int(index_val) + 1
    elif btn == "back":
        index_val = int(index_val) - 1
    
    achats = ACTIVE_CHATS[str(chat_id)]
    configs = await db.find_chat(chat_id)
    pm_file_chat = configs["configs"]["pm_fchat"]
    show_invite = configs["configs"]["show_invite_link"]
    show_invite = (False if pm_file_chat == True else show_invite)
    
    results = FIND.get(query).get("results")
    leng = FIND.get(query).get("total_len")
    max_pages = FIND.get(query).get("max_pages")
    
    try:
        temp_results = results[index_val].copy()
    except IndexError:
        return # Quick Fix🏃🏃
    except Exception as e:
        print(e)
        return

    if ((index_val + 1 )== max_pages) or ((index_val + 1) == len(results)): # Max Pages
        temp_results.append([
            InlineKeyboardButton("⏪ Back", callback_data=f"navigate({index_val}|back|{query})")
        ])

    elif int(index_val) == 0:
        pass

    else:
        temp_results.append([
            InlineKeyboardButton("⏪ Back", callback_data=f"navigate({index_val}|back|{query})"),
            InlineKeyboardButton("Next ⏩", callback_data=f"navigate({index_val}|next|{query})")
        ])

    if not int(index_val) == 0:    
        temp_results.append([
            InlineKeyboardButton(f"🔰 Page {index_val + 1}/{len(results) if len(results) < max_pages else max_pages} 🔰", callback_data="ignore")
        ])
    
    if show_invite and int(index_val) !=0 :
        
        ibuttons = []
        achatId = []
        await gen_invite_links(configs, chat_id, bot, update)
        
        for x in achats["chats"] if isinstance(achats, dict) else achats:
            achatId.append(int(x["chat_id"])) if isinstance(x, dict) else achatId.append(x)
        
        for y in INVITE_LINK.get(str(chat_id)):
            
            chat_id = int(y["chat_id"])
            
            if chat_id not in achatId:
                continue
            
            chat_name = y["chat_name"]
            invite_link = y["invite_link"]
            
            if ((len(ibuttons)%2) == 0):
                ibuttons.append(
                    [
                        InlineKeyboardButton
                            (
                                f"⚜ {chat_name} ⚜", url=invite_link
                            )
                    ]
                )

            else:
                ibuttons[-1].append(
                    InlineKeyboardButton
                        (
                            f"⚜ {chat_name} ⚜", url=invite_link
                        )
                )
            
        for x in ibuttons:
            temp_results.insert(0, x)
        ibuttons = None
        achatId = None
    
    reply_markup = InlineKeyboardMarkup(temp_results)


    text=f"**මෙන්න ඔයා හොයපු 👉 {query} /n/n[©️ ɪɴғɪɴɪᴛʏ ʙᴏᴛs](https://t.me/BOTS_Infinity) **" ,
        
    try:
        await update.message.edit(
                text,
                reply_markup=reply_markup,
                parse_mode="markdown",
                disable_web_page_preview=True
        )
        
    except FloodWait as f: # Flood Wait Caused By Spamming Next/Back Buttons
        await asyncio.sleep(f.x)
        await update.message.edit(
                text,
                reply_markup=reply_markup,
                parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"settings"), group=2)
async def cb_settings(bot, update: CallbackQuery):
    """
    A Callback Funtion For Back Button in /settings Command
    """
    global VERIFY
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)): # Check If User Is Admin
        return

    bot_status = await bot.get_me()
    bot_fname= bot_status.first_name
    
    text =f"<i>{bot_fname}'s</i> Settings Pannel.....\n"
    text+=f"\n<i>You Can Use This Menu To Change Connectivity And Know Status Of Your Every Connected Channel, Change Filter Types, Configure Filter Results And To Know Status Of Your Group...</i>"
    
    buttons = [
        [
            InlineKeyboardButton
                (
                    "🎬 CHANNELS", callback_data=f"channel_list({chat_id})"
                ), 
            
            InlineKeyboardButton
                (
                    "🔍 FILTER TYPES", callback_data=f"types({chat_id})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⚙️ CONFIG", callback_data=f"config({chat_id})"
                )
        ], 
        [
            InlineKeyboardButton
                (
                    "📋 STATUS", callback_data=f"status({chat_id})"
                ),
            
            InlineKeyboardButton
                (
                    "⏱️ BOT STATUS", callback_data=f"about({chat_id})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"warn\((.+)\)"), group=2)
async def cb_warn(bot, update: CallbackQuery):
    """
    A Callback Funtion For Acknowledging User's About What Are They Upto
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    chat_name = chat_name.encode('ascii', 'ignore').decode('ascii')[:35]
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return
    
    channel_id, channel_name, action = re.findall(r"warn\((.+)\)", query_data)[0].split("|", 2)
    
    if action == "connect":
        text=f"<i>සුවර්ද මේ channel එකට connect කරන්න ඕනෙ කියල 😂</i> <code>{channel_name}</code><i>..???</i>\n"
        text+=f"\n<i>රිසාල්ට් පෙන්නනකොට  </i><code>{channel_name}</code> <i>channel එකේ  එව්වත් පෙන්නන්නවා</i>..."
    
    elif action == "disconnect":
        text=f"<code>{channel_name}</code> <i>චැනල් එක ගෲපෙන් අයින් කරන්න ඔනෙ කියල විශ්වාසද? </i>\n"
        text+=f"\n<i>ෆයිල් ටික ඩිලීට් වෙන්නෙ නැති නිසා ඔනෙම වෙලාවක කනෙක්ට් කරගන්න පුලුවන්...</i>\n"
        text+=f"\nවක්කඩේ හකුරැ හැංගුව වගේ නෙමෙ හැබැයි😅😂 ... "
    
    elif action == "c_delete":
        text=f"<code>{channel_name}</code> <i>චැනල් එක සිරාවටම ඩිලීට් කරනවද ? </i>\n"
        text+=f"\n<i><b>ෆයිල් ඔක්කොම ඩිලීට් වෙනවා (DB එකෙන්😂)</b>ආයෙ ගන්න ඕනෙනම් චැනල් එක ඇඩ් කරන්න වෙනවා 😂</i>\n"
        text+=f"\nආයෙ හැංගිලිනෑ පු#ට පයින් ගහල එලවිල්ලක් මේක😅😂"
        
    
    elif action=="f_delete":
        text=f"<code>{channel_name}</code><i><i>චැට් එකේ දාල තියෙන හැම චැනල් එකේම ෆිල්ටර් ඩිලීට් වෙනවා </i>මෙව්ව ඕනෙද බන් 😂😂, කතා කරල විසද ගමු 😁\n"
        text+=f"\n<i>This Will Erase All Files From DB..</i>"
        
    buttons = [
        [
            InlineKeyboardButton
                (
                    "✅ අවුලක් නෑ", callback_data=f"{action}({channel_id}|{channel_name})"
                ), 
            
            InlineKeyboardButton
                (
                    "❎ බුදාම්මෝ එපා", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"channel_list\((.+)\)"), group=2)
async def cb_channel_list(bot, update: CallbackQuery):    
    """
    A Callback Funtion For Displaying All Channel List And Providing A Menu To Navigate
    To Every COnnect Chats For Furthur Control
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    chat_name = chat_name.encode('ascii', 'ignore').decode('ascii')[:35]
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return
        
    chat_id =  re.findall(r"channel_list\((.+)\)", query_data)[0]
    
    text = "<i>මක්කද ඩිලීට් කරන්නෙ 😁...</i>\n\n<i> Channel එකක් Connect කරාන් ඉස්සෙල්ලා😂😂.</i>"
    
    db_list = await db.find_chat(int(chat_id))
    
    channel_id_list = []
    channel_name_list = []
    
    if db_list:
        for x in db_list["chat_ids"]:
            channel_id = x["chat_id"]
            channel_name = x["chat_name"]
            
            try:
                if (channel_id == None or channel_name == None):
                    continue
            except:
                break
            
            channel_name = remove_emoji(channel_name).encode('ascii', 'ignore').decode('ascii')[:35]
            channel_id_list.append(channel_id)
            channel_name_list.append(channel_name)
        
    buttons = []

    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ) 

    if channel_name_list:
        
        text=f" <code>{chat_name}</code> <i>ගෲපත් එක්ක කනෙක්ට් කරල තියෙන චැනල් </i>\n"
    
        for x in range(1, (len(channel_name_list)+1)):
            text+=f"\n<code>{x}. {channel_name_list[x-1]}</code>\n"
    
        text += "\nසෙටින්ස් හදන්න ඕන කරන චැනල් එක බටන් වලින් තෝරන්න"
    
        
        btn_key = [
            "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", 
            "1️⃣1️⃣", "1️⃣2️⃣", "1️⃣3️⃣", "1️⃣4️⃣", "1️⃣5️⃣", "1️⃣6️⃣", "1️⃣7️⃣", 
            "1️⃣8️⃣", "1️⃣9️⃣", "2️⃣0️⃣" # Just In Case 😂🤣
        ]
    
        for i in range(1, (len(channel_name_list) + 1)): # Append The Index Number of Channel In Just A Single Line
            if i == 1:
                buttons.insert(0,
                    [
                    InlineKeyboardButton
                        (
                            btn_key[i-1], callback_data=f"info({channel_id_list[i-1]}|{channel_name_list[i-1]})"
                        )
                    ]
                )
        
            else:
                buttons[0].append(
                    InlineKeyboardButton
                        (
                            btn_key[i-1], callback_data=f"info({channel_id_list[i-1]}|{channel_name_list[i-1]})"
                        )
                )
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
            text = text,
            reply_markup=reply_markup,
            parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"info\((.+)\)"), group=2)
async def cb_info(bot, update: CallbackQuery):
    """
    A Callback Funtion For Displaying Details Of The Connected Chat And Provide
    Ability To Connect / Disconnect / Delete / Delete Filters of That Specific Chat
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"info\((.+)\)", query_data)[0].split("|", 1)
    
    f_count = await db.cf_count(chat_id, int(channel_id)) 
    active_chats = await db.find_active(chat_id)

    if active_chats: # Checks for active chats connected to a chat
        dicts = active_chats["chats"]
        db_cids = [ int(x["chat_id"]) for x in dicts ]
        
        if int(channel_id) in db_cids:
            active_chats = True
            status = "Connected"
            
        else:
            active_chats = False
            status = "Disconnected"
            
    else:
        active_chats = False
        status = "Disconnected"

    text=f"<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>{status}</code>\n"


    if active_chats:
        buttons = [
                    [
                        InlineKeyboardButton
                            (
                                "✂️ DISCONNECT", callback_data=f"warn({channel_id}|{channel_name}|disconnect)"
                            ),
                        
                        InlineKeyboardButton
                            (
                                "❌ DELETE", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                            )
                    ]
        ]

    else:
        buttons = [ 
                    [
                        InlineKeyboardButton
                            (
                                "🧲 CONNECT", callback_data=f"warn({channel_id}|{channel_name}|connect)"
                            ),
                        
                        InlineKeyboardButton
                            (
                                "❌ DELETE", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                            )
                    ]
        ]

    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⛔ REMOVE FILTERS", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )

    reply_markup = InlineKeyboardMarkup(buttons)
        
    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"^connect\((.+)\)"), group=2)
async def cb_connect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat Active Chat Which Will
    Make The Bot To Fetch Results From This Channel Too
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    

    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    f_count = await db.cf_count(chat_id, channel_id)
    
    add_active = await db.update_active(chat_id, channel_id, channel_name)
    
    if not add_active:
        await update.answer(f"{channel_name} එක active ඉන්නෙ", show_alert=True)
        return

    text= f"<code>{channel_name}</code><i> එක CONNECTඋනා </i> \n"
    text+=f"\n<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>Connected</code>\n"

    buttons = [
                [
                    InlineKeyboardButton
                        (
                            "✂️ DISCONNECT", callback_data=f"warn({channel_id}|{channel_name}|disconnect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "❌ DELETE", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⛔ REMOVE FILTERS", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    await recacher(chat_id, False, True, bot, update)
    
    reply_markup = InlineKeyboardMarkup(buttons)
        
    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"disconnect\((.+)\)"), group=2)
async def cb_disconnect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat inactive Chat Which Will
    Make The Bot To Avoid Fetching Results From This Channel
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    
    f_count = await db.cf_count(chat_id, int(channel_id))
    
    remove_active = await db.del_active(chat_id, int(channel_id))
    
    if not remove_active:
        await update.answer("Couldnt Full Fill YOur Request...\n Report This @BOTS_Infinity Along With Bot's Log", show_alert=True)
        return
    
    text= f" <code>{channel_name}</code> <i>එක Disconnected කරා</i>\n"
    text+=f"\n<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>Disconnected</code>\n"
    
    buttons = [ 
                [
                    InlineKeyboardButton
                        (
                            "🧲 CONNECT", callback_data=f"warn({channel_id}|{channel_name}|connect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "❌ DELETE", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⛔ REMOVE FILTERS", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await recacher(chat_id, False, True, bot, update)

    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"c_delete\((.+)\)"), group=2)
async def cb_channel_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Channel Connection From A Group Chat History
    Along With All Its Filter Files
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"c_delete\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    c_delete = await db.del_chat(chat_id, channel_id)
    a_delete = await db.del_active(chat_id, channel_id) # pylint: disable=unused-variable
    f_delete = await db.del_filters(chat_id, channel_id)

    if (c_delete and f_delete ):
        text=f"<code>{channel_name} [ {channel_id} ]</code> එකේ එව්ව ඔක්කොම අහක් කරා 🤣...."

    else:
        text=f"<i>එකක්වත් ඩිලීට් කරන්ට බැරි උනා</i>\n<i>log එක බලලා .ටික වෙලාවකින් ආපහු උත්සහ කරන්න!!</i>"
        await update.answer(text=text, show_alert=True)

    buttons = [
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"channel_list({chat_id})"
                ),
                
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]

    await recacher(chat_id, True, True, bot, update)
    
    reply_markup=InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"f_delete\((.+)\)"), group=2)
async def cb_filters_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Specific Channel's Filters Connected To A Group
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"f_delete\((.+)\)", query_data)[0].split("|", 1)

    f_delete = await db.del_filters(chat_id, int(channel_id))

    if not f_delete:
        text="<b><i>හප්පට..!!</i></b>\n\nඩිලීට් කරන්න බැරි උනානෙ....\nLog බලල මොකක්ද්ද ප්‍රශ්නෙ කියල හොයන්න...."
        await update.answer(text=text, show_alert=True)
        return

    text =f"<code>{channel_id}[{channel_name}]</code> චැනල් එකේ ඔක්කොම අහක් කරා.."

    buttons=[
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )
    


@Client.on_callback_query(filters.regex(r"types\((.+)\)"), group=2)
async def cb_types(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Result Types To Be Shown In While Sending Results
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id = re.findall(r"types\((.+)\)", query_data)[0]
    
    _types = await db.find_chat(int(chat_id))
    
    text=f"<i>මෙතනින් ෆිල්ටර් ටෛප් හදන්න පුලුවන් <code>{chat_name}</code> එකේ </i>\n"
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    buttons = []
    
    if vid:
        text+="\n<i><b>Video Index:</b> Enabled</i>\n"
        v_e = "✅"
        vcb_data = f"toggle({chat_id}|video|False)"
    
    else:
        text+="\n<i><b>Video Index:</b> Disabled</i>\n"
        v_e="❎"
        vcb_data = f"toggle({chat_id}|video|True)"

    if doc:
        text+="\n<i><b>Document Index:</b> Enabled</i>\n"
        d_e = "✅"
        dcb_data = f"toggle({chat_id}|document|False)"

    else:
        text+="\n<i><b>Document Index:</b> Disabled</i>\n"
        d_e="❎"
        dcb_data = f"toggle({chat_id}|document|True)"

    if aud:
        text+="\n<i><b>Audio Index:</b> Enabled</i>\n"
        a_e = "✅"
        acb_data = f"toggle({chat_id}|audio|False)"

    else:
        text+="\n<i><b>Audio Index:</b> Disabled</i>\n"
        a_e="❎"
        acb_data = f"toggle({chat_id}|audio|True)"

    
    text+="\n<i>ඔයාලගෙ චැනල් වල තියෙන ඒව ෆිල්ටර් කරගන්න Enabled / Disabled බටන් පාවිච්චි කරන්න....\n</i>"
    text+="<i>This Will Take Into Action As Soon As You Change Them....</i>"
    
    buttons.append([InlineKeyboardButton(f"Video Index: {v_e}", callback_data=vcb_data)])
    buttons.append([InlineKeyboardButton(f"Audio Index: {a_e}", callback_data=acb_data)])
    buttons.append([InlineKeyboardButton(f"Document Index: {d_e}", callback_data=dcb_data)])
    
    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"settings"
                )
        ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"toggle\((.+)\)"), group=2)
async def cb_toggle(bot, update: CallbackQuery):
    """
    A Callback Funtion Support handler For types()
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id, types, val = re.findall(r"toggle\((.+)\)", query_data)[0].split("|", 2)
    
    _types = await db.find_chat(int(chat_id))
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    if types == "video":
        vid = True if val=="True" else False
    elif types == "audio":
        aud = True if val=="True" else False
    elif types == "document":
        doc = True if val=="True" else False
    
        
    settings = {
        "video": vid,
        "audio": aud,
        "document": doc
    }

    process = await db.update_settings(chat_id, settings)
    
    if process:
        await update.answer(text="හරෙහ් ! Type එක අප්ඩේට් කරා", show_alert=True)
    
    else:
        text="අවුලක් ගිහින් . ලොග් බලන්න...."
        await update.answer(text, show_alert=True)
        return
    
    _types = await db.find_chat(int(chat_id))
    
    text =f"<i>ඒක Enable කරා <code>{update.message.chat.title}</code> එකේ </i>\n"
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    buttons = []
    
    if vid:
        text+="\n<i><b>Video Index:</b> Enabled</i>\n"
        v_e = "✅"
        vcb_data = f"toggle({chat_id}|video|False)"
    
    else:
        text+="\n<i><b>Video Index:</b> Disabled</i>\n"
        v_e="❎"
        vcb_data = f"toggle({chat_id}|video|True)"

    if doc:
        text+="\n<i><b>Document Index:</b> Enabled</i>\n"
        d_e = "✅"
        dcb_data = f"toggle({chat_id}|document|False)"

    else:
        text+="\n<i><b>Document Index:</b> Disabled</i>\n"
        d_e="❎"
        dcb_data = f"toggle({chat_id}|document|True)"

    if aud:
        text+="\n<i><b>Audio Index:</b> Enabled</i>\n"
        a_e = "✅"
        acb_data = f"toggle({chat_id}|audio|False)"

    else:
        text+="\n<i><b>Audio Index:</b> Disabled</i>\n"
        a_e="❎"
        acb_data = f"toggle({chat_id}|audio|True)"

    
    text+="\n<i>ඔයාලගෙ චැනල් වල තියෙන ඒව ෆිල්ටර් කරගන්න Enabled / Disabled බටන් පාවිච්චි කරන්න....\n</i>"
    text+="<i>This Will Take Into Action As Soon As You Change Them....</i>"
    
    buttons.append([InlineKeyboardButton(f"Video Index : {v_e}", callback_data=vcb_data)])
    buttons.append([InlineKeyboardButton(f"Audio Index : {a_e}", callback_data=acb_data)])
    buttons.append([InlineKeyboardButton(f"Document Index : {d_e}", callback_data=dcb_data)])
    
    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"settings"
                )
        ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"config\((.+)\)"), group=2)
async def cb_config(bot, update: CallbackQuery):
    """
    A Callback Funtion For Chaning The Number Of Total Pages / 
    Total Results / Results Per pages / Enable or Diable Invite Link /
    Enable or Disable PM File Chat
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id = re.findall(r"config\((.+)\)", query_data)[0]
    
    settings = await db.find_chat(int(chat_id))
    
    mp_count = settings["configs"]["max_pages"]
    mf_count = settings["configs"]["max_results"]
    mr_count = settings["configs"]["max_per_page"]
    show_invite = settings["configs"]["show_invite_link"]
    pm_file_chat  = settings["configs"]["pm_fchat"]
    accuracy_point = settings["configs"].get("accuracy", 0.80)
    
    text=f"<i><b> <u><code>{chat_name}</code></u> ගෲපෙ Filter Settings...</b></i>\n"
    
    text+=f"\n<i>{chat_name}</i> Current Settings:\n"

    text+=f"\n - Max Filter: <code>{mf_count}</code>\n"
    
    text+=f"\n - Max Pages: <code>{mp_count}</code>\n"
    
    text+=f"\n - Max Filter Per Page: <code>{mr_count}</code>\n"

    text+=f"\n - Accuracy Percentage: <code>{accuracy_point}</code>\n"
    
    text+=f"\n - Show Invitation Link: <code>{show_invite}</code>\n"
    
    text+=f"\n - Provide File In Bot PM: <code>{pm_file_chat}</code>\n"
    
    text+="\nAdjust Above Value Using Buttons Below... "
    buttons=[
        [
            InlineKeyboardButton
                (
                    "FILTER/PAGE", callback_data=f"mr_count({mr_count}|{chat_id})"
                ), 
    
            InlineKeyboardButton
                (
                    "MAX PAGE",       callback_data=f"mp_count({mp_count}|{chat_id})"
                )
        ]
    ]


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "TOTAL FILTER COUNT", callback_data=f"mf_count({mf_count}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [                
             InlineKeyboardButton
                (
                    "SHOW INVITE LINKS", callback_data=f"show_invites({show_invite}|{chat_id})"
                ),

            InlineKeyboardButton
                (
                    "BOT FILE CHAT", callback_data=f"inPM({pm_file_chat}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "SEARCH ACCURACY", callback_data=f"accuracy({accuracy_point}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"settings"
                )
        ]
    )
    
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mr_count\((.+)\)"), group=2)
async def cb_max_buttons(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Result To Be Shown Per Page
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mr_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>එක රිසාල්ට් එකක පහලට එන බටන් ගාන</i> <code>{chat_name}</code>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "5 Filters", callback_data=f"set(per_page|5|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 Filters", callback_data=f"set(per_page|10|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "15 Filters", callback_data=f"set(per_page|15|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "20 Filters", callback_data=f"set(per_page|20|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "25 Filters", callback_data=f"set(per_page|25|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "30 Filters", callback_data=f"set(per_page|30|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mp_count\((.+)\)"), group=2)
async def cb_max_page(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Result Pages To Be Shown
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mp_count\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i> උපරිම filter page count එක</i> <code>{chat_name}</code>"
    
    buttons = [

        [
            InlineKeyboardButton
                (
                    "2 Pages", callback_data=f"set(pages|2|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "4 Pages", callback_data=f"set(pages|4|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "6 Pages", callback_data=f"set(pages|6|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "8 Pages", callback_data=f"set(pages|8|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 Pages", callback_data=f"set(pages|10|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"config({chat_id})"
                )
        ]

    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mf_count\((.+)\)"), group=2)
async def cb_max_results(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Files TO Be Fetched From Database
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mf_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>එක රිසාල්ට් එකක තියෙන්න ඕනෙ උපරිම ෆිල්ටර් ගාන</i> <code>{chat_name}</code>"

    buttons = [

        [
            InlineKeyboardButton
                (
                    "50 Results", callback_data=f"set(results|50|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "100 Results", callback_data=f"set(results|100|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "150 Results", callback_data=f"set(results|150|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "200 Results", callback_data=f"set(results|200|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "250 Results", callback_data=f"set(results|250|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "300 Results", callback_data=f"set(results|300|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"show_invites\((.+)\)"), group=2)
async def cb_show_invites(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling Invite Link Buttons
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    value, chat_id = re.findall(r"show_invites\((.+)\)", query_data)[0].split("|", 1)
    
    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "❎ DISABLE", callback_data=f"set(showInv|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "✅ ENABLE", callback_data=f"set(showInv|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>එන රිසාල්ට් වල චැනල් එකට යන බටන් එකක්  ඇඩ් කරන්න පුලුවන් මේකෙන්.....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"inPM\((.+)\)"), group=2)
async def cb_pm_file(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling File Transfer Through Bot PM
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    value, chat_id = re.findall(r"inPM\((.+)\)", query_data)[0].split("|", 1)

    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "❎ DISABLE", callback_data=f"set(inPM|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "✅ ENABLE", callback_data=f"set(inPM|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "⬇️ BACK", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>මෙතනින් ඔයාට පුලුවන් බොට්ගෙන් ෆයිල් open වෙනවද නැත්තන් කෙලින්ම චැනල් එකෙන් open වෙනවද කියන එක හදන්න ....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"accuracy\((.+)\)"), group=2)
async def cb_accuracy(bot, update: CallbackQuery):
    """
    A Callaback Funtion to control the accuracy of matching results
    that the bot should return for a query....
    """
    global VERIFY
    chat_id = update.message.chat.id
    chat_name = update.message.chat.title
    user_id = update.from_user.id
    query_data = update.data
    
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    val, chat_id = re.findall(r"accuracy\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i>'Accuracy Perceentage' මේකෙන් පුලුවන් filter වල sensitivity එක වෙනස් කරන්න</i> <code>{chat_name}</code>\n\n"
    text+= f"<i>NB: ඔයා වැඩි අගයක් තේරැවොත් request එකට අදාලම දේ ලැබෙන එකෙ සම්භාව්‍යතාව වැඩී, ඔයා අඩු අගයක් තේරැවොත් ඉතින් හරිම එක ලැබෙනවා.( ඉල්ලන රික්වෙස්ට් එකේ අකුරැ වචන වලට ගැලපෙන වෙන ඒවත් එනවා ඒව අදාල නැති උනත්)..</i>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "100 %", callback_data=f"set(accuracy|1.00|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "80 %", callback_data=f"set(accuracy|0.80|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "65 %", callback_data=f"set(accuracy|0.65|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "60 %", callback_data=f"set(accuracy|0.60|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "55 %", callback_data=f"set(accuracy|0.55|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "50 %", callback_data=f"set(accuracy|0.50|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"config({chat_id})"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"set\((.+)\)"), group=2)
async def cb_set(bot, update: CallbackQuery):
    """
    A Callback Funtion Support For config()
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    action, val, chat_id, curr_val = re.findall(r"set\((.+)\)", query_data)[0].split("|", 3)

    try:
        val, chat_id, curr_val = float(val), int(chat_id), float(curr_val)
    except:
        chat_id = int(chat_id)
    
    if val == curr_val:
        await update.answer("කලින් තිබ්බෙත් ඕකමයි 😂 , වෙන එකක් තෝරන්න 😂😂...!!!", show_alert=True)
        return
    
    prev = await db.find_chat(chat_id)

    accuracy = float(prev["configs"].get("accuracy", 0.80))
    max_pages = int(prev["configs"].get("max_pages"))
    max_results = int(prev["configs"].get("max_results"))
    max_per_page = int(prev["configs"].get("max_per_page"))
    pm_file_chat = True if prev["configs"].get("pm_fchat") == (True or "True") else False
    show_invite_link = True if prev["configs"].get("show_invite_link") == (True or "True") else False
    
    if action == "accuracy": # Scophisticated way 😂🤣
        accuracy = val
    
    elif action == "pages":
        max_pages = int(val)
        
    elif action == "results":
        max_results = int(val)
        
    elif action == "per_page":
        max_per_page = int(val)

    elif action =="showInv":
        show_invite_link = True if val=="True" else False

    elif action == "inPM":
        pm_file_chat = True if val=="True" else False
        

    new = dict(
        accuracy=accuracy,
        max_pages=max_pages,
        max_results=max_results,
        max_per_page=max_per_page,
        pm_fchat=pm_file_chat,
        show_invite_link=show_invite_link
    )
    
    append_db = await db.update_configs(chat_id, new)
    
    if not append_db:
        text="Something Wrong Please Check Bot Log For More Information...."
        await update.answer(text=text, show_alert=True)
        return
    
    text=f"හරෙහ් 😂 \nSettings update කරා..."
        
    buttons = [
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data=f"config({chat_id})"
                ),
            
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"status\((.+)\)"), group=2)
async def cb_status(bot, update: CallbackQuery):
    """
    A Callback Funtion For Showing Overall Status Of A Group
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return
    
    chat_id = re.findall(r"status\((.+)\)", query_data)[0]
    
    total_filters, total_chats, total_achats = await db.status(chat_id)
    
    text = f"<b><i>Status of {chat_name}</i></b>\n"
    text += f"\n<b>Total Connected Chats:</b> <code>{total_chats}</code>\n"
    text += f"\n<b>Total Active Chats:</b> <code>{total_achats}</code>\n"
    text += f"\n<b>Total Filters:</b> <code>{total_filters}</code>"
    
    buttons = [
        [
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"about\((.+)\)"), group=2)
async def cb_about(bot, update: CallbackQuery):
    """
    A Callback Funtion For Showing About Section In Bot Setting Menu
    """
    global VERIFY
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    text=f"<b><u>Bot's Status</u></b>\n"
    text+=f"\n<b>Bot's Uptime:</b> <code>{time_formatter(time.time() - start_uptime)}</code>\n"
    text+=f"\n<b>Bot Funtion:</b> <i>Auto Filter Files</i>\n"
    text+=f"""\n<b>Bot Support:</b> <a href="https://t.me/BOTS_Infinity">©️ ɪɴғɪɴɪᴛʏ ʙᴏᴛs</a>\n"""

    buttons = [
        [
            #InlineKeyboardButton
                #(
                    #"😊 DEVELOPER", url="https://t.me/BOTS_Infinity"
                #),
                
            InlineKeyboardButton
                (
                    "⬇️ BACK", callback_data="settings"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "🔐 CLOSE", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html" , disable_web_page_preview=True
    )



@Client.on_callback_query(filters.regex(r"^(start|help|about|close)$"), group=2)
async def callback_data(bot, update: CallbackQuery):

    query_data = update.data

    if query_data == "start":
        buttons = [[
        InlineKeyboardButton("📫 SUPPORT", url="https://t.me/BOTS_Infinity"),
        InlineKeyboardButton("📕 ABOUT", callback_data="about")
    ],[
        InlineKeyboardButton("💡 HELP", callback_data="help"),
        InlineKeyboardButton("🔐 CLOSE", callback_data="close")
    ]]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.START_TEXT.format(update.from_user.mention, GROUP_USERNAME, ADMIN_USERNAME),
            reply_markup=reply_markup,
            parse_mode="html",
            disable_web_page_preview=True
        )


    elif query_data == "help":
        buttons = [[
        InlineKeyboardButton('⬇️ BACK', callback_data='start'),
        InlineKeyboardButton('🔐 CLOSE', callback_data='close')
    ]]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.HELP_TEXT,
            reply_markup=reply_markup,
            parse_mode="html",
            disable_web_page_preview=True
        )


    elif query_data == "about": 
        buttons = [[
        InlineKeyboardButton('⬇️ BACK', callback_data='start'),
        InlineKeyboardButton('🔐 CLOSE', callback_data='close')
    ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_text(
            Translation.ABOUT_TEXT.format(BOT_NAME),
            reply_markup=reply_markup,
            parse_mode="markdown",
            disable_web_page_preview=True
        )


    elif query_data == "close":
        await update.message.delete()
        


def time_formatter(seconds: float) -> str:
    """ 
    humanize time 
    """
    minutes, seconds = divmod(int(seconds),60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "")
    return tmp

