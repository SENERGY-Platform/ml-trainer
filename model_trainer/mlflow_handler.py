import mlflow 

class MlflowHandler():
    def __init__(self, config):
        mlflow.set_tracking_uri(config.MLFLOW_URL)

    def experiment_name_can_be_used(self, experiment_name):
        return True, None
        experiment = mlflow.get_experiment_by_name(experiment_name)

        if not experiment:
            return True, None

        if experiment.lifecycle_stage == 'active':
            return False, f"Experiment {experiment_name} exists already and is active"
        
        if experiment.lifecycle_stage == 'deleted':
            return False, f"Experiment {experiment_name} is deleted"