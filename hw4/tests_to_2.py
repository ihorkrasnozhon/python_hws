
import unittest
from part2_SOLO import add_user, add_bank, add_account, modify_user, modify_bank, modify_account, \
    delete_user, delete_bank, delete_account, transfer_money




class TestBank(unittest.TestCase):


    def test_add_user(self):
        result = add_user({'user_full_name': 'Jo Do', 'birth_day': '1990-01-01', 'accounts': '2'})
        self.assertEqual(result['status'], 'success')

    def test_add_bank(self):
        result = add_bank({'name': 'Bank A', 'capital': 1000000})
        self.assertEqual(result['status'], 'success')

    def test_add_account(self):
        add_user({'user_full_name': 'Alla Asses', 'birth_day': '1990-01-01', 'accounts': '3'})
        add_bank({'name': 'Bank B', 'capital': 100000})
        result = add_account({
            'user_id': 1,
            'type': 'debit',
            'account_number': 'ID--ABC-123456-ZZM',
            'bank_id': 1,
            'bank_name': 'Bank A',
            'currency': 'USD',
            'balance': 500,
            'status': 'gold'
        })
        self.assertEqual(result['status'], 'success')
#     #
    def test_modify_user(self):
        add_user({'user_full_name': 'John Doe', 'birth_day': '1990-01-01', 'accounts': '4'})
        result = modify_user( 1, name='Jane', surname='Smith')
        self.assertEqual(result['status'], 'success')
#     #
    def test_modify_bank(self):
        add_bank({'name': 'Bank C', 'capital': 1000000})
        result = modify_bank(1, name='Bank Test', capital=2000000)
        self.assertEqual(result['status'], 'success')
#     #
    def test_modify_account(self):
        add_user({'user_full_name': 'Pes Patron', 'birth_day': '1990-01-01', 'accounts': '5'})
        add_bank({'name': 'Bank D', 'capital': 1500000})
        add_account({
            'user_id': 1,
            'type': 'debit',
            'account_number': 'ID--ADC-123426-ZZM',
            'bank_id': 1,
            'bank_name': 'Bank B',
            'currency': 'USD',
            'balance': 500,
            'status': 'gold'
        })
        result = modify_account( 2, balance=100)
        self.assertEqual(result['status'], 'success')
#     #
    def test_delete_user(self):
        add_user({'user_full_name': 'Petro Poroshenko', 'birth_day': '1990-01-01', 'accounts': '6'})
        result = delete_user(1)
        self.assertEqual(result['status'], 'success')

    def test_delete_bank(self):
        add_bank({'name': 'Bank A', 'capital': 1000000})
        result = delete_bank(2)
        self.assertEqual(result['status'], 'success')

    def test_delete_account(self):
        add_user({'user_full_name': 'Boris Johnson', 'birth_day': '1990-01-01', 'accounts': ''})
        add_bank({'name': 'Bank X', 'capital': 10000})
        add_account({
            'user_id': 3,
            'type': 'debit',
            'account_number': 'ID--ABC-654321-ZZM',
            'bank_id': 1,
            'bank_name': 'Bank A',
            'currency': 'USD',
            'balance': 500,
            'status': 'platinum'
        })
        result = delete_account(1)
        self.assertEqual(result['status'], 'success')
#     #
    def test_transfer_money(self):
        add_user({'user_full_name': 'Johnie Sins', 'birth_day': '1990-01-01', 'accounts': ''})
        add_bank({'name': 'Monobank', 'capital': 1000000})
        add_account({
            'user_id': 1,
            'type': 'credit',
            'account_number': 'ID--LNM-654321-ZPI',
            'bank_id': 3,
            'bank_name': 'Bank C',
            'currency': 'USD',
            'balance': 500,
            'status': 'gold'
        })
        add_account({
            'user_id': 2,
            'type': 'debit',
            'account_number': 'ID--WSD-654321-ZZM',
            'bank_id': 4,
            'bank_name': 'Bank D',
            'currency': 'USD',
            'balance': 300,
            'status': 'silver'
        })





        result = transfer_money(3, 4, 200)
        self.assertEqual(result['status'], 'success')
