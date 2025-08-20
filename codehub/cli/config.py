import os
from pathlib import Path


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
