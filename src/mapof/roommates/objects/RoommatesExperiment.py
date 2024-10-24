#!/usr/bin/env python
import ast
import copy
import csv
import itertools
from abc import ABC
from multiprocessing import Process
from time import sleep
import time

import mapof.core.persistence.experiment_exports as exports
from mapof.core.objects.Experiment import Experiment
from mapof.roommates.objects.RoommatesFamily import RoommatesFamily
from mapof.roommates.objects.Roommates import Roommates
import mapof.roommates.distances as metr
import mapof.roommates.features.basic_features as basic
import mapof.roommates.features_ as features
from mapof.core.utils import *
from mapof.core.glossary import *
from mapof.core.persistence.experiment_imports import get_values_from_csv_file

try:
    from sklearn.manifold import MDS
    from sklearn.manifold import TSNE
    from sklearn.manifold import SpectralEmbedding
    from sklearn.manifold import LocallyLinearEmbedding
    from sklearn.manifold import Isomap
except ImportError as error:
    MDS = None
    TSNE = None
    SpectralEmbedding = None
    LocallyLinearEmbedding = None
    Isomap = None
    print(error)


class RoommatesExperiment(Experiment, ABC):
    """Abstract set of elections."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.default_num_agents = 10
        self.matchings = {}
        try:
            self.import_matchings()
        except:
            pass

    def add_culture(self, name, function):
        pass

    def add_distance(self, name, function):
        pass

    def add_feature(self, name, function):
        pass

    def add_folders_to_experiment(self) -> None:

        dirs = ["experiments"]
        for dir in dirs:
            if not os.path.isdir(dir):
                os.mkdir(os.path.join(os.getcwd(), dir))

        if not os.path.isdir(os.path.join(os.getcwd(), "experiments", self.experiment_id)):
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id))

        list_of_folders = ['distances',
                           'features',
                           'coordinates',
                           'instances']

        for folder_name in list_of_folders:
            if not os.path.isdir(os.path.join(os.getcwd(), "experiments",
                                              self.experiment_id, folder_name)):
                os.mkdir(os.path.join(os.getcwd(), "experiments",
                                      self.experiment_id, folder_name))

        path = os.path.join(os.getcwd(), "experiments", self.experiment_id, "map.csv")
        if not os.path.exists(path):
            with open(path, 'w') as file_csv:
                file_csv.write(
                    "size;num_agents;culture_id;params;color;alpha;"
                    "family_id;label;marker\n")
                file_csv.write("3;10;ic;{};black;1;ic;Impartial Culture;o\n")

    def import_matchings(self):
        matchings = {}

        path = os.path.join(os.getcwd(), 'experiments', self.experiment_id, 'features',
                            'stable_sr.csv')
        with open(path, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')

            for row in reader:
                election_id = row['instance_id']
                value = row['matching']
                if value == '':
                    matchings[election_id] = None
                else:
                    matchings[election_id] = value

        self.matchings = matchings

    def add_instances_to_experiment(self):

        instances = {}

        for family_id in self.families:
            single = self.families[family_id].single

            ids = []
            for j in range(self.families[family_id].size):
                instance_id = get_instance_id(single, family_id, j)
                instance = Roommates(self.experiment_id, instance_id)
                instances[instance_id] = instance
                ids.append(str(instance_id))

            self.families[family_id].instance_ids = ids

        return instances

    def add_instance(self,
                     culture_id="none",
                     instance_id=None,
                     params=None,
                     label=None,
                     color="black",
                     alpha=1.,
                     show=True,
                     marker='x',
                     size=1,
                     num_agents=None
                     ):

        if num_agents is None:
            num_agents = self.default_num_agents

        return self.add_family(
            culture_id=culture_id,
            instance_id=instance_id,
            params=params,
            size=size,
            label=label,
            color=color,
            alpha=alpha,
            show=show,
            marker=marker,
            family_id=instance_id,
            num_agents=num_agents,
            single_instance=True
        )

    def add_family(self,
                   culture_id: str = "none",
                   instance_id: str = None,
                   params: dict = None,
                   size: int = 1,
                   label: str = None,
                   color: str = "black",
                   alpha: float = 1.,
                   show: bool = True,
                   marker: str = 'o',
                   family_id: str = None,
                   single_instance: bool = False,
                   num_agents: int = None,
                   path: dict = None
                   ):

        if instance_id is not None:
            family_id = instance_id

        if num_agents is None:
            num_agents = self.default_num_agents

        if self.families is None:
            self.families = {}

        if params is None:
            params = {}

        if family_id is None:
            family_id = culture_id + '_' + str(num_agents)

        if label is None:
            label = family_id

        self.families[family_id] = RoommatesFamily(
            culture_id=culture_id,
            family_id=family_id,
            params=params,
            label=label,
            color=color,
            alpha=alpha,
            single=single_instance,
            show=show,
            size=size, marker=marker,
            num_agents=num_agents,
            path=path)

        self.num_families = len(self.families)
        self.num_instances = sum([self.families[family_id].size for family_id in self.families])

        new_instances = self.families[family_id].prepare_family(
            is_exported=self.is_exported,
            experiment_id=self.experiment_id
        )

        for instance_id in new_instances:
            self.instances[instance_id] = new_instances[instance_id]

        self.families[family_id].instance_ids = list(new_instances.keys())

        # if self.is_exported:
        #     self.update_map_csv()  # To be implemented

        return list(new_instances.keys())

    def compute_distances(
            self,
            distance_id: str = 'l1-mutual_attraction',
            num_processes: int = 1,
            self_distances: bool = False
    ) -> None:
        """ Compute distances between instances (using processes) """

        self.distance_id = distance_id

        matchings = {instance_id: {} for instance_id in self.instances}
        distances = {instance_id: {} for instance_id in self.instances}
        times = {instance_id: {} for instance_id in self.instances}

        ids = []
        for i, instance_1 in enumerate(self.instances):
            for j, instance_2 in enumerate(self.instances):
                if i == j:
                    if self_distances:
                        ids.append((instance_1, instance_2))
                elif i < j:
                    ids.append((instance_1, instance_2))

        num_distances = len(ids)

        if self.experiment_id == 'virtual' or num_processes == 1:
            metr.run_single_process(self, ids, distances, times, matchings)

        else:
            processes = []
            for process_id in range(num_processes):
                print(f'Starting process: {process_id}')
                sleep(0.1)
                start = int(process_id * num_distances / num_processes)
                stop = int((process_id + 1) * num_distances / num_processes)
                instances_ids = ids[start:stop]

                process = Process(target=metr.run_multiple_processes, args=(self,
                                                                            instances_ids,
                                                                            distances,
                                                                            times,
                                                                            matchings,
                                                                            process_id))
                process.start()
                processes.append(process)

            for process in processes:
                process.join()

            distances = {instance_id: {} for instance_id in self.instances}
            times = {instance_id: {} for instance_id in self.instances}
            for t in range(num_processes):

                file_name = f'{distance_id}_p{t}.csv'
                path = os.path.join(os.getcwd(), "experiments", self.experiment_id, "distances",
                                    file_name)

                with open(path, 'r', newline='') as csv_file:
                    reader = csv.DictReader(csv_file, delimiter=';')

                    for row in reader:
                        distances[row['instance_id_1']][row['instance_id_2']] = float(
                            row['distance'])
                        times[row['instance_id_1']][row['instance_id_2']] = float(row['time'])

        if self.is_exported:
            exports.export_distances_to_file(self, distance_id, distances, times, ids)

        self.distances = distances
        self.times = times
        self.matchings = matchings

    def import_controllers(self):
        """ Import controllers from a file """

        families = {}

        path = os.path.join(os.getcwd(), 'experiments', self.experiment_id, 'map.csv')
        file_ = open(path, 'r')

        header = [h.strip() for h in file_.readline().split(';')]
        reader = csv.DictReader(file_, fieldnames=header, delimiter=';')

        starting_from = 0
        for row in reader:

            culture_id = None
            color = None
            label = None
            params = None
            alpha = None
            size = None
            marker = None
            num_agents = None
            family_id = None
            show = True

            if 'culture_id' in row.keys():
                culture_id = str(row['culture_id']).strip()

            if 'color' in row.keys():
                color = str(row['color']).strip()

            if 'label' in row.keys():
                label = str(row['label'])

            if 'family_id' in row.keys():
                family_id = str(row['family_id'])

            if 'params' in row.keys():
                params = ast.literal_eval(str(row['params']))

            if 'alpha' in row.keys():
                alpha = float(row['alpha'])

            if 'size' in row.keys():
                size = int(row['size'])

            if 'marker' in row.keys():
                marker = str(row['marker']).strip()

            if 'num_agents' in row.keys():
                num_agents = int(row['num_agents'])

            if 'path' in row.keys():
                path = ast.literal_eval(str(row['path']))

            if 'show' in row.keys():
                show = row['show'].strip() == 'process_id'

            single_instance = size == 1

            families[family_id] = RoommatesFamily(culture_id=culture_id,
                                                  family_id=family_id,
                                                  params=params, label=label,
                                                  color=color, alpha=alpha, show=show,
                                                  size=size, marker=marker,
                                                  starting_from=starting_from,
                                                  num_agents=num_agents, path=path,
                                                  single=single_instance)
            starting_from += size

        self.num_families = len(families)
        self.num_instances = sum([families[family_id].size for family_id in families])
        self.main_order = [i for i in range(self.num_instances)]

        file_.close()
        return families

    def prepare_instances(self):

        if self.instances is None:
            self.instances = {}

        for family_id in self.families:

            new_instances = self.families[family_id].prepare_family(
                is_exported=self.is_exported,
                experiment_id=self.experiment_id)

            for instance_id in new_instances:
                self.instances[instance_id] = new_instances[instance_id]

    def compute_stable_sr(self):
        for instance_id in self.instances:
            print(instance_id)
            if instance_id in ['roommates_test']:
                self.matchings[instance_id] = 'None'
            else:
                usable_matching = basic.compute_stable_SR(self.instances[instance_id].votes)
                self.matchings[instance_id] = usable_matching

        if self.is_exported:

            path_to_folder = os.path.join(os.getcwd(), "election", self.experiment_id,
                                          "features")
            make_folder_if_do_not_exist(path_to_folder)
            path_to_file = os.path.join(path_to_folder, f'stable_sr.csv')

            with open(path_to_file, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(
                    ["instance_id", "matching"])

                for instance_id in self.instances:
                    usable_matching = self.matchings[instance_id]
                    writer.writerow([instance_id, usable_matching])

    def compute_feature(self,
                        feature_id: str = None,
                        feature_params=None) -> dict:

        if feature_params is None:
            feature_params = {}

        feature_dict = {'value': {}, 'time': {}, 'std': {}}

        features_with_std = {'avg_num_of_bps_for_rand_matching'}

        num_iterations = 1
        if 'num_iterations' in feature_params:
            num_iterations = feature_params['num_iterations']

        if feature_id in MAIN_GLOBAL_FEATUERS:

            feature = features.get_global_feature(feature_id)

            values = feature(self, election_ids=list(self.instances))

            for instance_id in self.instances:
                feature_dict['value'][instance_id] = values[instance_id]
                feature_dict['time'][instance_id] = 0

        elif feature_id in ['distortion_from_all', 'max_distortion_from_all']:
            feature = features.get_global_feature(feature_id)
            for instance_id in self.instances:
                values = feature(self, self.instances[instance_id])
                print(instance_id, values)
                feature_dict['value'][instance_id] = values
                feature_dict['time'][instance_id] = 0
        else:

            if feature_id == 'summed_rank_difference':
                minimal = get_values_from_csv_file(self, feature_id='summed_rank_minimal_matching')
                maximal = get_values_from_csv_file(self, feature_id='summed_rank_maximal_matching')

                for instance_id in self.instances:
                    if minimal[instance_id] is None:
                        value = 'None'
                    else:
                        value = abs(maximal[instance_id] - minimal[instance_id])
                    feature_dict['value'][instance_id] = value
                    feature_dict['time'][instance_id] = 0

            else:
                for instance_id in self.instances:
                    feature = features.get_local_feature(feature_id)
                    instance = self.instances[instance_id]

                    start = time.time()

                    for _ in range(num_iterations):

                        if feature_id in ['summed_rank_minimal_matching',
                                          'summed_rank_maximal_matching',
                                          'minimal_rank_maximizing_matching',
                                          ] \
                                and (self.matchings[instance_id] is None or self.matchings[
                            instance_id] == 'None'):
                            value = 'None'
                        else:
                            value = feature(instance)

                        print(value)

                    total_time = time.time() - start
                    total_time /= num_iterations

                    if feature_id in features_with_std:
                        feature_dict['value'][instance_id] = value[0]
                        feature_dict['time'][instance_id] = total_time
                        feature_dict['std'][instance_id] = value[1]
                    else:
                        feature_dict['value'][instance_id] = value
                        feature_dict['time'][instance_id] = total_time

        if self.is_exported:

            path_to_folder = os.path.join(os.getcwd(), "experiments", self.experiment_id,
                                          "features")
            make_folder_if_do_not_exist(path_to_folder)
            path_to_file = os.path.join(path_to_folder, f'{feature_id}.csv')

            with open(path_to_file, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')

                if feature_id in features_with_std:
                    writer.writerow(["election_id", "value", 'time', 'std'])
                    for key in feature_dict['value']:
                        writer.writerow([key, feature_dict['value'][key],
                                         round(feature_dict['time'][key], 3),
                                         round(feature_dict['std'][key], 3)])
                else:
                    writer.writerow(["election_id", "value", 'time'])
                    for key in feature_dict['value']:
                        writer.writerow([key, feature_dict['value'][key],
                                         round(feature_dict['time'][key], 3)])

        self.features[feature_id] = feature_dict
        return feature_dict

    def create_structure(self) -> None:

        dirs = ["experiments", "images", "trash"]
        for dir in dirs:
            if not os.path.isdir(dir):
                os.mkdir(os.path.join(os.getcwd(), dir))

        try:
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id))
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id, "distances"))
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id, "features"))
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id, "coordinates"))
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id, "instances"))
            os.mkdir(os.path.join(os.getcwd(), "election", self.experiment_id, "matrices"))

            # PREPARE MAP.CSV FILE
            path = os.path.join(os.getcwd(), "election", self.experiment_id, "map.csv")

            with open(path, 'w') as file_csv:
                file_csv.write(
                    "size;num_agents;culture_id;params;color;alpha;family_id;label;marker;show\n")
                file_csv.write("10;20;roommates_ic;{};black;1;IC;IC;o;process_id\n")
        except:
            pass
