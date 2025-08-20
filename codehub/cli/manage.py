import os
import time
from codehub.cli.k8s.helpers import get_external_ip, get_namespaced_deployments
from codehub.cli.gcp.helpers import authenticate_k8s_GKE
from codehub.cli.helpers import get_latest_deployment
from codehub.cli.config import SLEEP_TIME, SLEEP_THRESHOLD, TIMEOUT_ERROR


def get_ip(name, deploy_dir=None):
    authenticate_k8s_GKE(name)

    if deploy_dir is None:
        deploy_dir = os.path.join(get_latest_deployment(name), "k8s")

    return f"http://{get_external_ip(deploy_dir)}"


def wait_for_hub_to_get_ready(deploy_dir):
    total_sleep_time = 0
    while not (get_external_ip(deploy_dir) and __hub_is_ready(deploy_dir)):
        time.sleep(SLEEP_TIME)
        total_sleep_time = total_sleep_time + SLEEP_TIME

        if total_sleep_time > SLEEP_THRESHOLD:
            raise TimeoutError(TIMEOUT_ERROR)

    return


def __hub_is_ready(deploy_dir):
    res = get_namespaced_deployments(deploy_dir)

    for deployment in res.items:
        if deployment.metadata.name == "hub":
            if deployment.status.available_replicas:
                return True
    return False
