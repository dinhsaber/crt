import numpy as np
import math

class CRT:
    @staticmethod
    def _extended_gcd(a, b):
        if b == 0:
            return a, 1, 0
        else:
            g, x, y = CRT._extended_gcd(b, a % b)
            return g, y, x - (a // b) * y

    @staticmethod
    def _modinv(a, m):
        g, x, _ = CRT._extended_gcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        return x % m

    @staticmethod
    def chinese_remainder_theorem(a_list, n_list):
        N = 1
        for n in n_list:
            N *= n
        result = 0
        for ai, ni in zip(a_list, n_list):
            Ni = N // ni
            Mi = CRT._modinv(Ni, ni)
            result += ai * Ni * Mi
        return result % N

    @staticmethod
    def encode_shares(secret, moduli):
       
        shares = [np.remainder(secret, m).astype(np.uint16) for m in moduli]
        return shares

    @staticmethod
    def decode_secret(shares, moduli):
       
        shares = [np.array(s).astype(np.int64) for s in shares]
        moduli = [int(m) for m in moduli]
        stacked = np.stack(shares, axis=0)
        flat = stacked.reshape(len(moduli), -1)
        rec_flat = np.zeros(flat.shape[1], dtype=np.int64)
        for i in range(flat.shape[1]):
            ai = [int(flat[j, i]) for j in range(len(moduli))]
            rec_flat[i] = CRT.chinese_remainder_theorem(ai, moduli)
        rec_secret = rec_flat.reshape(shares[0].shape)
        return rec_secret

    @staticmethod
    def validate_moduli(moduli, k, secret_max):
        # Check pairwise coprime
        for i in range(len(moduli)):
            for j in range(i+1, len(moduli)):
                if math.gcd(moduli[i], moduli[j]) != 1:
                    raise Exception(f"Moduli {moduli[i]} and {moduli[j]} are not coprime.")
        # Check product of k moduli >= secret_max
        from itertools import combinations
        found = False
        for comb in combinations(moduli, k):
            prod = math.prod(comb)
            if prod >= secret_max:
                found = True
                break
        if not found:
            raise Exception(f"No combination of {k} moduli has product >= secret_max ({secret_max})")
        # Check product of (k-1) moduli < secret_max
        for comb in combinations(moduli, k-1):
            prod = math.prod(comb)
            if prod >= secret_max:
                raise Exception(f"A combination of {k-1} moduli has product >= secret_max ({secret_max}), which is not allowed.")

