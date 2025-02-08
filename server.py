import websockets
import asyncio

FP = 'data/datafeed_messages.txt'

async def send_data(websocket):
    try:
        with open(FP, 'r') as file:
            for line in file:
                if line.strip():
                    await websocket.send(line.strip())
                    print(f'sent: {line.strip()}')
                    await asyncio.sleep(0.1)
    except Exception as e:
        print(f"error: {e}")

async def start_server():
    async with websockets.serve(send_data, 'localhost', 8765):
        print('websocket server running at ws://localhost:8765')
        await asyncio.Future() # keep running indefinitely


if __name__ == "__main__":
    asyncio.run(start_server())
