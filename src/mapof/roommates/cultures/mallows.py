import mapof.core.features.mallows as ml
from mapof.core.utils import *

from mapof.roommates.cultures._utils import convert


def generate_mallows_votes(*args, **kwargs):
    return ml.generate_mallows_votes(*args, **kwargs)


def generate_norm_mallows_votes(num_agents: int = None,
                                normphi: float = 0.5,
                                weight: float = 0,
                                **kwargs):
    phi = ml.phi_from_normphi(num_agents, normphi=normphi)

    votes = generate_mallows_votes(num_agents, num_agents, phi=phi, weight=weight)

    return convert(votes)


def mallows_vote(vote, phi):
    num_candidates = len(vote)
    raw_vote = generate_mallows_votes(1, num_candidates, phi=phi, weight=0)[0]
    new_vote = [0] * len(vote)
    for i in range(num_candidates):
        new_vote[raw_vote[i]] = vote[i]
    return new_vote


def mallows_votes(votes, phi):
    for i in range(len(votes)):
        votes[i] = mallows_vote(votes[i], phi)
    return votes


def generate_malasym_votes(
        num_agents: int = None,
        normphi=0.5,
        **_kwargs
):
    """ Mallows on top of Asymmetric instance """

    votes = [list(range(num_agents)) for _ in range(num_agents)]

    votes = [rotate(vote, shift) for shift, vote in enumerate(votes)]

    # if 'norm-phi' not in params:
    #     params['norm-phi'] = np.random.rand()

    phi = ml.phi_from_normphi(num_agents, normphi=normphi)
    votes = mallows_votes(votes, phi)

    return convert(votes)
