import random

def random_num_generator(lower_bound, upper_bound):
    """Generates a random number between the lower and upper bound."""
    return random.randint(lower_bound, upper_bound)

def choose_word(text):
    """Chooses a random word from the text."""
    text = text.split()
    return random.choice(text)