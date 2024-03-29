# Subgroup enumeration for cyclic, dicyclic, and tricyclic integer groups.
# PM Larsen, 2019
#
# The theory implemented here is described for two-dimensional groups in:
#     Representing and counting the subgroups of the group Z_m x Z_n
#     Mario Hampejs, Nicki Holighaus, László Tóth, and Christoph Wiesmeyr
#     Journal of Numbers, vol. 2014, Article ID 491428
#     http://dx.doi.org./10.1155/2014/491428
#     https://arxiv.org/abs/1211.1797
#
# and for three-dimensional groups in:
#     On the subgroups of finite Abelian groups of rank three
#     Mario Hampejs and László Tóth
#     Annales Univ. Sci. Budapest., Sect. Comp. 39 (2013), 111–124
#     https://arxiv.org/abs/1304.2961

import itertools
import numpy as np
from collections import defaultdict


def get_divisors(n):
    return [i for i in range(1, n + 1) if n % i == 0]


def get_subgroup_elements(orders, H):
    dimension = len(orders)
    assert dimension in [1, 2, 3]

    if dimension == 1:
        m = orders[0]
    elif dimension == 2:
        m, n = orders
    else:
        m, n, r = orders

    size = 1
    for e, x in zip(np.diag(H), orders):
        if e != 0:
            size *= x // e

    indices = np.zeros((size, dimension)).astype(np.int)
    indices[:, 0] = H[0, 0] * np.arange(size)

    if dimension >= 2 and H[1, 1] != 0:
        k = m // H[0, 0]
        p = np.arange(size) // k
        indices[:, 0] += H[1, 0] * p
        indices[:, 1] += H[1, 1] * p

    if dimension == 3 and H[2, 2] != 0:
        k = m * n // (H[1, 1] * H[0, 0])
        p = np.arange(size) // k
        indices[:, 0] += H[2, 0] * p
        indices[:, 1] += H[2, 1] * p
        indices[:, 2] += H[2, 2] * p

    return indices % orders


def consistent_first_rows(dimension, dm, ffilter):
    for a in dm:
        H = np.zeros((dimension, dimension)).astype(np.int)
        H[0, 0] = a
        if ffilter is None or ffilter(H):
            yield a


def solve_linear_congruence(r, a, b, c, s, v):
    for u in range(a + 1):
        if (r // c * u) % a == (r * v * s // (b * c)) % a:
            return u
    raise Exception("u not found")


def enumerate_subgroup_bases(orders, ffilter=None):
    """Get the subgroup bases of a cyclic/dicyclic/tricyclic integer group.

    Parameters:

    orders: list-like integer object
        Orders of the constituent groups.
        [m] if the group is a cyclic group Zm
        [m, n] if the group is a dicyclic group Zm x Zn
        [m, n, r] if the group is a tricyclic group Zm x Zn x Zr

    ffilter: function, optional
        A boolean filter function. Avoids generation of unwanted subgroups by
        rejecting partial bases.

    Returns iterator object yielding:

    H: integer ndarray
        Subgroup basis.
    """

    gcd = np.gcd
    dimension = len(orders)
    assert dimension in [1, 2, 3]
    if dimension == 1:
        m = orders[0]
    elif dimension == 2:
        m, n = orders
    else:
        m, n, r = orders
    dm = get_divisors(m)

    if dimension == 1:
        for d in consistent_first_rows(dimension, dm, ffilter):
            yield np.array([[d]])

    elif dimension == 2:
        dn = get_divisors(n)

        for a in consistent_first_rows(dimension, dm, ffilter):
            for b in dn:
                for t in range(gcd(a, n // b)):
                    s = t * a // gcd(a, n // b)
                    yield np.array([[a, 0], [s, b]])

    elif dimension == 3:
        dn = get_divisors(n)
        dr = get_divisors(r)

        for a in consistent_first_rows(dimension, dm, ffilter):
            for b, c in itertools.product(dn, dr):
                A = gcd(a, n // b)
                B = gcd(b, r // c)
                C = gcd(a, r // c)
                ABC = A * B * C
                X = ABC // gcd(a * r // c, ABC)

                for t in range(A):
                    s = a * t // A

                    H = np.zeros((dimension, dimension)).astype(np.int)
                    H[0] = [a, 0, 0]
                    H[1] = [s, b, 0]
                    if ffilter is not None and not ffilter(H):
                        continue

                    for w in range(B * gcd(t, X) // X):
                        v = b * X * w // (B * gcd(t, X))
                        u0 = solve_linear_congruence(r, a, b, c, s, v)

                        for z in range(C):
                            u = u0 + a * z // C
                            yield np.array([[a, 0, 0], [s, b, 0], [u, v, c]])


def count_subgroups(orders, count_orders=False):
    """Count the number of subgroups of a cyclic/dicyclic/tricyclic integer
    group.

    Parameters:

    orders: list-like integer object
        Orders of the constituent groups.
        [m] if the group is a cyclic group Zm
        [m, n] if the group is a dicyclic group Zm x Zn
        [m, n, r] if the group is a tricyclic group Zm x Zn x Zr

    Returns:

    n: integer
        Subgroup basis.
    """
    gcd = np.gcd

    def P(n):
        return sum([gcd(k, n) for k in range(1, n + 1)])

    dimension = len(orders)
    assert dimension in [1, 2, 3]
    if dimension == 1:
        m = orders[0]
    elif dimension == 2:
        m, n = orders
    else:
        m, n, r = orders
    dm = get_divisors(m)

    counts = defaultdict(int)
    if dimension == 1:
        for a in dm:
            counts[a] += 1
    elif dimension == 2:
        dn = get_divisors(n)
        for a, b in itertools.product(dm, dn):
            num = gcd(a, b)
            counts[np.prod([a, b])] += num
    else:
        dn = get_divisors(n)
        dr = get_divisors(r)

        for a, b, c in itertools.product(dm, dn, dr):
            A = gcd(a, n // b)
            B = gcd(b, r // c)
            C = gcd(a, r // c)
            ABC = A * B * C
            X = ABC // gcd(a * r // c, ABC)
            num = ABC // X**2 * P(X)
            counts[np.prod([a, b, c])] += num

    if count_orders:
        return sorted(counts.items())
    else:
        return sum(counts.values())
