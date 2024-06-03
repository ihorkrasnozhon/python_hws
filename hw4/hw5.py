import unittest
from part3 import *
from part2 import *
from part1 import *

class TestBankFunctions(unittest.TestCase):

    def test_get_users_with_discounts(self):
        users_with_discounts = get_users_with_discounts()
        self.assertIsInstance(users_with_discounts, dict)

    def test_get_users_with_debts(self):
        users_with_debts = get_users_with_debts()
        for user in users_with_debts:
            self.assertIsInstance(user, tuple)
            self.assertEqual(len(user), 3)

    # def test_get_bank_with_biggest_capital(self):
    #     bank_with_biggest_capital = get_bank_with_biggest_capital()
    #     self.assertIsInstance(bank_with_biggest_capital, tuple)
    #     self.assertEqual(len(bank_with_biggest_capital), 2)

    def test_get_bank_serving_oldest_client(self):
        bank_serving_oldest_client = get_bank_serving_oldest_client()
        self.assertIsInstance(bank_serving_oldest_client, tuple)
        self.assertEqual(len(bank_serving_oldest_client), 2)

    def test_get_bank_with_highest_outbound_transactions(self):
        bank_with_highest_outbound_transactions = get_bank_with_highest_outbound_transactions()
        self.assertIsInstance(bank_with_highest_outbound_transactions, tuple)
        self.assertEqual(len(bank_with_highest_outbound_transactions), 2)



    def test_get_user_transactions_past_3_months(self):
        # Replace user_id with an actual user ID from your database
        user_id = 3
        user_transactions = get_user_transactions_past_3_months(user_id)
        for transaction in user_transactions:
            self.assertIsInstance(transaction, tuple)
            self.assertEqual(len(transaction), 8)

if __name__ == "__main__":
    unittest.main()
