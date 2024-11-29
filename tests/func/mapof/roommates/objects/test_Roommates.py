import numpy as np

import mapof.roommates as mapof


class TestMarriageElection:

    def test_marriage_instance(self):

        num_agents = np.random.randint(10, 50)
        culture_id = 'impartial'

        instance = mapof.generate_roommates_instance(culture_id=culture_id,
                                                     num_agents=num_agents)

        assert type(instance) is mapof.Roommates



