import logging
import math

logging.basicConfig(
    filename='logfile.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

def calculate_square_root(number):
    square_root = math.sqrt(number)
    logging.info(f"Input number: {number}")
    logging.info(f"Calculated square root: {square_root}")
    return square_root

calculate_square_root(16)
