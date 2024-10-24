import mapof.roommates as mapof


class TestInstancesImport:

    def test_prepare_instances(self):
        self.experiment_1 = mapof.prepare_offline_roommates_experiment(experiment_id="test_id")
        self.experiment_1.prepare_instances()

        self.experiment_2 = mapof.prepare_offline_roommates_experiment(experiment_id="test_id")
        assert self.experiment_2.num_instances == self.experiment_1.num_instances
