import codecs
from itertools import cycle


def hex_to_base64(hex_bytes):
    return codecs.encode(codecs.decode(hex_bytes, 'hex_codec'), 'base64_codec')


def fixed_xor(encoded_1, encoded_2):
    """ Take two equal length strings, hex decode them and produce their XOR combination.

    Args:
        encoded_1: First string.
        encoded_2: Second string.

    Returns:
        A instance of the bytes class containing the XOR combination of the two input strings.
    """
    if not isinstance(encoded_1, str) or not isinstance(encoded_2, str):
        raise ValueError('Inputs must be strings!')
    if len(encoded_1) != len(encoded_2):
        raise ValueError('Inputs must have same length!')
    buffer_1, buffer_2 = [bytes.fromhex(string) for string in [encoded_1, encoded_2]]
    return bytes([byte_1 ^ byte_2 for byte_1, byte_2 in zip(buffer_1, buffer_2)])


def decrypt_single_byte_xor_cipher(encoded):
    """ Decrypt a hex encoded string that has been XOR'd against a single character.

    Args:
        encoded: A hex encoded string.

    Returns:
        The decrypted string.
    """
    numbers = bytes.fromhex(encoded)
    strings = (''.join(chr(number ^ key) for number in numbers) for key in range(256))
    return max(strings, key=lambda s: s.count(' '))


def detect_single_byte_xor_cipher(encoded_strings, n=5):
    """ Detect a single byte XOR encrypted hex encoded string and decrypt it.

    Args:
        encoded_strings: A list of hex encoded strings
        n: Integer, number of strings to return. (Default=5)

    Returns:

    """
    strings = [decrypt_single_byte_xor_cipher(encoded) for encoded in encoded_strings]
    return sorted(strings, key=lambda s: -s.count(' '))[:n]


def encrypt(text, key):
    """ Encrypt a string using a repeating key XOR cipher.

    Args:
        text: String, the text to encrypt.
        key: String, key to encrypt the text with.

    Returns:
        The encrypted text as a hex encoded string.
    """
    return bytes(ord(char_string) ^ ord(char_key) for char_string, char_key in zip(text, cycle(key))).hex()


def edit_distance(string_1, string_2):
    """ Calculate the edit (Hamming) distance between two strings.

    Args:
        string_1: The first string.
        string_2: The second string.

    Returns:
        The edit distance between the strings as an integer.
    """
    if not isinstance(string_1, str) or not isinstance(string_2, str):
        raise ValueError('Inputs must be strings!')
    if len(string_1) != len(string_2):
        raise ValueError('Inputs must have same length!')
    distance = 0
    for char_1, char_2 in zip(string_1, string_2):
        binary_1, binary_2 = (bin(ord(char))[2:].zfill(8) for char in (char_1, char_2))
        distance += sum(bit_1 != bit_2 for bit_1, bit_2 in zip(binary_1, binary_2))
    return distance


def main():
    string_1 = 'this is a test'
    string_2 = 'wokka wokka!!!'
    print(edit_distance(string_1, string_2))


if __name__ == '__main__':
    main()
