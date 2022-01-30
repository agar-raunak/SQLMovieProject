import sqlite3
import time
import matplotlib.pyplot as plt

db_path = ""
connection = None
cursor = None
unoptimizedTimes = []
selfOptimizedTimes = []
userOptimizedTimes = []

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()

def createUndefinedTables():
    global connection, cursor
    cursor.execute('''CREATE TABLE IF NOT EXISTS "Customers_undefined" ( 
	"customer_id" TEXT,
	"customer_postal_code" INTEGER
    );''')

    cursor.execute('''INSERT INTO "Customers_undefined"
    SELECT customer_id, customer_postal_code
    FROM Customers''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "Sellers_undefined" (
	"seller_id"	TEXT,
	"seller_postal_code" INTEGER
    );''')

    cursor.execute('''INSERT INTO "Sellers_undefined"
    SELECT seller_id, seller_postal_code
    FROM Sellers''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "Orders_undefined" (
	"order_id" TEXT,
	"customer_id" TEXT
    );''')

    cursor.execute('''INSERT INTO "Orders_undefined"
    SELECT order_id, customer_id
    FROM Orders''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "Order_items_undefined" (
	"order_id" TEXT,
	"order_item_id" INTEGER,
	"product_id" TEXT,
	"seller_id"	TEXT
    );''')

    cursor.execute('''INSERT INTO "Order_items_undefined"
    SELECT order_id, order_item_id, product_id, seller_id 
    FROM Order_items''')

    connection.commit()

def dropUndefinedTables():
    cursor.execute('''DROP TABLE IF EXISTS Customers_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Sellers_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Orders_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Order_items_undefined;''')
    connection.commit()

def createIndexes():
    query = '''CREATE INDEX order_items_order_id_seller_id
    ON Order_items(order_id, seller_id);
    '''
    cursor.execute(query)

    query = '''CREATE INDEX sellers_seller_id
    ON Sellers(seller_id);
    '''
    cursor.execute(query)

    connection.commit()

def dropIndexes():
    cursor.execute("DROP INDEX IF EXISTS orders_order_id")
    cursor.execute("DROP INDEX IF EXISTS order_items_order_id_seller_id")
    cursor.execute("DROP INDEX IF EXISTS sellers_seller_id")
    connection.commit()

def createTable():
    global unoptimizedTimes, selfOptimizedTimes, userOptimizedTimes

    bottomUserOptimized = []
    for i in range(3):
        bottomUserOptimized.append(unoptimizedTimes[i] + selfOptimizedTimes[i])

    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    width = 0.75

    fig, ax = plt.subplots()

    ax.bar(labels, unoptimizedTimes, width, label = "Unoptimized")
    ax.bar(labels, selfOptimizedTimes, width, bottom = unoptimizedTimes ,label = "Self-Optimized")
    ax.bar(labels, userOptimizedTimes, width, bottom = bottomUserOptimized, label = "User-Optimized")

    ax.set_ylabel('Time (ms)')
    ax.set_title('Query 4')
    ax.legend()

    plt.savefig('./Q4A3chart.png')

def queryUnoptimzed(db_path):
    global connection, cursor, unoptimizedTimes
    connect(db_path)

    createUndefinedTables()
    cursor.execute(' PRAGMA automatic_index=OFF; ')
    cursor.execute(' PRAGMA foreign_keys=OFF; ')

    totalTime = 0
    for i in range(50):
        order_id = ""
        query = '''SELECT order_id
        FROM Orders_undefined
        ORDER BY RANDOM()
        LIMIT 1;'''

        cursor.execute(query)
        rows = cursor.fetchall()

        order_id = rows[0][0]

        start = time.time()

        query = '''SELECT COUNT(DISTINCT(S.seller_postal_code))
        FROM Order_items_undefined OI, Sellers_undefined S
        WHERE OI.order_id =:oid
        AND S.seller_id = OI.seller_id;'''

        cursor.execute(query, {"oid": order_id})

        end = time.time()
        totalTime = totalTime + (end - start)
    
    print(totalTime * 1000, "ms")
    unoptimizedTimes.append((totalTime) * 1000)

    dropUndefinedTables()
    connection.close()

def querySelfOptimzed(db_path):
    global connection, cursor, selfOptimizedTimes
    connect(db_path)

    cursor.execute(' PRAGMA automatic_index=ON; ')
    cursor.execute(' PRAGMA foreign_keys=ON; ')    

    totalTime = 0
    for i in range(50):
        order_id = ""
        query = '''SELECT order_id
        FROM Orders
        ORDER BY RANDOM()
        LIMIT 1;'''

        cursor.execute(query)
        rows = cursor.fetchall()

        order_id = rows[0][0]

        start = time.time()

        query = '''SELECT COUNT(DISTINCT(S.seller_postal_code))
        FROM Order_items OI, Sellers S
        WHERE OI.order_id =:oid
        AND S.seller_id = OI.seller_id;'''
        
        cursor.execute(query, {"oid": order_id})


        end = time.time()
        totalTime = totalTime + (end - start)

    print(totalTime * 1000, "ms")
    selfOptimizedTimes.append((totalTime) * 1000)

    connection.close()

def queryUserOptimzed(db_path):
    global connection, cursor, userOptimizedTimes
    connect(db_path)

    cursor.execute(' PRAGMA automatic_index=OFF; ')
    cursor.execute(' PRAGMA foreign_keys=ON; ')

    createIndexes();

    totalTime = 0
    for i in range(50):
        order_id = ""
        query = '''SELECT order_id
        FROM Orders
        ORDER BY RANDOM()
        LIMIT 1;'''

        cursor.execute(query)
        rows = cursor.fetchall()

        order_id = rows[0][0]

        start = time.time()

        query = '''SELECT COUNT(DISTINCT(S.seller_postal_code))
        FROM Order_items OI, Sellers S
        WHERE OI.order_id =:oid
        AND S.seller_id = OI.seller_id;'''

        cursor.execute(query, {"oid": order_id})

        end = time.time()
        totalTime = totalTime + (end - start)

    print(totalTime * 1000, "ms")
    userOptimizedTimes.append((totalTime) * 1000)

    dropIndexes()
    connection.close()

def main():
    global unoptimizedTimes, selfOptimizedTimes, userOptimizedTimes

    db_path = './A3Small.db'
    print("Small Unoptimized:")
    queryUnoptimzed(db_path)
    print("Small Self Optimized:")
    querySelfOptimzed(db_path)
    print("Small User Optimized:")
    queryUserOptimzed(db_path)

    print("-----------------------")
    
    db_path = './A3Medium.db'
    print("Medium Unoptimized:")
    queryUnoptimzed(db_path)
    print("Medium Self Optimized:")
    querySelfOptimzed(db_path)
    print("Medium User Optimized:")
    queryUserOptimzed(db_path)

    print("-----------------------")

    db_path = './A3Large.db'
    print("Large Unoptimized:")
    queryUnoptimzed(db_path)
    print("Large Self Optimized:")
    querySelfOptimzed(db_path)
    print("Large User Optimized:")
    queryUserOptimzed(db_path)

    createTable()

if __name__ == "__main__":
    main()