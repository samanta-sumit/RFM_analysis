import pandas as pd
import datetime as dt
import os

def load_data(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data = pd.read_csv(file_path)
    data['OrderDate'] = pd.to_datetime(data['OrderDate'], format='%d-%m-%Y')
    return data

def calculate_rfm(data):
    NOW = dt.datetime(2024, 5, 13)
    rfmTable = data.groupby('Email').agg({
        'OrderDate': lambda x: (NOW - x.max()).days,
        'OrderID': 'count',
        'GrandTotal': 'sum'
    }).reset_index()
    rfmTable.columns = ['Email', 'Recency', 'Frequency', 'Monetary']
    
    quantiles = rfmTable.quantile(q=[0.25, 0.5, 0.75]).to_dict()
    
    def RClass(x, p, d):
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]:
            return 3
        else:
            return 4

    def FMClass(x, p, d):
        if x <= d[p][0.25]:
            return 4
        elif x <= d[p][0.50]:
            return 3
        elif x <= d[p][0.75]:
            return 2
        else:
            return 1

    rfmTable['R'] = rfmTable['Recency'].apply(RClass, args=('Recency', quantiles,))
    rfmTable['F'] = rfmTable['Frequency'].apply(FMClass, args=('Frequency', quantiles,))
    rfmTable['M'] = rfmTable['Monetary'].apply(FMClass, args=('Monetary', quantiles,))
    rfmTable['RFM_Segment'] = rfmTable['R'].map(str) + rfmTable['F'].map(str) + rfmTable['M'].map(str)
    rfmTable['RFM_Score'] = rfmTable[['R', 'F', 'M']].sum(axis=1)
    
    top_customers = rfmTable[rfmTable['RFM_Score'] >= 9]
    top_customers['Coupon_Code'] = ['COUPON' + str(i).zfill(4) for i in range(1, len(top_customers) + 1)]
    return top_customers

# def visualize_data(data):
    # return data.describe(), data.groupby('Email').size().reset_index(name='counts').sort_values(by='counts', ascending=False)

def visualize_data(data):
    stats = data.describe()
    top_emails = data.groupby('Email').size().reset_index(name='counts').sort_values(by='counts', ascending=False).head(10)
    return stats, top_emails



