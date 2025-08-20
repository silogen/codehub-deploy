import os
from kubernetes import client as k8s_client
from codehub.cli.helpers import read_yaml


def get_external_ip(deploy_dir):
    namespace = read_yaml(os.path.join(deploy_dir, "namespace.yaml"))["metadata"][
        "name"
    ]

    res = k8s_client.CoreV1Api().list_namespaced_service(namespace=namespace)

    for svc in res.items:
        if svc.metadata.name == "proxy-public":
            if svc.status.load_balancer.ingress is not None:
                return svc.status.load_balancer.ingress[0].ip

    return None


def get_namespaced_deployments(deploy_dir):
    namespace = read_yaml(os.path.join(deploy_dir, "namespace.yaml"))["metadata"][
        "name"
    ]

    res = k8s_client.AppsV1Api().list_namespaced_deployment(namespace=namespace)

    return res
