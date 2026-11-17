import asyncio, os, json, urllib.request, urllib.parse
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp

chat = int(os.environ["CHAT_ID"]); q = os.environ["QUERY"].strip()

def extract(target):
    opts = {"format": "bestaudio/best", "quiet": True, "noplaylist": True}
    if os.path.exists("cookies.txt"): opts["cookiefile"] = "cookies.txt"
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(target, download=False)
        if "entries" in info: info = info["entries"][0]
        return info

def yt_title(link):
    u = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(link, safe="")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)["title"]

info = None
try:
    info = extract(q if q.startswith("http") else f"ytsearch:{q}")
except Exception as e:
    print("YouTube failed:", e)
    try:
        name = yt_title(q) if q.startswith("http") else q
        print("Searching SoundCloud for:", name)
        info = extract(f"scsearch:{name}")
    except Exception as e2:
        print("SoundCloud failed:", e2)
        raise SystemExit(1)

async def main():
    app = Client("a", api_id=int(os.environ["API_ID"]), api_hash=os.environ["API_HASH"],
                 session_string=os.environ["SESSION_STRING"], in_memory=True)
    calls = PyTgCalls(app)
    await app.start(); await calls.start()
    await calls.play(chat, MediaStream(info["url"]))
    await asyncio.sleep(int(info.get("duration") or 300) + 5)
    await calls.leave_call(chat)
asyncio.run(main())
