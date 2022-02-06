import datetime as dt
from multiprocessing.sharedctypes import Value


def get_date_from_user(text,dateformat):
    cl_input = input(text)
    try:
        return dt.datetime.strptime(cl_input, dateformat)
    except ValueError as e:
        print(f"Provided value is probably wrong. Please provide date with format: '{dateformat}'.")
        raise

def get_words_from_user(text):
    cl_input = input(text)
    arr = cl_input.split(' ')
    if len(arr) == 0:
        raise ValueError("There are no words provided.")
    return arr
