#!/usr/bin/env python3

import mapel.elections as mapel

if __name__ == "__main__":

    experiment_id = 'mallows'
    distance_id = 'emd-positionwise'
    instance_type = 'ordinal'

    experiment = mapel.prepare_experiment(experiment_id=experiment_id,
                                          distance_id=distance_id,
                                          instance_type=instance_type)

    # generate elections according to a default map.csv file
    # that is generated by mapel on the fly
    experiment.prepare_elections()

    # compute distances between each pair of elections
    experiment.compute_distances(distance_id=distance_id)




