# Examples

Each example was run against `vending.db` with `gpt-4o-mini` at temperature 0. Prices are stored in cents. "Zero-shot" gives the model only the schema and sample rows. "Few-shot" also gives it three example question/SQL pairs from this database.

## 1. Which machine has made the most money?

Worked in both strategies.

```sql
SELECT vm.name, SUM(s.price_sold_at) / 100.0 AS total_dollars
FROM sale s JOIN vending_machine vm ON vm.vending_machine_id = s.vending_machine_id
GROUP BY vm.vending_machine_id
ORDER BY total_dollars DESC
LIMIT 1;
```

Rows: `[('Engineering Machine', 22.5)]`

Answer: The Engineering Machine has made the most money, with a total of $22.50.

Checked by hand against `seed.sql`: 2 x $1.50 + 4 x $2.00 + 2 x $1.25 + 3 x $1.50 + 2 x $2.25 = $22.50.

## 2. How much profit has each product made?

Zero-shot **failed**, few-shot worked.

Zero-shot SQL:

```sql
SELECT p.name, SUM(s.price_sold_at - ptv.buy_price) AS profit
FROM sale s
JOIN product_to_vending ptv ON s.vending_machine_id = ptv.vending_machine_id AND s.product_id = ptv.product_id
JOIN product p ON ptv.product_id = p.product_id
GROUP BY p.name;
```

Error: `no such column: ptv.buy_price`. The model put `buy_price` on the wrong table. It is on `product`.

Few-shot SQL (correct):

```sql
SELECT p.name, SUM(s.price_sold_at - p.buy_price) / 100.0 AS profit_dollars
FROM sale s JOIN product p ON p.product_id = s.product_id
GROUP BY p.product_id;
```

Answer: Coke $8.10, Water $3.00, Gatorade $5.50, Doritos $3.15, Pretzels $1.50, Snickers $4.25, Skittles $2.70, Granola Bar $2.40, Trail Mix $2.90, Orange Juice $1.40.

Caveat: this question is almost identical to one of the few-shot examples, so the model could mostly copy it.

## 3. Which products are out of stock in any machine?

Worked in both strategies. Few-shot also reported which machine.

```sql
SELECT p.name, vm.name
FROM product p
JOIN product_to_vending pv ON p.product_id = pv.product_id
JOIN vending_machine vm ON pv.vending_machine_id = vm.vending_machine_id
WHERE pv.quantity = 0;
```

Rows: `[('Skittles', 'Engineering Machine'), ('Snickers', 'Dorm Machine')]`

Answer: Skittles in the Engineering Machine and Snickers in the Dorm Machine are out of stock.

## 4. Which machine needs restocking?

Ran in both strategies, but the question is vague, so the model invented a rule.

```sql
SELECT vm.name, p.name, pv.quantity
FROM product_to_vending pv
JOIN vending_machine vm ON vm.vending_machine_id = pv.vending_machine_id
JOIN product p ON p.product_id = pv.product_id
WHERE pv.quantity < 5;
```

Rows: Skittles 0 (Engineering), Trail Mix 4 (Gym), Doritos 3 (Dorm), Snickers 0 (Dorm).

Answer: Listed all four. The zero-shot answer added "needs restocking soon" for the low-stock items.

The database has no restock threshold. Both strategies picked `< 5` without saying they guessed, and the English answer presented it as fact.

## 5. What's the most expensive product?

Ran in both strategies, but neither answer is fully right.

Zero-shot SQL:

```sql
SELECT name, MAX(sell_price) AS most_expensive_price
FROM product_to_vending JOIN product ON product_to_vending.product_id = product.product_id;
```

Rows: `[('Trail Mix', 225)]`. Answer: Trail Mix, $2.25. This hides a tie. Orange Juice also sells for $2.25 (in the Dorm Machine), and the query only returns one row.

Few-shot SQL:

```sql
SELECT name, buy_price FROM product ORDER BY buy_price DESC LIMIT 1;
```

Rows: `[('Gatorade', 90)]`. Answer: "Gatorade, which costs $0.90". This is the price the owner pays, not what customers pay. Customers pay $2.00 for Gatorade, so the answer is misleading. Few-shot did worse than zero-shot on this question.

## 6. How many combos of items can you get for 5 dollars? (my own question)

Did not work in either strategy.

```sql
SELECT COUNT(*) FROM product_to_vending WHERE sell_price <= 500;
```

Rows: `[(18,)]`. Answer: "You can get 18 different combos of items for 5 dollars."

Both strategies generated essentially the same query. It counts every row in `product_to_vending` (18 machine/product listings) because every single item costs under $5. It does not build any combinations. The question never says how many items per combo, whether items can repeat, or whether the combo must come from one machine, and the model guessed none of that.

## 7. How many pairs of different items from the Library Machine cost 5 dollars or less together?

The reworded version of question 6. Worked in both strategies.

```sql
SELECT COUNT(*)
FROM product_to_vending p1
JOIN product_to_vending p2 ON p1.vending_machine_id = p2.vending_machine_id AND p1.product_id < p2.product_id
WHERE p1.sell_price + p2.sell_price <= 500 AND p1.vending_machine_id = 1;
```

Rows: `[(10,)]`. Answer: 10 pairs.

I checked this against the data: the Library Machine carries 5 products, so there are 10 possible pairs. The limit is not really tested here. The two most expensive items cost $1.75 each ($3.50 together), so every pair is under $5. Larger combos, such as triples, would be a better test of the price limit. Spelling out "pairs", "different items" and "Library Machine" turned a failure into a correct answer. The self-join on `p1.product_id < p2.product_id` avoids counting a pair twice and avoids pairing an item with itself.
