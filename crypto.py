import base64
from itertools import cycle


def hex_to_base64(hex_string):
    """ Convert a hex encoded string to base64.

    Args:
        hex_string: A hex encoded string.

    Returns:
        The base64 encoded bytes string.
    """
    return base64.b64encode(bytes.fromhex(hex_string))


def score(string):
    """ Score a piece of english plaintext according to letter frequencies.

    Source: https://en.wikipedia.org/wiki/Letter_frequency

    Args:
        string: The string to be scored.

    Returns:
        The score of the string normalized by the length of the string.
    """
    letter_frequencies = {
        'a': 0.0651738, 'b': 0.0124248, 'c': 0.0217339, 'd': 0.0349835, 'e': 0.1041442, 'f': 0.0197881, 'g': 0.0158610,
        'h': 0.0492888, 'i': 0.0558094, 'j': 0.0009033, 'k': 0.0050529, 'l': 0.0331490, 'm': 0.0202124, 'n': 0.0564513,
        'o': 0.0596302, 'p': 0.0137645, 'q': 0.0008606, 'r': 0.0497563, 's': 0.0515760, 't': 0.0729357, 'u': 0.0225134,
        'v': 0.0082903, 'w': 0.0171272, 'x': 0.0013692, 'y': 0.0145984, 'z': 0.0007836, ' ': 0.1918182
    }
    return sum(letter_frequencies.get(char, 0) for char in string.lower()) / len(string)


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


def _arg_max(pairs):
    return max(pairs, key=lambda x: x[1])[0]


def arg_max_index(values):
    """ Find the index of the largest value in a list.

    Args:
        values: A list of values.

    Returns:
        The index (int) of the largest value in values.
    """
    return _arg_max(enumerate(values))


def decrypt_single_character_xor(encrypted):
    """ Decrypt a series of bytes that has been XOR'd against a single character.

    Args:
        encrypted: The encrypted sequence of bytes

    Returns:
        The key used to encrypt the string and the decrypted string.
    """
    decrypted = [''.join(chr(byte ^ key) for byte in encrypted) for key in range(256)]
    scores = [score(string) for string in decrypted]
    key_index = arg_max_index(scores)
    key = chr(key_index)
    return key, decrypted[key_index]


def detect_single_byte_xor_cipher(encrypted, n=5):
    """ Detect a single byte XOR encrypted hex encoded string and decrypt it.

    Args:
        encrypted: A list of hex encoded strings
        n: Integer, number of strings to return. (Default=5)

    Returns:
        The first n most probable decrypted strings.
    """
    strings = [decrypt_single_character_xor(byte) for byte in bytes.fromhex(encrypted)]
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


def edit_distance_string(string_1, string_2):
    if not isinstance(string_1, str) or not isinstance(string_2, str):
        raise ValueError('Inputs must be strings!')


def decrypt(encrypted, min_key_size=2, max_key_size=40):
    smallest_distance, key_size = None, None
    for test_key_size in range(min_key_size, max_key_size + 1):
        # Take the first test_key_size worth of bytes and the second test_key_size worth of bytes.
        bytes_1, bytes_2 = (encrypted[i * test_key_size: (i + 1) * test_key_size] for i in range(2))
        assert len(bytes_1) == len(bytes_2), 'bytes_1 and bytes_2 do not have the same length!'
        # Calculate the edit distance between the first and the second test_key_size worth of bytes.
        distance = edit_distance(*(''.join(chr(byte) for byte in bytes_) for bytes_ in (bytes_1, bytes_2)))
        # Normalize the edit distance by dividing by test_key_size.
        distance /= test_key_size
        # The test_key_size with the smallest normalized edit distance is probably the test_key_size of the actual key.
        if smallest_distance is None or distance < smallest_distance:
            smallest_distance, key_size = distance, test_key_size
    # Split the encrypted bytes in blocks of length key_size.
    n_blocks = len(encrypted) // key_size
    blocks = [encrypted[i * key_size: (i + 1) * key_size] for i in range(n_blocks)]
    for block in blocks:
        assert len(block) == key_size, 'Block length does not equal key_size!'
    # Transpose the blocks: make a block that is the first byte of every block and so on.
    transposed_blocks = [bytes(transposed_block) for transposed_block in zip(*blocks)]
    assert len(transposed_blocks) == key_size, 'Number of transposed blocks does not equal key_size!'
    for transposed_block in transposed_blocks:
        assert len(transposed_block) == n_blocks, 'Transposed block length does not equal n_blocks!'
    # Solve each block as if it was single-character XOR.
    for byte in transposed_blocks[0]:
        print([byte ^ key for key in range(256)])


def main():
    string = '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'
    print(decrypt_single_character_xor(bytes.fromhex(string)))


if __name__ == '__main__':
    main()
