import itertools
import subgroup_enumeration


for dim in [1, 2, 3]:
    for dims in itertools.product(range(12), repeat=dim):
        bases = subgroup_enumeration.enumerate_subgroup_bases(dims)
        num = sum(1 for _ in bases)
        assert num == subgroup_enumeration.count_subgroups(dims)
