import logging

import mapof.roommates.cultures.euclidean as euclidean
import mapof.roommates.cultures.impartial as impartial
import mapof.roommates.cultures.mallows as mallows
import mapof.roommates.cultures.urn as urn
import numpy as np

registered_roommates_culture = {
    'impartial': impartial.generate_impartial_votes,
    'identity': impartial.generate_identity_votes, # deprecated names
    'chaos': impartial.generate_chaos_votes,
    'symmetric': impartial.generate_symmetric_votes,
    'asymmetric': impartial.generate_asymmetric_votes,
    'urn': urn.generate_urn_votes,
    'fame': euclidean.generate_fame_votes,
    'expectation': euclidean.generate_expectation_votes,
    'attributes': euclidean.generate_attributes_votes,
    'euclidean': euclidean.generate_euclidean_votes,
    'reverse_euclidean': euclidean.generate_reverse_euclidean_votes,
    'group_ic': impartial.generate_group_ic_votes,
    'norm-mallows': mallows.generate_norm_mallows_votes,
    'mallows_euclidean': euclidean.generate_mallows_euclidean_votes,
    'malasym': mallows.generate_malasym_votes,

    'ic': impartial.generate_impartial_votes, # deprecated names
    'id': impartial.generate_identity_votes, # deprecated names
}


def generate_votes(culture_id: str = None, num_agents: int = None,
                   params: dict = None) -> list | np.ndarray:
    """

    Parameters
    ----------

    Returns
    -------
         list[list[int]]
            A list where each sublist represents an agent's preference list.
            The ith list represents the preferences of the ith agents.


    """

    if culture_id in registered_roommates_culture:
        return registered_roommates_culture.get(culture_id)(num_agents=num_agents, **params)

    else:
        logging.warning(f'No such culture id: {culture_id}')
        return []
