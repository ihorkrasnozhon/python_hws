import unittest
from unittest.mock import Mock, patch

from tests_training import add_numbers, is_even, fetch_data, process_mock_object, run_data_pipeline, divide_numbers, \
    check_even_odd, DataProcessor


class TestFunctions(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(add_numbers(1, 2), 3)
        self.assertEqual(add_numbers(-1, 1), 0)

    def test_is_even(self):
        self.assertTrue(is_even(2))
        self.assertFalse(is_even(3))

    @patch('my_module.requests.get')
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

    @patch.object(DataProcessor, 'process_data')
    @patch.object(DataProcessor, 'analyze_data')
    @patch.object(DataProcessor, 'save_result')
    def test_run_data_pipeline(self, mock_save, mock_analyze, mock_process):
        mock_data_processor = Mock(DataProcessor)
        mock_process.return_value = [2, 4, 6]
        mock_analyze.return_value = 12

        run_data_pipeline(mock_data_processor)

        mock_process.assert_called_once()
        mock_analyze.assert_called_once_with([2, 4, 6])
        mock_save.assert_called_once_with(12)

    def test_divide_numbers(self):
        self.assertEqual(divide_numbers(10, 2), 5)
        self.assertIsNone(divide_numbers(10, 0))

        with self.assertRaises(TypeError):
            divide_numbers(10, 'a')

    @patch('my_module.requests.get')
    def test_check_even_odd(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'results': [{'value': 2}]}
        mock_get.return_value = mock_response

        self.assertEqual(check_even_odd([1, 2], "http://example.com"), ["Odd", "Even"])

        mock_response.json.return_value = {'results': [{'value': 3}]}
        self.assertEqual(check_even_odd([1, 3], "http://example.com"), ["Odd", "Odd"])

    def test_DataProcessor(self):
        processor = DataProcessor()
        data = [1, 2, 3]

        self.assertEqual(processor.process_data(data), [2, 4, 6])
        self.assertEqual(processor.analyze_data(data), 12)


if __name__ == '__main__':
    unittest.main()
