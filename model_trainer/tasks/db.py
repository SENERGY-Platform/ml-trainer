import mlflow
import mlflow.pyfunc

def store_model(checkpoint, userid, model_type, experiment, model_artifact_name, task):
    print('store model')
    model_artifact = checkpoint.to_dict()['model']

    mlflow.end_run()
    mlflow.set_experiment(experiment)
    run_relative_artifcat_path = 'models'

    # Create a new model version and save model
    with mlflow.start_run(run_name="final-train") as run:
        mlflow.pyfunc.log_model(
            artifact_path=run_relative_artifcat_path,
            python_model=model_artifact,
            registered_model_name=model_artifact_name
        )
    
    model_uri = f"runs:/{run.info.run_id}/{run_relative_artifcat_path}"
    mlflow.register_model(model_uri, model_artifact_name, tags={
        "userid": userid,
        "model_type": model_type,
        "task": task
    })