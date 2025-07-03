import pandas as pd
import numpy as np

import os
print("Current working directory:", os.getcwd())

#generating dummy data for privacy purpose
def generateDummyData():
    #Load Data
    df = pd.read_csv("path", sep=';',  on_bad_lines='skip')
    df.columns = df.columns.str.strip()

    df_sample = df.sample(n=100, random_state=42).copy()
    df_sample['username'] = 'user_' + (df_sample.groupby('username').ngroup() + 1).astype(str)
    df_sample['variant'] = 'dummy_' + (df_sample.groupby('variant').ngroup() + 1).astype(str)
    df_sample['order_number'] = ['ORD_' + str(i+1).zfill(4) for i in range(len(df_sample))]
    df_sample.to_csv('data/sample_data.csv', index=False)

    print("success generate sample_data.csv")

generateDummyData()