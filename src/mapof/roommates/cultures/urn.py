import numpy as np
from mapof.roommates.cultures._utils import convert


def generate_roommates_urn_votes(
        num_agents: int = None,
        alpha: int = 0.1,
        **kwargs
) -> list[list[int]]:
    """
    Generates a list of votes based on the urn model.

    Parameters
    ----------
        num_agents : int
            Number of agents.
        alpha : float, optional
            Parameter for the urn model. Default is 0.1.
        **kwargs
            Additional parameters for customization.

    Returns
    -------
        list[list[int]]
            A list of votes.
    """
    votes = np.zeros([num_agents, num_agents], dtype=int)
    urn_size = 1.
    for j in range(num_agents):
        rho = np.random.uniform(0, urn_size)
        if rho <= 1.:
            votes[j] = np.random.permutation(num_agents)
        else:
            votes[j] = votes[np.random.randint(0, j)]
        urn_size += alpha

    return convert(votes)