#!/usr/bin/env python

import math
import os
import numpy as np
import time
from threading import Thread


from mapel.voting.objects.Election import Election

from time import sleep
import csv

from mapel.voting.metrics import main_distances as md

# from mapel.voting.matrices import get_positionwise_matrix


# MAIN FUNCTIONS
def get_distance(election_1, election_2, distance_name=''):
    """ Main function """
    inner_distance, main_distance = distance_name.split('-')

    metrics_without_params = {
        'discrete': md.compute_voter_subelection,
        'voter_subelection': md.compute_voter_subelection,
        'candidate_subelection': md.compute_candidate_subelection,
        'spearman': md.compute_spearman_distance,
    }

    metrics_with_inner_distance = {
        'positionwise': md.compute_positionwise_distance,
        'bordawise': md.compute_bordawise_distance,
        'pairwise': md.compute_pairwise_distance,
        'voterlikeness': md.compute_voterlikeness_distance,
        'agg_voterlikeness': md.compute_agg_voterlikeness_distance,
    }

    if main_distance in metrics_without_params:
        return metrics_without_params.get(main_distance)(election_1, election_2)

    elif main_distance in metrics_with_inner_distance:
        return metrics_with_inner_distance.get(main_distance)(election_1, election_2, inner_distance)


def single_thread(experiment, distances, times, thread_ids, t):
    """ Single thread for computing distance """

    for election_id_1, election_id_2 in thread_ids:
        start_time = time.time()
        distance = get_distance(experiment.elections[election_id_1],
                                experiment.elections[election_id_2],
                                distance_name=experiment.distance_name)

        distances[election_id_1][election_id_2] = distance
        distances[election_id_2][election_id_1] = distances[election_id_1][election_id_2]
        times[election_id_1][election_id_2] = time.time() - start_time
        times[election_id_2][election_id_1] = times[election_id_1][election_id_2]

    print("thread " + str(t) + " is ready :)")


# deprecated
# def compute_distances(experiment_id, distance_name='emd-positionwise', num_threads=1):
#     """ Compute distances between elections (using threads)"""
#
#     experiment = Experiment(experiment_id, distance_name=distance_name, elections='import', with_matrices=True)
#     distances = {}
#     for election_id in experiment.elections:
#         distances[election_id] = {}
#
#     threads = [{} for _ in range(num_threads)]
#
#     ids = []
#     for i, election_1 in enumerate(experiment.elections):
#         for j, election_2 in enumerate(experiment.elections):
#             if i < j:
#                 ids.append((election_1, election_2))
#
#     num_distances = len(ids)
#
#     for t in range(num_threads):
#         print('thread: ', t)
#         sleep(0.1)
#         start = int(t * num_distances / num_threads)
#         stop = int((t + 1) * num_distances / num_threads)
#         thread_ids = ids[start:stop]
#
#         threads[t] = Thread(target=single_thread, args=(experiment, distances, thread_ids, t))
#         threads[t].start()
#
#     for t in range(num_threads):
#         threads[t].join()
#
#     path = os.path.join(os.getcwd(), "experiments", experiment_id, "distances",
#                         str(distance_name) + ".csv")
#
#     with open(path, 'w', newline='') as csv_file:
#         writer = csv.writer(csv_file, delimiter=',')
#         writer.writerow(["election_id_1", "election_id_2", "distance"])
#
#         for i, election_1 in enumerate(experiment.elections):
#             for j, election_2 in enumerate(experiment.elections):
#                 if i < j:
#                     distance = str(distances[election_1][election_2])
#                     writer.writerow([election_1, election_2, distance])


# NEEDS UPDATE #

# deprecated
# def extend_distances(experiment_id, distance_name='emd-positionwise',
#                       num_threads=1, starting_from=0, ending_at=10000):
#     """ Compute distance using threads"""
#
#     if starting_from == 0 and ending_at == 10000:
#         experiment = obj..Experiment(experiment_id, distance_name=distance_name)
#         distances = {}
#         for election_id in experiment.elections:
#             distances[election_id] = {}
#     else:
#         experiment = Experiment_xd(experiment_id, distance_name=distance_name)
#         distances = {}
#         for election_id in experiment.elections:
#             distances[election_id] = {}
#         for i, election_id_1 in enumerate(experiment.elections):
#             for j, election_id_2 in enumerate(experiment.elections):
#                 if i < j:
#                     try:
#                         distances[election_id_1][election_id_2] = experiment.distances[election_id_1][election_id_2]
#                     except:
#                         pass
#
#     threads = [{} for _ in range(num_threads)]
#
#     ids = []
#     for i, election_1 in enumerate(experiment.elections):
#         for j, election_2 in enumerate(experiment.elections):
#             if i < j:
#                 ids.append((election_1, election_2))
#
#     num_distances = len(ids)
#
#     for t in range(num_threads):
#         print('thread: ', t)
#         sleep(0.1)
#         start = int(t * num_distances / num_threads)
#         stop = int((t + 1) * num_distances / num_threads)
#         thread_ids = ids[start:stop]
#
#         threads[t] = Thread(target=single_thread, args=(experiment, distances, thread_ids, t))
#         threads[t].start()
#
#     for t in range(num_threads):
#         threads[t].join()
#
#     path = os.path.join(os.getcwd(), "experiments", experiment_id, "distances",
#                         str(distance_name) + ".csv")
#
#     with open(path, 'w', newline='') as csv_file:
#         writer = csv.writer(csv_file, delimiter=',')
#         writer.writerow(["election_id_1", "election_id_2", "distance"])
#
#         for i, election_1 in enumerate(experiment.elections):
#             for j, election_2 in enumerate(experiment.elections):
#                 if i < j:
#                     distance = str(distances[election_1][election_2])
#                     writer.writerow([election_1, election_2, distance])

### NEW 13.07.2021 ###


def compute_distances_between_votes(dict_with_votes, distance_name='emd-positionwise'):
    elections = {}
    for election_id in dict_with_votes:
        elections[election_id] = Election("virtual", "virtual", votes=dict_with_votes[election_id])

    distances = {}
    for election_id in elections:
        distances[election_id] = {}

    for i, election_id_1 in enumerate(elections):
        for j, election_id_2 in enumerate(elections):
            if i < j:
                distance = get_distance(elections[election_id_1],
                                        elections[election_id_2],
                                        distance_name=distance_name)
                distances[election_id_1][election_id_2] = distance
                distances[election_id_2][election_id_1] = distances[election_id_1][election_id_2]
    return distances
