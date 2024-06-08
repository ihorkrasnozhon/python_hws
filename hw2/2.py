import requests
import pandas as pd
from datetime import datetime, timedelta

class MovieData:
    def __init__(self, num_pages):
        self.num_pages = num_pages
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
        }
        self.data = []
        self.fetch_data()

    def fetch_data(self):
        for page in range(1, self.num_pages + 1):
            response = requests.get(f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={page}", headers=self.headers)
            self.data.extend(response.json()['results'])
        genres_response = requests.get("https://api.themoviedb.org/3/genre/movie/list?language=en", headers=self.headers)
        self.genres = genres_response.json()['genres']

    def get_all_data(self):
        return self.data

    def get_data_by_index(self):
        return [self.data[i] for i in range(3, 20, 4)]

    def get_most_popular_title(self):
        return max(self.data, key=lambda x: x['popularity'])['title']

    def get_titles_by_keywords(self, keywords):
        return [movie['title'] for movie in self.data if any(keyword in movie['overview'] for keyword in keywords)]

    def get_unique_genres(self):
        return set(genre['name'] for genre in self.genres)

    def delete_movies_by_genre(self, genre_name):
        genre_id = next((genre['id'] for genre in self.genres if genre['name'] == genre_name), None)
        if genre_id is not None:
            self.data = [movie for movie in self.data if genre_id not in movie['genre_ids']]

    def get_most_popular_genres(self):
        genre_counts = {genre['name']: 0 for genre in self.genres}
        for movie in self.data:
            for genre_id in movie['genre_ids']:
                genre_name = next((genre['name'] for genre in self.genres if genre['id'] == genre_id), None)
                if genre_name is not None:
                    genre_counts[genre_name] += 1
        return genre_counts

    def get_titles_grouped_by_genres(self):
        titles_by_genre = {genre['name']: [] for genre in self.genres}
        for movie in self.data:
            for genre_id in movie['genre_ids']:
                genre_name = next((genre['name'] for genre in self.genres if genre['id'] == genre_id), None)
                if genre_name is not None:
                    titles_by_genre[genre_name].append(movie['title'])
        return titles_by_genre

    def replace_first_genre_id(self):
        initial_data = self.data.copy()
        for movie in self.data:
            if movie['genre_ids']:
                movie['genre_ids'][0] = 22
        return initial_data, self.data

    def get_structured_data(self):
        structured_data = []
        for movie in self.data:
            structured_data.append({
                'Title': movie['title'],
                'Popularity': round(movie['popularity'], 1),
                'Score': int(movie['vote_average']),
                'Last_day_in_cinema': (datetime.strptime(movie['release_date'], '%Y-%m-%d') + timedelta(days=74)).strftime('%Y-%m-%d')
            })
        return sorted(structured_data, key=lambda x: (x['Score'], x['Popularity']), reverse=True)

    def write_to_csv(self, path):
        structured_data = self.get_structured_data()
        df = pd.DataFrame(structured_data)
        df.to_csv(path, sep=';', index=False)

if __name__ == "__main__":
            movie_data = MovieData(1)  # Создаем экземпляр класса MovieData для одной страницы данных
            # print(movie_data.get_all_data())  # Получаем и печатаем все данные
            print(movie_data.get_most_popular_title())  # Получаем и печатаем самый популярный фильм
            movie_data = MovieData(1)  # Создаем экземпляр класса MovieData для одной страницы данных
            movie_data.write_to_csv('movies.csv')  # Записываем данные в файл CSV
