from datetime import datetime, timedelta

import pandas as pd
import requests


class hw2:
    # Инициализация класса с заголовками и методами и списком для данных
    def __init__(self, num_pages):
        self.num_pages = num_pages
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
        }
        self.data = []
        self.genres = []
        self.fetch_data()


    # 1.Fetch the data from desired amount of pages
    def fetch_data(self):
        for page in range(1, self.num_pages + 1):
            response = requests.get(
                f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={page}",
                headers=self.headers)
            # записую в дату данніе с респонса
            self.data.extend(response.json().get('results', []))


        # а ето для 6 метода
        genres_response = requests.get(
            "https://api.themoviedb.org/3/genre/movie/list?language=en",
            headers=self.headers)
        self.genres = genres_response.json().get('genres', [])

    # 2.Give a user all data
    def get_all_data(self):
        print("All data: ", self.data)

        #3.All data about movies with indexes from 3 till 19 with step 4
    def method3(self):
        # віводит данніе по фильмам только от 3 до 19 каждій 4 фильм
        selected_movies = [self.data[i] for i in range(3, 20, 4) if i < len(self.data)]
        print("All data about movies with indexes from 3 till 19 with step 4: ", selected_movies)

        #4.Name of the most popular title
    def method4(self):
        # ищет максимальное значение по ключу популярити
         print("Most popular title: ", max(self.data, key=lambda x: x['popularity'])['title'])


        #5.Names of titles which has in description key words
    def method5(self, keywords):
        #ключевое слово к нижнему регистру
        keyword_lower = keywords.lower()
        #писок для хранения названий фильмов
        movies_with_keyword = []
        #роходим по каждому фильму и приводим его описание к нижнему регистру и проверяем
        for movie in self.data:
            # Приводим описание к нижнему регистру
            overview_lower = movie['overview'].lower()
            if keyword_lower in overview_lower:
                #если найден кейворд, аппендим название фильма в список
                movies_with_keyword.append(movie['title'])
        print("Names of titles which has in description key words:", movies_with_keyword)


        #6.Unique collection of present genres
    def method6(self):
        # в цикле насетали имена жанров что мы получили выше и вывели их
        print("Unique collection of present genres: ", set(genre['name'] for genre in self.genres))

    #7.Delete all movies with user provided genre
    #короче оно удаляет реально надо дважды запустить и посмотреть например сколько КОМЕДИЙ
    #потом удалить комедии и будет 0 в некст методе
    def method7(self, genre_name):
        # тут мі ищем идентификатор введенного жанра, а если не находим то ставим заместь его айди нан
        genre_id = next((genre['id'] for genre in self.genres if genre['name'] == genre_name), None)
        # если мі чтото нашли таки
        if genre_id is not None:
            #оставляем только фильмы где нету введенного жанра ?????
            self.data = [movie for movie in self.data if genre_id not in movie['genre_ids']]


        #8.Names of most popular genres with numbers
    def method8(self):
        #словарь с ключем имя жанра и значением сначала ноль но потом увеличится
        genre_counts = {genre['name']: 0 for genre in self.genres}
        # по каждому фильму
        for movie in self.data:
            # по каждому жанру
            for genre_id in movie['genre_ids']:
            # типа генератор которій перебирает все жанрі по идентификатору и возвращает его имя, и нан если не находит
                genre_name = next((genre['name'] for genre in self.genres if genre['id'] == genre_id), None)
               # ну и тут чисто подсчитать появления опредленного жанра и обновить значение в словарпе
                if genre_name is not None:
                    genre_counts[genre_name] += 1
        print("Names of most popular genres with numbers: ", genre_counts)

        #9.Collection of film titles  grouped in pairs by common genres
    def method9(self):
        #тоже короче инициализируем словар где ключ єто имя жанра а значение єто список с названием ифльмов но сначала пустой
        titles_by_genre = {genre['name']: [] for genre in self.genres}
        for movie in self.data:
            for genre_id in movie['genre_ids']:
                #ну тут опять ищем имя жанра по его айди а если не нашли то нан
                genre_name = next((genre['name'] for genre in self.genres if genre['id'] == genre_id), None)
                if genre_name is not None:
                    if len(titles_by_genre[genre_name]) < 2:
                        #ну и аппендим в словарь под ключ текущего жанра тайтлі попарно
                        titles_by_genre[genre_name].append(movie['title'])
        print("Collection of film titles  grouped in pairs by common genres: ", titles_by_genre)


#initial data and copy of initial data where first id in list of film genres was replaced with 22
    def method10(self):
        print("Self data(NOT modified): ", self.data)
        initial_data = self.data.copy()
        #ну и тут просто первій жанр каждого фильма меняется на 22
        for movie in self.data:
            if movie['genre_ids']:
                movie['genre_ids'][0] = 22
        print("Initial data: ",initial_data)
        print("Self data(modified): ",self.data)
        return initial_data

        #11.Collection of structures with part of initial data
    def method11(self, initial_data):
        #пустой спиисок
        structured_data = []
        for movie in initial_data:
            #аппендим в словарь под такими именами такие поля
            structured_data.append({
                'Title': movie['title'],
            # with 1 decimal point with maximum precision)
                'Popularity': round(movie['popularity'], 1),
                'Score': int(movie['vote_average']),
                #2 months and 2 weeks after the release_date
                'Last_day_in_cinema': (datetime.strptime(movie['release_date'], '%Y-%m-%d') + timedelta(days=74)).strftime('%Y-%m-%d')
            })
            # сортирует по убіванию по скору а при одинаковом скоре по популярности
        print("Collection of structures with part of initial data: ",sorted(structured_data, key=lambda x: (x['Score'], x['Popularity']), reverse=True))
        return (sorted(structured_data, key=lambda x: (x['Score'], x['Popularity']), reverse=True))

    #Write information to a csv file using path provided by user
    def method12(self, path, structured_data):
        #создается датафрейм из даты из предыдущенго метода
        # датафрейм єто типа файл-таблица-двумерніймассив
        df = pd.DataFrame(structured_data)
        # то цсв єто метод либки панлас
        df.to_csv(path, sep=';', index=False)
        print("CSV done")



if __name__ == "__main__":
    num_pages = int(input("Enter amount of pages: "))
    #осоздается новая сущность с нужным количеством страниц
    hw2_instance = hw2(num_pages)
    hw2_instance.get_all_data()
    hw2_instance.method3()
    hw2_instance.method4()

    keywords = input("Keywords for searching in film description: ")
    hw2_instance.method5(keywords)
    hw2_instance.method6()
    hw2_instance.method8()
    banned_genre = input("Provide a genre to ban titles with it: ")
    hw2_instance.method7(banned_genre)
    hw2_instance.method8()
    hw2_instance.method9()
    initial_data = hw2_instance.method10()
    structured_data = hw2_instance.method11(initial_data)
    #C:\Users\1456112\PycharmProjects\python_hws\hw2\output.csv
    csv_path = input("Provide path to save CSV file: ")
    hw2_instance.method12(csv_path, structured_data)
