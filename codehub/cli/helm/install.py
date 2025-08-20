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
    install_template_fp = os.path.join(STRUCTURE["templates"]["helm"], "install.yaml")
    install_deploy_fp = os.path.join(helm_deploy_dir, "install.yaml")

    placeholder_replacements = dict(REGION=region)
    fill_file_placeholders(
        install_template_fp, install_deploy_fp, placeholder_replacements
    )

    helm = read_yaml(install_deploy_fp)

    chart_release = helm["release"]
    cluster_namespace = helm["namespace"]
    region = helm["region"]

    helm_chart = os.path.join(helm_deploy_dir, "helm-chart")

    config_file = os.path.join(hub_deploy_dir, "config.yaml")

    cmds = []
    cmds.append(
        [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            f"--location={region}",
            cluster_name,
        ]
    )

    if upgrade:
        cmds.append(
            [
                "helm",
                "upgrade",
                "--cleanup-on-fail",
                chart_release,
                helm_chart,
                "--namespace",
                cluster_namespace,
                "--values",
                config_file,
            ]
        )
    else:
        cmds.append(
            [
                "helm",
                "upgrade",
                "--cleanup-on-fail",
                "--install",
                chart_release,
                helm_chart,
                "--namespace",
                cluster_namespace,
                "--values",
                config_file,
            ]
        )

    for cmd in cmds:
        run_cmd(cmd)
