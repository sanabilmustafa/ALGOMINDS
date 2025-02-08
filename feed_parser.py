import datetime
import pytz

FEED_FIELDS = [
   "record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag",
    "bid_volume", "bid_price", "ask_price", "ask_volume", "last_trade_price",
    "last_trade_volume", "last_trade_time", "last_day_close_price", "symbol_direction",
    "average_price", "high_price", "low_price", "net_change", "total_traded_volume",
    "total_trades", "open_price"
]

def parse_numeric(value):
    if value == '':
        return None
    try:
        return float(value) if '.' in value else int(value  )
    except ValueError:
        return None

def parse_feed(raw_feed):
    initial_values = raw_feed.split("|")
    if initial_values[0] != "FEED":
        return None

    additional_values = initial_values[1].split(";")
    values = initial_values[:1] + additional_values

    feed = {
        field: parse_numeric(values[i]) if field not in ["record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag",] else values[i]
        for i, field in enumerate(FEED_FIELDS)
    }

    pkt_tz = pytz.timezone('Asia/Karachi')
    feed["timestamp"] = datetime.datetime.now(pkt_tz).strftime('%Y-%m-%d %H:%M:%S')

    return feed
