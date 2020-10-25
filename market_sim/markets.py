import bisect


class Order:
    def __init__(self, order_type_, trader_id_, quantity_, limit_price_ = None):
        self.order_type = self._get_type(order_type_)
        self.trader_id = trader_id_
        self.quantity = quantity_
        self.limit_price = self._check_limit_price(limit_price_)
    
    def _get_type(self, order_type_):
        if (order_type_ != "limit") and (order_type_ != "market"):
            raise Exception("Unknown Order Type")
        else:
            return order_type_
    
    def _check_limit_price(self, limit_price_):
        if (limit_price_ is None) and (self.order_type == "limit"):
            raise Exception("Limit Price cannot be None for Limit Orders")
        elif (limit_price_ is not None) and (self.order_type == "limit"):
            return limit_price_
        

class OrderBook:
    
    def __init__(self):
        self.bid_book = {}
        self.bid_book_prices = []
        self.ask_book = {}
        self.ask_book_prices = []
        self.bid_size = 0
        self.ask_size = 0
        
        self.order = 0
        self.market_price = 0
        self.matches = []
        
    def initialize(self, dir_):
        if dir_ == "ask":
            _dir = self.ask_book_prices
        elif dir_ == "bid":
            _dir =  self.bid_book_prices
            
        if not _dir:
            bisect.insort(_dir, self.order.limit_price)

    def push(self, order_):
        self.order = order_
        if self.order.order_type == "limit":
            self.process_limit_order()
        elif self.order.order_type == "market":
            self.process_market_order()
        else:
            raise Exception("Unknown Order Type")
        #self.book_keeping()
        
    def get_market_price(self):
        return self.market_price
    
    def process_limit_order(self):
        if self.order.quantity > 0.0:
            self.order.quantity = abs(self.order.quantity)
            self.initialize("ask")
            self.add_to_ask_book()
        
        elif self.order.quantity < 0.0:
            self.order.quantity = abs(self.order.quantity)
            self.initialize("bid")
            self.add_to_bid_book()
        else:
            raise Exception("Order cannot be zero")
        
    def add_to_ask_book(self):
            
        if self.bid_book_prices and (self.order.limit_price >= self.bid_book_prices[0]):
            self.match_limit_ask()
        else:
            self.update_ask_book()
    
    def add_to_bid_book(self):
            
        if self.ask_book_prices and (self.order.limit_price <= self.ask_book_prices[-1]):
            self.match_limit_bid()
        else:
            self.update_bid_book()
    
    def update_ask_book(self):
        if self.order.limit_price in self.ask_book:
            self.ask_book[self.order.limit_price]["number_orders"] += 1
            self.ask_book[self.order.limit_price]["size"] += self.order.quantity
            self.ask_book[self.order.limit_price]["orders"][self.order.trader_id] = self.order

        else:
            if not self.order.limit_price in self.ask_book_prices:
                bisect.insort(self.ask_book_prices, self.order.limit_price)
            self.ask_book[self.order.limit_price] = {
                "number_orders": 1,
                "size": self.order.quantity,
                "orders": {self.order.trader_id: self.order},
            }

    def update_bid_book(self):
        if self.order.limit_price in self.bid_book:
            self.bid_book[self.order.limit_price]["number_orders"] += 1
            self.bid_book[self.order.limit_price]["size"] += self.order.quantity
            self.bid_book[self.order.limit_price]["orders"][self.order.trader_id] = self.order

        else:
            if not self.order.limit_price in self.bid_book_prices:
                bisect.insort(self.bid_book_prices, self.order.limit_price)
            self.bid_book[self.order.limit_price] = {
                "number_orders": 1,
                "size": self.order.quantity,
                "orders": {self.order.trader_id: self.order},
            }
    
    ########################
    def match_handler(self, trader_id_, price_, quantity_):
        self.market_price = price_
        print(str(trader_id_) + " gets " + str(quantity_) + " at " + str(price_))
        
        match = {trader_id_: (price_, quantity_)}
        self.matches.append(match)
    
    def clear_matches(self):
        self.matches = []
    
    def remove_bid_order_price(self, strike_):
        self.bid_book_prices.remove(strike_)
        self.bid_book.pop(strike_)
    
    def remove_bid_order(self, strike_, ask_quantity_,bid_trader_id_):
        self.bid_book[strike_]["number_orders"] -= 1
        self.bid_book[strike_]["size"] -= ask_quantity_
        self.bid_book[strike_]['orders'].pop(bid_trader_id_)
            
    def update_bid_order(self, strike_, ask_quantity_):
        
        if not self.bid_book[strike_]['orders'] or (self.bid_book[strike_]['number_orders'] == 0):
            self.remove_bid_order_price(strike_)
            return ask_quantity_
        
        bid_trader_id = list(self.bid_book[strike_]['orders'])[0]
        bid_order = list(self.bid_book[strike_]['orders'].values())[0]
        diff = ask_quantity_ - bid_order.quantity
        
        print(diff)
        if diff > 0:
            self.match_handler(bid_trader_id, strike_, -bid_order.quantity) # seller gets this
            self.match_handler(self.order.trader_id, strike_, bid_order.quantity) # buyer gets this
            self.remove_bid_order(strike_, bid_order.quantity, bid_trader_id)
            return self.update_bid_order(strike_, diff)
        
        if diff == 0:
            self.remove_bid_order_price(strike_)
            self.match_handler(bid_trader_id, strike_, -bid_order.quantity) # seller gets this
            self.match_handler(self.order.trader_id, strike_, bid_order.quantity) #
            
            return 0
        
        if diff < 0:
            print("HERE " + str(ask_quantity_))
            self.match_handler(bid_trader_id, strike_, -abs(ask_quantity_)) # seller gets this
            self.match_handler(self.order.trader_id, strike_, abs(ask_quantity_))
            
            self.bid_book[strike_]['orders'][bid_trader_id].quantity = abs(diff)
            self.bid_book[strike_]["size"] = abs(diff)
            print(self.bid_book[strike_]['orders'][bid_trader_id].quantity)
            
            return 0
          
    def match_limit_ask(self):
        
        ask_quantity = self.order.quantity
        
        while ask_quantity > 0:
            
            if not self.bid_book_prices: # no orders to match
                self.order.quantity = ask_quantity
                self.update_ask_book()
                print("Order partially filled")
                break
                
            strike = self.bid_book_prices[0]
            
            if (self.order.limit_price < strike): # order doesn_t fill!
                self.order.quantity = ask_quantity
                self.update_ask_book()
                print("Order partially filled")
                break
            
            if self.order.limit_price >= strike:
                ask_quantity = self.update_bid_order(strike, ask_quantity)
            
            if ask_quantity == 0:
                self.clean_prices()
                print("Order Filled!")
                break
                
            print(ask_quantity)
            
    ##############################
    
    def remove_ask_order_price(self, strike_):
        self.ask_book_prices.remove(strike_)
        self.ask_book.pop(strike_)
    
    def remove_ask_order(self, strike_, bid_quantity_, ask_trader_id_):
        self.ask_book[strike_]["number_orders"] -= 1
        self.ask_book[strike_]["size"] -= bid_quantity_
        self.ask_book[strike_]['orders'].pop(ask_trader_id_)
          
    def update_ask_order(self, strike_, bid_quantity_):
        print(self.ask_book)
        print(strike_)
        if not self.ask_book[strike_]['orders'] or self.ask_book[strike_]['size'] == 0:
            self.remove_ask_order_price(strike_)
            return bid_quantity_
        
        ask_trader_id = list(self.ask_book[strike_]['orders'])[0]
        ask_order = list(self.ask_book[strike_]['orders'].values())[0]
        diff = bid_quantity_ - ask_order.quantity
        
        print(diff)
        
        if diff > 0:
            self.match_handler(ask_trader_id, strike_, -ask_order.quantity) # seller gets this
            self.match_handler(self.order.trader_id, strike_, ask_order.quantity) # buyer gets this
            self.remove_ask_order(strike_, ask_order.quantity, ask_trader_id)
            return self.update_ask_order(strike_, diff)
        
        if diff == 0:
            self.remove_ask_order_price(strike_)
            self.match_handler(ask_trader_id, strike_, -ask_order.quantity) # seller gets this
            self.match_handler(self.order.trader_id, strike_, ask_order.quantity) #
            
            return 0
        
        if diff < 0:
            print("HERE " + str(bid_quantity_))
            self.match_handler(ask_trader_id, strike_, -abs(bid_quantity_)) # seller gets this
            self.match_handler(self.order.trader_id, strike_, abs(bid_quantity_))
            
            self.ask_book[strike_]['orders'][ask_trader_id].quantity = abs(diff) 
            self.ask_book[strike_]["size"] = abs(diff) 
            print(self.ask_book[strike_]['orders'][ask_trader_id].quantity)
            
            return 0    
        
    def match_limit_bid(self):
        
        bid_quantity = self.order.quantity
        
        while bid_quantity > 0:
            
            if not self.ask_book_prices: # no orders to match
                self.order.quantity = bid_quantity
                self.update_bid_book()
                print("Order partially filled or no match")
                break
                
            strike = self.ask_book_prices[-1]
            
            if (self.order.limit_price > strike): # order doesn_t fill!
                self.order.quantity = bid_quantity
                print("this is " + str(bid_quantity))
                self.update_bid_book()
                print("Order partially filled")
                break
            
            if self.order.limit_price <= strike:
                bid_quantity = self.update_ask_order(strike, bid_quantity)
            
            if bid_quantity == 0:
                self.clean_prices()
                print("Order Filled!")
                break
    #####################################

    def process_market_order(self):
        self.book_keeping()
        if self.order.quantity > 0.0:
            self.order.quantity = abs(self.order.quantity)

            if not self.bid_book_prices:
                print("WHAT")
                return
            else:
                self.match_market_ask()

        elif self.order.quantity < 0.0:
            self.order.quantity = abs(self.order.quantity)

            if not self.ask_book_prices:
                print("WHAT")
                return
            else:
                self.match_market_bid()
        else:
            raise Exception("Order cannot be zero")

    def get_bid_size(self):
        self.bid_size = 0
        for key, value in self.bid_book.items():
            self.bid_size += value["size"]

    def get_ask_size(self):
        self.ask_size = 0
        for key, value in self.ask_book.items():
            self.ask_size += value["size"]

    def match_market_ask(self):

        ask_quantity = self.order.quantity
        
        if ask_quantity > self.bid_size:
            return

        while ask_quantity > 0:

            strike = self.bid_book_prices[0]
            ask_quantity = self.update_bid_order(strike, ask_quantity)
            if ask_quantity == 0:
                print("Order Filled!")
                break

    def match_market_bid(self):

        bid_quantity = self.order.quantity
        
        if bid_quantity > self.ask_size:
            return

        while bid_quantity > 0:

            strike = self.ask_book_prices[-1]
            bid_quantity = self.update_ask_order(strike, bid_quantity)
            if bid_quantity == 0:
                print("Order Filled!")
                break
                
    def clean_prices(self):
        
        for key in self.ask_book_prices:
            if key not in self.ask_book:
                self.ask_book_prices.remove(key)
        
        for key in self.bid_book_prices:
            if key not in self.bid_book:
                self.bid_book_prices.remove(key)
    
    def get_bid_size(self):
        self.bid_size = 0
        for key, value in self.bid_book.items():
            self.bid_size += value["size"]

    def get_ask_size(self):
        self.ask_size = 0
        for key, value in self.ask_book.items():
            self.ask_size += value["size"]
    
    def book_keeping(self):
        self.get_bid_size()
        self.get_ask_size()
        
#############################################


class Market(object):
    
    def __init__(self, initial_market_price_):
        self.orderbook = OrderBook()
        self.market_price = initial_market_price_
        self.initial_market_price = initial_market_price_
        self.matches = [] # list of dictionaries!
    
    def push(self, order_):
        # update traders and push state back to the trader - 
        # order comes in and is submitted to 
        
        self.orderbook.push(order_)
        self.market_price = self.get_market_price()
        print("Market price is " + str(self.market_price))
        self.matches = self.orderbook.matches # get matches here
        self.orderbook.clear_matches()
        
    def get_market_price(self):
        if self.orderbook.get_market_price() == 0:
            return self.initial_market_price
        else:
            return self.orderbook.get_market_price()
        

