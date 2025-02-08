import websockets
import asyncio
from feed_parser import parse_feed
from database import insert_feed_data
import json
async def handle_data():
    try:
        async with websockets.connect('ws://localhost:8765') as main_ws:
            async for message in main_ws:
                parsed_feed = parse_feed(message)
                insert_feed_data(parsed_feed)
                print(f"Received from main server and after parsing: {parsed_feed}")
                # Create a task to send the message to the app concurrently
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

# import websockets
# import asyncio

# async def handle_data():
#     try:
#         # Connect to the main server (server.py)
#         async with websockets.connect('ws://localhost:8765') as main_ws:
#             async for message in main_ws:
#                 print(f"Received from main server: {message}")
#                 await send_to_app(message)  # Send the received data to the app
#     except Exception as e:
#         print(f"Error in handle_data: {e}")


# async def send_to_app(message):
#     try:
#         # Connect to the app server (app.py)
#         async with websockets.connect('ws://localhost:8766') as app_ws:
#             await app_ws.send(message)  # Send the message to the app
#             response = await app_ws.recv()  # Wait for a response from the app
#             print(f"Received from app: {response}")
#     except Exception as e:
#         print(f"Error in send_to_app: {e}")


# async def main():
#     # Run handle_data function to receive data from server and send to app
#     await handle_data()


# if __name__ == '__main__':
#     asyncio.run(main())


# import websockets
# import asyncio

# # Persistent connection to the application WebSocket server
# app_ws = None

# # Function to handle data from the main server
# async def handle_data():
#     try:
#         # Connect to the main server
#         async with websockets.connect('ws://localhost:8765') as main_ws:
#             async for message in main_ws:
#                 print(f"Received from main server: {message}")
#                 await send_to_app(message)
#     except Exception as e:
#         print(f"Error in handle_data: {e}")

# # Function to send data to the application WebSocket server
# async def send_to_app(message):
#     print("called")
#     global app_ws
#     if app_ws is None:
#         try:
#             # Establish a persistent connection to the app server
#             app_ws = await websockets.connect('ws://localhost:8766')
#             print("Connected to app WebSocket server")
#         except Exception as e:
#             print(f"Failed to connect to app WebSocket server: {e}")
#             return

#     try:
#         # Send the message and await a response
#         await app_ws.send(message)
#         response = await app_ws.recv()
#         print(f"Received from app server: {response}")
#     except Exception as e:
#         print(f"Error in send_to_app: {e}")
#         app_ws = None  # Reset the connection to retry next time

# # Main function to start the client
# async def main():
#     await handle_data()

# if __name__ == '__main__':
#     asyncio.run(main())

# import websockets
# import asyncio

# # Function to receive data from the main server and send it to the app
# async def handle_data():
#     try:
#         # Connect to the main server
#         async with websockets.connect('ws://localhost:8765') as ws:
#             async for message in ws:
#                 print(f"Received: {message}")
#                 await send_to_app(message)
#     except Exception as e:
#         print(f"Error in handle_data: {e}")

# # Function to send data to the application WebSocket server
# async def send_to_app(message):
#     try:
#         # Connect to the application server
#         async with websockets.connect('ws://localhost:8766') as app_ws:
#             await app_ws.send(message)
#             response = await app_ws.recv()
#             print(f"Received from the app: {response}")
#     except Exception as e:
#         print(f"Error in send_to_app: {e}")

# # Main function to run the client
# async def main():
#     await handle_data()

# if __name__ == '__main__':
#     asyncio.run(main())
