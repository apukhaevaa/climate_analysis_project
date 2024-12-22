import requests



def get_current_temperature(city, api_key):

    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {

        "q": city,

        "appid": api_key,

        "units": "metric"  # Температура в градусах Цельсия

    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:

        data = response.json()

        return data['main']['temp']

    elif response.status_code == 401:

        return {"error": "Invalid API key"}

    else:

        return {"error": response.json().get("message", "Unknown error")}



# Пример использования

if __name__ == "__main__":

    city = "Moscow"

    api_key = "cf1ffecf676ee9636934a5a70447f741"

    result = get_current_temperature(city, api_key)

    if isinstance(result, dict) and "error" in result:

        print(f"Ошибка: {result['error']}")

    else:

        print(f"Текущая температура в {city}: {result}°C")