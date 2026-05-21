"""
This program implements the RSA algorithm for cryptography.
It randomly selects two prime numbers from a txt file of prime numbers and 
uses them to produce the public and private keys. Using the keys, it can 
either encrypt or decrypt messages.
"""

import random
from typing import Callable
import time
import json


def timed(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        time_taken = end - start
        return result, time_taken

    return wrapper


def gcd(a: int, b: int) -> int:
    """
    Performs the Euclidean algorithm and returns the gcd of a and b
    """

    while b != 0:
        a, b = b, a % b
    return a


def xgcd(a: int, b: int) -> tuple:
    """
    Performs the extended Euclidean algorithm
    a * x + b * y = gcd(a, b)
    gcd(e, phi) = 1
    Returns the gcd, coefficient of a (e) and coefficient of b (phi)
    """
    x, old_x = 0, 1
    y, old_y = 1, 0

    while b != 0:
        quotient = a // b
        a, b = b, a - quotient * b
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    return a, old_x, old_y


def choose_e(phi: int) -> int:
    """
    Chooses a random number, 1 < e < totient, and checks whether it is
    coprime with the totient, that is, gcd(e, totient) = 1
    """
    while True:
        e = random.randrange(2, phi)

        if gcd(e, phi) == 1:
            return e

@timed
def choose_keys(rand_a: int = 100, rand_b: int = 500, keys_file :str = 'keys.json') -> None:
    """
    Selects two random prime numbers from a list of prime numbers which has 
    values that go up to 100k. It creates a text file and stores the two 
    numbers there where they can be used later. Using the prime numbers, 
    it also computes and stores the public and private keys in two separate 
    files.
    """

    # choose two random numbers within the range of lines where 
    # the prime numbers are not too small and not too big
    rand1 = random.randint(rand_a, rand_b)
    rand2 = random.randint(rand_a, rand_b)

    # store the txt file of prime numbers in a python list
    with open('primes-to-100k.txt', 'r') as f:
        lines = f.read().splitlines()

    # store our prime numbers in these variables
    prime1 = int(lines[rand1])
    prime2 = int(lines[rand2])

    # compute n, phi, e
    n = prime1 * prime2

    phi = (prime1 - 1) * (prime2 - 1)
    e = choose_e(phi)

    # compute d, 1 < d < phi such that ed = 1 (mod phi)
    # e and d are inverses (mod phi)
    gcd_e_phi, x, y = xgcd(e, phi)

    # make sure d is positive
    d = x
    if x < 0:
        d += phi

    public_key = [e, n]
    private_key = [d, n]

    keys = {
        'public_key': public_key,
        'private_key': private_key,
    }

    # Save keys to a JSON file
    with open(keys_file, 'w') as f:
        json.dump(keys, f)


@timed
def encrypt(message: str, keys_file: str = 'keys.json', block_size: int = 2) -> str:
    """
    Encrypts a message (string) by raising each character's ASCII value to the 
    power of e and taking the modulus of n. Returns a string of numbers.
    file_name refers to file where the public key is located. If a file is not 
    provided, it assumes that we are encrypting the message using our own 
    public keys. Otherwise, it can use someone else's public key, which is 
    stored in a different file.
    block_size refers to how many characters make up one group of numbers in 
    each index of encrypted_blocks.
    """

    try:
        # Read public key
        with open(keys_file, 'r') as f:
            keys = json.load(f)
            public_key = keys['public_key']
            e, n = public_key


    # check for the possibility that the user tries to encrypt something
    # using a public key that is not found
    except FileNotFoundError as e:
        raise e

    encrypted_blocks = []
    ciphertext = -1

    if len(message) > 0:
        # initialize ciphertext to the ASCII of the first character of message
        ciphertext = ord(message[0])

    for i in range(1, len(message)):
        # add ciphertext to the list if the max block size is reached
        # reset ciphertext so we can continue adding ASCII codes
        if i % block_size == 0:
            encrypted_blocks.append(ciphertext)
            ciphertext = 0

        # multiply by 1000 to shift the digits over to the left by 3 places
        # because ASCII codes are a max of 3 digits in decimal
        ciphertext = ciphertext * 1000 + ord(message[i])

    # add the last block to the list
    encrypted_blocks.append(ciphertext)

    # encrypt all numbers by taking it to the power of e
    # and modding it by n
    for i in range(len(encrypted_blocks)):
        encrypted_blocks[i] = str(pow(encrypted_blocks[i], e, n))

    # create a string from the numbers
    encrypted_message = " ".join(encrypted_blocks)

    return encrypted_message


@timed
def decrypt( blocks: str, keys_file : str = 'keys.json', block_size: int = 2) -> str:
    """
    Decrypts a string of numbers by raising each number to the power of d and 
    taking the modulus of n. Returns the message as a string.
    block_size refers to how many characters make up one group of numbers in
    each index of blocks.
    """

    try:
        with open(keys_file, 'r') as f:
            keys = json.load(f)
            private_key = keys['private_key']
            d, n = private_key
    except FileNotFoundError as e:
        raise e

    # turns the string into a list of ints
    list_blocks = blocks.split(' ')
    int_blocks = []

    for s in list_blocks:
        int_blocks.append(int(s))

    message = ""

    # converts each int in the list to block_size number of characters
    # by default, each int represents two characters
    for i in range(len(int_blocks)):
        # decrypt all numbers by taking it to the power of d
        # and modding it by n
        int_blocks[i] = pow(int_blocks[i], d , n)

        tmp = ""
        # take apart each block into its ASCII codes for each character
        # and store it in the message string
        for _ in range(block_size):
            tmp = chr(int_blocks[i] % 1000) + tmp
            int_blocks[i] //= 1000
            if int_blocks[i] == 0:
                break
        message += tmp

    return message


def main():
    # we select our primes and generate our public and private keys,
    # usually done once
    choose_again = input('Do you want to generate new public and private keys? (y or n) ')
    if choose_again == 'y':
        choose_keys()

    instruction = input('Would you like to encrypt or decrypt? (Enter e or d): ')
    if instruction == 'e':
        message = input('What would you like to encrypt?\n')
        option = input('Do you want to encrypt using your own public key? (y or n) ')

        if option == 'y':
            print('Encrypting...')
            encryped, encyption_time = encrypt(message)
            print(encryped)
            print(f'{encyption_time = }')
        else:
            file_option = input('Enter the file name that stores the public key: ')
            print('Encrypting...')
            print(encrypt(message, file_option))

    elif instruction == 'd':
        message = input('What would you like to decrypt?\n')
        print('Decryption...')
        decripted, decryption_time = decrypt(message)
        print(decripted)
        print(f'{decryption_time = }')
    else:
        print('That is not a proper instruction.')


main()
