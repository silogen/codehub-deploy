import os
import sys
import shutil
import yaml
import subprocess
import logging
from codehub.cli.config import CLUSTER_MAX_LEN, DEPLOYMENTS, STRUCTURE


def validate_cluster_name(cluster_name):
    logger = logging.getLogger(__name__)
    if cluster_name.isalnum() and len(cluster_name) <= CLUSTER_MAX_LEN:
        return cluster_name.lower()
    else:
        logger.warning(f"Cluster name: {cluster_name} is invalid")
        logger.warning("Please only use alphanumeric characters")
        logger.warning(f"and a max length of {CLUSTER_MAX_LEN}")
        logger.warning("to comply with GCP naming restrictions")
        sys.exit(1)


def copy_file(input_fp, output_fp):
    with open(input_fp, "rt") as template_file:
        input_content = template_file.read()

    with open(output_fp, "wt") as output_file:
        output_file.write(input_content)


def read_yaml(fp):
    logger = logging.getLogger(__name__)
    with open(fp, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.exception(exc)

    return {}


def get_cloud_dir(name):
    return os.path.join(DEPLOYMENTS, name, "cloud")


def get_latest_deployment(name):
    deployments = [
        os.path.join(DEPLOYMENTS, name, deployment)
        for deployment in sorted(os.listdir(os.path.join(DEPLOYMENTS, name)))
        if os.path.isdir(os.path.join(DEPLOYMENTS, name, deployment))
        and deployment != "cloud"
    ]

    return deployments[-1]


def run_cmd_passthrough_stdout(cmd):
    """Stream stdout to terminal while process is running."""
    process = subprocess.Popen(cmd)
    process.wait()


def run_cmd(cmd, verbose=True):
    logger = logging.getLogger(__name__)
    if verbose:
        logger.info(f"\nRunning: {cmd}")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait()

    stdout = process.communicate()[0].decode("utf-8")

    if verbose:
        logger.info(f"Output: {stdout}")

    return stdout


def fill_file_placeholders(input_fp, output_fp, placeholder_replacements={}):
    with open(input_fp, "rt") as template_file:
        input_content = template_file.read()

    new_content = __replace_placeholders(input_content, placeholder_replacements)
    with open(output_fp, "wt") as output_file:
        output_file.write(new_content)


def __replace_placeholders(string, placeholder_replacements, prefix="{{", suffix="}}"):
    replaced = string
    for placeholder, replacement in placeholder_replacements.items():
        replaced = replaced.replace(f"{prefix}{placeholder}{suffix}", str(replacement))

    return replaced


def check_credentials():
    # Checking GCP credentials
    if not os.path.exists(STRUCTURE["secrets"]["gcp"]["sa"]):
        logging.getLogger(__name__).error("GCP service account not set correctly.")
        return False

    return True


def check_commands():
    logger = logging.getLogger(__name__)
    required_commands = ["kubectl", "helm", "gcloud", "tofu"]

    non_existing_commands = [
        command for command in required_commands if shutil.which(command) is None
    ]
    for command in non_existing_commands:
        logger.error(
            f"Command {command} is not available. Please install it and try again."
        )

    if "gcloud" not in non_existing_commands:
        auth_plugin_installed = "gke-gcloud-auth-plugin" in subprocess.run(
            ["gcloud", "-v"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.decode("utf-8")
        if not auth_plugin_installed:
            logger.error(
                "gke-gcloud-auth-plugin not installed. "
                "Run `gcloud components install gke-gcloud-auth-plugin` "
                "and try again."
            )
            return False

    return len(non_existing_commands) == 0
