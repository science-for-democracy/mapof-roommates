import pytest
import numpy as np

import mapof.roommates as roommates

registered_roommates_features_to_test = {
    'summed_rank_minimal_matching',
    'summed_rank_maximal_matching',
    'minimal_rank_maximizing_matching',
    'min_num_bps_matching',
    'num_of_bps_min_weight',
    'avg_num_of_bps_for_rand_matching',
    'mutuality',
    'dist_from_id_1',
    'dist_from_id_2'
}


class TestFeatures:

  @pytest.mark.parametrize("feature_id", registered_roommates_features_to_test)
  def test_roommates_features(self, feature_id):

    num_agents = 20

    instance = roommates.generate_roommates_instance(alpha=1,
                                                     culture_id='ic',
                                                     num_agents=num_agents,
                                                     is_imported=True)

    # To avoid that the test being flaky, we remove non-deteminism
    # To make test deterministic, we force specific instance votes
    # We cannot do it as an argument 'votes' to the above method
    # because this method anyway overwrites this parameter value
    # later
    instance_votes = [
        [18, 6, 17, 11, 10, 8, 15, 9, 5, 14, 2, 1, 3, 13, 4, 12, 19, 16,
         7], [13, 11, 9, 18, 0, 19, 8, 2, 12, 16, 17, 7, 14, 3, 4, 6, 15, 10, 5],
        [16, 8, 9, 19, 18, 4, 6, 12, 13, 10, 15, 17, 3, 5, 0, 7, 14, 11,
         1], [1, 12, 15, 13, 10, 6, 17, 7, 5, 2, 18, 16, 0, 4, 11, 9, 8, 19,
              14], [18, 16, 13, 3, 7, 8, 10, 15, 6, 12, 19, 0, 9, 2, 11, 1, 17, 5, 14],
        [8, 17, 16, 18, 2, 10, 0, 3, 15, 4, 14, 6, 9, 13, 19, 7, 12, 1,
         11], [17, 11, 0, 8, 19, 10, 1, 2, 18, 13, 3, 14, 9, 16, 15, 5, 12, 7,
               4], [8, 15, 5, 18, 11, 4, 2, 3, 0, 16, 10, 12, 1, 17, 6, 9, 13, 19, 14],
        [6, 10, 15, 3, 18, 1, 12, 11, 4, 7, 5, 2, 13, 14, 19, 0, 16, 9,
         17], [16, 4, 15, 5, 8, 10, 1, 0, 12, 2, 17, 11, 3, 6, 13, 19, 18, 7,
               14], [14, 12, 9, 19, 3, 15, 17, 18, 11, 4, 8, 0, 16, 5, 6, 13, 2, 1, 7],
        [16, 13, 18, 7, 10, 0, 14, 8, 1, 2, 15, 5, 9, 3, 17, 12, 4, 6,
         19], [6, 13, 5, 14, 16, 11, 3, 19, 15, 2, 7, 9, 4, 0, 10, 8, 1, 17,
               18], [17, 3, 1, 11, 6, 7, 8, 18, 2, 14, 10, 5, 9, 0, 19, 4, 15, 12, 16],
        [3, 6, 1, 16, 17, 2, 9, 11, 7, 19, 8, 10, 12, 4, 13, 18, 0, 5,
         15], [8, 11, 3, 0, 10, 5, 4, 13, 17, 1, 19, 12, 9, 14, 7, 18, 6, 16,
               2], [3, 10, 12, 5, 17, 4, 2, 14, 18, 19, 8, 6, 11, 13, 7, 15, 9, 1, 0],
        [13, 7, 15, 6, 4, 2, 9, 0, 8, 18, 1, 19, 10, 11, 12, 3, 14, 5,
         16], [14, 5, 11, 19, 17, 15, 10, 13, 1, 6, 9, 3, 0, 12, 8, 16, 7, 4,
               2], [6, 9, 16, 0, 12, 1, 8, 10, 14, 3, 7, 2, 4, 11, 5, 13, 18, 17, 15]
    ]
    instance.votes = instance_votes


    instance.compute_feature(feature_id)
