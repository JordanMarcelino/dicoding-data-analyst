import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydeck as pdk
import seaborn as sns
import streamlit as st

sns.set_theme(style="dark")


def create_top_products_sales_df(df: pd.DataFrame) -> pd.DataFrame:
    top_products_sales = (
        df.groupby("product_category_name_english")
        .agg({"order_id": "nunique"})
        .sort_values(by="order_id", ascending=False)
        .reset_index()
        .rename(
            columns={
                "order_id": "order_count",
                "product_category_name_english": "product_name",
            }
        )
    )

    return top_products_sales


def create_top_products_reviews_df(df: pd.DataFrame) -> pd.DataFrame:
    top_products_reviews = (
        df.groupby("product_category_name_english")
        .agg({"review_score": "mean"})
        .sort_values(by="review_score", ascending=False)
        .reset_index()
        .rename(
            columns={
                "review_score": "rating",
                "product_category_name_english": "product_name",
            }
        )
    )

    return top_products_reviews


def create_top_orders_city_df(df: pd.DataFrame) -> pd.DataFrame:
    orders_city = (
        df.groupby(["customer_city"])
        .agg({"order_id": "nunique"})
        .sort_values(by="order_id", ascending=False)
        .reset_index()
        .rename(
            columns={
                "order_id": "order_count",
            }
        )
    )

    return orders_city


def create_seller_revenue_df(df: pd.DataFrame) -> pd.DataFrame:
    seller_revenue = (
        df.groupby(["seller_city"])
        .agg({"price": "sum"})
        .sort_values(by="price", ascending=False)
        .reset_index()
    )

    return seller_revenue


def create_orders_approved_df(df: pd.DataFrame) -> pd.DataFrame:
    orders_approved = (
        df.groupby(["orders_received_hours", "orders_received_minutes"])
        .agg({"order_id": "nunique"})
        .sort_values(["orders_received_hours", "orders_received_minutes"])
        .reset_index()
    )
    orders_approved["label"] = orders_approved.apply(
        lambda row: f"{int(row['orders_received_hours'])}h {int(row['orders_received_minutes'])}m",
        axis=1,
    )
    return orders_approved


def create_delivery_time_df(df: pd.DataFrame) -> pd.DataFrame:
    delivery_time = (
        df.groupby("orders_delivery_time")
        .agg({"order_id": "nunique"})
        .reset_index()
        .sort_values("orders_delivery_time")
    )
    delivery_time["label"] = delivery_time.apply(
        lambda rows: f"{int(rows['orders_delivery_time'])} days", axis=1
    )
    return delivery_time


def create_reviews_answered_df(df: pd.DataFrame) -> pd.DataFrame:
    reviews_answered = (
        df.groupby("reviews_answered_hours")
        .agg({"order_id": "nunique"})
        .reset_index()
        .sort_values("reviews_answered_hours")
    )
    reviews_answered["label"] = reviews_answered.apply(
        lambda rows: f"{int(rows['reviews_answered_hours'])} h", axis=1
    )

    return reviews_answered


def create_orders_day_df(df: pd.DataFrame) -> pd.DataFrame:
    orders_day = (
        df.groupby(["orders_day"])
        .agg({"order_id": "nunique"})
        .sort_values("order_id", ascending=False)
        .reset_index()
    )

    return orders_day


def create_orders_month_df(df: pd.DataFrame) -> pd.DataFrame:
    orders_month = (
        df.groupby("orders_month")
        .agg({"order_id": "nunique"})
        .sort_values("order_id", ascending=False)
        .reset_index()
    )

    return orders_month


def create_payment_type_df(df: pd.DataFrame) -> pd.DataFrame:
    payment_type = (
        df.groupby("payment_type")
        .agg({"order_id": "nunique"})
        .sort_values("order_id", ascending=False)
        .reset_index()
    )

    return payment_type


def create_customer_demography_df(df: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    customer_demography = pd.merge(
        df,
        geo,
        left_on=["customer_zip_code_prefix", "customer_city", "customer_state"],
        right_on=[
            "geolocation_zip_code_prefix",
            "geolocation_city",
            "geolocation_state",
        ],
    )
    customer_demography = customer_demography[
        ~customer_demography.customer_id.duplicated()
    ].reset_index(drop=True)

    # Dilimit untuk 5000 sampel, agar tidak terlalu lag
    return customer_demography.sample(5000)


def create_seller_demography_df(df: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    seller_demography = pd.merge(
        df,
        geo,
        left_on=["seller_zip_code_prefix", "seller_city", "seller_state"],
        right_on=[
            "geolocation_zip_code_prefix",
            "geolocation_city",
            "geolocation_state",
        ],
    )
    seller_demography = seller_demography[
        ~seller_demography.customer_id.duplicated()
    ].reset_index(drop=True)

    # Dilimit untuk 5000 sampel, agar tidak terlalu lag
    return seller_demography.sample(5000)


all_df = pd.read_csv("dashboard/all_final.csv")
geolocation_df = pd.read_csv("dashboard/geolocation_final.csv")

all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

date_columns = [
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    all_df[column] = pd.to_datetime(all_df[column], format="mixed")


# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(
        "https://www.thepostcity.com/wp-content/uploads/2020/07/Ecommerce-780x470.jpg"
    )

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )


main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date))
    & (all_df["order_purchase_timestamp"] <= str(end_date))
]


top_products_sales_df = create_top_products_sales_df(main_df)
top_products_reviews_df = create_top_products_reviews_df(main_df)
top_orders_city = create_top_orders_city_df(main_df)
seller_revenue_df = create_seller_revenue_df(main_df)
orders_approved_df = create_orders_approved_df(main_df)
orders_delivery_time_df = create_delivery_time_df(main_df)
reviews_answered_df = create_reviews_answered_df(main_df)
orders_day_df = create_orders_day_df(main_df)
orders_month_df = create_orders_month_df(main_df)
payment_type_df = create_payment_type_df(main_df)
customer_demography_df = create_customer_demography_df(main_df, geolocation_df)
seller_demography_df = create_seller_demography_df(main_df, geolocation_df)

st.header("Public E-Commerce Dashboard :sparkles:")

# Product sales
st.subheader("Best & Worst Performing Products")

fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="order_count",
    y="product_name",
    data=top_products_sales_df.head(),
    ax=ax[0],
    hue="product_name",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=36)
ax[0].tick_params(axis="x", labelsize=36)

sns.barplot(
    x="order_count",
    y="product_name",
    data=top_products_sales_df.sort_values(by="order_count", ascending=True).head(),
    ax=ax[1],
    hue="product_name",
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=36)
ax[1].tick_params(axis="x", labelsize=36)

st.pyplot(fig)

# Product Rating
st.subheader("Best & Worst Rating Products")

fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="rating",
    y="product_name",
    data=top_products_reviews_df.head(),
    ax=ax[0],
    hue="product_name",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Rating Product", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=32)

sns.barplot(
    x="rating",
    y="product_name",
    data=top_products_reviews_df.sort_values(by="rating", ascending=True).head(),
    ax=ax[1],
    hue="product_name",
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Rating Product", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Most order city
st.subheader("City With The Most Orders")
fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
ax.pie(
    top_orders_city.head()["order_count"],
    labels=top_orders_city.head()["customer_city"],
    autopct="%1.1f%%",
    startangle=140,
)

st.pyplot(fig)

# City Revenue
st.subheader("Best & Worst City Revenue")
fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

xticks = np.linspace(
    seller_revenue_df.head()["price"].min(), seller_revenue_df.head()["price"].max(), 10
).round()
sns.barplot(
    x="price",
    y="seller_city",
    data=seller_revenue_df.head(),
    ax=ax[0],
    hue="seller_city",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best City Revenue", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=24)
ax[0].set_xticks(xticks)
ax[0].set_xticklabels([f"${revenue:,}" for revenue in xticks], rotation=45)

worst_sales = seller_revenue_df.sort_values(by="price", ascending=True).head()
xticks = np.linspace(0, worst_sales.head()["price"].max(), 10).round()
sns.barplot(
    x="price",
    y="seller_city",
    data=worst_sales,
    ax=ax[1],
    hue="seller_city",
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst City Revenue", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=24)
ax[1].set_xticks(xticks)
ax[1].set_xticklabels([f"${revenue:,}" for revenue in xticks], rotation=45)

st.pyplot(fig)

# Order approved time
st.subheader("Order Approved Time")
fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="order_id",
    y="label",
    data=orders_approved_df.head(),
    ax=ax[0],
    hue="label",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Order", fontsize=32)
ax[0].set_title("Quickest Approved Order", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=32)

sns.barplot(
    x="order_id",
    y="label",
    data=orders_approved_df.sort_values(
        ["orders_received_hours", "orders_received_minutes"], ascending=False
    ).head(),
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Order", fontsize=32)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Longest Approved Order", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Order delivery time
st.subheader("Order Delivery Time (day)")

fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="order_id",
    y="label",
    data=orders_delivery_time_df.head(),
    ax=ax[0],
    hue="label",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Order", fontsize=32)
ax[0].set_title("Quickest Delivery Time", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=32)

sns.barplot(
    x="order_id",
    y="label",
    data=orders_delivery_time_df.sort_values(
        by="orders_delivery_time", ascending=False
    ).head(),
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Order", fontsize=32)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Longest Delivery Time", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Review response time
st.subheader("Review Response Time (hour)")

fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="order_id", y="label", data=reviews_answered_df.head(), ax=ax[0], hue="label"
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Review", fontsize=32)
ax[0].set_title("Quickest Review Response", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=32)

sns.barplot(
    x="order_id",
    y="label",
    data=reviews_answered_df.sort_values(
        by="reviews_answered_hours", ascending=False
    ).head(),
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Review", fontsize=32)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Longest Review Response", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Order traffic
st.subheader("Order Traffic")

fig, ax = plt.subplots(1, 2, figsize=(30, 12), dpi=150)

sns.barplot(
    x="order_id",
    y="orders_month",
    data=orders_month_df.head(),
    ax=ax[0],
    hue="orders_month",
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Orders", fontsize=32)
ax[0].set_title("Month With Most Sales", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=32)
ax[0].tick_params(axis="x", labelsize=32)

sns.barplot(
    x="order_id",
    y="orders_month",
    data=orders_month_df.sort_values(by="order_id").head(),
    ax=ax[1],
    hue="orders_month",
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Orders", fontsize=32)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Month With Least Sales", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=32)
ax[1].tick_params(axis="x", labelsize=32)

st.pyplot(fig)

fig, ax = plt.subplots(figsize=(30, 12), dpi=200)
sns.barplot(x="order_id", y="orders_day", data=orders_day_df, ax=ax, hue="orders_day")
ax.set_title("Most and Least Sales by Days", fontsize=40)
ax.set_ylabel(None)
ax.set_xlabel("Total Orders", fontsize=32)
ax.tick_params(axis="y", labelsize=32)
ax.tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Payment type
st.subheader("Top Payment Type")

fig, ax = plt.subplots(figsize=(30, 12), dpi=200)
sns.barplot(
    x="order_id", y="payment_type", data=payment_type_df, ax=ax, hue="payment_type"
)
ax.set_title("Most and Least Used Payment Type", fontsize=40)
ax.set_ylabel(None)
ax.set_xlabel("Total Orders", fontsize=32)
ax.tick_params(axis="y", labelsize=32)
ax.tick_params(axis="x", labelsize=32)

st.pyplot(fig)

# Customer & seller demography
st.subheader("Customer Demography")

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=-23.549,
            longitude=-46.633,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=customer_demography_df,
                get_position="[geolocation_lng, geolocation_lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            )
        ],
    )
)

st.subheader("Seller Demography")
st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=-23.549,
            longitude=-46.633,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=seller_demography_df,
                get_position="[geolocation_lng, geolocation_lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            )
        ],
    )
)
