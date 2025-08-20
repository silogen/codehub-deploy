import click
import logging
import sys
from codehub.cli.create import create, upgrade, scale, create_infrastructure
from codehub.cli.delete import delete
from codehub.cli.helpers import check_commands, validate_cluster_name, check_credentials
from codehub.cli.manage import get_ip


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    logger = logging.getLogger(__name__)

    if not check_commands():
        logger.critical("Some commands are not available. Exiting.")
        sys.exit(1)

    if not check_credentials():
        logger.critical("Some credentials not set correctly. Exiting.")
        sys.exit(1)

    if ctx.invoked_subcommand is None:
        logger.warning("CLI invoked without subcommand")
    else:
        logger.info(f"Running command: {ctx.invoked_subcommand}")


@cli.command()
@click.option("--name", "-n", required=True)
@click.option("--admin", "-a", required=False, multiple=True, default=[])
@click.option("--region", "-r", required=False, default="europe-north1")
@click.option("--zone", "-z", required=False, default="europe-north1-a")
@click.option("--machine-type", "-m", required=False, default="e2-standard-2")
def createcluster(name, admin, region, zone, machine_type):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)
    logger.info(f"Creating cluster '{name}'")

    admins = [i.lower() for i in admin]

    res = create(
        name=name,
        admins=admins,
        region=region,
        zone=zone,
        machine_type=machine_type,
    )

    logger.debug(f"{create.__module__}.{create.__name__} output:")
    logger.debug(res)

    logger.info(f"Cluster '{name}' created successfully")


@cli.command()
@click.option("--name", "-n", required=True)
@click.option("--https", required=False)
@click.option("--client-id", required=False)
@click.option("--client-secret", required=False)
@click.option("--admin", "-a", required=False, multiple=True)
def upgradecluster(name, admin, https=None, client_id=None, client_secret=None):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)
    logger.info(f"Updating cluster '{name}'")

    https_passed = https is not None
    client_id_passed = client_id is not None
    client_secret_passed = client_secret is not None
    passed_correct_args = https_passed and (client_id_passed is client_secret_passed)
    passed_no_args = not https_passed and not (client_id_passed or client_secret_passed)

    admins = [i.lower() for i in admin]

    if passed_correct_args or passed_no_args:
        res = upgrade(
            name=name,
            admins=admins,
            https=https,
            client_id=client_id,
            client_secret=client_secret,
        )

        logger.debug(f"{upgrade.__module__}.{upgrade.__name__} output:")
        logger.debug(res)

        logger.info(f"Cluster '{name}' upgraded successfully")
    else:
        logger.warning("To add oauth you need to pass the following arguments")
        logger.warning("`--https` <host-name>")
        logger.warning("`--client-id` <github-client-id>")
        logger.warning("`--client-secret` <github-client-secret>")


@cli.command()
@click.option("--name", "-n", required=True)
@click.option("--nodes", required=True)
@click.option("--down", is_flag=True, required=False)
def scalecluster(name, nodes, down=True):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)
    logger.info(f"Scaling cluster '{name}'")
    res = scale(name=name, nodes=nodes, down_scale=down)
    logger.debug(f"{scale.__module__}.{scale.__name__} output:")
    logger.debug(res)
    logger.info(f"Cluster '{name}' scaled successfully")


@cli.command()
@click.option("--name", "-n", required=True)
def deletecluster(name):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)

    click.confirm(
        f"Cluster '{name}' will be deleted. Do you want to continue?",
        default=False,
        abort=True,
        show_default=True,
    )

    logger.info(f"Deleting cluster '{name}'")

    res = delete(
        name=name,
    )
    logger.debug(f"{delete.__module__}.{delete.__name__} output:")
    logger.debug(res)

    logger.info(f"Cluster '{name}' deleted successfully")


@cli.command()
@click.option("--name", "-n", required=True)
def getip(name):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)

    logger.info(f"Getting the IP of cluster '{name}'")
    res = get_ip(
        name=name,
    )
    logger.info(f"Cluster '{name}' IP address: {res}")


@cli.command()
@click.option("--name", "-n", required=True)
@click.option("--region", "-r", required=False, default="europe-north1")
@click.option("--zone", "-z", required=False, default="europe-north1-a")
@click.option("--machine-type", "-m", required=False, default="n1-standard-2")
def createclusterinfra(name, region, zone, machine_type):
    name = validate_cluster_name(name)
    logger = logging.getLogger(__name__)
    logger.info(f"Creating cluster '{name}'")

    res = create_infrastructure(
        name=name,
        region=region,
        zone=zone,
        machine_type=machine_type,
    )

    logger.debug(f"{create.__module__}.{create.__name__} output:")
    logger.debug(res)

    logger.info(f"Cluster '{name}' created successfully")
