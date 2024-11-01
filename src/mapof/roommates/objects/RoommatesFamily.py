#!/usr/bin/env python

import copy

from mapof.core.objects.Family import Family
from mapof.roommates.objects.Roommates import Roommates
from mapof.core.utils import *

import mapof.roommates.cultures.mallows as mallows


class RoommatesFamily(Family):

    def __init__(self,
                 culture_id: str = None,
                 family_id='none',
                 params: dict = None,
                 size: int = 1,
                 label: str = "none",
                 color: str = "black",
                 alpha: float = 1.,
                 ms: int = 20,
                 show=True,
                 marker='o',
                 starting_from: int = 0,
                 path: dict = None,
                 single: bool = False,
                 num_agents: int = None,
                 **kwargs):

        super().__init__(culture_id=culture_id,
                         family_id=family_id,
                         params=params,
                         size=size,
                         label=label,
                         color=color,
                         alpha=alpha,
                         ms=ms,
                         show=show,
                         marker=marker,
                         starting_from=starting_from,
                         path=path,
                         single=single,
                         **kwargs)

        self.num_agents = num_agents


    def prepare_family(self, experiment_id=None, is_exported=None):

        instances = {}

        _keys = []
        for j in range(self.size):

            params = copy.deepcopy(self.params)

            if params is not None and 'normphi' in params:
                params['phi'] = mallows.phi_from_normphi(self.num_agents,
                                                         relphi=params['normphi'])

            instance_id = get_instance_id(self.single, self.family_id, j)

            instance = Roommates(experiment_id, instance_id, is_imported=False,
                                 culture_id=self.culture_id, num_agents=self.num_agents)

            instance.prepare_instance(is_exported=is_exported, params=params)

            instances[instance_id] = instance

            _keys.append(instance_id)

        self.instance_ids = _keys

        return instances
