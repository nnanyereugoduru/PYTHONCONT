class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, quantity, price):
        if name in self.items:
            self.items[name]['quantity'] += quantity
            self.items[name]['price'] = price
        else:
            self.items[name] = {'quantity': quantity, 'price': price}

    def remove_item(self, name, quantity):
        if name in self.items:
            self.items[name]['quantity'] -= quantity
            if self.items[name]['quantity'] <= 0:
                del self.items[name]
        else:
            print('invalid')

    def apply_discount(self, name, percent):
        if name in self.items:
            original_price = self.items[name]['price']
            discount = original_price * percent / 100
            self.items[name]['price'] = original_price - discount
        else:
            print('invalid')

    def total_value(self):   
        total = 0
        for item, a in self.items.items():
            total += a['quantity'] * a['price']
        return total

    def low_stock_report(self, threshold= 5):
        low_stock = []
        for name, details in self.items.items():
            if details['quantity'] <= threshold:
                low_stock.append(name)
        return low_stock
    
    # used this to see what I was working with 
    def printitem(self):
        for row, a in self.items.items():
            print(row)
            print(a)
                        

def main():
    
        inv = Inventory()
        inv.add_item("Widget", 10, 2.50)
        inv.add_item("Gadget", 3, 15.00)
        inv.add_item("Gizmo", 7, 8.75)
        inv.printitem()
        
        inv.apply_discount("Widget", 20)
        inv.remove_item("Gadget", 100)

        print("Total inventory value:", inv.total_value())
        print("Low stock items:", inv.low_stock_report())

        inv.add_item("Widget", 5, 999.00)
        print("Total inventory value:", inv.total_value())
        print("Low stock items:", inv.low_stock_report())
        inv.printitem()
    
        


if __name__ == "__main__":
    main()
