#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @Dx_Doc | @AlbertEinsteinTG | @Hillard_Har 

class Translation(object):
    
    START_TEXT = """
😍 Hai {} ,

💡 Telegram Auto Filter Bot

I am a filter bot with advanced features currenty workig for any group. මේක ADV AUTO FILTER හි සිංහල සංස්කරණයයි.


🔅 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ:- @{}
"""   
    
    HELP_TEXT = """
<u>💡 𝐇𝐞𝐥𝐩</u>

<i>
📌 Add Me To Any Group And Make Me Admin
📌 Add Me To Your Desired Channel
(📌 බොට්ව connect කරන්න හදන Group එකටයි Channel එකටයි add කරල ඔක්කොම Previlages එක්ක Admin දෙන්න. )
</i>

<b>🔰 𝐌𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 (Works Only In Groups/ Group වල විතරයි command දෙන්න පුලුවන්) :</b>

    👉 <code>/add chat_id</code>
                OR                  - To Connect A Group With A Channel (Bot Should Be Admin With Full Previlages In Both Group And Channel.චැනල් එක connect කරන්න ඕනෙනම් /add ගහල space එකක තියල channel id එක ගහන්න)
     <code>/add @Username</code>
     
    👉 <code>/del chat_id</code>
                OR                  - To disconnect A Group With A Channel (channel එක group එකෙන් අයින් කරන්න ඕනෙනම්)
     <code>/del @Username</code>
     
    👉 <code>/delall</code>  - This Command Will Disconnect All Connected Channel With The Group And Deletes All Its File From DB (connect කරල තියෙන හැම චැනල් එකක්ම DB එකෙන් අයින් කරන්න ඕනෙනම්)
    
    👉 <code>/settings</code> -  This Command Will Display You A Settings Pannel Instance Which Can Be Used To Tweek Bot's Settings Accordingly (BOT settings හදන්න ඕනෙනම්)

🔰 𝐒𝐄𝐓𝐓𝐈𝐍𝐆 𝐏𝐀𝐍𝐄𝐋 (/settings command එක ගැහුවම එන එකේ )

            👉 <code>Channel</code> - Button Will Show You All The Connected Chats With The Group And Will Show Buttons Correspnding To There Order For Furthur Controls (දැනට connect කරල තියෙන channel ගාන පෙන්නනවා. මෙතනින් වෙන වෙනම චැනල් පාලනය කරන්න පුලුවන්)
            
            👉 <code>Filter Types</code> - Button Will Show You The 3 Filter Option Available In Bot... Pressing Each Buttons Will Either Enable or Disable Them And This Will Take Into Action As Soon As You Use Them Without The Need Of A Restart (Channel වල තියෙන Music , Documents , Video වෙන වෙනම ෆිල්ටර් වෙන එක නවත්ත්න්න පුලුවන්. ඒ කියන්නෙ ඔයාට චැනල් එකේ තියෙන music ඕනෙ නැත්තන් ඒක disable කරන්න පුලුවන්)

            👉 <code>Configure</code> - Button Will Helps You To Change No. of Pages/ Buttons Per Page/ Total Result Without Acutally Editing The Repo... Also It Provide Option To Enable/Disable For Showing Invite Link In Each Results (තවත් setting වගයක්. ඕනෙ විදිහට වෙනස් කරගන්න)
            
            👉 <code>Status</code> - Button Will Shows The Stats Of Your Channel (Connect වෙලා තියෙන filter ගාන වගේ ඒව පෙන්න්නනවා)
            
<b><a href="https://t.me/bots_infinity">©️ ɪɴғɪɴɪᴛʏ ʙᴏᴛs</a></b>
"""
    
    ABOUT_TEXT = """
📕 𝐀𝐛𝐨𝐮𝐭 𝐌𝐞 ,
\n○ ᴍʏ ɴᴀᴍᴇ : {}

○ ʟᴀɴɢᴜᴀɢᴇ : ᴘʏᴛʜᴏɴ 

○ ғʀᴀᴍᴇᴡᴏʀᴋ : ᴘʏʀᴏɢʀᴀᴍ 

○ sᴇʀᴠᴇʀ : ʜᴇʀᴏᴋᴜ 

○ ᴠᴇʀsɪᴏɴ : 1.0.0

○ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ : 🔐

○ ᴄʀᴇᴀᴛᴏʀ : [ᴅᴏᴄ ᴅx](https://t.me/dx_doc)

**[ɪɴғɪɴɪᴛʏ ʙᴏᴛs](https://t.me/bots_infinity)**
"""
