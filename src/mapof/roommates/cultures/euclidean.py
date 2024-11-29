import logging
import math

import numpy as np
from prefsampling.core.euclidean import EuclideanSpace
from prefsampling.core.euclidean import euclidean_space_to_sampler

from mapof.roommates.cultures.mallows import mallows_votes
from mapof.roommates.cultures.utils import convert


def generate_attributes_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space: str = None,
        **_kwargs) -> list[list[int]]:
    """
    Generate votes based on attributes model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        num_dimensions : int
            Dimension of the space.
        space : str
            Distribution of the agents.
        _kwargs

    Returns
    -------
        list[list[int]]
            Votes
    """
    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents_skills = np.array(sampler(**sampler_params))
    agents_weights = np.array(sampler(**sampler_params))

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)
    ones = np.ones([num_dimensions], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            if num_dimensions == 1:
                distances[v][c] = abs(1. - agents_skills[c]) * agents_weights[v]
            else:
                distances[v][c] = _weighted_l1(ones, agents_skills[c], agents_weights[v])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_euclidean_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space: str = None,
        **_kwargs
) -> list[list[int]]:
    """
    Generate votes based on Euclidean model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        num_dimensions : int
            Dimension of the space.
        space : str
            Distribution of the agents.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            Votes
    """

    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents = np.array(sampler(**sampler_params))

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    return convert(votes)


def generate_reverse_euclidean_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space: str = None,
        proportion: float = 0.5,
        **_kwargs
) -> list[list[int]]:
    """
    Generate votes based on expectation model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        num_dimensions : int
            Dimension of the space.
        space : str
            Distribution of the agents.
        proportion : float
            Proportion of the agents that will have the reverse order.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            Votes
    """

    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents = np.array(sampler(**sampler_params))

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


def generate_expectation_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space: str = None,
        std: float = 0.1,
        **_kwargs
) -> list[list[int]]:
    """
    Generate votes based on reverse Euclidean model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        num_dimensions : int
            Dimension of the space.
        space : str
            Distribution of the agents.
        std : float
            Standard deviation of the agents.
        _kwargs

    Returns
    -------
        list[list[int]]
            Votes
    """

    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents_reality = np.array(sampler(**sampler_params))
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


def generate_fame_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space: str = None,
        radius: float = 0.1,
        **_kwargs
) -> list[list[int]]:
    """
    Generate votes based on fame model (also known as radius model).

    Parameters
    ----------
        num_agents : int
            Number of agents.
        num_dimensions : int
            Dimension of the space.
        space : str
            Distribution of the agents.
        radius : float
            Radius of the agents.
        _kwargs

    Returns
    -------
        list[list[int]]
            Votes
    """

    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents = np.array(sampler(**sampler_params))
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


def generate_mallows_euclidean_votes(
        num_agents: int = None,
        num_dimensions: int = 2,
        space=None,
        phi=0.5,
        **_kwargs
) -> list[list[int]]:

    if space is None:
        space = EuclideanSpace.UNIFORM_CUBE

    sampler, sampler_params = euclidean_space_to_sampler(space, num_dimensions)
    sampler_params['num_points'] = num_agents

    agents = np.array(sampler(**sampler_params))

    votes = np.zeros([num_agents, num_agents], dtype=int)
    distances = np.zeros([num_agents, num_agents], dtype=float)

    for v in range(num_agents):
        for c in range(num_agents):
            votes[v][c] = c
            distances[v][c] = np.linalg.norm(agents[v] - agents[c])
        votes[v] = [x for _, x in sorted(zip(distances[v], votes[v]))]

    votes = mallows_votes(votes, phi)

    return convert(votes)


def _weighted_l1(a1, a2, w):
    total = 0
    for i in range(len(a1)):
        total += abs(a1[i] - a2[i]) * w[i]
    return total
