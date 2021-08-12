#!/usr/bin/env python

from itertools import chain
import random as rand
import numpy as np
from scipy.special import binom


def _decompose_tree(num_leaves, num_internal_nodes):
    """ Algorithm from: Uniform generation of a Schroder tree"""

    num_nodes = num_leaves + num_internal_nodes

    patterns = _generate_patterns(num_nodes, num_internal_nodes)
    seq, sizes = _generate_tree(num_nodes, num_internal_nodes, patterns)

    seq = cycle_lemma(seq)

    tree = _turn_pattern_into_tree(seq)

    return tree


def generate_group_separable_election(num_voters=None, num_candidates=None, params=None):
    """ Algorithm from: The Complexity of Election Problems with Group-Separable Preferences"""
    if params is not None and 'param_1' not in params:
        params = {'param_1': 0}

    while True:
        m = num_candidates
        n = num_voters

        if params['param_1'] == 0:
            func = lambda m, r: 1./(m-1) * binom(m - 1, r) * binom(m - 1 + r, m)
            buckets = [func(m, r) for r in range(1, m)]

            denominator = sum(buckets)
            buckets = [buckets[i]/denominator for i in range(len(buckets))]

            num_internal_nodes = np.random.choice(len(buckets), 1, p=buckets)[0]+1

            decomposition_tree = _decompose_tree(num_candidates, num_internal_nodes)

        elif params['param_1'] == 3:
            decomposition_tree = _caterpillar(m)

        all_inner_nodes = get_all_inner_nodes(decomposition_tree)

        votes = []
        for i in range(n):

            signature = [rand.choice([0, 1]) for _ in range(len(all_inner_nodes))]

            for i, node in enumerate(all_inner_nodes):
                node.reverse = signature[i]

            raw_vote = sample_a_vote(decomposition_tree)
            vote = [int(candidate.replace('x', '')) for candidate in raw_vote]
            votes.append(vote)

            for i, node in enumerate(all_inner_nodes):
                node.reverse = False

        return votes


REVERSE = {}


def get_all_leaves_names(node):
    if node.leaf:
        return [node.name]
    output = []
    for i in range(len(node.children)):
        output.append(get_all_leaves_names(node.children[i]))
    return list(chain.from_iterable(output))


def get_all_leaves_nodes(node):
    if node.leaf:
        return [node]
    output = []
    for i in range(len(node.children)):
        output.append(get_all_leaves_nodes(node.children[i]))
    return list(chain.from_iterable(output))


def get_bracket_notation(node):
    if node.leaf:
        return str(node.name)
    output = ''
    for i in range(len(node.children)):
        output += str(get_bracket_notation(node.children[i]))
    return '(' + output + ')'


def get_all_inner_nodes(node):
    if node.leaf:
        return []
    output = [[node]]
    for i in range(len(node.children)):
        output.append(get_all_inner_nodes(node.children[i]))
    return list(chain.from_iterable(output))


def sample_a_vote(node, reverse=False):
    if node.leaf:
        return [node.name]
    output = []
    if reverse == node.reverse:
        for i in range(len(node.children)):
            output.append(sample_a_vote(node.children[i]))
    else:
        for i in range(len(node.children)):
            output.append(sample_a_vote(node.children[len(node.children)-1-i], reverse=True))

    return list(chain.from_iterable(output))


class Node:

    total_num_leaf_descendants = 0

    def __init__(self, name):

        self.name = name
        self.children = []
        self.leaf = True
        self.reverse = False

        self.num_leaf_descendants = None
        self.depth = None
        self.scheme = {}
        self.scheme_1 = {}
        self.scheme_2 = {}
        self.vector = []

    def __str__(self):
        return self.name

    def add_child(self, child):
        self.children.append(child)
        self.leaf = False


def _generate_patterns(num_nodes, num_internal_nodes):
    # Step 1: Mixing the patterns
    patterns = ['M0' for _ in range(num_nodes-num_internal_nodes)] + ['M1' for _ in range(num_internal_nodes)]
    rand.shuffle(patterns)
    return patterns


def _generate_tree(num_nodes, num_internal_nodes, patterns):
    """ Algorithm from: A linear-time algorithm for the generation of trees """

    sequence = []
    sizes = []
    larges = []
    ctr = 0
    for i, pattern in enumerate(patterns):
        if pattern == 'M0':
            sequence.append('x' + str(ctr))
            sizes.append(1)
            ctr += 1
        elif pattern == 'M1':
            sequence.append('x')
            sequence.append('()1')   # instead of 'o'
            sequence.append('f1')
            sequence.append('f1')
            sizes.append(4)
            larges.append(i)

    num_classical_edges = 0
    num_semi_edges = 2*num_internal_nodes
    num_multi_edges = num_internal_nodes
    num_trees = 1
    pos = 1
    num_edges = num_nodes - num_trees - num_semi_edges - num_classical_edges

    pos_to_insert = []
    for i, elem in enumerate(sequence):
        if elem == '()1':
            pos_to_insert.append(i)

    choices = list(np.random.choice([i for i in range(len(pos_to_insert))], size=num_edges, replace=True))
    choices.sort(reverse=True)

    for choice in choices:
        sizes[larges[choice]] += 1
        sequence.insert(pos_to_insert[choice], 'f1')

    for i in range(len(pos_to_insert)):
        sequence.remove('()1')

    return sequence, sizes


def _turn_pattern_into_tree(pattern):
    stack = []
    for i, element in enumerate(pattern):
        if 'x' in element:
            stack.append(Node(element))
        if 'f' in element:
            parent = stack.pop()
            child = stack.pop()
            parent.add_child(child)
            stack.append(parent)
    return stack[0]


def cycle_lemma(sequence):

    pos = 0
    height = 0
    min = 0
    pos_min = 0
    for element in sequence:
        if 'x' in element:
            if height <= min:
                pos_min = pos
                min = height
            height += 1
        if 'f' in element:
            height -= 1
        pos += 1

    # rotate
    for _ in range(pos_min):
        element = sequence.pop(0)
        sequence.append(element)

    return sequence


def _add_num_leaf_descendants(node):
    """ add total number of descendants to each internal node """

    if node.leaf:
        node.num_leaf_descendants = 1
    else:
        node.num_leaf_descendants = 0
        for child in node.children:
            node.num_leaf_descendants += _add_num_leaf_descendants(child)

    return node.num_leaf_descendants


def _add_scheme(node):

    for starting_pos in node.scheme_1:

        pos = starting_pos
        for child in node.children:
            if pos in child.scheme_1:
                child.scheme_1[pos] += node.scheme_1[starting_pos]
            else:
                child.scheme_1[pos] = node.scheme_1[starting_pos]
            pos += child.num_leaf_descendants

    for starting_pos in node.scheme_2:

        pos = starting_pos
        for child in node.children:
            pos -= child.num_leaf_descendants
            if pos in child.scheme_2:
                child.scheme_2[pos] += node.scheme_2[starting_pos]
            else:
                child.scheme_2[pos] = node.scheme_2[starting_pos]

    if node.leaf:
        _construct_vector_from_scheme(node)
    else:
        for child in node.children:
            _add_scheme(child)


def _construct_vector_from_scheme(node):

    x = node.scheme_1
    y = node.scheme_2
    node.scheme = {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}

    weight = 1. / sum(node.scheme.values())

    node.vector = [0 for _ in range(Node.total_num_leaf_descendants)]
    for key in node.scheme:

        node.vector[int(key)] += node.scheme[key] * weight


def get_frequency_matrix_from_tree(root):

    _add_num_leaf_descendants(root)

    Node.total_num_leaf_descendants = root.num_leaf_descendants
    root.scheme_1 = {0: 1}
    root.scheme_2 = {int(Node.total_num_leaf_descendants - 1): 1}

    _add_scheme(root)

    nodes = get_all_leaves_nodes(root)

    m = Node.total_num_leaf_descendants
    array = np.zeros([m, m])

    for i in range(m):
        for j in range(m):
            array[i][j] = nodes[i].vector[j]

    return array


def _caterpillar(num_leaves):
    root = Node('root')
    tmp_root = root
    ctr = 0

    while num_leaves > 2:
        leaf = Node('x' + str(ctr))
        inner_node = Node('inner_node')
        tmp_root.add_child(leaf)
        tmp_root.add_child(inner_node)
        tmp_root = inner_node
        num_leaves -= 1
        ctr += 1

    leaf_1 = Node('x' + str(ctr))
    leaf_2 = Node('x' + str(ctr + 1))
    tmp_root.add_child(leaf_1)
    tmp_root.add_child(leaf_2)

    return root


### MATRICES ###
def get_gs_caterpillar_matrix(num_candidates):
    return get_gs_caterpillar_vectors(num_candidates).transpose()

def get_gs_caterpillar_vectors(num_candidates):
    return get_frequency_matrix_from_tree(_caterpillar(num_candidates))

# get_gs_caterpillar_matrix(10)

# 10votes = generate_group_separable_election(num_voters=10, num_candidates=14)
# print(votes)

# generate_group_separable_election(num_voters=100,num_candidates=40)