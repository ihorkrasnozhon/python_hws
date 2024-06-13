import unittest
from unittest.mock import Mock, patch
import requests


# функции
def add_numbers(a, b):
    return a + b


def is_even(number):
    return True if number % 2 == 0 else False


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def process_mock_object(obj):
    if obj.value > 0:
        return obj.value * 2
    else:
        return None


def run_data_pipeline(data_processor):
    prepared_data = data_processor.process_data()
    analyzed_data = data_processor.analyze_data(prepared_data)
    data_processor.save_result(analyzed_data)


def divide_numbers(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Error: Cannot divide by zero!")
        return None
    except TypeError:
        print("Error: Unsupported operand type(s) for division!")
        return None
    else:
        return result


def check_even_odd(numbers, url):
    result = []
    for number in numbers:
        response = requests.get(f'{url}/{number}').json()['results'][0]['value']
        if response % 2 == 0:
            result.append("Even")
        else:
            result.append("Odd")
    return result


class DataProcessor:
    def process_data(self, data):
        return [x * 2 for x in data]

    def analyze_data(self, data):
        processed_data = self.process_data(data)
        return sum(processed_data)

    def save_result(self, result):
        pass  # Реализация метода сохранения результата


# Тесты
class TestFunctions(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(add_numbers(1, 2), 3)
        self.assertEqual(add_numbers(-1, 1), 0)

    def test_is_even(self):
        self.assertTrue(is_even(2))
        self.assertFalse(is_even(3))


#Мокирование позволяет заменить реальные объекты или компоненты тестируемой системы на их имитации


    @patch('requests.get')
    def test_fetch_data(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        self.assertEqual(fetch_data("http://example.com"), {"key": "value"})

        mock_response.status_code = 404
        self.assertIsNone(fetch_data("http://example.com"))

    def test_process_mock_object(self):
        mock_obj = Mock()
        mock_obj.value = 10
        self.assertEqual(process_mock_object(mock_obj), 20)

        mock_obj.value = -5
        self.assertIsNone(process_mock_object(mock_obj))

    @patch.object(DataProcessor, 'process_data', return_value=[2, 4, 6])
    @patch.object(DataProcessor, 'analyze_data', return_value=12)
    @patch.object(DataProcessor, 'save_result')
    def test_run_data_pipeline(self, mock_save, mock_analyze, mock_process):
        mock_data_processor = DataProcessor()

        run_data_pipeline(mock_data_processor)

        mock_process.assert_called_once()
        mock_analyze.assert_called_once_with([2, 4, 6])
        mock_save.assert_called_once_with(12)

    def test_divide_numbers(self):
        self.assertEqual(divide_numbers(10, 2), 5)
        self.assertIsNone(divide_numbers(10, 0))
        self.assertIsNone(divide_numbers(10, 'a'))

    @patch('requests.get')
    def test_check_even_odd(self, mock_get):
        mock_response_even = Mock()
        mock_response_even.json.return_value = {'results': [{'value': 2}]}

        mock_response_odd = Mock()
        mock_response_odd.json.return_value = {'results': [{'value': 3}]}

        mock_get.side_effect = [mock_response_even, mock_response_even, mock_response_odd]

        self.assertEqual(check_even_odd([1, 2, 3], "http://example.com"), ["Even", "Even", "Odd"])

    def test_DataProcessor(self):
        processor = DataProcessor()
        data = [1, 2, 3]

        self.assertEqual(processor.process_data(data), [2, 4, 6])
        self.assertEqual(processor.analyze_data(data), 12)


if __name__ == '__main__':
    unittest.main()
