import numpy as np
import math
from numpy import linalg
from mapof.roommates.cultures._utils import convert
from mapof.roommates.cultures.mallows import mallows_votes

def get_range(params):
    if params['p_dist'] == 'beta':
        return np.random.beta(params['a'], params['b'])
    elif params['p_dist'] == 'uniform':
        return np.random.uniform(low=params['a'], high=params['b'])


def weighted_l1(a1, a2, w):
    total = 0
    for i in range(len(a1)):
        total += abs(a1[i] - a2[i]) * w[i]
    return total


def generate_roommates_attributes_votes(num_agents: int = None,
                                        dim: int = 2,
                                        space='uniform',
                                        **kwargs):
    name = f'{dim}d_{space}'

    agents_skills = np.array([get_rand(name) for _ in range(num_agents)])
    agents_weights = np.array([get_rand(name) for _ in range(num_agents)])

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)
    ones = np.ones([dim], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            if dim == 1:
                distances[v][c] = abs(1. - agents_skills[c]) * agents_weights[v]
            else:
                distances[v][c] = weighted_l1(ones, agents_skills[c], agents_weights[v])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_roommates_euclidean_votes(num_agents: int = None,
                                       dim: int = 2,
                                       space='uniform',
                                       **kwargs):
    name = f'{dim}d_{space}'

    agents = np.array([get_rand(name, i=i, num_agents=num_agents) for i in range(num_agents)])

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_roommates_reverse_euclidean_votes(num_agents: int = None,
                                               dim: int = 2,
                                               space='uniform',
                                               proportion=0.5,
                                               **kwargs):
    name = f'{dim}d_{space}'

    agents = np.array([get_rand(name, i=i, num_agents=num_agents) for i in range(num_agents)])

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    p = proportion

    for i in range(int(num_agents * (1. - p))):
        tmp = list(votes[i])
        tmp.reverse()
        votes[i] = tmp

    return convert(votes)


def generate_roommates_expectation_votes(num_agents: int = None,
                                         dim: int = 2,
                                         space='uniform',
                                         std=0.1,
                                         **kwargs):
    name = f'{dim}d_{space}'

    agents_reality = np.array([get_rand(name) for _ in range(num_agents)])
    agents_wishes = np.zeros([num_agents, 2])

    for v in range(num_agents):
        # while agents_wishes[v][0] <= 0 or agents_wishes[v][0] >= 1:
        agents_wishes[v][0] = np.random.normal(agents_reality[v][0], std)
        # while agents_wishes[v][1] <= 0 or agents_wishes[v][1] >= 1:
        agents_wishes[v][1] = np.random.normal(agents_reality[v][1], std)

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents_reality[c] - agents_wishes[v])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_roommates_fame_votes(num_agents: int = None,
                                  dim: int = 2,
                                  space='uniform',
                                  radius=0.1,
                                  **kwargs):
    # Also known as radius model

    name = f'{dim}d_{space}'

    agents = np.array([get_rand(name) for _ in range(num_agents)])
    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)
    rays = np.array([np.random.uniform(0, radius) for _ in range(num_agents)])

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
            distances[v][c] = distances[v][c] - rays[c]
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_roommates_mallows_euclidean_votes(num_agents: int = None,
                                               dim: int = 2,
                                               space='uniform',
                                               phi=0.5,
                                               **kwargs):
    name = f'{dim}d_{space}'

    agents = np.array([get_rand(name, i=i, num_agents=num_agents) for i in range(num_agents)])

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    votes = mallows_votes(votes, phi)

    return convert(votes)


####################################################
### UPDATE THIS TO MATCH THE RESAMPLING APPROACH ###
def get_rand(model: str, i: int = 0, num_agents: int = 0) -> list:
    """ generate random values"""

    point = [0]
    if model in {"1d_uniform", "1d_interval"}:
        return np.random.rand()
    elif model in {'1d_asymmetric'}:
        if np.random.rand() < 0.3:
            return np.random.normal(loc=0.25, scale=0.15, size=1)
        else:
            return np.random.normal(loc=0.75, scale=0.15, size=1)
    elif model in {"1d_gaussian"}:
        point = np.random.normal(0.5, 0.15)
        while point > 1 or point < 0:
            point = np.random.normal(0.5, 0.15)
    # elif model == "1d_one_sided_triangle":
    #     point = np.random.uniform(0, 1) ** 0.5
    # elif model == "1d_full_triangle":
    #     point = np.random.choice(
    #         [np.random.uniform(0, 1) ** 0.5, 2 - np.random.uniform(0, 1) ** 0.5])
    # elif model == "1d_two_party":
    #     point = np.random.choice([np.random.uniform(0, 1), np.random.uniform(2, 3)])
    elif model in {"2d_disc"}:
        phi = 2.0 * 180.0 * np.random.random()
        radius = math.sqrt(np.random.random()) * 0.5
        point = [0.5 + radius * math.cos(phi), 0.5 + radius * math.sin(phi)]
    elif model in {"2d_square", "2d_uniform"}:
        point = [np.random.random(), np.random.random()]
    # elif model in {'2d_asymmetric'}:
    #     if np.random.rand() < 0.3:
    #         return np.random.normal(loc=0.25, scale=0.15, size=2)
    #     else:
    #         return np.random.normal(loc=0.75, scale=0.15, size=2)
    # elif model == "2d_sphere":
    #     alpha = 2 * math.pi * np.random.random()
    #     x = 1. * math.cos(alpha)
    #     y = 1. * math.sin(alpha)
    #     point = [x, y]
    # elif model in ["2d_gaussian"]:
    #     point = [np.random.normal(0.5, 0.15), np.random.normal(0.5, 0.15)]
    #     while np.linalg.norm(point - np.array([0.5, 0.5])) > 0.5:
    #         point = [np.random.normal(0.5, 0.15), np.random.normal(0.5, 0.15)]
    # elif model in ["3d_cube", "3d_uniform"]:
    #     point = [np.random.random(), np.random.random(), np.random.random()]
    # elif model in ["5d_uniform"]:
    #     dim = 5
    #     point = [np.random.random() for _ in range(dim)]
    # elif model in ["10d_uniform"]:
    #     dim = 10
    #     point = [np.random.random() for _ in range(dim)]
    # elif model in {'3d_asymmetric'}:
    #     if np.random.rand() < 0.3:
    #         return np.random.normal(loc=0.25, scale=0.15, size=3)
    #     else:
    #         return np.random.normal(loc=0.75, scale=0.15, size=3)
    # elif model in ['3d_gaussian']:
    #     point = [np.random.normal(0.5, 0.15),
    #              np.random.normal(0.5, 0.15),
    #              np.random.normal(0.5, 0.15)]
    #     while np.linalg.norm(point - np.array([0.5, 0.5, 0.5])) > 0.5:
    #         point = [np.random.normal(0.5, 0.15),
    #                  np.random.normal(0.5, 0.15),
    #                  np.random.normal(0.5, 0.15)]
    # elif model == "4d_cube":
    #     dim = 4
    #     point = [np.random.random() for _ in range(dim)]
    # elif model == "5d_cube":
    #     dim = 5
    #     point = [np.random.random() for _ in range(dim)]
    else:
        print('unknown culture_id', model)
        point = [0, 0]
    return point

