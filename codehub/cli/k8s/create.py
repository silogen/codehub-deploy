from kubernetes import client as k8s_client
import os
from codehub.cli.helpers import read_yaml, fill_file_placeholders
from codehub.cli.config import STRUCTURE, DeployConfig


def create_k8s_resources(deploy_config: DeployConfig):
    k8s_dir = deploy_config.k8s_dir

    __create_cluster_role_binding(k8s_dir)

    namespace = read_yaml(
        os.path.join(STRUCTURE["templates"]["k8s"], "namespace.yaml")
    )["metadata"]["name"]

    placeholder_replacements = {"NAMESPACE": namespace}

    __create_namespace(k8s_dir, placeholder_replacements)
    __create_pvs(
        k8s_dir,
        deploy_config.cloud_state.nfs_name,
        deploy_config.cloud_state.nfs_ip,
        placeholder_replacements,
    )
    __create_pvcs(k8s_dir, placeholder_replacements)


def __create_cluster_role_binding(k8s_deploy_path):
    __create_k8s_resource_from_template(
        client_call=k8s_client.RbacAuthorizationV1Api(
            k8s_client.ApiClient()
        ).create_cluster_role_binding,
        k8s_deploy_path=k8s_deploy_path,
        template="clusterrolebinding.yaml",
    )


def __create_namespace(k8s_deploy_path, placeholder_replacements):
    __create_k8s_resource_from_template(
        client_call=k8s_client.CoreV1Api().create_namespace,
        k8s_deploy_path=k8s_deploy_path,
        template="namespace.yaml",
        placeholder_replacements=placeholder_replacements,
    )


def __create_pvs(k8s_deploy_path, nfs_name, nfs_ip, placeholder_replacements):
    placeholder_replacements["FILESTORE_NAME"] = nfs_name
    placeholder_replacements["FILESTORE_IP_ADDRESS"] = nfs_ip

    for pv in ["pv-personal.yaml", "pv-shared.yaml"]:
        __create_k8s_resource_from_template(
            client_call=k8s_client.CoreV1Api().create_persistent_volume,
            k8s_deploy_path=k8s_deploy_path,
            template=pv,
            placeholder_replacements=placeholder_replacements,
        )


def __create_pvcs(k8s_deploy_path, placeholder_replacements):
    for pvc in ["pvc-personal.yaml", "pvc-shared.yaml"]:
        __create_k8s_resource_from_template(
            client_call=k8s_client.CoreV1Api().create_namespaced_persistent_volume_claim,
            k8s_deploy_path=k8s_deploy_path,
            template=pvc,
            placeholder_replacements=placeholder_replacements,
            namespace=placeholder_replacements["NAMESPACE"],
        )


def __create_k8s_resource_from_template(
    client_call, k8s_deploy_path, template, placeholder_replacements={}, **kwargs
):
    input_fp = os.path.join(STRUCTURE["templates"]["k8s"], template)
    output_fp = os.path.join(k8s_deploy_path, template)

    fill_file_placeholders(input_fp, output_fp, placeholder_replacements)
    conf = read_yaml(fp=os.path.join(k8s_deploy_path, template))
    client_call(body=conf, **kwargs)
