import unittest
from unittest.mock import Mock
from funcs_examples import add_numbers, is_even, fetch_data, process_mock_object, run_data_pipeline, divide_numbers, check_even_odd, DataProcessor

class TestMyFunctions(unittest.TestCase):

    def test_add_numbers(self):
        self.assertEqual(add_numbers(1, 2), 3)
        self.assertEqual(add_numbers(-1, 1), 0)
        self.assertEqual(add_numbers(0, 0), 0)

    def test_is_even(self):
        self.assertTrue(is_even(2))
        self.assertFalse(is_even(3))
        self.assertTrue(is_even(0))

    def test_fetch_data(self):
        # Mocking requests.get() method
        requests = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"key": "value"}
        requests.get.return_value = response

        with unittest.mock.patch("my_module.requests", requests):
            self.assertEqual(fetch_data("http://example.com"), {"key": "value"})
            response.status_code = 404
            self.assertIsNone(fetch_data("http://example.com"))

    def test_process_mock_object(self):
        self.assertEqual(process_mock_object(Mock(value=2)), 4)
        self.assertIsNone(process_mock_object(Mock(value=-1)))

    def test_run_data_pipeline(self):
        # Mocking DataProcessor methods
        data_processor = Mock()
        data_processor.process_data.return_value = [2, 4, 6]
        data_processor.analyze_data.return_value = 12


        self.assertIsNone(run_data_pipeline(data_processor))

    def test_divide_numbers(self):
        self.assertEqual(divide_numbers(10, 2), 5)
        self.assertEqual(divide_numbers(-10, 2), -5)
        self.assertIsNone(divide_numbers(10, 0))
        self.assertIsNone(divide_numbers(10, "2"))

    def test_check_even_odd(self):
        # Mocking requests.get() method
        requests = Mock()
        response = Mock()
        response.json.return_value = {"results": [{"value": 2}, {"value": 3}, {"value": 4}]}
        requests.get.return_value = response

        with unittest.mock.patch("my_module.requests", requests):
            self.assertEqual(check_even_odd([1, 2, 3], "http://example.com"), ["Odd", "Even", "Odd"])

    def test_data_processor(self):
        data_processor = DataProcessor()
        self.assertEqual(data_processor.process_data([1, 2, 3]), [2, 4, 6])
        self.assertEqual(data_processor.analyze_data([1, 2, 3]), 12)

if __name__ == '__main__':
    unittest.main()
