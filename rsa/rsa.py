# Original Script by jchen2186
# Modified and Improved by Basel Al-Dwairi
# Modified Comments, Fixed Bug with odd length input, Improved performance by over 200k times with pow()

# Imports
import random
from typing import Callable
import time
import json
import argparse


def timed(func: Callable) -> Callable:
    """
    Decorator for timing functions
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        time_taken = end - start
        print()
        print(f'Finished in {time_taken} seconds')

        return result

    return wrapper


def gcd(a: int, b: int) -> int:
    """
    Performs Euclidean algorithm and returns gcd
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
    Chooses a random number, 1 < e < phi, and checks whether it is
    coprime with the phi, that is, gcd(e, phi) = 1
    """
    while True:
        e = random.randrange(2, phi)

        if gcd(e, phi) == 1:
            return e


@timed
def choose_keys(rand_a: int = 100, rand_b: int = 500, keys_file: str = 'keys.json') -> None:
    """
    Selects two random prime numbers from a list of prime numbers which has 
    values that go up to 100k. It Calculates both the public and private keys
    and stores them in a JSON file.
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

    print(f'Public key: {public_key}')
    print(f'Private key: {private_key}')


@timed
def encrypt(keys_file: str = 'keys.json', infile: str = 'infile.txt', outfile: str = 'otfile.txt',
            block_size: int = 2) -> str:
    """
    Encrypts a message (string) by raising each character's ASCII value to the 
    power of e and taking the modulus of n. Returns a string of numbers.
    file_name refers to file where the public key is located.
    block_size refers to how many characters make up one group of numbers in 
    each index of encrypted_blocks.
    """

    try:
        # Read public key
        with open(keys_file, 'r') as f:
            keys = json.load(f)
            public_key = keys['public_key']
            e, n = public_key

    except FileNotFoundError as e:
        raise e

    encrypted_blocks = []
    ciphertext = -1

    # Read input file and message
    with open(infile, 'r') as f:
        message = f.read()

    # Input is valid
    if not len(message) > 0:
        raise Exception('Input is Empty')

    ciphertext = 0

    for i in range(0, len(message)):
        # add ciphertext to the list if the max block size is reached
        # reset ciphertext so we can continue adding ASCII codes
        if i % block_size == 0 and i != 0:
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

    # Save encrypted message to output file
    with open(outfile, 'w') as f:
        f.write(encrypted_message)

    print(f'Message: {message}')
    print(f'Encrypted message: {encrypted_message}')

    return encrypted_message


@timed
def decrypt(keys_file: str = 'keys.json', infile: str = 'infile.txt', outfile: str = 'outfile.txt',
            block_size: int = 2) -> str:
    """
    Decrypts a string of numbers by raising each number to the power of d and 
    taking the modulus of n. Returns the message as a string.
    block_size refers to how many characters make up one group of numbers in
    each index of blocks.
    """

    # Read private key
    try:
        with open(keys_file, 'r') as f:
            keys = json.load(f)
            private_key = keys['private_key']
            d, n = private_key
    except FileNotFoundError as e:
        raise e

    # Read input file and encrypted message
    with open(infile, 'r') as f:
        blocks = f.read()

    # turns the string into a list of ints
    int_blocks = [int(num) for num in blocks.split(' ')]

    message = ""

    # converts each int in the list to block_size number of characters
    # by default, each int represents two characters
    for i in range(len(int_blocks)):
        # decrypt all numbers by taking it to the power of d
        # and modding it by n
        int_blocks[i] = pow(int_blocks[i], d, n)

        tmp = ""
        # take apart each block into its ASCII codes for each character
        # and store it in the message string
        for _ in range(block_size):
            tmp = chr(int_blocks[i] % 1000) + tmp
            int_blocks[i] //= 1000
            if int_blocks[i] == 0:
                break
        message += tmp

    # Save message to output file
    with open(outfile, 'w') as f:
        f.write(message)

    print(f'Encrypter Message: {blocks}')
    print(f'Message: {message}')

    return message


def main():
    # Parser
    parser = argparse.ArgumentParser(description="DES Encryption/Decryption Tool (ECB Mode)")

    # Parse script mode
    crypt_group = parser.add_mutually_exclusive_group(required=True)
    crypt_group.add_argument('-e', action='store_const', dest='option', const='e', help='Encrypt the input file.')
    crypt_group.add_argument('-d', action='store_const', dest='option', const='d', help='Decrypt the input file.')
    crypt_group.add_argument('-g', action='store_const', dest='option', const='g', help='Generate Keys.')

    # Static files
    keys_file = 'keys.json'
    infile = 'infile.txt'
    outfile = 'outfile.txt'
    block_size = 2

    args = parser.parse_args()

    # Execute Script
    if args.option == 'g':
        choose_keys(keys_file=keys_file)
    elif args.option == 'e':
        encrypt(keys_file=keys_file, infile=infile, outfile=outfile, block_size=block_size)
    elif args.option == 'd':
        decrypt(keys_file=keys_file, infile=infile, outfile=outfile, block_size=block_size)


if __name__ == '__main__':
    main()
