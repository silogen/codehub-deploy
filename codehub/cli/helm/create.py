import os
from secrets import token_hex
from dotenv import load_dotenv
from codehub.cli.helpers import read_yaml, copy_file, fill_file_placeholders
from codehub.cli.config import STRUCTURE, DeployConfig, HubConfig


def create_deploy(
    deploy_config: DeployConfig,
    hub_config: HubConfig,
):
    oauth_config = hub_config.oauth_config
    config_fps = __get_config_fps(
        https=hub_config.https, oauth=oauth_config is not None
    )
    template_fp = __build_template(deploy_config.hub_dir, config_fps)

    placeholder_replacements = read_yaml(
        os.path.join(STRUCTURE["templates"]["hub"], "config_variables.yaml")
    )
    placeholder_replacements["SECRET_TOKEN"] = token_hex(32)
    placeholder_replacements["CLUSTER_NAME"] = deploy_config.name
    placeholder_replacements["HOST_NAME"] = hub_config.https
    placeholder_replacements["CONTACT_EMAIL"] = hub_config.contact_email
    if oauth_config is not None:
        placeholder_replacements["GITHUB_OAUTH_CLIENT_ID"] = oauth_config.client_id
        placeholder_replacements["GITHUB_OAUTH_CLIENT_SECRET"] = (
            oauth_config.client_secret
        )

    admins = hub_config.admins.copy()
    if "admin" not in admins:
        admins.append("admin")

    def admin_to_yaml_str(admin):
        return f"\n{' ' * 6}- {admin}"

    placeholder_replacements["HUB_ADMINS"] = "".join(
        [admin_to_yaml_str(admin) for admin in admins]
    )
    placeholder_replacements["SUDOERS"] = " ".join(admins)

    cloud_state = deploy_config.cloud_state
    placeholder_replacements["REGISTRY_HOSTNAME"] = cloud_state.docker_registry_hostname
    # The spaces after newline are important for the indentation in the yaml file
    placeholder_replacements["REGISTRY_PASSWORD"] = cloud_state.hub_sa_key.replace(
        "\n", "\n    "
    )
    placeholder_replacements["DOCKER_IMAGE"] = cloud_state.docker_image

    if "DOCKER_IMAGE_TAG" not in placeholder_replacements:
        placeholder_replacements["DOCKER_IMAGE_TAG"] = "stable"

    __add_config_content(deploy_config.hub_dir, template_fp, placeholder_replacements)

    __add_helm_chart_config(deploy_config.helm_dir)


def __get_config_fps(https=None, oauth=None):
    """
    The sequence of the file is important as the config.yaml file will follow this sequence
    """
    config_fps = ["header.yaml", "imagePullSecrets.yaml", "hub.yaml", "auth.yaml"]

    if oauth:
        config_fps = config_fps + ["oauth.yaml"]

    config_fps = config_fps + ["singleuser.yaml", "scaling.yaml", "proxy.yaml"]

    if https:
        config_fps = config_fps + ["https.yaml"]

    config_fps = [
        os.path.join(STRUCTURE["templates"]["hub"], config) for config in config_fps
    ]

    return config_fps


def __add_config_content(hub_deploy_dir, template_fp, placeholder_replacements):
    output_fp = os.path.join(hub_deploy_dir, "config.yaml")
    fill_file_placeholders(template_fp, output_fp, placeholder_replacements)


def __build_template(hub_deploy_dir, config_fps):
    output_fp = os.path.join(hub_deploy_dir, "template.yaml")

    with open(output_fp, "wt") as output_file:
        for config_fp in config_fps:
            with open(config_fp, "rt") as input_file:
                input_file_content = input_file.read()
                output_file.write(input_file_content)

    return output_fp


def __add_helm_chart_config(helm_deploy_dir):
    load_dotenv()

    repo_template_fp = os.path.join(STRUCTURE["templates"]["helm"], "chart.yaml")
    repo_deploy_fp = os.path.join(helm_deploy_dir, "chart.yaml")
    copy_file(repo_template_fp, repo_deploy_fp)
