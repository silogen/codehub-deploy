from codehub.cli.gcp.terraform import terraform_destroy
from codehub.cli.helpers import get_cloud_dir


def delete(name):
    terraform_destroy(cloud_dir=get_cloud_dir(name))
