import statistics
import sys
from random import shuffle

import gurobipy as gp
import networkx as nx
from gurobipy import GRB
from matching.games import StableRoommates

from mapof.roommates.features.register import register_roommates_feature

sys.setrecursionlimit(10000)
# warnings.filterwarnings("error")


def number_blocking_pairs(instance, matching: dict[int, int]) -> int:
    """
    Calculates the number of blocking pairs for a given matching in the given instance.
    A pair of agents is blocking when they prefer each other to their assigned partners
    in the given matching.

    Parameters
    ----------
    instance : Roommates
        Roommates instance.
    matching : dict[int, int]
        The current matching of agents, represented as a dictionary where keys are agents and
        values are their assigned partners.

    Returns
    -------
        int
            The number of blocking pairs in the given matching.
    """
    bps = 0
    num_agents = len(instance)
    for i in range(num_agents):
        for j in range(i + 1, num_agents):
            if i != j:
                partner_i = matching[i]
                partneri_index = instance[i].index(partner_i)
                partner_j = matching[j]
                partnerj_index = instance[j].index(partner_j)
                if instance[i].index(j) < partneri_index:
                    if instance[j].index(i) < partnerj_index:
                        bps += 1
    return bps


def compute_stable_SR(instance) -> dict[int, int] or str:
    """
    Computes a stable matching in the given instance using the matchings.games library.

    Uses Irving's algorithm to find a stable matching, if one exists.
    Returns 'None' if no stable matching is found.

    Parameters
    ----------
    instance : Roommates
        Roommates instance.

    Returns
    -------
        dict[int, int] or str
            A dictionary representing the stable matching if one exists, mapping each agent to their
            matched partner. If no stable matching exists, returns 'None'.
    """
    dict_instance = {}
    num_agents = len(instance)
    for i in range(num_agents):
        dict_instance[i] = instance[i]
    game = StableRoommates.create_from_dictionary(dict_instance)
    try:
        matching = game.solve()
        usable_matching = {}
        for m in matching:
            usable_matching[m.name] = matching[m].name
        return usable_matching
    except Exception:
        return 'None'


def rank_matching(
        instance,
        maximize: bool,
        summed: bool
) -> tuple[int, dict[int, int]]:
    """
    Computes different types of stable matchings based on the rank that agents assign to their partner in the matching.
    The lower the rank, the more preferred is the agent by their partner.
    Should only be called on instances that admit a stable matching.


    This function formulates and solves a Mixed Integer Program (MIP) to find one of three types of stable matchings:
    1. Stable matching minimizing the summed rank that agents assign to their partner in the matching.
    2. Stable matching maximizing the summed rank that agents assign to their partner in the matching. This can be understood as the worst possible matching.
    3. Stable matching minimizing the maximum rank an agent assigns to their partner in the matching (optimize the worst-off agent).

    Matching 1 can be computed by setting summed=True, maximize=False
    Matching 2 can be computed by setting summed=True, maximize=True
    Matching 3 can be computed by setting summed=False, maximize=False

    Parameters
    ----------
    instance : Roommates
        Roommates instance.
    maximize : bool
        If `True`, search for the maximizing the selected criterion;
        if `False`, search for the worst.
    summed : bool
        If `True`, optimizes the summed rank of agents for their partners; if `False`, optimizes
        the minimal rank of an agent for their partner.

    Returns
    -------
    tuple[int, dict[int, int]]
        A tuple containing the objective value of the optimized matching and the optimal matching as a dictionary mapping
        each agent to their assigned partner.
    """
    num_agents = len(instance)
    m = gp.Model("mip1")
    m.setParam('OutputFlag', False)
    m.setParam('Threads', 10)
    x = m.addVars(num_agents, num_agents, lb=0, ub=1, vtype=GRB.BINARY)
    opt = m.addVar(vtype=GRB.INTEGER, lb=0, ub=num_agents * num_agents)
    for i in range(num_agents):
        m.addConstr(x[i, i] == 0)
    for i in range(num_agents):
        for j in range(num_agents):
            m.addConstr(x[i, j] == x[j, i])
    for i in range(num_agents):
        m.addConstr(gp.quicksum(x[i, j] for j in range(num_agents)) == 1)
    for i in range(num_agents):
        for j in range(i + 1, num_agents):
            better_pairs = []
            for t in range(0, instance[i].index(j) + 1):
                better_pairs.append([i, instance[i][t]])
            for t in range(0, instance[j].index(i) + 1):
                better_pairs.append([j, instance[j][t]])
            m.addConstr(gp.quicksum(x[a[0], a[1]] for a in better_pairs) >= 1)
    if summed:
        # print(instance[0])
        m.addConstr(gp.quicksum(instance[i].index(j) * x[i, j] for i in range(num_agents) for j in
                                [x for x in range(num_agents) if x != i]) == opt)
        if maximize:
            m.setObjective(opt, GRB.MAXIMIZE)
        else:
            m.setObjective(opt, GRB.MINIMIZE)
    else:
        for i in range(num_agents):
            m.addConstr(gp.quicksum(instance[j].index(i) * x[i, j] for j in
                                    [x for x in range(num_agents) if x != i]) <= opt)
        m.setObjective(opt, GRB.MINIMIZE)
    m.optimize()
    if m.status != GRB.Status.OPTIMAL:
        raise RuntimeError("Could not optimize model during roommates feature "
                           f"computation. Gurobi status {m.status} returned.")
    matching = {}
    for i in range(num_agents):
        for j in range(num_agents):
            if abs(x[i, j].X - 1) < 0.05:
                matching[i] = j
                matching[j] = i
    return int(m.objVal), matching


@register_roommates_feature('min_num_bps_matching')
def min_num_bps_matching(instance) -> int:
    """
    Computes a matching with the minimum number of blocking pairs for a given instance.

    Uses a Mixed Integer Program (MIP) to find a matching that minimizes the number of blocking pairs.
    This matching can be understood as being "as stable as possible".
    The function is particularly relevant for instances that do not admit a stable matching.

    Parameters
    ----------
    instance : Roommates
        Roommates instance.

    Returns
    -------
        int
            The minimum number of blocking pairs achievable in a matching.
    """
    num_agents = len(instance.votes)
    m = gp.Model("mip1")
    m.setParam('OutputFlag', False)
    x = m.addVars(num_agents, num_agents, lb=0, ub=1, vtype=GRB.BINARY)
    y = m.addVars(num_agents, num_agents, lb=0, ub=1, vtype=GRB.BINARY)
    opt = m.addVar(vtype=GRB.INTEGER, lb=0, ub=num_agents * num_agents)
    m.addConstr(gp.quicksum(y[i, j] for i in range(num_agents) for j in range(num_agents)) <= opt)
    for i in range(num_agents):
        m.addConstr(x[i, i] == 0)
    for i in range(num_agents):
        for j in range(num_agents):
            m.addConstr(x[i, j] == x[j, i])
    for i in range(num_agents):
        m.addConstr(gp.quicksum(x[i, j] for j in range(num_agents)) <= 1)
    for i in range(num_agents):
        for j in range(i + 1, num_agents):
            better_pairs = []
            for t in range(0, instance.votes[i].index(j) + 1):
                better_pairs.append([i, instance.votes[i][t]])
            for t in range(0, instance.votes[j].index(i) + 1):
                better_pairs.append([j, instance.votes[j][t]])
            m.addConstr(gp.quicksum(x[a[0], a[1]] for a in better_pairs) >= 1 - y[i, j])

    m.setObjective(opt, GRB.MINIMIZE)
    m.optimize()
    matching = {}
    for i in range(num_agents):
        for j in range(num_agents):
            if abs(x[i, j].X - 1) < 0.05:
                matching[i] = j
                matching[j] = i
    # return int(m.objVal), matching
    return int(m.objVal)


@register_roommates_feature('summed_rank_maximal_matching')
def summed_rank_maximal_matching(instance) -> int:
    """
    Computes a stable matching with the maximal summed rank agents assign to their partner.

    Calls the `rank_matching` function with parameters set to maximize the summed ranks of agents for their partners.
    This can be interpreted as the worst stable matching from a utilitarian perspective.
    Only call on instances admitting a stable matching.

    Parameters
    ----------
    instance : Roommates
        Roommates instance.

    Returns
    -------
        int
            The summed rank agents have for their partner in a stable matching maximizing this value.
    """
    val, matching = rank_matching(instance.votes, True, True)
    if number_blocking_pairs(instance.votes, matching) > 0:
        print('ERROR IN summed_rank_maximal_matching')
        exit(0)
    return val


@register_roommates_feature('summed_rank_minimal_matching')
def summed_rank_minimal_matching(instance) -> int:
    """
    Computes a stable matching with the minimum summed rank agents assign to their partner.

    Calls the `rank_matching` function with parameters set to minimize the summed ranks of agents for their partners.
    This can be interpreted as the best stable matching from a utilitarian perspective.
    Only call on instances admitting a stable matching.

    Parameters
    ----------
        instance : Roommates
            Roommates instance.

    Returns
    -------
        int
            The summed rank agents have for their partner in a stable matching minimizing this value.
    """
    val, matching = rank_matching(instance.votes, False, True)
    if number_blocking_pairs(instance.votes, matching) > 0:
        print('ERROR IN summed_rank_minimal_matching')
        exit(0)
    return val


@register_roommates_feature('minimal_rank_maximizing_matching')
def minimal_rank_maximizing_matching(instance) -> int:
    """
    Computes a stable matching minimizing the maximum rank an agent assigns to their partner in the matching

    Calls the `rank_matching` function with parameters set to minimize the maximal rank.
    This can be interpreted as the best stable matching from an egalitarian perspective.
    Only call on instances admitting a stable matching.

    Parameters
    ----------
        instance : Roommates
            Roommates instance.

    Returns
    -------
    int
        The maximum rank an agent has for their partner in a stable matching minimzing this value.
    """
    val, matching = rank_matching(instance.votes, True, False)
    if number_blocking_pairs(instance.votes, matching) > 0:
        print('ERROR IN minimal_rank_maximizing_matching')
        exit(0)
    return val


@register_roommates_feature('avg_num_of_bps_for_rand_matching')
def avg_num_of_bps_for_random_matching(instance, iterations: int = 100) -> tuple[
    float, float]:
    """
    Approximates the average number of blocking pairs for a random perfect matching.

    Generates iterations-many random matchings, calculates the number of
    blocking pairs for each matching, and returns the mean and standard deviation.

    Parameters
    ----------
        instance : Roommates
            Roommates instance.
    iterations : int, default: 100
        The number of generated random matchings for calculating blocking pairs.

    Returns
    -------
    tuple[float, float]
        A tuple with the mean and standard deviation of blocking pairs across the random matchings.
    """
    bps = []
    num_agents = len(instance.votes)
    for _ in range(iterations):
        # create random matching
        agents = list(range(num_agents))
        shuffle(agents)
        matching = [agents[i:i + 2] for i in range(0, num_agents, 2)]
        matching_dict = {}
        for m in matching:
            matching_dict[m[0]] = m[1]
            matching_dict[m[1]] = m[0]
        bps.append(number_blocking_pairs(instance.votes, matching_dict))
    return statistics.mean(bps), statistics.stdev(bps)


@register_roommates_feature('num_of_bps_min_weight')
def num_of_bps_maximumWeight(instance) -> int:
    """
    Computes the number of blocking pairs for a (not necessarily stable) matching minimzing the summed rank agents have for their partner.

    Constructs a weighted graph based on agents' preference lists, where the weight of an edge is antiproportional
    to the summed rank at which the two agents rank each other.
    Computes the matching maximizing the edge values.
    This corresponds to the matching that minimizes the summed rank agents have for their partner (aka. the total satisfaction).
    This can be interpreted as a heuristic for finding a stable matching.

    Parameters
    ----------
        instance : Roommates
            Roommates instance.

    Returns
    -------
    int
        The number of blocking pairs in the ``maximum-weight'' matching.
    """
    num_agents = len(instance.votes)
    G = nx.Graph()
    for i in range(num_agents):
        for j in range(i + 1, num_agents):
            G.add_edge(i, j,
                       weight=2 * (num_agents - 1) - instance.votes[i].index(j) - instance.votes[
                           j].index(i))
            # G.add_edge(i, j, weight=instance[i].index(j) + instance[j].index(i))
    matching = nx.max_weight_matching(G, maxcardinality=True)
    matching_dict = {}
    for p in matching:
        matching_dict[p[0]] = p[1]
        matching_dict[p[1]] = p[0]
    return number_blocking_pairs(instance.votes, matching_dict)


@register_roommates_feature('mutuality')
def mutuality(instance) -> int:
    """
    Computes the mutuality score of a stable roommates instance.

    The mutuality score captures how different agent pairs rank each other.
    A low mutuality score indicates that if agent a likes agent b, then b likely likes a.

    Parameters
    ----------
        instance : Roommates
            Roommates instance.

    Returns
    -------
    int
        The mutuality score of the instance.
    """
    vectors = instance.get_retrospective_vectors()
    score = 0
    for vector in vectors:
        for i, v in enumerate(vector):
            score += abs(v - i)
    return score
