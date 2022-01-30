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
    connection.commit()
    
def dropUndefinedTables():
    global connection, cursor
    cursor.execute('''DROP TABLE IF EXISTS Customers_undefined;''')
    cursor.execute('''DROP TABLE IF EXISTS Orders_undefined;''')
    connection.commit()

def createIndexes():
    global connection, cursor
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cust_name3 ON Customers(customer_postal_code, customer_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id2 ON Orders(customer_id);')
    connection.commit()
    
def dropIndexes():
    global connection, cursor
    cursor.execute('DROP INDEX IF EXISTS idx_cust_name3')
    cursor.execute('DROP INDEX IF EXISTS idx_order_id2')
    connection.commit()
    
def queryUnoptimized(db_path): 
    global connection, cursor, UnOptimizedTimes
    connect(db_path)
    
    createUndefinedTables()
    cursor.execute('PRAGMA automatic_index=OFF; ')
    cursor.execute('PRAGMA foreign_keys=OFF; ')
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
        query = '''SELECT COUNT(*)
        FROM Orders_undefined O 
        WHERE O.Customer_id IN (
        SELECT C.customer_id
        FROM Customers_undefined C
        WHERE C.customer_postal_code = :target_code
        );
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    UnOptimizedTimes.append((end - start) * 100)
    dropUndefinedTables()
    print((end - start)*100)
    connection.close()

def querySelfOptimized(db_path): 
    global connection, cursor, SelfOptimizedTimes
    connect(db_path)
    
    cursor.execute('PRAGMA automatic_index=ON; ')
    cursor.execute('PRAGMA foreign_keys=ON; ')
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
        query = '''SELECT COUNT(*)
        FROM Orders O 
        WHERE O.Customer_id IN (
        SELECT C.customer_id
        FROM Customers C
        WHERE C.customer_postal_code = :target_code
        );
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    SelfOptimizedTimes.append((end - start) * 100)
    print((end - start) * 100)
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
        query = '''SELECT COUNT(*)
        FROM Orders O 
        WHERE O.Customer_id IN (
        SELECT C.customer_id
        FROM Customers C
        WHERE C.customer_postal_code = :target_code
        );
        '''
        cursor.execute(query, {"target_code": target_postal_code})
    end = time.time()
    UserOptimizedTimes.append((end - start) * 100)
    print((end - start)*100)
    
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
    ax.set_title('Query 1')
    ax.legend()

    plt.savefig('./Q1A3chart.png')
    
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
    
    