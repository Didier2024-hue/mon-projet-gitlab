CREATE DATABASE test;

\c test

CREATE TABLE IF NOT EXISTS customer (
  id UUID,
  lastname VARCHAR,
  firstname VARCHAR,
  sex VARCHAR,
  modification_date TIMESTAMP,
  street_number SMALLINT,
  street_name VARCHAR,
  city VARCHAR,
  postcode VARCHAR,
  region VARCHAR,
  PRIMARY KEY(id, modification_date)
);

CREATE TABLE IF NOT EXISTS product (
  id UUID,
  name VARCHAR,
  categories VARCHAR,
  price REAL,
  weight REAL,
  modification_date TIMESTAMP,
  PRIMARY KEY(id, modification_date)
);

CREATE TABLE IF NOT EXISTS "order" (
  id UUID,
  date_order TIMESTAMP,
  date_shipping TIMESTAMP,
  quantity SMALLINT,
  price REAL,
  customer_id UUID,
  product_id UUID,
  CONSTRAINT fk_customer
    FOREIGN KEY (customer_id, date_order)
    REFERENCES customer (id, modification_date),
  CONSTRAINT fk_product
    FOREIGN KEY (product_id, date_order)
    REFERENCES product (id, modification_date)
);
