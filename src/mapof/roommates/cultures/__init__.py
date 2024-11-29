import logging

import mapof.roommates.cultures.euclidean as euclidean
import mapof.roommates.cultures.impartial as impartial
import mapof.roommates.cultures.mallows as mallows
import mapof.roommates.cultures.urn as urn
import numpy as np

from mapof.roommates.cultures.register import registered_roommates_cultures




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

    if culture_id in registered_roommates_cultures:
        return registered_roommates_cultures.get(culture_id)(num_agents=num_agents, **params)

    else:
        logging.warning(f'No such culture id: {culture_id}')
        return []
