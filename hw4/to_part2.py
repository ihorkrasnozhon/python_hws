# Import the functions from your script
from part2 import add_user, add_bank, add_account, perform_money_transfer

# Example usage of the functions
if __name__ == "__main__":
    # Add a user
    user_data = {"user_full_name": "John Doe", "birth_day": "1990-01-01", "accounts": "123456789,987654321"}
    print(add_user(user_data))

    # Add a bank
    bank_data = {"name": "American Bank"}
    print(add_bank(bank_data))

    # Add an account
    account_data = {
        "user_id": 2,
        "type": "debit",
        "account_number": "32132132",
        "bank_id": 2,
        "currency": "USD",
        "amount": 1000,
        "status": "gold"
    }
    print(add_account(account_data))

    # Perform a money transfer
    sender_account_id = 2
    receiver_account_id = 3
    amount = 500
    print(perform_money_transfer(sender_account_id, receiver_account_id, amount))
