import logging

from mapof.core.distances import extract_distance_id

from mapof.roommates.distances import fast_distances as mrd
from mapof.roommates.objects.Roommates import Roommates
from mapof.roommates.distances.register import registered_roommates_distances



def get_distance(election_1: Roommates,
                 election_2: Roommates,
                 distance_id: str = None
                 ) -> float or (float, list):
    """ Return: distance between ordinal elections, (if applicable) optimal matching """

    inner_distance, main_distance = extract_distance_id(distance_id)

    if main_distance in registered_roommates_distances:
        return registered_roommates_distances.get(main_distance)(election_1,
                                                                 election_2,
                                                                 inner_distance)
    else:
        logging.warning('No such metric!')