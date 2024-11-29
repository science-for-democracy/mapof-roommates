import logging

import numpy as np
from mapof.core.utils import *

from mapof.roommates.cultures.utils import convert

from mapof.roommates.cultures.register import register_roommates_culture

from prefsampling.ordinal import (
    impartial,
    identity,
)


@register_roommates_culture('impartial')
def generate_impartial_votes(num_agents: int = None, **_kwargs) -> list[list[int]]:
    """
    Generates a list of votes based on the impartial culture model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    votes = impartial(num_agents, num_agents)
    return convert(votes)


@register_roommates_culture('group_impartial')
def generate_group_impartial_votes(
        num_agents: int = None,
        proportion=0.5,
        **_kwargs
) -> list[list[int]]:
    """
    Generates a list of votes based on the group impartial culture model with two groups.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        proportion : float, optional
            Proportion of agents in the first group. Default is 0.5.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    size_1 = int(proportion * num_agents)
    size_2 = int(num_agents - size_1)
    votes_1 = [list(np.random.permutation(size_1)) +
               list(np.random.permutation([j for j in range(size_1, num_agents)]))
               for _ in range(size_1)]
    votes_2 = [list(np.random.permutation([j for j in range(size_1, num_agents)])) +
               list(np.random.permutation(size_1))
               for _ in range(size_2)]
    votes = votes_1 + votes_2
    return convert(votes)


@register_roommates_culture('identity')
def generate_identity_votes(num_agents: int = None, **_kwargs) -> list[list[int]]:
    """
    Generates a list of votes based on the identity model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    votes = identity(num_agents, num_agents)
    return convert(votes)


@register_roommates_culture('asymmetric')
def generate_asymmetric_votes(num_agents: int = None, **_kwargs) -> list[list[int]]:
    """
    Generates a list of votes based on the Asymmetric model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    votes = [list(range(num_agents)) for _ in range(num_agents)]
    votes = [rotate(vote, shift) for shift, vote in enumerate(votes)]
    return convert(votes)


@register_roommates_culture('symmetric')
def generate_symmetric_votes(num_agents: int = None, **_kwargs) -> list[list[int]]:
    """
    Generates a matrix of votes based on the Symmetric model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        **_kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    num_rounds = num_agents - 1

    def next(agents):
        first = agents[0]
        last = agents[-1]
        middle = agents[1:-1]
        new_agents = [first, last]
        new_agents.extend(middle)
        return new_agents

    agents = [i for i in range(num_agents)]
    rounds = []

    for _ in range(num_rounds):
        pairs = []
        for i in range(num_agents // 2):
            agent_1 = agents[i]
            agent_2 = agents[num_agents - 1 - i]
            pairs.append([agent_1, agent_2])
        rounds.append(pairs)
        agents = next(agents)

    votes = np.zeros([num_agents, num_agents - 1], dtype=int)

    for pos, partition in enumerate(rounds):
        for x, y in partition:
            votes[x][pos] = y
            votes[y][pos] = x

    return votes.tolist()


@register_roommates_culture('chaos')
def generate_chaos_votes(num_agents: int = None, **kwargs) -> list[list[int]]:
    """
    Generates a matrix of votes based on the Chaos model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        **kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    if num_agents-1 % 3 == 0:
        logging.warning("Incorrect realization of Chaos instance")

    num_rooms = num_agents // 2
    matrix = np.zeros([num_agents, num_agents - 1], dtype=int)

    matrix[0] = [i for i in range(num_agents - 1)]

    for i in range(1, num_agents):
        for j in range(num_rooms):
            matrix[i][2 * j] = (i + j - 1) % (num_agents - 1)
            if j < num_rooms - 1:
                matrix[i][2 * j + 1] = (num_rooms + i + j - 1) % (num_agents - 1)

    votes = np.zeros([num_agents, num_agents - 1], dtype=int)

    for k1 in range(num_agents):
        for k2 in range(num_agents - 1):
            for i in range(num_agents):
                if k1 != i and matrix[i][matrix[k1][k2]] == matrix[k1][k2]:
                    votes[k1][k2] = i

    return votes.tolist()
