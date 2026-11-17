import asyncio, os
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp

chat = int(os.environ["CHAT_ID"]); q = os.environ["QUERY"]
opts = {"format": "bestaudio", "quiet": True}
if os.path.exists("cookies.txt"): opts["cookiefile"] = "cookies.txt"
with yt_dlp.YoutubeDL(opts) as y:
    info = y.extract_info(q if q.startswith("http") else f"ytsearch:{q}", download=False)
    if "entries" in info: info = info["entries"][0]

async def main():
    app = Client("a", api_id=int(os.environ["API_ID"]), api_hash=os.environ["API_HASH"],
                 session_string=os.environ["SESSION_STRING"], in_memory=True)
    calls = PyTgCalls(app)
    await app.start(); await calls.start()
    await calls.play(chat, MediaStream(info["url"]))
    await asyncio.sleep(int(info.get("duration") or 300) + 5)
    await calls.leave_call(chat)
asyncio.run(main())
