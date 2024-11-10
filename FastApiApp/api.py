from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Загружаем данные
movies_df = pd.read_csv('IMDB-films.csv')

# Инициализация FastAPI приложения
app = FastAPI()

# Создание TF-IDF матрицы
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(movies_df['Description'])


# Обучение модели KMeans
num_clusters = 55
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(tfidf_matrix)
movies_df['Cluster'] = kmeans.labels_

def get_recommendations_by_content(df, title, n=10):
    movie_index = df[df['Title'].str.lower() == title.lower()].index
    if movie_index.empty:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    movie_index = movie_index[0]
    movie_cluster = df.loc[movie_index, 'Cluster']

    cluster_movies = df[df['Cluster'] == movie_cluster]
    recommended_movies = cluster_movies[cluster_movies.index != movie_index].head(n)[['Title', 'Rating']].to_dict(orient='records')

    return recommended_movies



def get_top_movies(df, n=10):
    sorted_df = df.sort_values(by='Rating', ascending=False)
    top_movies = sorted_df.head(n)[['Title', 'Rating']].to_dict(orient='records')
    return top_movies

def filter_movies_by_genre(df, genre):
    return df[df['Genre'].str.contains(genre, case=False, na=False)]

def get_top_movies_by_genre(df, genre, n=10):
    genre_movies = filter_movies_by_genre(df, genre)
    sorted_genre_movies = genre_movies.sort_values(by='Rating', ascending=False)
    top_genre_movies = sorted_genre_movies.head(n)[['Title', 'Rating']].to_dict(orient='records')
    return top_genre_movies



@app.get('/movies_by_cluster')
def movies_by_cluster(cluster: int = Query(..., description="Cluster number")):
    cluster_movies = movies_df[movies_df['Cluster'] == cluster]
    return cluster_movies[['Title', 'Rating']].to_dict(orient='records')

@app.get('/top_movies')
def top_movies():
    return get_top_movies(movies_df)

@app.get('/recommend_by_genre')
def recommend_by_genre(genre: str = Query(..., description="Genre of the movie")):
    return get_top_movies_by_genre(movies_df, genre)

@app.get('/recommend_by_content')
def recommend_by_content(title: str = Query(..., description="Title of the movie")):
    return get_recommendations_by_content(movies_df, title)
    # return get_recommendations_by_content(title, similarity_matrix, movies_df)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)