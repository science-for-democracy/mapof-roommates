import logging

from mapof.core.distances import extract_distance_id

from mapof.roommates.distances import main_distances as mrd
from mapof.roommates.objects.Roommates import Roommates

registered_roommates_distances = {
    'mutual_attraction': mrd.compute_retrospective_distance,
    'positionwise': mrd.compute_positionwise_distance,
}


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