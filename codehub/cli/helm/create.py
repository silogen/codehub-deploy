import os
from secrets import token_hex
from dotenv import load_dotenv
from codehub.cli.gcp.terraform import TerraformOutput
from codehub.cli.helpers import read_yaml, run_cmd, copy_file, fill_file_placeholders
from codehub.cli.config import STRUCTURE


def create_deploy(
    cluster_name,
    hub_deploy_dir,
    helm_deploy_dir,
    cloud_state: TerraformOutput,
    contact_email=None,
    https=None,
    client_id=None,
    client_secret=None,
    admins=[],
):
    config_fps = __get_config_fps(https=https, oauth=(client_id and client_secret))
    template_fp = __build_template(hub_deploy_dir, config_fps)

    placeholder_replacements = read_yaml(
        os.path.join(STRUCTURE["templates"]["hub"], "config_variables.yaml")
    )
    placeholder_replacements["SECRET_TOKEN"] = token_hex(32)
    placeholder_replacements["CLUSTER_NAME"] = cluster_name
    placeholder_replacements["HOST_NAME"] = https
    placeholder_replacements["CONTACT_EMAIL"] = contact_email
    placeholder_replacements["GITHUB_OAUTH_CLIENT_ID"] = client_id
    placeholder_replacements["GITHUB_OAUTH_CLIENT_SECRET"] = client_secret

    if "admin" not in admins:
        admins.append("admin")

    def admin_to_yaml_str(admin):
        return f"\n{' ' * 6}- {admin}"

    placeholder_replacements["HUB_ADMINS"] = "".join(
        [admin_to_yaml_str(admin) for admin in admins]
    )
    placeholder_replacements["SUDOERS"] = " ".join(admins)

    placeholder_replacements["REGISTRY_HOSTNAME"] = cloud_state.docker_registry_hostname
    # The spaces after newline are important for the indentation in the yaml file
    placeholder_replacements["REGISTRY_PASSWORD"] = cloud_state.hub_sa_key.replace(
        "\n", "\n    "
    )
    placeholder_replacements["DOCKER_IMAGE"] = cloud_state.docker_image

    if "DOCKER_IMAGE_TAG" not in placeholder_replacements:
        placeholder_replacements["DOCKER_IMAGE_TAG"] = "stable"

    __add_config_content(hub_deploy_dir, template_fp, placeholder_replacements)

    __download_helm_chart(helm_deploy_dir)


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


def __download_helm_chart(helm_deploy_dir):
    load_dotenv()

    repo_template_fp = os.path.join(STRUCTURE["templates"]["helm"], "repo.yaml")
    repo_deploy_fp = os.path.join(helm_deploy_dir, "repo.yaml")
    copy_file(repo_template_fp, repo_deploy_fp)

    k8s_conf = read_yaml(repo_deploy_fp)
    jupyterhub_url = k8s_conf["url"]
    k8s_hash = k8s_conf["hash"]

    jupyterhub_repo = os.path.join(helm_deploy_dir, "jupyterhub_repo")
    helm_chart = os.path.join(helm_deploy_dir, "helm-chart")

    cmds = [
        ["git", "clone", jupyterhub_url, jupyterhub_repo],
        ["cd", jupyterhub_repo, "&&", "git", "reset", "--hard", k8s_hash],
        ["mv", os.path.join(jupyterhub_repo, "jupyterhub"), helm_chart],
        ["rm", "-rf", os.path.join(jupyterhub_repo)],
    ]

    for cmd in cmds:
        run_cmd(cmd)

    files_to_replace = ["Chart.yaml", "values.yaml"]
    for fn in files_to_replace:
        fp = os.path.join(helm_chart, fn)
        with open(fp) as f:
            newText = (
                f.read()
                .replace("set.by.chartpress", "2.0.0")
                .replace("set-by-chartpress", "2.0.0")
            )
        with open(fp, "w") as f:
            f.write(newText)

    return helm_chart
