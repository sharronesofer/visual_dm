import asyncio
import websockets
import json
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

HOST = "localhost"
PORT = 8766

PROMPT_TEMPLATE = (
    "You are a social interaction analyst in a fantasy world. Given the following player dialogue, NPC personality, and relationship context, classify the type of information being shared (e.g., flattery, deception, warning, threat, request, etc.), and assess whether it is likely to benefit or harm the NPC.\n"
    "Player Dialogue: {dialogue}\n"
    "NPC Personality: {npc_personality}\n"
    "Relationship: {relationship}\n"
    "Recent History: {history}\n"
    "Classify the information type, and provide a brief explanation.\n"
    "Respond in JSON: {{\"info_type\": <type>, \"benefit\": <true/false>, \"explanation\": <string>}}\n"
)

async def handle_social_check(websocket, path):
    try:
        data = await websocket.recv()
        request = json.loads(data)
        dialogue = request.get("Dialogue", "")
        npc_personality = request.get("NpcPersonality", "unknown")
        relationship = request.get("Relationship", "neutral")
        history = request.get("History", "none")
        prompt = PROMPT_TEMPLATE.format(
            dialogue=dialogue,
            npc_personality=npc_personality,
            relationship=relationship,
            history=history,
        )
        result = await analyze_social_check(prompt)
        await websocket.send(json.dumps(result))
    except Exception as e:
        fallback = {"info_type": "unknown", "benefit": None, "explanation": f"[Social check analysis error: {str(e)}]"}
        await websocket.send(json.dumps(fallback))

async def analyze_social_check(prompt):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.7,
        )
        content = response.choices[0].message["content"].strip()
        # Try to parse the JSON from the response
        try:
            result = json.loads(content)
        except Exception:
            result = {"info_type": "parse_error", "benefit": None, "explanation": content}
        return result
    except Exception as e:
        return {"info_type": "api_error", "benefit": None, "explanation": f"[OpenAI error: {str(e)}]"}

async def main():
    print(f"Starting GPT Social Check WebSocket server on ws://{HOST}:{PORT}")
    async with websockets.serve(handle_social_check, HOST, PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 