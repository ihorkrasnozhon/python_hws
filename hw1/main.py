import random

matrix = [[random.randint(-1, 5) for _ in range(5)] for _ in range(5)]
        #  рандомные инты         циклы для создания 5 листов по 5 элементов

# Вывод исходной матрицы
print("Исходная матрица:")
for row in matrix:
    print(row)

# Функция для вычисления характеристики столбца
def column_characteristic(column):
    return sum(abs(x) for x in column if x < 0 and x % 2 != 0)
    #    вычисление сумы подходяших   проверка на отрицателность и нечетность


# Вычисление характеристики для каждого столбца
characteristics = [column_characteristic([row[i] for row in matrix]) for i in range(5)]
#мы типа передаем в функцию оту сверху итый элемент от каждого рядка от 0 до 5
#и делаем из полученных данных (характеристик) лист


# Перестановка столбцов в соответствии с ростом характеристик
sorted_indices = sorted(range(len(characteristics)), key=lambda k: characteristics[k])
#сортирует типа по ключу роста характеристик последовательность от 0 до колва столбцов

# Новая матрица с переставленными столбцами
sorted_matrix = [[row[i] for i in sorted_indices] for row in matrix]

# Вывод матрицы с переставленными столбцами
print("\nМатрица с переставленными столбцами (в порядке роста характеристик):")
for row in sorted_matrix:
    print(row)

# Нахождение суммы элементов в столбцах, которые содержат хотя бы один отрицательный элемент
sum_neg_columns = sum(sum(row) for row in sorted_matrix if any(x < 0 for x in row))

# Вывод суммы элементов в таких столбцах
print("\nСумма элементов в столбцах с хотя бы одним отрицательным элементом:", sum_neg_columns)
