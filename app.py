import websockets
import asyncio
import psycopg2
import pandas as pd
from indicators import calculate_rsi, calculate_sma
from datetime import datetime, timedelta
from flask_cors import CORS 
from flask import Flask, render_template, request, jsonify
from flask_sock import Sock

import signal

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}}) 
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})

sock = Sock(app)

connected_clients = set()  # Store connected clients

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="AlgoMinds",
        user="algominds",
        password="sanabi101database"
    )
    return conn

# Function to handle incoming WebSocket connections
async def handle_connection(websocket):
    # Register the client
    connected_clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Received: {message}")
            # Broadcast the message to all other connected clients
            await send_to_clients(message, websocket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Unregister the client
        connected_clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

# Function to send data to all connected clients except the sender
async def send_to_clients(message, sender):
    for client in connected_clients:
        if client != sender:
            try:
                await client.send(message)
                print(f"Sent to {client.remote_address}: {message}")
            except Exception as e:
                print(f"Failed to send to {client.remote_address}: {e}")

# Function to start the WebSocket server
async def start_server():
    async with websockets.serve(handle_connection, 'localhost', 8766):
        print("WebSocket server running at ws://localhost:8766")
        await asyncio.Future()  # Keep the server running indefinitely


def get_indicators():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_id, date, close, symbol
        FROM historical
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY stock_id, date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=["stock_id", "date", "close", "symbol"])

    # Group by stock_id for per-stock indicator calculation
    results = []
    for stock_id, group in df.groupby("stock_id"):
        group = group.sort_values(by="date")  # Ensure sorted by date
        group["rsi"] = calculate_rsi(group["close"])
        group["sma"] = calculate_sma(group["close"], period=14)
        results.append(group.iloc[-1])  # Take the latest row with indicators
    return pd.DataFrame(results).to_dict(orient="records")# Convert to dict


@app.route('/apply_technical_indicator', methods=['POST'])
def apply_technical_indicator():
    data = request.get_json()
    rsi_interval = data.get('rsiInterval')
    rsi_time_interval = data.get('rsiTimeInterval')
    sma_time_period = data.get('smaTimePeriod')
    sma_time_interval = data.get('smaTimeInterval')
    indicator = data.get('indicator')

    if indicator == 'rsi':
        data = fetch_data_from_db(rsi_time_interval,rsi_interval)
        # Group data by symbol_code and calculate RSI for each group
        def calculate_stock_rsi(group):
            group['rsi'] = calculate_rsi(group['close'], int(rsi_interval))
            return group

        # Apply RSI calculation to each stock group
        result = data.groupby('symbol_code').apply(calculate_stock_rsi).reset_index(drop=True)

        # If you only need the most recent RSI for each stock:
        latest_rsi = result.groupby('symbol_code').tail(1)[['symbol_code', 'rsi']]

        print('Latest RSI for each stock:')
        print(latest_rsi)

        # Convert to JSON response
        response = latest_rsi.to_dict(orient='records')
        return jsonify({
            'message': f'RSI with interval {rsi_interval} applied successfully! with response {response}',
            'rsi_results': response
        })
    elif indicator == 'sma':
        data = fetch_data_from_db(sma_time_interval,sma_time_period)
        # Parse the SMA periods sent by the client (e.g., [40, 100])
        sma_periods = int(request.json.get('smaTimePeriod', []))

        if not sma_periods:
            return jsonify({
                'message': 'No SMA periods specified!',
                'sma_results': []
            }), 400

        # Group data by symbol_code and calculate SMA for each requested period
        def calculate_stock_sma(group):
            # for period in sma_periods:
            column_name = f'sma{sma_periods}'
            group[column_name] = group['close'].rolling(window=int(sma_periods)).mean()
            return group

        # Apply SMA calculation to each stock group
        result = data.groupby('symbol_code').apply(calculate_stock_sma).reset_index(drop=True)

        # Extract the latest SMA values for each stock and each requested period
        latest_sma = result.groupby('symbol_code').tail(1)

        # Prepare the response by including all SMA columns
        sma_columns = [f'sma{sma_periods}']
        response = latest_sma[['symbol_code'] + sma_columns].to_dict(orient='records')

        print('Latest SMA for each stock:')
        print(response)

        # Convert to JSON response
        return jsonify({
            'message': f'SMA for periods {sma_periods} applied successfully!',
            'sma_results': response
        })



def fetch_data_from_db(interval, period):
    print('from fetch data: ',interval, period)
    if interval == '1min':
        start_date = (datetime.now() - timedelta(minutes=float(period)),)
    elif interval == '30min':
        start_date = (datetime.now() - timedelta(minutes=30 * float(period)),)
    elif interval == '1day':
        start_date = datetime.now() - timedelta(days=float(period))
    else:
        raise ValueError("Unsupported interval")

    print('starting date is : ', start_date)
    conn = get_db_connection()  # Replace with actual DB connection logic
    cursor = conn.cursor()

    # Query logic based on the interval
    if interval in ['1min', '30min']:
        interval = 1  # Set your desired interval in minutes
        query = """
            WITH interval_data AS (
                SELECT 
                    DATEADD(
                        MINUTE,
                        DATEDIFF(MINUTE, '2000-01-01', timestamp) / %s * %s,
                        '2000-01-01'
                    ) AS interval_start,
                    symbol_code AS symbol,
                    MIN(open_price) AS open,
                    MAX(high_price) AS high,
                    MIN(low_price) AS low,
                    MAX(last_trade_price) AS close,
                    SUM(total_traded_volume) AS volume
                FROM market_data
                GROUP BY
                    DATEADD(
                        MINUTE,
                        DATEDIFF(MINUTE, '2000-01-01', timestamp) / %s * %s,
                        '2000-01-01'
                    ),
                    symbol_code
            )
            SELECT 
                interval_start, 
                symbol, 
                open, 
                high, 
                low, 
                close, 
                volume
            FROM interval_data
            ORDER BY symbol, interval_start;
        """
        cursor.execute(query, (interval, interval, interval, interval))

        # query = """
        #     SELECT timestamp, symbol_code AS symbol, open_price AS open, high_price AS high, 
        #         low_price AS low, last_trade_price AS close, total_traded_volume AS volume
        #     FROM (
        #         SELECT timestamp, symbol_code, open_price, high_price, low_price, 
        #             last_trade_price, total_traded_volume,
        #             ROW_NUMBER() OVER (PARTITION BY symbol_code ORDER BY timestamp DESC) AS row_num
        #         FROM market_data
        #     ) subquery
        #     WHERE row_num <= %s
        #     ORDER BY symbol, timestamp;
        #     """
        # cursor.execute(query, (int(period),))


    elif interval == '1day':
        # Fetch data from `historical`
        query = """
            SELECT date AS timestamp, symbol, open, high, low, close, volume
            FROM (
                SELECT date, symbol, open, high, low, close, volume,
                    ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) AS row_num
                FROM historical
            ) subquery
            WHERE row_num <= %s
            ORDER BY symbol, date;
            """
        cursor.execute(query, (int(period),))



    # Fetch and return the data as a DataFrame
    rows = cursor.fetchall()
    if interval in ['1min', '30min']:
        df = pd.DataFrame(rows, columns=['timestamp','symbol_code', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')  # Ensure numeric type

    elif interval == '1day':
        df = pd.DataFrame(rows, columns=['timestamp','symbol_code', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')  # Ensure numeric type


    conn.close()
    return df



@app.route('/api/stocks')
def get_stocks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_id, date, close, symbol
        FROM historical
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY stock_id, date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=["stock_id", "date", "close", "symbol"])
    return df


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (md.symbol_code) 
        md.*, 
        s.company, 
        s.sector
        FROM market_data md
        JOIN stock s ON md.symbol_code = s.symbol
        WHERE md.market_code = 'REG'    
        ORDER BY md.symbol_code, md.timestamp DESC;
    """)
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    stocks = [dict(zip(column_names, row)) for row in rows]

    # Extract column names dynamically
    column_names = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    results = get_indicators()
    # print(results)

    # Generate column config dynamically
    column_config = [
        {"id": col, "label": col.replace("_", " ").title(), "visible" : False ,"editable": False}
        for col in column_names
    ]
    # print(stocks)
    return render_template('index.html', stocks=stocks, indicators=results, column_config=column_config)



# Main function
async def main():
     # Run Flask in its own asyncio task
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:5000"]
    flask_task = asyncio.create_task(serve(app, config))

    # Run WebSocket server in another asyncio task
    websocket_task = asyncio.create_task(start_server())

    # Run both tasks concurrently
    await asyncio.gather(flask_task, websocket_task)

if __name__ == '__main__':
    asyncio.run(main())