import asyncio
import json
import uuid
import websockets


async def run_ws_test():
    run_id = uuid.uuid4().hex[:8]
    session_id = f"session_ui_{run_id}"
    uri = f"ws://127.0.0.1:8000/ws/{session_id}"

    async with websockets.connect(uri, open_timeout=20) as websocket:
        print("\n--- Connected ---")
        print(await websocket.recv())

        payload = {
            "type": "interact",
            "data": {
                "message": "We need enterprise pricing, onboarding support, and a demo for our team.",
                "session_id": session_id,
                "user_name": "Faizan",
                "metadata": {
                    "source": "websocket_ui"
                }
            }
        }

        print("\n--- Sending ---")
        print(json.dumps(payload))

        await websocket.send(json.dumps(payload))

        while True:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=20)
                print(msg)

                if '"event_type":"interaction_complete"' in msg:
                    break

            except asyncio.TimeoutError:
                print("Timed out waiting for more events.")
                break


if __name__ == "__main__":
    asyncio.run(run_ws_test())