from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import websockets
import asyncio
import json

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

@app.route('/api/new-order', methods=['POST'])
def new_order():
    data = request.get_json()  # ✅ Use get_json() to handle JSON data
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    # Generate a random order hash
    data['ordHash'] = hashlib.md5(data['55'].encode()).hexdigest()

    print("Received Order Data:", data)

    return jsonify({"success": True, "message": "Order received!", "order": data})


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # ✅ Make sure the port is 5000 to match frontend request






# from flask import Flask, request, jsonify
# import hashlib
# import websockets
# import asyncio

# app = Flask(__name__) 

# @app.route('/api/new-order', methods=['POST'])
# def new_order():
#     # Receive form data from client
#     data = request.json
#     if not data:
#         return jsonify({"error": "Invalid input"}), 400

#     # Generate a random order hash
#     data['ordHash'] = hashlib.md5(data['symbol'].encode()).hexdigest()

#     # Log the received data
#     print("Received Order Data:", data)

#     # Simulate sending to WebSocket (WebSocket implementation can be added later)
#     # asyncio.run(send_to_websocket(data))

#     return jsonify({"success": True, "message": "Order received!", "order": data})


# # Simulated WebSocket sender (can be completed once the WebSocket API is ready)
# async def send_to_websocket(order_data):
#     ws_url = "wss://base_url:port_no?socket_token=your_token"  # Replace with actual URL
#     async with websockets.connect(ws_url) as websocket:
#         await websocket.send(json.dumps(order_data))
#         response = await websocket.recv()
#         print("WebSocket Response:", response)


# if __name__ == '__main__':
#     app.run(debug=True)
