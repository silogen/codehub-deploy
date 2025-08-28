import dataclasses
import json
import os
from typing import Any, List, Optional
from distutils.dir_util import copy_tree
from codehub.cli.config import STRUCTURE, CreateConfig
from codehub.cli.helpers import (
    fill_file_placeholders,
    run_cmd,
    run_cmd_passthrough_stdout,
)


@dataclasses.dataclass
class TerraformOutput:
    nfs_ip: str
    nfs_name: str
    cluster_id: str
    hub_sa_key: str
    cluster_endpoint: str
    cluster_cert: str
    gcp_token: str
    docker_registry_hostname: str
    docker_image: str


def setup_terraform(
    *,
    config: CreateConfig,
    cloud_dir: str,
) -> None:
    copy_tree(STRUCTURE["templates"]["cloud"], cloud_dir)

    gcp_sa_path = STRUCTURE["secrets"]["gcp"]["sa"]
    gcp_project = _get_project_from_sa(gcp_sa_path)

    placeholder_replacements = dict(
        CLUSTER_NAME=config.name,
        REGION=config.region,
        ZONE=config.zone,
        MACHINE_TYPE=config.machine_type,
        GCP_SA_PATH=gcp_sa_path,
        GCP_PROJECT_NAME=gcp_project,
    )

    variable_file_path = os.path.join(cloud_dir, "variables.tfvars")
    fill_file_placeholders(
        variable_file_path,
        variable_file_path,
        placeholder_replacements=placeholder_replacements,
    )


def terraform_apply(
    *,
    cloud_dir: str,
    additional_vars: Optional[dict[str, Any]] = None,
) -> TerraformOutput:
    terraform_cmd = _terraform_cmd(cloud_dir)
    run_cmd(terraform_cmd + ["init"])

    apply_cmd = terraform_cmd + [
        "apply",
        "--var-file=variables.tfvars",
        "-input=false",
        "-auto-approve",
    ]
    if additional_vars:
        apply_cmd += [f"-var='{var}={val}'" for var, val in additional_vars.items()]

    run_cmd_passthrough_stdout(apply_cmd)
    return terraform_output(cloud_dir=cloud_dir)


def terraform_destroy(*, cloud_dir: str):
    run_cmd_passthrough_stdout(
        _terraform_cmd(cloud_dir)
        + [
            "destroy",
            "--var-file=variables.tfvars",
            "-input=false",
            "-auto-approve",
        ]
    )


def terraform_output(*, cloud_dir: str) -> TerraformOutput:
    command = _terraform_cmd(cloud_dir) + ["output", "-json"]
    terraform_output: dict[str, dict[str, Any]] = json.loads(
        run_cmd(command, verbose=False)
    )
    output = {key: val_dict["value"] for key, val_dict in terraform_output.items()}
    return TerraformOutput(**output)


def _get_project_from_sa(gcp_sa_path: str) -> str:
    with open(gcp_sa_path, "r") as key_file:
        return json.load(key_file)["project_id"]


def _terraform_cmd(cloud_dir: str) -> List[str]:
    return ["tofu", f"-chdir={cloud_dir}"]
