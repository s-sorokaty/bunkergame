import random
import logging

from .names import last_names, first_names

def game_logger(action:str):
    #logging.basicConfig(level=logging.INFO)
    logging.info(f"LOGGED ACTIONS: {action}")


def get_random_value(min_val=0, max_val=29, excepted_values = None) -> int:
    rand_value = random.randint(min_val, max_val)

    if excepted_values:
        while rand_value in excepted_values:
            rand_value = random.randint(min_val, max_val)
        return rand_value
    else:    
        return rand_value 

def generate_name() -> str:
    return first_names[get_random_value(max_val=len(first_names)-1)] + " " + last_names[get_random_value(max_val=len(last_names)-1)]