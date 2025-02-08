import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            database="AlgoMinds",
            user="algominds",
            password="machinedatabase",
            host='localhost',
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def insert_feed_data(feed_data):
    conn = get_db_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            if len(feed_data) != 22:
                print(f"Error: Expected 21 fields but got {len(feed_data)}")
                return
            # SQL query to insert data
            insert_query = """
            INSERT INTO market_data (
                record_identifier, symbol_code, market_code, symbol_state, 
                symbol_flag, bid_volume, bid_price, ask_price, ask_volume, 
                last_trade_price, last_trade_volume, last_trade_time, 
                last_day_close_price, symbol_direction, average_price, high_price, 
                low_price, net_change, total_traded_volume, total_trades, open_price, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            # Extract values from the parsed feed data
            values = (
                feed_data.get('Record Identifier'),
                feed_data.get('Symbol Code'),
                feed_data.get('Market Code'),
                feed_data.get('Symbol State'),
                feed_data.get('Symbol Flag', ''),
                feed_data.get('Bid Volume'),
                feed_data.get('Bid Price'),
                feed_data.get('Ask Price'),
                feed_data.get('Ask Volume'),
                feed_data.get('Last Trade Price'),
                feed_data.get('Last Trade Volume'),
                feed_data.get('Last Trade Time'),
                feed_data.get('Last Day Close Price'),
                feed_data.get('Symbol Direction', ''),
                feed_data.get('Average Price'),
                feed_data.get('High Price'),
                feed_data.get('Low Price'),
                feed_data.get('Net Change'),
                feed_data.get('Total Traded Volume'),
                feed_data.get('Total Trades'),
                feed_data.get('Open Price'),
                feed_data.get('Timestamp')
            )
            
            # Execute the insert query
            cur.execute(insert_query, values)
            conn.commit()  # Commit the transaction
            
            print("Data inserted successfully")
            
        except Exception as e:
            print(f"Error inserting data: {e}")
        finally:
            cur.close()
            conn.close()
    else:
        print("Connection to database failed.")