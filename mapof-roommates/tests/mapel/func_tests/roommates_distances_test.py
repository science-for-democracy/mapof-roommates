import pytest
import numpy as np

import mapof.roommates as mapel

registered_roommates_distances_to_test = {
    'l1-mutual_attraction',
}


class TestRoommatesDistances:

    @pytest.mark.parametrize("distance_id", registered_roommates_distances_to_test)
    def test_roommates_distances(self, distance_id):
        num_agents = int(np.random.randint(5, 50) * 2)

        instance_1 = mapel.generate_roommates_instance(culture_id='ic',
                                                       num_agents=num_agents)

        instance_2 = mapel.generate_roommates_instance(culture_id='ic',
                                                       num_agents=num_agents)

        distance, mapping = mapel.compute_distance(instance_1, instance_2,
                                                   distance_id=distance_id)
        assert type(float(distance)) is float
