#!/usr/bin/env python
import os

from mapel.voting.objects.ElectionExperiment import ElectionExperiment
from mapel.voting.objects.OrdinalElection import OrdinalElection

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


class OrdinalElectionExperiment(ElectionExperiment):
    """Abstract set of elections."""

    def __init__(self, elections=None, distances=None,
                 coordinates=None, distance_name='emd-positionwise', experiment_id=None,
                 election_type='ordinal', attraction_factor=1, ):
        super().__init__(elections=elections, distances=distances,
                         coordinates=coordinates, distance_name=distance_name,
                         experiment_id=experiment_id,
                         election_type=election_type, attraction_factor=attraction_factor, )

    def add_elections_to_experiment(self, with_matrices=False):
        """ Import elections from a file """

        elections = {}

        for family_id in self.families:

            ids = []
            if self.families[family_id].single_election:
                election_id = family_id
                election = OrdinalElection(self.experiment_id, election_id,
                                           with_matrix=with_matrices)
                elections[election_id] = election
                ids.append(str(election_id))
            else:
                for j in range(self.families[family_id].size):
                    election_id = family_id + '_' + str(j)
                    election = OrdinalElection(self.experiment_id, election_id,
                                               with_matrix=with_matrices)
                    elections[election_id] = election
                    ids.append(str(election_id))

            self.families[family_id].election_ids = ids

        return elections

    def create_structure(self) -> None:

        # PREPARE STRUCTURE

        if not os.path.isdir("experiments/"):
            os.mkdir(os.path.join(os.getcwd(), "experiments"))

        if not os.path.isdir("images/"):
            os.mkdir(os.path.join(os.getcwd(), "images"))

        if not os.path.isdir("trash/"):
            os.mkdir(os.path.join(os.getcwd(), "trash"))

        try:
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id))
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id, "distances"))
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id, "features"))
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id, "coordinates"))
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id, "elections"))
            os.mkdir(os.path.join(os.getcwd(), "experiments", self.experiment_id, "matrices"))

            # PREPARE MAP.CSV FILE

            path = os.path.join(os.getcwd(), "experiments", self.experiment_id, "map.csv")

            with open(path, 'w') as file_csv:
                file_csv.write(
                    "size;num_candidates;num_voters;model;params;color;alpha;label;marker;show\n")
                file_csv.write("3;10;100;impartial_culture;{};black;1;Impartial Culture;o;t\n")
                file_csv.write("3;10;100;iac;{};black;0.7;IAC;o;t\n")
                file_csv.write("3;10;100;conitzer;{};limegreen;1;SP by Conitzer;o;t\n")
                file_csv.write("3;10;100;walsh;{};olivedrab;1;SP by Walsh;o;t\n")
                file_csv.write("3;10;100;spoc_conitzer;{};DarkRed;0.7;SPOC;o;t\n")
                file_csv.write("3;10;100;group-separable;{};blue;1;Group-Separable;o;t\n")
                file_csv.write("3;10;100;single-crossing;{};purple;0.6;Single-Crossing;o;t\n")
                file_csv.write("3;10;100;1d_interval;{};DarkGreen;1;1D Interval;o;t\n")
                file_csv.write("3;10;100;2d_disc;{};Green;1;2D Disc;o;t\n")
                file_csv.write("3;10;100;3d_cube;{};ForestGreen;0.7;3D Cube;o;t\n")
                file_csv.write("3;10;100;2d_sphere;{};black;0.2;2D Sphere;o;t\n")
                file_csv.write("3;10;100;3d_sphere;{};black;0.4;3D Sphere;o;t\n")
                file_csv.write("3;10;100;urn_model;{'alpha':0.1};yellow;1;Urn model 0.1;o;t\n")
                file_csv.write(
                    "3;10;100;norm-mallows;{'norm-phi':0.5};blue;1;Norm-Mallows 0.5;o;t\n")
                file_csv.write("3;10;100;urn_model;{'alpha':0};orange;1;Urn model (gamma);o;t\n")
                file_csv.write(
                    "3;10;100;norm-mallows;{'norm-phi':0};cyan;1;Norm-Mallows (uniform);o;t\n")
                file_csv.write("1;10;100;identity;{};blue;1;Identity;x;t\n")
                file_csv.write("1;10;100;uniformity;{};black;1;Uniformity;x;t\n")
                file_csv.write("1;10;100;antagonism;{};red;1;Antagonism;x;t\n")
                file_csv.write("1;10;100;stratification;{};green;1;Stratification;x;t\n")
                file_csv.write("1;10;100;walsh_matrix;{};olivedrab;1;Walsh Matrix;x;t\n")
                file_csv.write("1;10;100;conitzer_matrix;{};limegreen;1;Conitzer Matrix;x;t\n")
                file_csv.write(
                    "1;10;100;single-crossing_matrix;{};purple;0.6;Single-Crossing Matrix;x;t\n")
                file_csv.write(
                    "1;10;100;gs_caterpillar_matrix;{};green;1;GS Caterpillar Matrix;x;t\n")
                file_csv.write("3;10;100;unid;{};blue;1;UNID;3;f\n")
                file_csv.write("3;10;100;anid;{};black;1;ANID;3;f\n")
                file_csv.write("3;10;100;stid;{};black;1;STID;3;f\n")
                file_csv.write("3;10;100;anun;{};black;1;ANUN;3;f\n")
                file_csv.write("3;10;100;stun;{};black;1;STUN;3;f\n")
                file_csv.write("3;10;100;stan;{};red;1;STAN;3;f\n")
        except FileExistsError:
            print("Experiment already exists!")

