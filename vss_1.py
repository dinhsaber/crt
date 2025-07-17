import numpy as np
def generateRandomKey(key_shape):
    dealer_key = np.random.randint(0, 256, size=key_shape).astype(int)
    return dealer_key

def encode_vss(img):
    key_vss = generateRandomKey(img.shape)
    encrypted_im = np.bitwise_xor(img.astype(int), key_vss.astype(int))
    return key_vss, encrypted_im

def decode_vss(encrypted_im, rand_key):
    decrypted_im = np.bitwise_xor(encrypted_im.astype(int), rand_key.astype(int))
    return decrypted_im
