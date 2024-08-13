from kubernetes import client, config
from kubernetes.client.rest import ApiException
from model_trainer.exceptions import K8sException
from model_trainer.schema import Job 

# - darts==0.24.0 

PIP_VERSION = "22.0.4"

class KubernetesAPIClient():
    def __init__(self):
        self.setup_config()
        self.api_instance = client.CustomObjectsApi()
    
    def setup_config(self):
        config.load_incluster_config()
        #config.load_kube_config(config_file="~/.kube/prod.yaml")

    def create_env_string(self, envs): 
        env_string = ""
        for env, value in envs.items():
            env_string += f"{env}: '{value}'\n  "
        return env_string 

    def get_job_status(self, job_name):
        group = 'ray.io' 
        version = 'v1' 
        plural = 'rayjobs'
        namespace = 'trainer' 
        try:
            api_response = self.api_instance.get_namespaced_custom_object(group=group, version=version, plural=plural, namespace=namespace, name=job_name)
            print(api_response)
            job_status_result = api_response.get('status', {'jobStatus': "RUNNING"}) # Sometimes the status field is missing... assume running
            msg = job_status_result.get('message')
            k8s_job_status = job_status_result['jobStatus']
            job_status = "unknown" 
            if k8s_job_status == "SUCCEEDED":
                job_status = "done"
            if k8s_job_status == "RUNNING" or k8s_job_status == "PENDING":
                job_status = "running"
            if k8s_job_status == "FAILED":
                job_status = "error"
            return job_status, msg

        except ApiException as e:
            print("Exception when calling CustomObjectsApi->get_cluster_custom_object: %s\n" % e)
            raise(K8sException(e.status, e.body))
    
    def create_job(
        self, 
        envs, 
        job_name, 
        job: Job
    ):
        # See https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/config.html
        env_string = self.create_env_string(envs)
        print(f"Set env: {env_string}")
        data = {
            "apiVersion": "ray.io/v1",
            "kind": "RayJob",
            "metadata": {
                "name": job_name
            },
            "spec": {
                "entrypoint": "python /opt/run_task.py",
                "shutdownAfterJobFinishes": True,
                "ttlSecondsAfterFinished": 600,
                "runtimeEnvYAML": f"""env_vars:
  {env_string}
pip_version: "=={PIP_VERSION}"
pip:
  - cryptography==38.0.4 
  - toolbox[data, {job.task}] @ git+https://github.com/SENERGY-Platform/timeseries-toolbox@{job.toolbox_version}
  - python-dotenv==1.0.0""",
                "rayClusterSpec": {
                    "rayVersion": job.ray_version, #"2.9.0",
                    "headGroupSpec": {
                        "rayStartParams": {
                            "dashboard-host": "0.0.0.0",
                            "num-cpus": "0", # Head node has 0 logical ressources -> no work is scheduled there to guarantee high availability 
                            "num-gpus": "0"
                        },
                        "template": {
                            "spec": {
                                "containers": [
                                {
                                    "name": "ray-head",
                                    "image": job.ray_image,
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
                                        "cpu": "1",
                                        "memory": "20G"
                                    },
                                    "requests": {
                                        "cpu": "200m",
                                        "memory": "20G"
                                    }
                                    },
                                }
                                ],
                            }
                        }
                    },
                    "workerGroupSpecs": [
                        {
                        "replicas": job.cluster.number_workers,
                        "minReplicas": 1,
                        "maxReplicas": 5,
                        "groupName": "small-group",
                        "rayStartParams": {},
                        "template": {
                            "spec": {
                            "containers": [
                                {
                                "name": "ray-worker",
                                "image": job.ray_image,
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
                                        "cpu": job.cluster.cpu_worker_limit,
                                        "memory": job.cluster.memory_worker_limit
                                    },
                                    "requests": {
                                        "cpu": job.cluster.cpu_worker_limit # See ray guide, limit should be same as requests as ray will use limit as logical resources for scheduling
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

        group = 'ray.io' # str | The custom resource's group name
        version = 'v1' # str | The custom resource's version
        plural = 'rayjobs' # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.
        namespace = 'trainer' # must be same namespace, otherwise RBAC will complain
        try:
            api_response = self.api_instance.create_namespaced_custom_object(group=group, version=version, plural=plural, body=data, namespace=namespace)
            print(api_response)
        except ApiException as e:
            print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)
            raise(K8sException(e.status, e.body))
