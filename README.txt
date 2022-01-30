Group #1
ysrivast - Yash Srivastava
cjen - Cameron Jen
raunak1 - Raunak Agarwal
atmakuri - Revanth Atmakuri


References:
- https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html
- https://stackoverflow.com/questions/2279706/select-random-row-from-a-sqlite-table
- https://www.youtube.com/watch?v=fsG1XaZEa78 

We declare that we did not collaborate with anyone outside our own group in this assignment. 

Assumptions: We have assumed that the database files are in the same file/directory as the python files.
____________________________________________________________________________
Here is our query for question #1: 
“SELECT COUNT(*)
FROM Orders O 
WHERE O.Customer_id IN (
        SELECT C.customer_id
        FROM Customers C
        WHERE C.customer_postal_code = :target_code
        )
;”

This query will search through the table Orders to find all of the orders which correspond to a customer_id (found in Customers) which exists in a target postal code. 

With this in mind, we created the following two indexes: 
* CREATE INDEX IF NOT EXISTS idx_cust_name3 ON Customers(customer_postal_code, customer_id);')
* CREATE INDEX IF NOT EXISTS idx_order_id2 ON Orders(customer_id);

The first index is intended to make the speed of our inner query much faster. It first does this by making all of the customers with our target postal code readily available, as it first indexes by customer postal code. It then indexes by customer_id, which should theoretically make the process of an unsuccessful search much faster (i.e. once the query encounters a record with a customer_id greater than the provided customer_id, it knows the search is unsuccessful, and does not have to traverse through the remaining records). 
The second index makes the speed of our outer query much faster, by sorting the Orders table by customer_id. Similarly, this index should also speed up an unsuccessful search; as once a customer_id becomes greater than all of the customer_ids in the inner query, the outer query will know that its remaining tuples are unsuccessful.

When we run this query and use SQLite’s EXPLAIN QUERY PLAN, both of these indexes are incorporated, and this results in a highly significant reduction in query runtime compared to the unoptimized/self-optimized query settings.
One thing worth noting is the similarity in running times between the unoptimized and self-optimized query. It is worth mentioning that, while running the self-optimized query (i.e. turning foreign and primary keys on), there are no additional indexes being used when we use SQLite’s EXPLAIN QUERY PLAN. As a result, there is no significant reduction in time when we run the query in these two settings. 
____________________________________________________________________________
Here is our query for question #2: 
“CREATE VIEW IF NOT EXISTS OrderSize(oid, size)
AS SELECT O.order_id, COUNT(*)
FROM Orders O, Order_items O_items
WHERE O.order_id == O_items.order_id
GROUP BY O.order_id;”

The first part of the query (shown above) creates the OrderSize view, which consists of two columns; Order_id, and the number of items in that order (which correspond to records in order_items with the corresponding order_id). 
 
“SELECT denom AS Total_number_of_orders, num / denom AS Average_number_of_items_per_order FROM( (
SELECT CAST (SUM(OS.size) AS REAL) AS num
FROM Customers C, Orders O, OrderSize OS
WHERE C.customer_postal_code = :target_code AND C.customer_id = O.customer_id AND O.order_id = OS.oid
),
(SELECT count() AS denom
FROM Orders o
WHERE o.customer_id IN(
SELECT c.customer_id
FROM Customers c
WHERE c.customer_postal_code =:target_code)));”


The next part of the query (shown above) displays the total number of orders for a given postal code, and the average orders per postal code. The total number of orders is calculated using our query from question 1. The average number of items per order is calculated using the OrderSize view we created, by summing the amount of items across all tuples with an order_id that exists in our target postal code. 

We created the following indexes: 
* CREATE INDEX IF NOT EXISTS idx_cust ON Customers(customer_postal_code, customer_id);
* CREATE INDEX IF NOT EXISTS idx_order ON Orders(customer_id,order_id);
For this query, the indexes that make the processing faster are idx_cust and idx_order. idx_cust sorts the data in the Customers table on the basis of customer_postal_code which helps the inner query return the data faster. idx_order sorts the data in the Orders table on the basis of customer_id, which makes it easier for it to look through the Orders table. 
One thing to take note of is the large amount of time required to execute the Self-optimized query compared to the unoptimized query. For the self-optimized query, we noticed that the tables Orders and Customers were sorted on the basis of their primary keys, which is not very efficient. It does not do any sorting for the Order_items table which makes the query quite slow. This makes the time for the user optimized query to be slower. 
____________________________________________________________________________
Here is our query for question #3: 
“SELECT denom, num / denom From( (SELECT o.order_id, CAST(count(*) as REAL) as num
            from Customers c, Orders o, Order_items oi
            where c.customer_id = o.customer_id  and oi.order_id = o.order_id and c.customer_postal_code=:target_code),
            (SELECT count(*) as denom
            From Orders o
            Where o.customer_id in(
            SELECT c.customer_id
            FROM Customers c
            WHERE c.customer_postal_code =:target_code)));”

The query finds a number, ‘num’, which is the sum of all the orders that have been placed by the customer from the postal_code target_code. It then finds another number, ‘denom’, which is the sum of all the customers/orders from the same postal code. Dividing these two gives us the average number of orders placed from that postal code. Both ‘num’ and the quotient from this division equation are returned. 

Unoptimized Query Plan (130-170 ms runtime)
If we look at the unoptimized query plan,  we observe that there is no sorting and the tables that are used do not have primary keys or foreign keys. This distributes the data randomly throughout the tables and the searching for data is random which can make it faster than self-optimized or slower depending on the distribution of data.

Self-optimized Query Plan (330- 450 ms runtime)
For the self optimized query plan, it only sorts table Orders and Customers on the basis of their primary keys, which is not very efficient. It does not do any sorting for the Order_items table which makes the query quite slow. This makes the time even slower. According to the Query Plan, the auto_indexing for table Orders is on the basis of order_id and for Customers is on customer_id.

User-optimized Query Plan (3-6 ms runtime)

Used Indexes:
* CREATE INDEX IF NOT EXISTS idx_cust ON Customers(customer_postal_code, customer_id)
* CREATE INDEX IF NOT EXISTS idx_order ON Orders(customer_id,order_id)
* CREATE INDEX IF NOT EXISTS idx_order_items ON Order_items(order_id);

1)    “SELECT count(*) as denom
                       From Orders o
                       Where o.customer_id in(
                       SELECT c.customer_id
                       FROM Customers c
                       WHERE c.customer_postal_code =:target_code));”
For this query, the indexes that make the processing faster are idx_cust and idx_order. idx_cust sorts the data in the Customers table on the basis of customer_postal_code which helps the inner query return the data faster. idx_order sorts the data in the Orders table on the basis of customer_id, which makes it easier for it to look through the Orders table.

2)     “(SELECT o.order_id, CAST(count(*) as REAL) as num
            from Customers c, Orders o, Order_items oi
        where c.customer_id = o.customer_id  and oi.order_id = o.order_id and
c.customer_postal_code=:target_code);”
For this query, the indexes that make the processing faster are idx_order and idx_order_items. idx_order sorts the data in the Orders table on the basis of order_id and idx_order_items sorts the data in the Order_items table on the basis of order_id as well. This makes the search time very efficient.
This query is faster than query 2, because it makes use of a total of 3 indexes created by us, which significantly decreases the search time.
____________________________________________________________________________
Here is our query for question #4: 
We executed the following SQL query:
1)  “SELECT COUNT(DISTINCT(S.seller_postal_code))
FROM Order_items OI, Sellers S
WHERE OI.order_id =:oid
AND S.seller_id = OI.seller_id;”

In the query, we first need to obtain Order_items tuples corresponding to the target order_id. From here, we collect the seller_ids which correspond to the given order_id. This is done in order to check the number of different postal codes corresponding to these seller_ids, which is returned from this query. 
Therefore, we thought it would be best to create an index on Order_items that is first sorted by order_id, then seller_id. For the Sellers table, we just need to create an index on Sellers.seller_id.

The two indices that we created were:
* CREATE INDEX order_items_order_id_seller_id ON Order_items(order_id, seller_id)
* CREATE INDEX sellers_seller_id ON Sellers(seller_id);

When we timed all queries we received interesting results. The unoptimized times would take longer than both the self-optimized and user-optimized times and the self-optimized and user-optimized times were similar. 
We found that the automatic indexes created by the DBMS create the indexes on the primary keys on both tables namely seller_id for Sellers and order_id for Order_items. Therefore, the index for the Sellers table that was created automatically was the same as the index the I created (in fact when using SQLites, EXPLAIN QUERY PLAN for the user optimized, the automatic index was being used instead) and the automatic index for the Order_items and the index that I created both contain order_id and seller_id and should perform similarly.
Due to this similarity, it should be expected that both the self optimized and user optimized queries should have similar timings, and should both be faster than the unoptimized query.