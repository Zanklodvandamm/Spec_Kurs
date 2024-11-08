import streamlit as st
import requests
import pandas as pd

# API base URL
API_BASE_URL = "http://127.0.0.1:8000/"

# Загружаем данные
movies_df = pd.read_csv('IMDB-films.csv')

# Получаем уникальные жанры
def allGenres():
    unique_genres = set()
    for genres in movies_df['Genre']:
        genres_list = genres.split(',')
        for genre in genres_list:
            unique_genres.add(genre)
    return unique_genres

st.title("Приложение ")

option = st.selectbox("Выберите опцию", ["Справка", "Топ-10 популярных фильмов", "Рекомендации по жанру", "Рекомендации по контенту"])

if option == "Справка":
    st.write("""
    Это приложение поддерживает следующие команды:

    1. **Топ-10 популярных фильмов**: Возвращает список из 10 фильмов с наивысшим рейтингом.

    2. **Рекомендации по жанру**: Позволяет получить топ-10 фильмов для указанного жанра.

    3. **Рекомендации по контенту**: Находит фильмы, похожие на указанный фильм по его описанию.
    """)
else:
    if option == "Рекомендации по жанру":
        genre = st.selectbox("Выберите жанр", allGenres())
        input_text = genre
    else:
        input_text = st.text_input("Введите текст")

    if st.button("Получить данные"):
        if option == "Топ-10 популярных фильмов":
            response = requests.get(f"{API_BASE_URL}/top_movies")
        elif option == "Рекомендации по жанру":
            response = requests.get(f"{API_BASE_URL}/recommend_by_genre", params={"genre": input_text})
        elif option == "Рекомендации по контенту":
            response = requests.get(f"{API_BASE_URL}/recommend_by_content", params={"title": input_text})
        else:
            st.write("Неверная опция")
            response = None

        if response and response.status_code == 200:
            movies = response.json()
            for movie in movies:
                st.write(f"**{movie['Title']}** - Рейтинг: {movie['Rating']}")
        else:
            st.write("Ошибка при получении данных")