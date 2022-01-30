import sqlite3
import time
import matplotlib.pyplot as plt

db_path = ""
connection = None
cursor = None
UnOptimizedTimes = []
SelfOptimizedTimes = []
UserOptimizedTimes = []

def connect(path): 
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

def createUndefinedTables(): 
    global connection, cursor
    cursor.execute('''CREATE TABLE IF NOT EXISTS "Customers_undefined" ( 
        "customer_id" TEXT,
        "customer_postal_code" INTEGER)
    ;''')
    
    cursor.execute('''INSERT INTO "Customers_undefined"
        SELECT customer_id, customer_postal_code
        FROM Customers
    ;''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS "Orders_undefined" (
	"order_id" TEXT,
	"customer_id" TEXT)
    ;''')

    cursor.execute('''INSERT INTO "Orders_undefined"
    SELECT order_id, customer_id
    FROM Orders
    ;''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "Order_items_undefined"(
    "order_id" TEXT,
    "order_item_id" INTEGER,
    "product_id" TEXT,
    "seller_id" TEXT)
    ;''')

    cursor.execute('''INSERT INTO "Order_items_undefined"
        SELECT order_id, order_item_id, product_id, seller_id
        FROM Order_items
        ;''')

    connection.commit()
    
def dropUndefinedTables():
    global connection, cursor
    cursor.execute('''DROP TABLE IF EXISTS Customers_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Orders_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Order_items_undefined''')
    connection.commit()

def createIndexes():
    global connection, cursor
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cust ON Customers(customer_postal_code, customer_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order ON Orders(customer_id,order_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items ON Order_items(order_id);')
    connection.commit()
    
def dropIndexes():
    global connection, cursor
    cursor.execute('DROP INDEX IF EXISTS idx_cust')
    cursor.execute('DROP INDEX IF EXISTS idx_order')
    cursor.execute('DROP INDEX IF EXISTS idx_order_items')
    connection.commit()
    
def queryUnoptimized(db_path): 
    global connection, cursor, UnOptimizedTimes
    connect(db_path)
    
    createUndefinedTables()
    cursor.execute('PRAGMA automatic_index=0; ')
    cursor.execute('PRAGMA foreign_keys=0; ')
    connection.commit()
    list_of_target_postal_codes = []
    for i in range(50):
        query = '''SELECT customer_postal_code
        FROM Customers_undefined
        ORDER BY RANDOM()
        LIMIT 1;
        '''
        cursor.execute(query)
        row = cursor.fetchall()
        list_of_target_postal_codes.append(row[0][0])
    start = time.time()
    for i in range(50):
        target_postal_code = list_of_target_postal_codes[i]
        query = '''SELECT denom, num / denom From( (SELECT o.order_id, CAST(count(*) as REAL) as num
        from Customers_undefined c, Orders_undefined o, Order_items_undefined oi
        where c.customer_id = o.customer_id  and oi.order_id = o.order_id and c.customer_postal_code =:target_code),
        (SELECT count(*) as denom
        From Orders_undefined o
        Where o.customer_id in(
        SELECT c.customer_id
        FROM Customers_undefined c
        WHERE c.customer_postal_code =:target_code)));
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    UnOptimizedTimes.append((end - start) * 1000)
    dropUndefinedTables()
    print((end - start)*1000)
    connection.close()

def querySelfOptimized(db_path): 
    global connection, cursor, SelfOptimizedTimes
    connect(db_path)
    
    cursor.execute('PRAGMA automatic_index=1; ')
    cursor.execute('PRAGMA foreign_keys=1; ')
    connection.commit()
    list_of_target_postal_codes = []
    for i in range(50):
        query = '''SELECT customer_postal_code
        FROM Customers
        ORDER BY RANDOM()
        LIMIT 1;
        '''
        cursor.execute(query)
        row = cursor.fetchall()
        list_of_target_postal_codes.append(row[0][0])
    start = time.time()
    for i in range(50):
        target_postal_code = list_of_target_postal_codes[i]
        query = '''SELECT denom, num / denom From( (SELECT o.order_id, CAST(count(*) as REAL) as num
        from Customers c, Orders o, Order_items oi
        where c.customer_id = o.customer_id  and oi.order_id = o.order_id and c.customer_postal_code =:target_code),
        (SELECT count(*) as denom
        From Orders o
        Where o.customer_id in(
        SELECT c.customer_id
        FROM Customers c
        WHERE c.customer_postal_code =:target_code)));
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    SelfOptimizedTimes.append((end - start) * 1000)
    print((end - start) * 1000)
    connection.close()

def queryUserOptimized(db_path): 
    global connection, cursor, UserOptimizedTimes
    connect(db_path)
    
    cursor.execute('PRAGMA automatic_index=OFF; ')
    cursor.execute('PRAGMA foreign_keys=ON; ')
    connection.commit()
    createIndexes()
    
    list_of_target_postal_codes = []
    for i in range(50):
        query = '''SELECT customer_postal_code
        FROM Customers
        ORDER BY RANDOM()
        LIMIT 1;
        '''
        cursor.execute(query)
        row = cursor.fetchall()
        list_of_target_postal_codes.append(row[0][0])
    start = time.time()
    for i in range(50):
        target_postal_code = list_of_target_postal_codes[i]
        query = '''SELECT denom, num / denom From( (SELECT o.order_id, CAST(count(*) as REAL) as num
        from Customers c, Orders o, Order_items oi
        where c.customer_id = o.customer_id  and oi.order_id = o.order_id and c.customer_postal_code =:target_code),
        (SELECT count(*) as denom
        From Orders o
        Where o.customer_id in(
        SELECT c.customer_id
        FROM Customers c
        WHERE c.customer_postal_code =:target_code)));
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    UserOptimizedTimes.append((end - start) * 1000)
    print((end - start)*1000)
    
    dropIndexes()
    connection.close()

def createTable():
    global UnOptimizedTimes, SelfOptimizedTimes, UserOptimizedTimes

    BottomUserOptimized = []
    for i in range(3):
        BottomUserOptimized.append(UnOptimizedTimes[i] + SelfOptimizedTimes[i])

    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    width = 0.75

    fig, ax = plt.subplots()

    ax.bar(labels, UnOptimizedTimes, width, label = "Unoptimized")
    print(UnOptimizedTimes, SelfOptimizedTimes, UserOptimizedTimes)
    ax.bar(labels, SelfOptimizedTimes, width, bottom = UnOptimizedTimes ,label = "Self-Optimized")
    ax.bar(labels, UserOptimizedTimes, width, bottom = BottomUserOptimized, label = "User-Optimized")

    ax.set_ylabel('Time (ms)')
    ax.set_title('Query 3')
    ax.legend()

    plt.savefig('./Q3A3chart.png')
    
def main():
    global unoptimizedTimes, selfOptimizedTimes, userOptimizedTimes

    db_path = './A3Small.db'
    print("Small Unoptimized:")
    queryUnoptimized(db_path)
    print("Small Self Optimized:")
    querySelfOptimized(db_path)
    print("Small User Optimized:")
    queryUserOptimized(db_path)

    print("-----------------------")
    
    db_path = './A3Medium.db'
    print("Medium Unoptimized:")
    queryUnoptimized(db_path)
    print("Medium Self Optimized:")
    querySelfOptimized(db_path)
    print("Medium User Optimized:")
    queryUserOptimized(db_path)

    print("-----------------------")

    db_path = './A3Large.db'
    print("Large Unoptimized:")
    queryUnoptimized(db_path)
    print("Large Self Optimized:")
    querySelfOptimized(db_path)
    print("Large User Optimized:")
    queryUserOptimized(db_path)

    print("-----------------------")
    createTable()
    
if __name__ == "__main__":
    main()
    
    