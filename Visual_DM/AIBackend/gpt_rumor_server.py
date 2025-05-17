import asyncio
import websockets
import json
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

HOST = "localhost"
PORT = 8765

PROMPT_TEMPLATE = (
    "You are a rumor-monger in a fantasy world. Given the following event, NPC personality, and distortion level, transform the event into a rumor. "
    "Keep the rumor plausible but allow for natural distortion.\n"
    "Event: {event}\n"
    "NPC Personality: {npc_personality}\n"
    "Distortion Level: {distortion_level}\n"
    "Theme: {theme}\n"
    "Retelling Count: {retelling_count}\n"
    "Time Since Event: {time_since_event}\n"
    "Rumor:"
)

async def handle_rumor(websocket, path):
    try:
        data = await websocket.recv()
        request = json.loads(data)
        event = request.get("EventData", "")
        params = request.get("Parameters", {})
        prompt = PROMPT_TEMPLATE.format(
            event=event,
            npc_personality=params.get("NpcPersonality", "unknown"),
            distortion_level=params.get("DistortionLevel", 0.5),
            theme=params.get("Theme", "general"),
            retelling_count=params.get("RetellingCount", 1),
            time_since_event=params.get("TimeSinceEvent", 0.0),
        )
        rumor = await generate_rumor(prompt)
        response = {"Rumor": rumor}
        await websocket.send(json.dumps(response))
    except Exception as e:
        fallback = f"[Rumor generation error: {str(e)}]"
        await websocket.send(json.dumps({"Rumor": fallback}))

async def generate_rumor(prompt):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.85,
        )
        rumor = response.choices[0].message["content"].strip()
        return rumor
    except Exception as e:
        return f"[Rumor generation failed: {str(e)}]"

async def main():
    print(f"Starting GPT Rumor WebSocket server on ws://{HOST}:{PORT}")
    async with websockets.serve(handle_rumor, HOST, PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 