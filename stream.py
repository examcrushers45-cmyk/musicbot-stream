import asyncio, os, re, json, urllib.request, urllib.parse
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
        if "entries" in info:
            entries = [e for e in info["entries"] if e and e.get("url")]
            if not entries: raise Exception("no results")
            info = entries[0]
        return info

def yt_title(link):
    u = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(link, safe="")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)["title"]

def candidates(title):
    t = re.sub(r"[\(\[].*?[\)\]]", " ", title)
    t = re.split(r"\|", t)[0]
    t = re.sub(r"(?i)\b(official|lyrical|lyrics|video|audio|full song|hd)\b", " ", t)
    t = re.sub(r"\s+", " ", t.replace("-", " ")).strip()
    words = t.split()
    out = [t, " ".join(words[:4]), " ".join(words[:2])]
    return [c for i, c in enumerate(out) if c and c not in out[:i]]

info = None
try:
    info = extract(q if q.startswith("http") else f"ytsearch:{q}")
except Exception as e:
    print("YouTube failed:", str(e)[:200])
    try:
        name = yt_title(q) if q.startswith("http") else q
        for c in candidates(name):
            print("Trying SoundCloud:", c)
            try:
                info = extract(f"scsearch5:{c}")
                break
            except Exception as e2:
                print("No luck:", str(e2)[:100])
    except Exception as e3:
        print("Title lookup failed:", e3)
if not info:
    print("NOTHING PLAYABLE FOUND")
    raise SystemExit(1)

async def main():
    app = Client("a", api_id=int(os.environ["API_ID"]), api_hash=os.environ["API_HASH"],
                 session_string=os.environ["SESSION_STRING"], in_memory=True)
    calls = PyTgCalls(app)
    await app.start(); await calls.start()
    print("Joining voice chat in", chat)
    await calls.play(chat, MediaStream(info["url"]))
    print("Playing:", info.get("title"))
    await asyncio.sleep(int(info.get("duration") or 300) + 5)
    await calls.leave_call(chat)
asyncio.run(main())
