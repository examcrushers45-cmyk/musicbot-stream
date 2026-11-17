import asyncio, os, re, json, urllib.request, urllib.parse
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp

chat = int(os.environ["CHAT_ID"]); q = os.environ["QUERY"].strip()
BASE = {"format": "bestaudio/best", "quiet": True, "noplaylist": True}

def one(url):
    with yt_dlp.YoutubeDL(BASE) as y:
        info = y.extract_info(url, download=False)
        if "entries" in info: info = info["entries"][0]
        if not info.get("url"): raise Exception("no stream url")
        return info

def sc_search(name):
    with yt_dlp.YoutubeDL({**BASE, "extract_flat": True}) as y:
        res = y.extract_info(f"scsearch8:{name}", download=False)
    for e in res.get("entries") or []:
        u = e.get("url") or e.get("webpage_url")
        if not u: continue
        try:
            print("Trying:", u)
            return one(u)
        except Exception as ex:
            print("Skipped:", str(ex)[:90])
    return None

def yt_title(link):
    u = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(link, safe="")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)["title"]

def candidates(title):
    t = re.sub(r"[\(\[].*?[\)\]]", " ", title)
    t = t.split("|")[0]
    t = re.sub(r"(?i)\b(official|lyrical|lyrics|video|audio|full song|hd)\b", " ", t)
    t = re.sub(r"\s+", " ", t.replace("-", " ")).strip()
    w = t.split()
    out = [t, " ".join(w[:4]), " ".join(w[:2])]
    return [c for i, c in enumerate(out) if c and c not in out[:i]]

info = None
is_direct = q.startswith("http") and not re.search(r"youtu\.?be", q)
try:
    if is_direct:
        info = one(q)
    elif q.startswith("http"):
        info = one(q)
    else:
        info = one(f"ytsearch:{q}")
except Exception as e:
    print("Primary failed:", str(e)[:150])
    if not is_direct:
        try:
            name = yt_title(q) if q.startswith("http") else q
            for c in candidates(name):
                print("SoundCloud search:", c)
                info = sc_search(c)
                if info: break
        except Exception as e3:
            print("Fallback failed:", str(e3)[:150])
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
