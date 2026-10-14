INSERT INTO vending_machine (vending_machine_id, name, location, status) VALUES
    (1, 'Library Machine',  'Harold B. Lee Library, 1st floor', 'active'),
    (2, 'Engineering Machine', 'Engineering Building lobby',    'active'),
    (3, 'Gym Machine',      'Smith Fieldhouse',                 'out_of_service'),
    (4, 'Dorm Machine',     'Helaman Halls, building C',        'maintenance');

INSERT INTO product (product_id, type_of_product, name, buy_price) VALUES
    (1,  'drink',   'Coke',               60),
    (2,  'drink',   'Water',              25),
    (3,  'drink',   'Gatorade',           90),
    (4,  'snack',   'Doritos',            70),
    (5,  'snack',   'Pretzels',           50),
    (6,  'candy',   'Snickers',           65),
    (7,  'candy',   'Skittles',           60),
    (8,  'healthy', 'Granola Bar',        55),
    (9,  'healthy', 'Trail Mix',          80),
    (10, 'drink',   'Orange Juice',       85);

INSERT INTO product_to_vending (vending_machine_id, product_id, sell_price, quantity) VALUES
    (1, 1, 150, 12), (1, 2, 100, 20), (1, 4, 175, 8),  (1, 6, 150, 10), (1, 8, 175, 6),
    (2, 1, 150, 5),  (2, 3, 200, 9),  (2, 5, 125, 14), (2, 7, 150, 0),  (2, 9, 225, 7),
    (3, 2, 100, 15), (3, 3, 200, 11), (3, 8, 175, 10), (3, 9, 225, 4),
    (4, 1, 150, 18), (4, 4, 175, 3),  (4, 6, 150, 0),  (4, 10, 225, 6);

INSERT INTO sale (vending_machine_id, product_id, price_sold_at) VALUES
    (1, 1, 150), (1, 1, 150), (1, 1, 150), (1, 1, 150), (1, 1, 150),
    (1, 2, 100), (1, 2, 100), (1, 2, 100),
    (1, 4, 175), (1, 4, 175),
    (1, 6, 150), (1, 6, 150), (1, 6, 150),
    (1, 8, 175),
    (2, 1, 150), (2, 1, 150),
    (2, 3, 200), (2, 3, 200), (2, 3, 200), (2, 3, 200),
    (2, 5, 125), (2, 5, 125),
    (2, 7, 150), (2, 7, 150), (2, 7, 150),
    (2, 9, 225), (2, 9, 225),
    (3, 2, 100), (3, 3, 200), (3, 8, 175),
    (4, 1, 150), (4, 1, 150), (4, 4, 175), (4, 6, 150), (4, 6, 150), (4, 10, 225);
