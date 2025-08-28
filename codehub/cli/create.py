import datetime
import os
import logging
import json
from codehub.cli.gcp.terraform import (
    setup_terraform,
    terraform_apply,
    terraform_output,
)
from distutils.dir_util import copy_tree
from codehub.cli.config import (
    STRUCTURE,
    CreateConfig,
    DeployConfig,
    HubConfig,
    UpgradeConfig,
)
from codehub.cli.gcp.helpers import authenticate_k8s_GKE
from codehub.cli.k8s.create import create_k8s_resources
from codehub.cli.helm.create import create_deploy
from codehub.cli.helm.install import install_helm_chart
from codehub.cli.helpers import get_cloud_dir, get_latest_deployment, read_yaml
from codehub.cli.manage import wait_for_hub_to_get_ready, get_ip
import kubernetes.client.rest  # Add this import for the exception handling


def create_infrastructure(config: CreateConfig):
    helm_dir, hub_dir, k8s_dir, cloud_dir = __create_deploy_structure(config.name)

    setup_terraform(
        config=config,
        cloud_dir=cloud_dir,
    )

    cloud_state = terraform_apply(cloud_dir=cloud_dir)
    deploy_config = DeployConfig(
        config.name, config.region, helm_dir, hub_dir, k8s_dir, cloud_state
    )
    __create_k8s_resources(deploy_config)

    return get_ip(config.name, k8s_dir)


def create(config: CreateConfig):
    helm_dir, hub_dir, k8s_dir, cloud_dir = __create_deploy_structure(config.name)

    setup_terraform(
        config=config,
        cloud_dir=cloud_dir,
    )

    cloud_state = terraform_apply(cloud_dir=cloud_dir)
    deploy_config = DeployConfig(
        config.name, config.region, helm_dir, hub_dir, k8s_dir, cloud_state
    )
    hub_config = HubConfig(config.admins)

    __create_k8s_resources(deploy_config)

    __create_deploy(deploy_config, hub_config)
    install_helm_chart(deploy_config, upgrade=False)

    wait_for_hub_to_get_ready(k8s_dir)

    return get_ip(config.name, k8s_dir)


def upgrade(config: UpgradeConfig):
    old_deploy_dir = get_latest_deployment(config.name)

    helm_dir, hub_dir, k8s_dir, cloud_dir = __upgrade_deploy_structure(
        config.name, old_deploy_dir
    )
    cloud_state = terraform_output(cloud_dir=cloud_dir)

    region = read_yaml(os.path.join(old_deploy_dir, "helm", "chart.yaml"))["install"][
        "region"
    ]
    deploy_config = DeployConfig(
        config.name, region, helm_dir, hub_dir, k8s_dir, cloud_state
    )

    __create_deploy(
        deploy_config,
        config.hub_config,
    )
    install_helm_chart(deploy_config, upgrade=True)

    authenticate_k8s_GKE(config.name)
    wait_for_hub_to_get_ready(k8s_dir)


def scale(name, nodes, down_scale=True):
    cloud_dir = get_cloud_dir(name)
    scaling_config = {
        "min_nodes": 0 if down_scale else nodes,
        "max_nodes": nodes,
    }
    terraform_apply(
        cloud_dir=cloud_dir,
        additional_vars=scaling_config,
    )


def __create_deploy_structure(name):
    now = datetime.datetime.now()

    helm_dir = STRUCTURE["deployments"]["helm"].format(name=name, date=now)
    hub_dir = STRUCTURE["deployments"]["hub"].format(name=name, date=now)
    k8s_dir = STRUCTURE["deployments"]["k8s"].format(name=name, date=now)
    cloud_dir = STRUCTURE["deployments"]["cloud"].format(name=name)

    for deploy_dir in [helm_dir, hub_dir, k8s_dir, cloud_dir]:
        os.makedirs(deploy_dir, exist_ok=True)

    return helm_dir, hub_dir, k8s_dir, cloud_dir


def __upgrade_deploy_structure(name, old_deploy_dir):
    helm_dir, hub_dir, k8s_dir, cloud_dir = __create_deploy_structure(name)

    copy_tree(os.path.join(old_deploy_dir, "k8s"), k8s_dir)

    return helm_dir, hub_dir, k8s_dir, cloud_dir


def __create_k8s_resources(deploy_config: DeployConfig):
    authenticate_k8s_GKE(deploy_config.name)
    try:
        create_k8s_resources(deploy_config)
    except kubernetes.client.rest.ApiException as e:
        logger = logging.getLogger(__name__)
        # If the error is due to a resource already existing, we can continue
        if e.status == 409 and "already exists" in str(e):
            logger.warning("Resource already exists. Continuing deployment...")
        else:
            # Re-raise the exception if it's not a "resource already exists" error
            raise


def __create_deploy(
    deploy_config: DeployConfig,
    hub_config: HubConfig,
):
    with open(STRUCTURE["secrets"]["gcp"]["sa"], "rt") as f:
        hub_config.contact_email = json.loads(f.read())["client_email"]

    create_deploy(deploy_config, hub_config)
