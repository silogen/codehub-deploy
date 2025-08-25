import os
from codehub.cli.helpers import run_cmd, read_yaml, fill_file_placeholders
from codehub.cli.config import STRUCTURE


def install_helm_chart(cluster_name, region, helm_deploy_dir, hub_deploy_dir):
    __upgrade_or_install_helm_chart(
        cluster_name, region, helm_deploy_dir, hub_deploy_dir, upgrade=False
    )


def upgrade_helm_chart(cluster_name, region, helm_deploy_dir, hub_deploy_dir):
    __upgrade_or_install_helm_chart(
        cluster_name, region, helm_deploy_dir, hub_deploy_dir, upgrade=True
    )


def __upgrade_or_install_helm_chart(
    cluster_name, region, helm_deploy_dir, hub_deploy_dir, upgrade=False
):
    chart_template_fp = os.path.join(STRUCTURE["templates"]["helm"], "chart.yaml")
    chart_deploy_fp = os.path.join(helm_deploy_dir, "chart.yaml")

    placeholder_replacements = dict(REGION=region)
    fill_file_placeholders(chart_template_fp, chart_deploy_fp, placeholder_replacements)

    helm_config = read_yaml(chart_deploy_fp)
    repo_config = helm_config["repo"]
    install_config = helm_config["install"]

    config_file = os.path.join(hub_deploy_dir, "config.yaml")

    cmds = []
    cmds.append(
        [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            f"--location={install_config['region']}",
            cluster_name,
        ]
    )

    # Add and update Helm repo
    cmds.append(["helm", "repo", "add", repo_config["repo_name"], repo_config["url"]])
    cmds.append(["helm", "repo", "update"])

    # Main helm command
    helm_command = [
        "helm",
        "upgrade",
        "--cleanup-on-fail",
    ]
    if not upgrade:
        helm_command.append("--install")
    helm_command += [
        install_config["release"],
        f"{repo_config['repo_name']}/{install_config['chart_name']}",
        "--namespace",
        install_config["namespace"],
        "--version",
        install_config["chart_version"],
        "--values",
        config_file,
    ]
    cmds.append(helm_command)

    for cmd in cmds:
        run_cmd(cmd)
