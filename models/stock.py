import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

BIG_PRICE = 100
POS_COLOUR = '#089981'
NEG_COLOUR = '#F23645'

class Stock:
    def __init__(self, name, symbol, price, price_history = []):
        self.name = name
        self.symbol = symbol
        self.price = price
        self.price_history : list[float] = price_history

        # If the price history is empty, must be new stock, ergo fill price history (1 month in hours)
        if len(self.price_history) == 0:
            self.price_history = [price] * 720 # 720 hours in 1 month

        self.investors : map[int,float] = {}
        volatility_scale = min(max(1.0, BIG_PRICE / self.price), 0.05)
        self.volatility = (random.random() * volatility_scale + 0.05)

    @classmethod
    def from_database(cls, raw_stock):
        symbol = raw_stock[0]
        name = raw_stock[1]
        price = raw_stock[2]
        price_history = []
        for item in raw_stock[3].split(','):
            if item:
                price_history.append(float(item))
        investors = {}
        for item in raw_stock[4].split(','):
            if item:
                investor_id, stock_amount = item.split(':')
                investors.append({int(investor_id) : float(stock_amount)})

        stock = cls(name, symbol, price, price_history)
        stock.volatility = raw_stock[5]
        stock.investors = investors
        return stock

    def __str__(self):
        return f'{self.name} ({self.symbol}): {self.price}c'
    
    # Returns the amount of stock the investor has purchased for buying the stock
    def add_investor(self, investor_id : int, amount : float):
        stock_purchased = amount / self.price
        self.investors[investor_id] = self.investors.get(investor_id, 0) + stock_purchased
        return stock_purchased

    # Returns the amount of copium the investor would receive for selling the stock
    def remove_investor(self, investor_id : int, amount : float) -> float:
        if not investor_id in self.investors:
            return 0
        stock_sold = min(amount, self.investors[investor_id])
        self.investors[investor_id] -= stock_sold
        if self.investors[investor_id] == 0:
            del self.investors[investor_id]
        return self.price * stock_sold
    
    def tick(self, times = 1):
        for i in range(0,times):
            self.price += random.uniform(-self.volatility, self.volatility)
            self.price = round(self.price, 2)
            self.price = max(0, self.price)
            self.price_history.pop()
            self.price_history.insert(0, self.price)
        self.create_graph_images()

    def create_graph_image(self, values : list[float], filename : str):
        font_size = 8
        title_time_scale = ''
        ticks_to_show = []
        tick_labels = []
        if filename == '1day':
            now = datetime.now()
            title_time_scale = datetime.now().date().strftime('%d/%m')
            custom_x_values = [i for i in range(24)]
            ticks_to_show.append(custom_x_values[0])
            ticks_to_show.extend(custom_x_values[-1::-3])
            ticks_to_show.append(custom_x_values[-1])
            tick_labels.append(((now - timedelta(hours=24)).strftime('%H') + ':00'))
            tick_labels.extend([((now - timedelta(hours=i)).strftime('%H')+ ':00') for i in range(24)][::3])
            tick_labels.append(now.strftime('%H') + ':00')
        elif filename == '1week':
            today = datetime.now()
            title_time_scale = 'w/c ' + (today - timedelta(days=7)).strftime('%d/%m')
            custom_x_values = [i for i in range(168)]
            ticks_to_show.append(custom_x_values[0])
            ticks_to_show.extend(custom_x_values[-1::-24])
            ticks_to_show.append(custom_x_values[-1])
            tick_labels.append((today - timedelta(days=7)).strftime('%d/%m'))
            tick_labels.extend([(today - timedelta(days=i)).strftime('%d/%m') for i in range(7)])
            tick_labels.append(today.strftime('%d/%m'))
        else:
            today = datetime.now()
            title_time_scale = 'm/c ' + (datetime.now().date() - timedelta(days=30)).strftime('%d/%m')
            font_size = 5
            custom_x_values = [i for i in range(720)]
            ticks_to_show.append(custom_x_values[0])
            ticks_to_show.extend(custom_x_values[-1::-48])
            ticks_to_show.append(custom_x_values[-1])
            tick_labels.append((today - timedelta(days=30)).strftime('%d/%m'))
            tick_labels.extend([(today - timedelta(hours=i)).strftime('%d/%m') for i in range(720)][::48])
            tick_labels.append(today.strftime('%d/%m'))

        colour = POS_COLOUR if values[0] > values[-1] else NEG_COLOUR
        plt.plot(custom_x_values, values[::-1], color=colour)
        plt.xticks(ticks_to_show, tick_labels)
        plt.title(f'{self.symbol} Price - {title_time_scale}', color='#D7D4CF')
        plt.grid(True, axis='y', alpha=0.35)
        plt.gcf().set_facecolor('#181A1B')
        plt.gca().set_facecolor('#181A1B')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_position(('outward',3))
        plt.gca().spines['bottom'].set_position(('outward',3))
        plt.tick_params(axis='x', colors='#D1D4DC', labelsize=font_size)
        plt.tick_params(axis='y', colors='#D1D4DC')
        plt.savefig(f'models/stock_images/{self.symbol}_{filename}.png', dpi=200, bbox_inches='tight')
        plt.clf()
    
    def create_graph_images(self):
        self.create_graph_image(self.price_history[:24], '1day')
        self.create_graph_image(self.price_history[:168], '1week')
        self.create_graph_image(self.price_history, '1month')

class StockMarket:
    def __init__(self):
        self.stocks : list[Stock] = []

    def add_stock(self, stock : Stock):
        self.stocks.append(stock)

    def get_stock(self, symbol : str):
        for stock in self.stocks:
            if stock.symbol == symbol:
                return stock
        return None
    
    def tick_stock_market(self):
        for stock in self.stocks:
            stock.tick()

    def regen_images(self):
        for stock in self.stocks:
            stock.create_graph_images()