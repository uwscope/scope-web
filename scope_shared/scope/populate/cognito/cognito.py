import random
import string


def generate_temporary_password() -> str:
    """
    Generate a temporary password with requirements:
    - 8 characters long
    - Includes at least 1 lowercase, uppercase, number, and symbol

    Allowable Cognito symbols are:
      ^$*.[]{}()?!@#%&/\,><'":;|_~`=+-

    For readability of generated passwords that are emailed to people, we use:
      !@#$%^&*
    """

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    numbers = string.digits
    symbols = "!@#$%^&*"
    combined_not_symbols = lowercase + uppercase + numbers

    # List to build up a sequence of password characters
    characters = []

    # Include 1 of each class of character
    characters.extend(
        [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(numbers),
            random.choice(symbols),
        ]
    )

    # Include 3 characters that are not symbols
    characters.extend(random.sample(combined_not_symbols, 3))
    random.shuffle(characters)

    # Prefix with a character that is not a symbol
    characters = [random.choice(combined_not_symbols)] + characters

    # Convert the list into a string
    temporary_password = "".join(characters)

    return temporary_password
