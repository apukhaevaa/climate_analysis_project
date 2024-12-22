import pandas as pd

import numpy as np

import matplotlib.pyplot as plt



# Загрузка данных

data = pd.read_csv('temperature_data.csv')

data['timestamp'] = pd.to_datetime(data['timestamp'])



# Скользящее среднее

data['rolling_mean'] = data.groupby('city')['temperature'].transform(

    lambda x: x.rolling(window=30, min_periods=1).mean()

)



# Среднее и стандартное отклонение

season_stats = data.groupby(['city', 'season']).agg(

    mean_temperature=('temperature', 'mean'),

    std_temperature=('temperature', 'std')

).reset_index()



# Аномалии

def detect_anomalies(city_data):

    city_data = city_data.copy()

    for season in city_data['season'].unique():

        mean_temp = season_stats.loc[

            (season_stats['city'] == city_data['city'].iloc[0]) &

            (season_stats['season'] == season),

            'mean_temperature'

        ].values[0]

        std_temp = season_stats.loc[

            (season_stats['city'] == city_data['city'].iloc[0]) &

            (season_stats['season'] == season),

            'std_temperature'

        ].values[0]

        city_data.loc[city_data['season'] == season, 'anomaly'] = (

            (city_data['temperature'] < mean_temp - 2 * std_temp) |

            (city_data['temperature'] > mean_temp + 2 * std_temp)

        )

    return city_data



data = data.groupby('city').apply(detect_anomalies)



# Сохранение данных с аномалиями

data.to_csv('temperature_data_with_anomalies.csv', index=False)

print("Анализ завершен. Данные сохранены в 'temperature_data_with_anomalies.csv'.")