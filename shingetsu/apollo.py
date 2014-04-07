'''Signature Module.
'''
#
# Copyright (c) 2005,2013 shinGETsu Project.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import base64
from compatible import md5

# Count for Rabin-Miller test.
# Error rate is 1/(4^count).
sprp_test_count = 10

little_prime = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
    317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
    503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601,
    607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
    701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809,
    811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
    911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009,
    1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087,
    1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171,
    1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259,
    1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327,
    1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447,
    1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523,
    1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607,
    1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697,
    1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787,
    1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879,
    1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993,
    1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081,
    2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153,
    2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269,
    2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351,
    2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437,
    2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549,
    2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659,
    2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719,
    2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803,
    2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909,
    2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019,
    3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121,
    3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229,
    3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329,
    3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433,
    3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529,
    3533, 3539, 3541, 3547, 3557, 3559, 3571, 3581, 3583, 3593, 3607, 3613,
    3617, 3623, 3631, 3637, 3643, 3659, 3671, 3673, 3677, 3691, 3697, 3701,
    3709, 3719, 3727, 3733, 3739, 3761, 3767, 3769, 3779, 3793, 3797, 3803,
    3821, 3823, 3833, 3847, 3851, 3853, 3863, 3877, 3881, 3889, 3907, 3911,
    3917, 3919, 3923, 3929, 3931, 3943, 3947, 3967, 3989, 4001, 4003, 4007,
    4013, 4019, 4021, 4027, 4049, 4051, 4057, 4073, 4079, 4091, 4093, 4099,
    4111, 4127, 4129, 4133, 4139, 4153, 4157, 4159, 4177, 4201, 4211, 4217,
    4219, 4229, 4231, 4241, 4243, 4253, 4259, 4261, 4271, 4273, 4283, 4289,
    4297, 4327, 4337, 4339, 4349, 4357, 4363, 4373, 4391, 4397, 4409, 4421,
    4423, 4441, 4447, 4451, 4457, 4463, 4481, 4483, 4493, 4507, 4513, 4517,
    4519, 4523, 4547, 4549, 4561, 4567, 4583, 4591, 4597, 4603, 4621, 4637,
    4639, 4643, 4649, 4651, 4657, 4663, 4673, 4679, 4691, 4703, 4721, 4723,
    4729, 4733, 4751, 4759, 4783, 4787, 4789, 4793, 4799, 4801, 4813, 4817,
    4831, 4861, 4871, 4877, 4889, 4903, 4909, 4919, 4931, 4933, 4937, 4943,
    4951, 4957, 4967, 4969, 4973, 4987, 4993, 4999]

def spsp(n, a):
    """Rabin-Miller test.

    n should be odd number and 1 < b < n-1.
    """
    if n % 2 == 0:
        return False    

    # find s,d: n-1=2^s*d, d: odd number
    n1 = n - 1
    d = n1
    r = 1
    s = 0
    while r != 0:
        r = d % 2
        d = d // 2
        s += 1

    # start with p = a^q (mod n)
    p = a
    p = pow(p, d, n)

    # when p=1 or p=n-1 with i=0, n is a prim number.
    if (p == 1) or (p == n1):
        return True

    for i in range(1, s):
        p = pow(p, 2, n)
        if p == n1:
            return True

    # p!=n-1 with i<s, n is not a prim number.
    return False

def spsptest(n):
    """Do Rabin-Miller test with ``count'' prime number.

    See: http://primes.utm.edu/prove/prove2_3.html
    If n < 1,373,653 is a both 2 and 3-SPRP, then n is prime.
    If n < 25,326,001 is a 2, 3 and 5-SPRP, then n is prime.
    If n < 25,000,000,000 is a 2, 3, 5 and 7-SPRP,
      then either n = 3,215,031,751 or n is prime.
      (This is actually true for n < 118,670,087,467.)
    If n < 2,152,302,898,747 is a 2, 3, 5, 7 and 11-SPRP, then n is prime.
    If n < 3,474,749,660,383 is a 2, 3, 5, 7, 11 and 13-SPRP, then n is prime.
    If n < 341,550,071,728,321 is a 2, 3, 5, 7, 11, 13 and 17-SPRP,
      then n is prime.
    If n < 9,080,191 is a both 31 and 73-SPRP, then n is prime.
    If n < 4,759,123,141 is a 2, 7 and 61-SPRP, then n is prime.
    If n < 1,000,000,000,000 is a 2, 13, 23, and 1662803-SPRP, then n is prime.
    """
    for i in little_prime[0:sprp_test_count+1]:
        if not spsp(n, i):
            return False
    return True

def littletest(n):
    """Test n is prim number or not, using little_prime."""
    if n == 1:
        return False
    for i in little_prime:
        if n % i == 0:
            return False
    return True

def primize(x):
    """Make x a plime number.

    Result >= x.
    """
    if x % 2 == 0:
        x += 1

    while True:
        if littletest(x) and spsptest(x):
            return x
        else:
            x += 2


rsa_public_e = 0x10001
rsa_create_giveup = 300

def modinv(a, n):
    """Extended Euclid's algorithm.

    See http://www.finetune.co.jp/~lyuka/technote/mod_calc/exeuclid.html
    """
    s = a
    t = n
    u = 1
    v = 0

    while s > 0:
        q = t // s
        w = t - q * s
        t = s
        s = w
        w = v - q * u
        v = u
        u = w
    return (v + n) % n

def rsa_base_generate(p_seed, q_seed):
    e = rsa_public_e
    test = 0

    q = q_seed
    p = p_seed

    for count in xrange(rsa_create_giveup):
        q = primize(q)
        q1 = q - 1
        p = primize(p)
        phi = p - 1
        phi = phi * q1
        key_d = modinv(e, phi)
        if key_d == 0:
            continue
        key_n = p*q
        test = 0x7743
        test = pow(test, e, key_n)
        test = pow(test, key_d, key_n)
        if test == 0x7743:
            return (key_n, key_d)
        p += 2
        q += 2

    return (0, 0)

def rsa_base_encrypt(m, key_n, key_d):
    return pow(m, key_d, key_n)

def rsa_base_decrypt(m, n):
    return pow(m, rsa_public_e, n)

base64en = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

base64de = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 62, 0, 0, 0, 63,
    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 0, 0, 0, 0, 0,
    0, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def base64_to_int(s):
    tmp = 0
    buf = list(s)
    buf.reverse()
    for i in buf:
        tmp = tmp*64 + base64de[ord(i)]
    return tmp

def int_to_base64(n):
    buf = []
    while n > 0:
        buf.append(base64en[n%64])
        n //= 64
    return "".join(buf) + (base64en[0] * (86-len(buf)))

def bin_to_int(bin):
    """Binary to int.

    0x16 0x22 -> 0x16*256 + 0x22.
    """
    tmp = 0
    buf = list(bin)
    buf.reverse()
    for i in buf:
        tmp = tmp*256 + ord(i)
    return tmp

def rsa_sign(mes, publickey, secretkey):
    key_n = base64_to_int(publickey)
    key_d = base64_to_int(secretkey)
    m = bin_to_int(mes)
    m = rsa_base_encrypt(m, key_n, key_d)
    signature = int_to_base64(m)
    return signature

def rsa_verify(mes, testsignature, publickey):
    if len(mes)*4 > len(publickey)*3:
        return False
    m = bin_to_int(mes)
    n = base64_to_int(publickey)
    c = base64_to_int(testsignature)
    c = rsa_base_decrypt(c, n)
    return m == c

def make512pq(keystr):
    seedbuf = md5.new(keystr).digest()
    seedbuf += md5.new(keystr+"pad1").digest()
    seedbuf += md5.new(keystr+"pad2").digest()
    seedbuf += md5.new(keystr+"pad3").digest()
    p = bin_to_int(seedbuf[0:28])
    q = bin_to_int(seedbuf[28:64])
    p |= 2**215
    q |= 2**279
    return (p, q)

def keycreate512(keystr):
    (p, q) = make512pq(keystr)
    (key_n, key_d) = rsa_base_generate(p, q)
    if key_n == 0:
        return ("", "")
    else:
        publickey = int_to_base64(key_n)
        secretkey = int_to_base64(key_d)
        return (publickey, secretkey)


def key_pair(key_generator):
    """Generate key pair."""
    (pubkey, prikey) = keycreate512(key_generator[:512])
    return (pubkey, prikey)

def sign(target, pubkey, prikey):
    """Sign Message."""
    sign = rsa_sign(target[:512], pubkey[:512], prikey[:512])
    return sign

def verify(target, sign, pubkey):
    """Verify Signature."""
    result = rsa_verify(target[:512], sign[:512], pubkey[:512])
    return result

def cut_key(key):
    """Cut KeyStr to 11words."""
    short_key = base64.encodestring(md5.new(key[:512]).digest())[:11]
    return short_key
