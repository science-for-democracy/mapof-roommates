import math
import os
import random as rand

import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import Callable

from mapel.voting.metrics import lp

from mapel.voting.objects.ApprovalElection import ApprovalElection


# MAIN APPROVAL DISTANCES
def compute_approvalwise(election_1: ApprovalElection, election_2: ApprovalElection,
                         inner_distance: Callable) -> float:
    """ Return: approvalwise distance """
    return inner_distance(election_1.approvalwise_vector, election_2.approvalwise_vector)


def compute_coapproval_frequency_vectors(election_1: ApprovalElection, election_2: ApprovalElection,
                                         inner_distance: Callable) -> (float, list):
    """ Return: coapproval frequency distance, optimal matching """
    cost_table = get_matching_cost_coapproval_frequency_vectors(
        election_1, election_2, inner_distance)
    return solve_matching_vectors(cost_table)


def compute_candidatelikeness(election_1: ApprovalElection, election_2: ApprovalElection,
                              inner_distance: Callable) -> (float, list):
    """ Return: candidatelikeness distance, optimal matching """
    cost_table = get_matching_cost_candidatelikeness(
        election_1, election_2, inner_distance)
    return solve_matching_vectors(cost_table)


def compute_hamming(election_1: ApprovalElection, election_2: ApprovalElection) -> float:
    """ Return: Hamming distance """
    votes_1 = election_1.votes
    votes_2 = election_2.votes
    params = {'voters': election_1.num_voters, 'candidates': election_2.num_candidates}
    file_name = str(rand.random()) + '.lp'
    path = os.path.join(os.getcwd(), "trash", file_name)
    lp.generate_ilp_distance(path, votes_1, votes_2, params, 'hamming')
    objective_value = lp.solve_ilp_distance(path, votes_1, votes_2, params, 'hamming')
    lp.remove_lp_file(path)
    return objective_value


def compute_voterlikeness(election_1: ApprovalElection, election_2: ApprovalElection,
                          inner_distance: Callable) -> (float, list):
    """ Return: voterlikeness distance, optimal matching """
    cost_table = get_matching_cost_voterlikeness_vectors(
        election_1, election_2, inner_distance)
    return solve_matching_vectors(cost_table)


def compute_pairwise(election_1: ApprovalElection, election_2: ApprovalElection,
                     inner_distance: Callable) -> (float, list):
    """ Return: approval pairwise distance, optimal matching """
    length = election_1.num_candidates
    matrix_1 = election_1.pairwise_matrix
    matrix_2 = election_2.pairwise_matrix
    return solve_matching_matrices(matrix_1, matrix_2, length, inner_distance)


def compute_flow(ele_1, ele_2):
    cost_table = get_flow_helper_1(ele_1, ele_2)
    objective_value, matching = solve_matching_vectors(cost_table)
    objective_value /= 1000.
    return objective_value, matching


# HELPER FUNCTIONS #
def flow_helper(v_1, v_2, num_candidates=8, num_voters=50):
    # print(v_1, v_2)

    def normalize(x):
        # return 1000

        if x == 0:
            return 0
        x = math.log(1 / x)
        x = int(x * 1000)
        return x

    max_capacity = num_voters * num_candidates
    total_demand = num_voters * num_candidates

    m = float(num_candidates)
    int_m = int(m)
    source = 'source'
    sink = 'sink'
    graph = nx.DiGraph()
    epsilon = 0.1

    graph.add_node(source, demand=-total_demand)
    for i in range(1, 2 * int(m) + 1):
        graph.add_node(i, demand=0)
    graph.add_node(sink, demand=total_demand)

    for i in range(1, 2 * int(m) + 1):
        # print(int(v_1[i-1]*total_demand))
        graph.add_edge(source, i, capacity=int(v_1[i - 1] * total_demand + epsilon), weight=0)
        graph.add_edge(i, sink, capacity=int(v_2[i - 1] * total_demand + epsilon), weight=0)

    # upper row
    for k in range(1, int_m + 1):
        prob_right = (m - k) / m
        prob_left = k / m
        prob_left_down = prob_left / k
        prob_left_up = prob_left - prob_left_down

        # go left down
        graph.add_edge(k, k + int_m, capacity=int(max_capacity), weight=normalize(prob_left_down))
        # go left up
        if 1 < k:
            graph.add_edge(k, k - 1, capacity=int(max_capacity), weight=normalize(prob_left_up))
        # go right
        if k < m:
            graph.add_edge(k, k + 1, capacity=int(max_capacity), weight=normalize(prob_right))
        # print(k, prob_left_up, prob_left_down, prob_right)

    # lower row
    for k in range(0, int_m):
        prob_right = (m - k) / m
        prob_left = k / m
        prob_right_up = prob_right / (m - k)
        prob_right_down = prob_right - prob_right_up

        # go right up
        my_pos = k + int_m + 1
        graph.add_edge(my_pos, k + 1, capacity=int(max_capacity), weight=normalize(prob_right_up))
        # go right down
        if k < m - 1:
            graph.add_edge(my_pos, my_pos + 1, capacity=int(max_capacity),
                           weight=normalize(prob_right_down))
        # go left
        if 0 < k:
            graph.add_edge(my_pos, my_pos - 1, capacity=int(max_capacity),
                           weight=normalize(prob_left))
        # print("p", prob_right_up, prob_right_down, prob_left)

    # print("start")
    objective_value = nx.min_cost_flow_cost(graph)
    # print("stop")
    # print('obj', objective_value)

    return objective_value


def get_flow_helper_1(ele_1, ele_2):
    vectors_1 = ele_1.coapproval_frequency_vectors
    vectors_2 = ele_2.coapproval_frequency_vectors
    size = ele_1.num_candidates
    cost_table = [[flow_helper(vectors_1[i], vectors_2[j])
                   for i in range(size)] for j in range(size)]
    return cost_table


def get_matching_cost_coapproval_frequency_vectors(ele_1, ele_2, inner_distance):
    vectors_1 = ele_1.coapproval_frequency_vectors
    vectors_2 = ele_2.coapproval_frequency_vectors
    size = ele_1.num_candidates
    cost_table = [[inner_distance(vectors_1[i], vectors_2[j])
                   for i in range(size)] for j in range(size)]
    return cost_table


def get_matching_cost_candidatelikeness(election_1: ApprovalElection, election_2: ApprovalElection,
                                        inner_distance: Callable):
    vectors_1 = election_1.candidatelikeness_sorted_vectors
    vectors_2 = election_2.candidatelikeness_sorted_vectors
    size = election_1.num_candidates
    cost_table = [[inner_distance(vectors_1[i], vectors_2[j])
                   for i in range(size)] for j in range(size)]
    return cost_table


def get_matching_cost_voterlikeness_vectors(election_1: ApprovalElection,
                                            election_2: ApprovalElection,
                                            inner_distance: Callable):
    vectors_1 = election_1.voterlikeness_vectors
    vectors_2 = election_2.voterlikeness_vectors
    size = election_1.num_voters
    cost_table = [[inner_distance(vectors_1[i], vectors_2[j])
                   for i in range(size)] for j in range(size)]
    return cost_table


def solve_matching_vectors(cost_table) -> (float, list):
    """ Return: objective value, optimal matching"""
    cost_table = np.array(cost_table)
    row_ind, col_ind = linear_sum_assignment(cost_table)
    return cost_table[row_ind, col_ind].sum(), list(col_ind)


def solve_matching_matrices(matrix_1, matrix_2, length, inner_distance) -> float:
    file_name = str(rand.random()) + '.lp'
    path = os.path.join(os.getcwd(), "trash", file_name)
    lp.generate_lp_file_matching_matrix(path, matrix_1, matrix_2, length,
                                        inner_distance)
    matching_cost = lp.solve_lp_matrix(path, matrix_1, matrix_2, length)
    lp.remove_lp_file(path)
    return matching_cost

# # # # # # # # # # # # # # # #
# LAST CLEANUP ON: 13.10.2021 #
# # # # # # # # # # # # # # # #
