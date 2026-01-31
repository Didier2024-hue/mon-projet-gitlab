import json
import pandas as pd
import numpy as np
import os


def extract_orders(data_dir):
    orders_path = os.path.join(data_dir, "to_ingest/bronze/orders.json")

    if not os.path.exists(orders_path):
        raise FileNotFoundError(f"Orders file not found at: {orders_path}")

    orders = []
    with open(orders_path) as json_file:
        for line in json_file:
            orders.append(json.loads(line))
    return orders


def build_df_customer_product(orders):
    customers = []
    products = []
    for order in orders:
        customer = order['customer']
        product = order['product']
        modification_date = order['date_order']

        customer['modification_date'] = modification_date
        product['modification_date'] = modification_date

        customers.append(customer)
        products.append(product)

    df_customer = pd.DataFrame(customers)
    df_product = pd.DataFrame(products)

    # À décommenter plus tard selon le TP
    df_customer = df_customer.drop_duplicates(subset=['id', 'modification_date'])
    df_product = df_product.drop_duplicates(subset=['id', 'modification_date'])

    return df_customer, df_product


def transform_df_customer(df_customer):
    df_delivery = pd.json_normalize(df_customer['delivery_address'])
    df_customer = df_customer.reset_index(drop=True)

    df_customer = pd.concat(
        [
            df_customer[['id', 'lastname', 'firstname', 'sex', 'modification_date']],
            df_delivery
        ],
        axis=1
    )

    df_customer['street_number'] = df_customer['street_number'].astype(int)
    return df_customer


def get_order_price(order):
    try:
        return round(order['product']['price'] * order['quantity'], 2)
    except:
        return np.nan


def transform_orders(orders):
    for order in orders:
        order['customer_id'] = order['customer']['id']
        order['product_id'] = order['product']['id']
        order['price'] = get_order_price(order)

        order.pop('customer', None)
        order.pop('product', None)

    return orders


def transform_df_product(df_product):
    df_product['weight'] = round(df_product['weight'].astype(float), 2)
    df_product['price'] = round(df_product['price'].astype(float), 2)
    return df_product


def load_data(orders, df_customer, df_product, data_dir):
    silver_path = os.path.join(data_dir, "to_ingest/silver")

    os.makedirs(silver_path, exist_ok=True)

    df_customer.to_csv(os.path.join(silver_path, "customers.csv"), index=False)
    df_product.to_csv(os.path.join(silver_path, "products.csv"), index=False)

    orders_file = os.path.join(silver_path, "orders.json")
    with open(orders_file, "w") as f:
        for order in orders:
            json.dump(order, f)
            f.write("\n")

    print(f"✔️ orders, customers and products loaded in {silver_path}")


if __name__ == '__main__':
    data_dir = os.getenv("DATA_DIR")
    if data_dir is None:
        print("❌ DATA_DIR environment variable not set")
        exit(1)

    orders = extract_orders(data_dir)
    df_customer, df_product = build_df_customer_product(orders)

    df_customer = transform_df_customer(df_customer.copy())
    df_product = transform_df_product(df_product.copy())
    orders = transform_orders(orders.copy())

    load_data(orders, df_customer, df_product, data_dir)
