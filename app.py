import streamlit as st

import pandas as pd

import numpy as np

import requests

import matplotlib.pyplot as plt

from concurrent.futures import ThreadPoolExecutor



# Функция для загрузки данных

@st.cache_data

def load_data(file):

    data = pd.read_csv(file, parse_dates=['timestamp'])

    data['season'] = data['timestamp'].dt.month.map(lambda x: {

        12: 'winter', 1: 'winter', 2: 'winter',

        3: 'spring', 4: 'spring', 5: 'spring',

        6: 'summer', 7: 'summer', 8: 'summer',

        9: 'autumn', 10: 'autumn', 11: 'autumn'

    }[x])

    return data



# Функция для получения текущей температуры

def get_current_temperature(api_key, city):

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        return data['main']['temp'], None

    else:

        return None, response.json().get('message', 'Unknown error')



# Функция анализа данных

def analyze_city_data(data, city):

    city_data = data[data['city'] == city].copy()
    city_data['rolling_mean'] = city_data['temperature'].rolling(window=30).mean()
    city_data['rolling_std'] = city_data['temperature'].rolling(window=30).std()
    city_data['upper_bound'] = city_data['rolling_mean'] + 2 * city_data['rolling_std']
    city_data['lower_bound'] = city_data['rolling_mean'] - 2 * city_data['rolling_std']
    city_data['anomaly'] = (city_data['temperature'] > city_data['upper_bound']) | \
    (city_data['temperature'] < city_data['lower_bound'])
    return city_data



# Интерфейс Streamlit

st.title("Анализ температурных данных и мониторинг")



# Загрузка данных

uploaded_file = st.file_uploader("Загрузите файл с историческими данными (CSV)", type="csv")

if uploaded_file:

    data = load_data(uploaded_file)

    cities = data['city'].unique()

    selected_city = st.selectbox("Выберите город для анализа", cities)



    # Ввод API-ключа

    api_key = st.text_input("Введите API-ключ OpenWeatherMap")

    

    # Анализ данных

    st.header(f"Анализ исторических данных: {selected_city}")

    analyzed_data = analyze_city_data(data, selected_city)

    

    # Статистика

    st.write("Описательная статистика:")

    st.write(analyzed_data[['temperature', 'rolling_mean', 'rolling_std']].describe())

    

    # Графики

    st.subheader("Временной ряд температур с выделением аномалий")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(analyzed_data['timestamp'], analyzed_data['temperature'], label='Температура', alpha=0.5)

    ax.plot(analyzed_data['timestamp'], analyzed_data['rolling_mean'], label='Скользящее среднее (30 дней)', color='orange')

    ax.fill_between(analyzed_data['timestamp'], analyzed_data['lower_bound'], analyzed_data['upper_bound'], color='orange', alpha=0.2, label='±2σ')

    ax.scatter(analyzed_data['timestamp'][analyzed_data['anomaly']], analyzed_data['temperature'][analyzed_data['anomaly']], color='red', label='Аномалии')

    ax.set_title(f"Температурный тренд и аномалии в {selected_city}")

    ax.set_xlabel("Дата")

    ax.set_ylabel("Температура (°C)")

    ax.legend()

    st.pyplot(fig)

    

    # Сезонные профили

    st.subheader("Сезонные профили температуры")

    seasonal_stats = analyzed_data.groupby('season')['temperature'].agg(['mean', 'std'])

    st.write(seasonal_stats)

    

    # Мониторинг текущей температуры

    st.header("Мониторинг текущей температуры")

    if api_key:

        current_temp, error = get_current_temperature(api_key, selected_city)

        if error:

            st.error(f"Ошибка: {error}")

        else:

            st.write(f"Текущая температура в {selected_city}: {current_temp}°C")

            season = analyzed_data.loc[analyzed_data['timestamp'] == analyzed_data['timestamp'].max(), 'season'].values[0]

            season_mean = seasonal_stats.loc[season, 'mean']

            season_std = seasonal_stats.loc[season, 'std']

            lower_bound = season_mean - 2 * season_std

            upper_bound = season_mean + 2 * season_std

            st.write(f"Нормальный диапазон для сезона ({season}): {lower_bound:.2f}°C — {upper_bound:.2f}°C")

            if lower_bound <= current_temp <= upper_bound:

                st.success("Текущая температура находится в нормальном диапазоне.")

            else:

                st.warning("Текущая температура выходит за пределы нормального диапазона!")

    else:

        st.warning("Введите API-ключ для мониторинга текущей температуры.")