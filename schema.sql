PRAGMA foreign_keys = ON;

-- Prices are stored in cents (e.g. 150 = $1.50)

CREATE TABLE vending_machine (
    vending_machine_id INTEGER PRIMARY KEY,
    name               TEXT NOT NULL,
    location           TEXT NOT NULL,
    status             TEXT NOT NULL CHECK (status IN ('active', 'out_of_service', 'maintenance'))
);

CREATE TABLE product (
    product_id      INTEGER PRIMARY KEY,
    type_of_product TEXT NOT NULL CHECK (type_of_product IN ('drink', 'snack', 'candy', 'healthy')),
    name            TEXT NOT NULL,
    buy_price       INTEGER NOT NULL  -- what we pay per unit, in cents
);

-- Which products a machine carries, at what price, and how many are left
CREATE TABLE product_to_vending (
    vending_machine_id INTEGER NOT NULL REFERENCES vending_machine(vending_machine_id),
    product_id         INTEGER NOT NULL REFERENCES product(product_id),
    sell_price         INTEGER NOT NULL,  -- price charged in this machine, in cents
    quantity           INTEGER NOT NULL,
    PRIMARY KEY (vending_machine_id, product_id)
);

CREATE TABLE sale (
    sale_id            INTEGER PRIMARY KEY,
    vending_machine_id INTEGER NOT NULL REFERENCES vending_machine(vending_machine_id),
    product_id         INTEGER NOT NULL REFERENCES product(product_id),
    price_sold_at      INTEGER NOT NULL   -- in cents
);
