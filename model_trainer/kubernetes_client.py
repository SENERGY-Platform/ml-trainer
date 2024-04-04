from kubernetes import client, config
from kubernetes.client.rest import ApiException


PIP_VERSION = "22.0.4"
PYTHON_VERSION = "3.8.16"

class KubernetesAPIClient():
    def __init__(self):
        self.setup_config()
    
    def setup_config(self):
        config.load_incluster_config()
        #config.load_kube_config(config_file="~/.kube/prod.yaml")

    def create_env_string(self, envs): 
        env_string = ""
        for env, value in envs:
            env_string += f"{env}: \"{value}\""
        return env_string 

    def create_job(self, envs, job_name):
        env_string = self.create_env_string(envs)
        data = {
            "apiVersion": "ray.io/v1",
            "kind": "RayJob",
            "metadata": {
                "name": job_name
            },
            "spec": {
                "entrypoint": "python /opt/run_task.py",
                "runtimeEnvYAML": f"""env_vars:
    {env_string}
pip_version: "=={PIP_VERSION};python_version=='{PYTHON_VERSION}'"
                """,
                "rayClusterSpec": {
                    "rayVersion": "2.9.0",
                    "headGroupSpec": {
                        "rayStartParams": {
                            "dashboard-host": "0.0.0.0"
                        },
                        "template": {
                            "spec": {
                                "containers": [
                                {
                                    "name": "ray-head",
                                    "image": "ghcr.io/senergy-platform/ray:v0.0.1",
                                    "ports": [
                                    {
                                        "containerPort": 6379,
                                        "name": "gcs-server"
                                    },
                                    {
                                        "containerPort": 8265,
                                        "name": "dashboard"
                                    },
                                    {
                                        "containerPort": 10001,
                                        "name": "client"
                                    }
                                    ],
                                    "resources": {
                                    "limits": {
                                        "cpu": "1"
                                    },
                                    "requests": {
                                        "cpu": "200m"
                                    }
                                    },
                                }
                                ],
                            }
                        }
                    },
                    "workerGroupSpecs": [
                        {
                        "replicas": 1,
                        "minReplicas": 1,
                        "maxReplicas": 2,
                        "groupName": "small-group",
                        "rayStartParams": {},
                        "template": {
                            "spec": {
                            "containers": [
                                {
                                "name": "ray-worker",
                                "image": "rayproject/ray:2.9.0",
                                "lifecycle": {
                                    "preStop": {
                                    "exec": {
                                        "command": [
                                        "/bin/sh",
                                        "-c",
                                        "ray stop"
                                        ]
                                    }
                                    }
                                },
                                "resources": {
                                    "limits": {
                                    "cpu": "1"
                                    },
                                    "requests": {
                                    "cpu": "200m"
                                    }
                                }
                                }
                            ]
                            }
                        }
                        }
                    ]
                }
            }
        }

        api_instance = client.CustomObjectsApi()
        group = 'ray.io' # str | The custom resource's group name
        version = 'v1' # str | The custom resource's version
        plural = 'rayjobs' # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.

        try:
            api_response = api_instance.create_namespaced_custom_object(group=group, version=version, plural=plural, body=data, namespace="ray")
            print(api_response)
        except ApiException as e:
            print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)