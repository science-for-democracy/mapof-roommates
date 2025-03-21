#!/usr/bin/env python
import copy
import logging

import numpy as np
from mapof.core.objects.Instance import Instance

from mapof.roommates.cultures import generate_votes
from mapof.roommates.features import get_local_feature
import mapof.roommates.persistence.instance_exports as exports
import mapof.roommates.persistence.instance_imports as imports


class Roommates(Instance):

    def __init__(self,
                 experiment_id,
                 instance_id,
                 culture_id=None,
                 num_agents=None,
                 is_imported=True,
                 votes=None,
                 params=None,
                 **kwargs):

        super().__init__(
            experiment_id,
            instance_id,
            culture_id=culture_id,
            params=params,
            **kwargs)

        self.num_agents = num_agents
        self.votes = votes

        self.retrospetive_vectors = None
        self.positionwise_vectors = None

        if is_imported and experiment_id is not None:
            try:
                self.votes, self.num_agents, self.params, self.culture_id = \
                    imports.import_real_instance(self)
            except Exception:
                logging.warning(f'Could not import instance {self.instance_id}.')

    def get_retrospective_vectors(self):
        if self.retrospetive_vectors is not None:
            return self.retrospetive_vectors
        return self.votes_to_retrospective_vectors()

    def get_positionwise_vectors(self):
        if self.positionwise_vectors is not None:
            return self.positionwise_vectors
        return self.votes_to_positionwise_vectors()

    def votes_to_retrospective_vectors(self):

        vectors = np.zeros([self.num_agents, self.num_agents - 1], dtype=int)

        order_votes = [[] for _ in range(self.num_agents)]

        for a in range(self.num_agents):
            (missing,) = set(range(self.num_agents)) - set(self.votes[a])
            order_votes[missing] = copy.deepcopy(self.votes[a])

        for a in range(self.num_agents):
            for i, b in enumerate(order_votes[a]):
                vectors[a][i] = int(list(order_votes[b]).index(a))

        self.retrospetive_vectors = vectors
        return vectors

    def votes_to_positionwise_vectors(self):

        vectors = np.zeros([self.num_agents, self.num_agents - 1])

        for i in range(self.num_agents):
            pos = 0
            for j in range(self.num_agents - 1):
                vote = self.votes[i][j]
                vectors[vote][pos] += 1
                pos += 1

        for i in range(self.num_agents):
            for j in range(self.num_agents - 1):
                vectors[i][j] /= float(self.num_agents)

        self.positionwise_vectors = vectors
        return vectors

    def prepare_instance(self, is_exported: bool = False):


        if self.culture_id == 'roommates_norm-mallows' and 'norm-phi' not in self.params:
            self.params['norm-phi'] = np.random.rand()
            # params['alpha'] = params['norm-phi']

        elif self.culture_id == 'roommates_urn' and 'alpha' not in self.params:
            self.params['alpha'] = np.random.rand()

        if 'variable' in self.params:
            self.params['alpha'] = self.params[self.params['variable']]

        self.votes = generate_votes(culture_id=self.culture_id,
                                    num_agents=self.num_agents,
                                    params=self.params)

        if is_exported:
            exports.export_instance_to_a_file(self)

    def compute_feature(self, feature_id, feature_long_id=None, **kwargs):
        if feature_long_id is None:
            feature_long_id = feature_id
        feature = get_local_feature(feature_id)
        self.features[feature_long_id] = feature(self, **kwargs)
