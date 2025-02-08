import websockets
import asyncio
from feed_parser import parse_feed
import json
import zmq

context = zmq.Context()

socket = context.socket(zmq.SUB)

socket.connect("tcp://192.168.99.44:15012")

socket.setsockopt_string(zmq.UNSUBSCRIBE, "")

socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("Connected to the data feed. waiting for the messages...")

async def handle_data():
    try:
        while True:
            message = socket.recv_string()
            parsed_feed = parse_feed(message)
            print(f"Received from main server and after parsing: {parsed_feed}")
            asyncio.create_task(send_to_app(json.dumps(parsed_feed)))
    except Exception as e:
        print(f"Error in handle_data: {e}")

async def send_to_app(message):
    try:
        async with websockets.connect('ws://localhost:8766') as app_ws:
            await app_ws.send(message)  # Send the message to the app
            # No need to wait for a response here
    except Exception as e:
        print(f"Error in send_to_app:  {e}")


async def main():
    # Run handle_data function to receive data from server and send to app
    await handle_data()


if __name__ == '__main__':
    asyncio.run(main())
