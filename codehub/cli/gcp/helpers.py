import os
import base64
from codehub.cli.gcp.terraform import terraform_output
from google.oauth2.service_account import Credentials as SACredentials
from kubernetes.client import Configuration as K8SConfiguration
from codehub.cli.config import STRUCTURE
from codehub.cli.helpers import get_cloud_dir


def authenticate_k8s_GKE(name):
    cloud_state = terraform_output(cloud_dir=get_cloud_dir(name))
    gcp_secrets = STRUCTURE["secrets"]["gcp"]

    ssl_ca_cert_path = gcp_secrets["cert"]
    __write_cluster_cert(cloud_state.cluster_cert, ssl_ca_cert_path)

    kubeconfig = K8SConfiguration()
    kubeconfig.host = f"https://{cloud_state.cluster_endpoint}"
    kubeconfig.ssl_ca_cert = ssl_ca_cert_path

    # The same service account is used in terraform and for k8s access
    kubeconfig_creds = SACredentials.from_service_account_file(
        gcp_secrets["sa"],
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
    )
    kubeconfig_creds.apply(kubeconfig.api_key, token=cloud_state.gcp_token)

    K8SConfiguration.set_default(kubeconfig)


def __write_cluster_cert(cluster_cert, path):
    try:
        os.remove(path)
    except OSError:
        pass

    cert = base64.b64decode(cluster_cert)
    cert_file = open(path, "wb")
    cert_file.write(cert)
    cert_file.close()
