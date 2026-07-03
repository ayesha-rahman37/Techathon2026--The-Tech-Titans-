"""
Office Monitor Discord Bot
Fetches live device data from the Django backend API
and replies in a friendly, humanized way using Groq LLM.
Commands: !status, !room <name>, !usage
"""

import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_BASE = "http://127.0.0.1:8000/api"

ROOM_SLUGS = {
    "drawing": "drawing_room",
    "work1": "work_room_1",
    "work2": "work_room_2",
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def friendly_reply(raw_data: str, instruction: str) -> str:
    """Send raw office data to Groq and get a short, friendly reply."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly office assistant bot in Discord. "
                        "The boss hates robotic data dumps. Reply in a warm, "
                        "casual, human tone. Keep it short (2-4 sentences max). "
                        "Use 1-2 fitting emojis. Always base your answer ONLY "
                        "on the real data given."
                    ),
                },
                {"role": "user", "content": f"{instruction}\n\nData: {raw_data}"},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content
    except Exception as e:
        # Groq fail korleo bot jeno data dite pare
        return f"(AI unavailable, raw data) {raw_data}"


@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")


@bot.command()
async def status(ctx):
    """!status — full office overview"""
    try:
        rooms = requests.get(f"{API_BASE}/rooms/", timeout=10).json()
        summary = []
        for room in rooms:
            fans_on = sum(1 for d in room["devices"] if d["device_type"] == "fan" and d["status"])
            lights_on = sum(1 for d in room["devices"] if d["device_type"] == "light" and d["status"])
            summary.append(f"{room['name']}: {fans_on} fan(s) ON, {lights_on} light(s) ON")
        reply = friendly_reply("; ".join(summary), "Give the boss a quick office status update.")
        await ctx.send(reply)
    except requests.exceptions.RequestException:
        await ctx.send("⚠️ Can't reach the office backend right now — is the server running?")


@bot.command()
async def room(ctx, room_name: str = None):
    """!room work1 — status of one room"""
    if room_name is None or room_name.lower() not in ROOM_SLUGS:
        await ctx.send("Please pick a room: `!room drawing`, `!room work1`, or `!room work2` 🙂")
        return
    try:
        slug = ROOM_SLUGS[room_name.lower()]
        rooms = requests.get(f"{API_BASE}/rooms/", timeout=10).json()
        target = next((r for r in rooms if r["slug"] == slug), None)
        if not target:
            await ctx.send("Hmm, couldn't find that room in the system.")
            return
        devices = ", ".join(
            f"{d['name']} {'ON' if d['status'] else 'OFF'}" for d in target["devices"]
        )
        data = f"{target['name']} — {devices}. Current draw: {target['total_power_draw']}W"
        reply = friendly_reply(data, f"Tell the boss the status of {target['name']}.")
        await ctx.send(reply)
    except requests.exceptions.RequestException:
        await ctx.send("⚠️ Can't reach the office backend right now — is the server running?")


@bot.command()
async def usage(ctx):
    """!usage — total power + estimated kWh"""
    try:
        data = requests.get(f"{API_BASE}/rooms/office_power/", timeout=10).json()
        raw = (
            f"Total power right now: {data['total_power_watt']}W. "
            f"Estimated daily usage: {data['estimated_daily_usage_kwh']} kWh. "
            f"Per room: {data['per_room']}"
        )
        reply = friendly_reply(raw, "Tell the boss how much power the office is using.")
        await ctx.send(reply)
    except requests.exceptions.RequestException:
        await ctx.send("⚠️ Can't reach the office backend right now — is the server running?")


bot.run(os.getenv("DISCORD_TOKEN"))