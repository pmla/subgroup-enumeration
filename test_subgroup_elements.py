import itertools
import numpy as np
import subgroup_enumeration


for dim in [1, 2, 3]:
    for dims in itertools.product(range(8), repeat=dim):
        bases = subgroup_enumeration.enumerate_subgroup_bases(dims)
        for H in bases:
            elements = subgroup_enumeration.get_subgroup_elements(dims, H)
            assert elements.shape == np.unique(elements, axis=0).shape
            group_index = np.prod([a // b for a, b in zip(dims, np.diag(H))])
            assert group_index == len(elements)
