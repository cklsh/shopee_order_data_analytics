import pandas as pd

def load_and_clean_data(filepath='../data/sample_data.csv'):
    #Load Data
    df = pd.read_csv(filepath, sep=',',  on_bad_lines='skip')
    df.columns = df.columns.str.strip()

    #Clean Data
    df= df[df['status'].str.lower() != 'batal']
    df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce')
    df['order_completion_date'] = pd.to_datetime(df['order_completion_date'], format='%d/%m/%y %H.%M', errors='coerce')

    return df

def define_customer_df_features(df):
    # aggregate customer data
    customer_df = df.groupby('username').agg(
        total_orders=('order_number', 'nunique'), #uniq order; frequency
        total_spent=('total_price', sum), #sum total price; monetary
        last_order=('order_completion_date', 'max') #get recency of order; recency
    ).reset_index()

    # add recency (in days)
    latest_date = df['order_completion_date'].max() #get the latest order date from all order
    customer_df['recency_days'] = (latest_date - customer_df['last_order']).dt.days #calculate the recency in days format
    customer_df['recency_days'] = customer_df['recency_days'].fillna(999) # to handle NaN value, imply the customer is inactive
    # add aov
    customer_df['aov'] = customer_df['total_spent']/ customer_df['total_orders'] #aov; total revenue/ total number of orders

    # drop unused column
    customer_df = customer_df.drop(columns=['last_order'])
    return customer_df

def customer_df_responded_to_upsell(df):
    df['size'] = df['product_name'].str.extract(r'(\d+\s?ML)', expand=False)
    df['size'] = df['size'].str.replace(' ','').str.upper()

    df_filtered = df[df['size'].isin(['5ML', '60ML'])]

    df_filtered['order_completion_date'] = pd.to_datetime(df_filtered['order_completion_date'])
    df_sorted = df_filtered.sort_values(['username', 'order_completion_date'])

    user_size_history = df_sorted.groupby('username')['size'].apply(list)

    def is_upsell(size_list):
        try:
            return int(size_list.index('5ML') < size_list.index('60ML'))
        except ValueError:
            return 0
    upsell_flags = user_size_history.apply(is_upsell)

    customer_df = define_customer_df_features(df)
    customer_df['responded_to_upsell'] = customer_df['username'].map(upsell_flags).fillna(0).astype(int)
    
    return customer_df

