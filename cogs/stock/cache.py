from models.stock import StockMarket, Stock
from database import mariadb as db
import cogs.stock.database_queries as queries

STOCK_MARKET = StockMarket()

def load_stocks(stock_market : StockMarket):
    raw_stocks = db.select_all(queries.GET_STOCKS)
    for raw_stock in raw_stocks:
        stock = Stock.from_database(raw_stock)
        stock_market.add_stock(stock)
    return stock_market

load_stocks(STOCK_MARKET)