from mapof.core.matchings import *
from mapof.roommates.objects.Roommates import Roommates


# MAIN DISTANCES
def compute_retrospective_distance(instance_1, instance_2, inner_distance):
    cost_table = get_matching_cost_retrospective(instance_1, instance_2, inner_distance)
    return solve_matching_vectors(cost_table)


def compute_positionwise_distance(instance_1, instance_2, inner_distance):
    cost_table = get_matching_cost_positionwise(instance_1, instance_2, inner_distance)
    return solve_matching_vectors(cost_table)


def get_matching_cost_retrospective(instance_1: Roommates, instance_2: Roommates,
                                    inner_distance: callable) -> list[list]:
    """ Return: Cost table """
    vectors_1 = instance_1.get_retrospective_vectors()
    vectors_2 = instance_2.get_retrospective_vectors()
    size = instance_1.num_agents
    return [[inner_distance(vectors_1[i], vectors_2[j]) for i in range(size)] for j in range(size)]


def get_matching_cost_positionwise(instance_1: Roommates, instance_2: Roommates,
                                   inner_distance: callable) -> list[list]:
    """ Return: Cost table """
    vectors_1 = instance_1.get_positionwise_vectors()
    vectors_2 = instance_2.get_positionwise_vectors()
    size = instance_1.num_agents
    return [[inner_distance(vectors_1[i], vectors_2[j]) for i in range(size)] for j in range(size)]
