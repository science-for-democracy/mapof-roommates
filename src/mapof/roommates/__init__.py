
from .objects.RoommatesExperiment import RoommatesExperiment
from .objects.Roommates import Roommates
from . import cultures as rom
from .distances import get_distance


def prepare_online_roommates_experiment(**kwargs):
    return prepare_roommates_experiment(**kwargs, is_exported=False, is_imported=False)


def prepare_offline_roommates_experiment(**kwargs):
    return prepare_roommates_experiment(**kwargs, is_exported=True, is_imported=True)


def prepare_roommates_experiment(experiment_id=None,
                                 distance_id=None,
                                 is_imported=None,
                                 is_exported=None,
                                 embedding_id=None):

    return RoommatesExperiment(experiment_id=experiment_id,
                               is_imported=is_imported,
                               distance_id=distance_id,
                               embedding_id=embedding_id,
                               is_exported=is_exported)


def generate_roommates_instance(**kwargs):
    instance = Roommates('virtual', 'tmp', **kwargs)
    instance.prepare_instance()
    return instance


def generate_roommates_votes(**kwargs):
    return rom.generate_votes(**kwargs)


def compute_distance(*args,
                     **kwargs):
    return get_distance(*args, **kwargs)