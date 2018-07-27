import base64
from itertools import cycle, permutations
from string import ascii_lowercase


class RepeatingKeyXOR:

    def __init__(self, key):
        self.key = key

    def encrypt(self, text):
        """ Encrypt text using a repeating-key XOR cipher.

        Args:
            text(String): The text to encrypt.

        Returns:
            The encrypted text (bytes).
        """
        return bytes(ord(text_char) ^ ord(key_char) for text_char, key_char in zip(text, cycle(self.key)))

    def decrypt(self, encrypted):
        """ Decrypt text using a repeating-key XOR cipher.

        Args:
            encrypted (Bytes): The bytes to decrypt.

        Returns:
            The decrypted text (string).
        """
        letters = (chr(encrypted_byte ^ ord(key_char)) for encrypted_byte, key_char in zip(encrypted, cycle(self.key)))
        return ''.join(letters)

    # def break_(self, encrypted, min_key_size=2, max_key_size=40):
    #     """ Break the repeating-key XOR and decrypt the text.
    #
    #     Args:
    #         encrypted (Bytes): The bytes to decrypt.
    #
    #     Returns:
    #         The decrypted text (string).
    #     """


def hex_to_base64(hex_string):
    """ Convert a hex encoded string to base64.

    Args:
        hex_string: A hex encoded string.

    Returns:
        The base64 encoded bytes string.
    """
    return base64.b64encode(bytes.fromhex(hex_string))


# def score(string):
#     """ Score a piece of english plaintext according to letter frequencies.
#
#     Source: https://en.wikipedia.org/wiki/Letter_frequency
#
#     Args:
#         string: The string to be scored.
#
#     Returns:
#         The score of the string normalized by the length of the string.
#     """
#     letter_frequencies = {
#         'a': 0.0651738, 'b': 0.0124248, 'c': 0.0217339, 'd': 0.0349835, 'e': 0.1041442, 'f': 0.0197881, 'g': 0.0158610,
#         'h': 0.0492888, 'i': 0.0558094, 'j': 0.0009033, 'k': 0.0050529, 'l': 0.0331490, 'm': 0.0202124, 'n': 0.0564513,
#         'o': 0.0596302, 'p': 0.0137645, 'q': 0.0008606, 'r': 0.0497563, 's': 0.0515760, 't': 0.0729357, 'u': 0.0225134,
#         'v': 0.0082903, 'w': 0.0171272, 'x': 0.0013692, 'y': 0.0145984, 'z': 0.0007836, ' ': 0.1918182
#     }
#     return sum(letter_frequencies.get(char, 0) for char in string.lower()) / len(string)


def score(text):
    """ Score a piece of english plaintext according to letter frequencies.

    Source: https://en.wikipedia.org/wiki/Letter_frequency

    Args:
        text: The text to be scored.

    Returns:
        The score of the string normalized by the length of the string.
    """
    character_frequencies = {
        'a': 0.0651738, 'b': 0.0124248, 'c': 0.0217339, 'd': 0.0349835, 'e': 0.1041442, 'f': 0.0197881, 'g': 0.0158610,
        'h': 0.0492888, 'i': 0.0558094, 'j': 0.0009033, 'k': 0.0050529, 'l': 0.0331490, 'm': 0.0202124, 'n': 0.0564513,
        'o': 0.0596302, 'p': 0.0137645, 'q': 0.0008606, 'r': 0.0497563, 's': 0.0515760, 't': 0.0729357, 'u': 0.0225134,
        'v': 0.0082903, 'w': 0.0171272, 'x': 0.0013692, 'y': 0.0145984, 'z': 0.0007836, ' ': 0.1918182
    }
    length = len(text)
    # Get rid of any characters that are not in ascii_lowercase + ' '.
    #text = ''.join(letter if letter in ascii_lowercase + ' ' else '' for letter in text.lower())
    text = text.lower()
    character_counts = {letter: text.count(letter) for letter in text}
    chi_squared = 0
    for character, observed_count in character_counts.items():
        expected_count = character_frequencies.get(character, 0.0001) * length
        chi_squared += (observed_count - expected_count) ** 2 / expected_count
    return chi_squared


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


def _arg_min(pairs):
    return min(pairs, key=lambda x: x[1])[0]


def arg_min_index(values):
    return _arg_min(enumerate(values))


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
    key_index = arg_min_index(scores)
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


def edit_distance(bytes1, bytes2):
    """ Calculate the edit (Hamming) distance between two byte sequences.

    Args:
        bytes1: The first sequence of bytes.
        bytes2: The second sequence of bytes.

    Returns:
        The edit distance between the two sequences of bytes as an integer.
    """
    if not isinstance(bytes1, bytes) or not isinstance(bytes2, bytes):
        raise ValueError('Inputs must be bytes!')
    if len(bytes1) != len(bytes2):
        raise ValueError('Inputs must have same length!')
    distance = 0
    for byte1, byte2 in zip(bytes1, bytes2):
        binary1, binary2 = (bin(byte)[2:].zfill(8) for byte in (byte1, byte2))
        distance += sum(bit1 != bit2 for bit1, bit2 in zip(binary1, binary2))
    return distance


def decrypt2(encrypted, min_key_size=2, max_key_size=40, n_key_size_blocks=2):
    smallest_distance, key_size = None, None
    for test_key_size in range(min_key_size, max_key_size + 1):
        # Take the first test_key_size worth of bytes and the second test_key_size worth of bytes.
        bytes_1, bytes_2 = (encrypted[i * test_key_size: (i + 1) * test_key_size] for i in range(2))
        assert len(bytes_1) == len(bytes_2), 'bytes_1 and bytes_2 do not have the same length!'
        # Calculate the edit distance between the first and the second test_key_size worth of bytes.
        distance = edit_distance(*(''.join(chr(byte) for byte in bytes_) for bytes_ in (bytes_1, bytes_2)))
        # Normalize the edit distance by dividing by test_key_size.
        distance /= test_key_size
        # The test_key_size with the smallest normalized edit distance is probably the key size of the actual key.
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
    # Solve each block as if it was single-character XOR and combine the single-character keys to get the whole key.
    key = ''.join((decrypt_single_character_xor(transposed_block)[0] for transposed_block in transposed_blocks))
    print(key_size)
    print(key)
    repeating_key_xor = RepeatingKeyXOR(key)
    return repeating_key_xor.decrypt(encrypted)


def get_blocks(encrypted, key_size, n_blocks):
    return [encrypted[i * key_size : (i + 1) * key_size] for i in range(n_blocks)]


def decrypt(encrypted, min_key_size=2, max_key_size=40, n_key_size_blocks=2):
    smallest_distance, key_size = None, None
    for test_key_size in range(min_key_size, max_key_size + 1):
        key_size_blocks = get_blocks(encrypted, test_key_size, n_key_size_blocks)
        distances = []
        for index1, index2 in permutations(range(n_key_size_blocks), r=2):
            key_size_block1, key_size_block2 = key_size_blocks[index1], key_size_blocks[index2]
            distances.append(edit_distance(key_size_block1, key_size_block2) / test_key_size)
        distance = sum(distances) / len(distances)
        if smallest_distance is None or distance < smallest_distance:
            smallest_distance = distance
            key_size = test_key_size
    # Split the encrypted bytes in blocks of length key_size.
    n_blocks = len(encrypted) // key_size
    blocks = get_blocks(encrypted, key_size, n_blocks)
    print(blocks)



def main():
    with open('challenge_6_data.txt', 'r') as f:
        decrypted = decrypt(base64.b64decode(f.read()), n_key_size_blocks=4)
        print(decrypted)


if __name__ == '__main__':
    main()
