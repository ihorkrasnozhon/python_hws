import logging
from part3 import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Main function to play with functionalities
def main():
    try:
        # Get users with discounts
        users_with_discounts = get_users_with_discounts()
        logging.info("Users with discounts:")
        logging.info(users_with_discounts)

        # Get users with debts
        users_with_debts = get_users_with_debts()
        logging.info("Users with debts:")
        for user in users_with_debts:
            logging.info(f"ID: {user[0]}, Name: {user[1]} {user[2]}")

        # Get bank with biggest capital
        bank_with_biggest_capital = get_bank_with_biggest_capital()
        logging.info(f"Bank with biggest capital: {bank_with_biggest_capital}")

        # Get bank serving oldest client
        bank_serving_oldest_client = get_bank_serving_oldest_client()
        logging.info(f"Bank serving oldest client: {bank_serving_oldest_client}")

        # Get bank with highest outbound transactions
        bank_with_highest_outbound_transactions = get_bank_with_highest_outbound_transactions()
        logging.info(f"Bank with highest outbound transactions: {bank_with_highest_outbound_transactions}")

        # Delete incomplete users and accounts
        delete_incomplete_users_and_accounts()
        logging.info("Incomplete users and accounts deleted successfully")

        # Get transactions of a particular user for the past 3 months
        user_id = 1
        user_transactions = get_user_transactions_past_3_months(user_id)
        logging.info(f"Transactions of user {user_id} for the past 3 months:")
        for transaction in user_transactions:
            logging.info(transaction)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
