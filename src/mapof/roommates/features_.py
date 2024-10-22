from itertools import combinations

import numpy as np
from mapof.core.inner_distances import l2

import mapof.roommates.features.basic_features as basic

registered_roommates_features = {
    'summed_rank_minimal_matching': basic.summed_rank_minimal_matching,
    'summed_rank_maximal_matching': basic.summed_rank_maximal_matching,
    'min_num_bps_matching': basic.min_num_bps_matching,
    'num_of_bps_min_weight': basic.num_of_bps_maximumWeight,
    'avg_num_of_bps_for_rand_matching': basic.avg_num_of_bps_for_random_matching,
    'mutuality': basic.mutuality,
    'dist_from_id_1': basic.dist_from_id_1,
    'dist_from_id_2': basic.dist_from_id_2,
    'minimal_rank_maximizing_matching': basic.minimal_rank_maximizing_matching,
}


def get_local_feature(feature_id):
    if feature_id in registered_roommates_features:
        return registered_roommates_features.get(feature_id)
    return {
    }.get(feature_id)


def get_global_feature(feature_id):
    global_features = {'monotonicity': monotonicity,
            'distortion_from_all': distortion_from_all,
            'max_distortion_from_all': max_distortion_from_all,
            }

    if feature_id not in global_features.keys():
        raise ValueError(f"Feature '{feature_id}' does not exist!")

    return global_features.get(feature_id)

# TMP FUNCS
def monotonicity(experiment, instance) -> float:
    e0 = instance.instance_id
    c0 = np.array(experiment.coordinates[e0])
    distortion = 0
    for e1, e2 in combinations(experiment.instances, 2):
        if e1 != e0 and e2 != e0:
            original_d1 = experiment.distances[e0][e1]
            original_d2 = experiment.distances[e0][e2]
            original_proportion = original_d1 / original_d2
            embedded_d1 = np.linalg.norm(c0 - experiment.coordinates[e1])
            embedded_d2 = np.linalg.norm(c0 - experiment.coordinates[e2])
            embedded_proportion = embedded_d1 / embedded_d2
            _max = max(original_proportion, embedded_proportion)
            _min = min(original_proportion, embedded_proportion)
            distortion += _max / _min
    return distortion


def distortion_from_all(experiment, election):
    values = np.array([])
    one_side_values = np.array([])
    election_id_1 = election.instance_id

    for election_id_2 in experiment.instances:
        if election_id_1 != election_id_2:
            true_distance = experiment.distances[election_id_1][election_id_2]
            true_distance /= experiment.distances['MD']['MA']
            embedded_distance = l2(np.array(experiment.coordinates[election_id_1]),
                                   np.array(experiment.coordinates[election_id_2]))

            embedded_distance /= \
                l2(np.array(experiment.coordinates['MD']),
                   np.array(experiment.coordinates['MA']))
            one_side_ratio = embedded_distance / true_distance
            one_side_values = np.append(one_side_values, one_side_ratio)

            ratio = max(embedded_distance, true_distance) / min(embedded_distance, true_distance)

            values = np.append(values, ratio)
    print(np.max(values))
    return np.mean(values)


def max_distortion_from_all(experiment, election):
    values = np.array([])
    one_side_values = np.array([])
    election_id_1 = election.instance_id

    for election_id_2 in experiment.instances:
        if election_id_1 != election_id_2:
            true_distance = experiment.distances[election_id_1][election_id_2]
            true_distance /= experiment.distances['MD']['MA']
            embedded_distance = l2(np.array(experiment.coordinates[election_id_1]),
                                   np.array(experiment.coordinates[election_id_2]))

            embedded_distance /= \
                l2(np.array(experiment.coordinates['MD']),
                   np.array(experiment.coordinates['MA']))
            one_side_ratio = embedded_distance / true_distance
            one_side_values = np.append(one_side_values, one_side_ratio)

            ratio = max(embedded_distance, true_distance) / min(embedded_distance, true_distance)

            values = np.append(values, ratio)
    return np.max(values)
