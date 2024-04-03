import requests 
from urllib.parse import urljoin

class KubernetesAPIClient():
    def __init__(self, url):
        self.url = url 

    def create_job(self):
        path = 'api/ray.io/v1/namespaces/ray/rayjobs'
        data = {
            "apiVersion": "ray.io/v1",
            "kind": "RayJob",
            "metadata": {
                "name": "rayjob-sample"
            },
            "spec": {
                "entrypoint": "python /opt/run_task.py",
                "runtimeEnvYAML": "pip:\n  - requests==2.26.0\n  - pendulum==2.1.2\nenv_vars:\n  counter_name: \"test_counter\"\n",
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
                                    "image": "rayproject/ray:2.9.0",
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
                                    "volumeMounts": [
                                    {
                                        "mountPath": "/home/ray/samples",
                                        "name": "code-sample"
                                    }
                                    ]
                                }
                                ],
                                "volumes": [
                                {
                                    "name": "code-sample",
                                    "configMap": {
                                    "name": "ray-job-code-sample",
                                    "items": [
                                        {
                                        "key": "sample_code.py",
                                        "path": "sample_code.py"
                                        }
                                    ]
                                    }
                                }
                                ]
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
        requests.post(urljoin(self.url, path), data)