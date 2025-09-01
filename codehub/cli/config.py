from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).parents[2]
PACKAGE_ROOT = Path(__file__).parents[1]

SECRETS = os.path.join(ROOT, "secrets")
DEPLOYMENTS = os.path.join(ROOT, "deployments")
TEMPLATES = os.path.join(PACKAGE_ROOT, "templates")

STRUCTURE = {
    "templates": {
        "hub": os.path.join(TEMPLATES, "hub"),
        "helm": os.path.join(TEMPLATES, "helm"),
        "k8s": os.path.join(TEMPLATES, "k8s"),
        "cloud": os.path.join(TEMPLATES, "cloud"),
    },
    "deployments": {
        "hub": os.path.join(DEPLOYMENTS, "{name}", "{date:%Y-%m-%d-%H-%M-%S}", "hub"),
        "helm": os.path.join(DEPLOYMENTS, "{name}", "{date:%Y-%m-%d-%H-%M-%S}", "helm"),
        "k8s": os.path.join(DEPLOYMENTS, "{name}", "{date:%Y-%m-%d-%H-%M-%S}", "k8s"),
        "cloud": os.path.join(DEPLOYMENTS, "{name}", "cloud"),
    },
    "secrets": {
        "gcp": {
            "sa": os.path.join(SECRETS, "gcp", "service-account.json"),
            "cert": os.path.join(SECRETS, "gcp", "cluster-ca-cert"),
        },
    },
}

SLEEP_TIME = 5
SLEEP_THRESHOLD = 600
TIMEOUT_ERROR = "Timeout expired."
CLUSTER_MAX_LEN = 14


@dataclass
class CloudState:
    nfs_ip: str
    nfs_name: str
    cluster_id: str
    hub_sa_key: str
    cluster_endpoint: str
    cluster_cert: str
    gcp_token: str
    docker_registry_hostname: str
    docker_image: str


@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str


@dataclass
class HubConfig:
    admins: list[str]
    https: Optional[str] = None
    oauth_config: Optional[OAuthConfig] = None
    contact_email: Optional[str] = None


@dataclass
class CreateConfig:
    name: str
    admins: list[str]
    region: str
    zone: str
    machine_type: str


@dataclass
class UpgradeConfig:
    name: str
    hub_config: HubConfig


@dataclass
class DeployConfig:
    name: str
    region: str
    helm_dir: str
    hub_dir: str
    k8s_dir: str
    cloud_state: CloudState
