# codehub-deployment

This repository contains the `codehub` CLI used to deploy the _CodeHub_
platform to Kubernetes. This README file summarizes installing, using and
developing the `codehub` CLI. More detailed information can be found in
the repository's Wiki pages.

## Requirements

Installing and using the `codehub` CLI requires the following:

- [git](https://www.git-scm.com)
- [conda](https://docs.conda.io/en/latest/) (or other python environment manager)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud)
- [gke-gcloud-auth-plugin](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)
- [opentofu](https://opentofu.org/)

## Installation

1. Clone the repository using Git.
2. Inside the repository's root folder, create a Conda environment with the
   required development requirements installed with the following command:

   ```sh
   conda env create -f dev_environment.yml
   ```

3. Activate the newly created Conda environment by running:

   ```sh
   conda activate codehub
   ```

4. Install the `codehub` CLI with:

   ```sh
   pip install -e .
   ```

## Alternative installation

Alternatively, you can create a virtual environment with virtualenv using the following instructions

```shell
pyenv install 3.9.10
pyenv local 3.9.10
pip install virtualenv
python -m venv .codehub
source .codehub/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r dev_requirements.txt
pip install -e .
```

## Dockerized CodeHub CLI

The dockerized version requires Docker only, and the rest of the tools will be installed into the container automatically.
Do the initial secrets setup from the _Usage_ parts 1—4 of the document, then you can use:

```sh
./dep.sh
```

Run it without any parameters to build (if necessary), start, and connect to the container.
After you terminate the initial instance, the container will automatically shut down.
If the container is already running, the script will connect you to it.

To perform force rebuild the image, use:

```sh
./dep.sh --rebuild
```

After building the proper image, it will connect you to the container, and all of the environment will be set up.

## Usage

Before you can use the CLI to deploy the CodeHub platform you need to set up a
number of secrets to grant you and the deployment access to the necessary
resources.

1. Go to [GCP Console Service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) and select the correct project.
   Ensure that a Service Account with sufficient permissions exists,
   go to the Keys tab -> Add key -> Create new key -> JSON.

   Store the JSON key-file as
   `service-account.json` in the `secrets/gcp` directory. Authenticate your
   `gcloud` CLI with the key by running:

   ```sh
   gcloud auth activate-service-account --key-file secrets/gcp/service-account.json
   ```

   - A sufficient list of permissions is `Artifact Registry Administrator`, `Cloud Filestore Editor`, `Cloud Filestore Viewer`, `Compute Admin`, `Create Service Accounts`, `Delete Service Accounts`, `Kubernetes Engine Admin`, `Service Account Key Admin`, `Service Account User`, `Storage Admin`

2. Set the correct project in your `gcloud` CLI by running:

   ```sh
   gcloud config set project <your-project-id>
   ```

3. Test the setup by creating and then deleting a new cluster (optional). The process can take ~10 minutes, check progress on the [Kubernetes clusters page](https://console.cloud.google.com/kubernetes/list/overview). Run the following commands:

   ```sh
   codehub createcluster --name mytestcluster -r europe-north1 && \
   codehub deletecluster --name mytestcluster
   ```

The main entrypoint for the CLI is the command `codehub`. For some more
information on this command as well as the available subcommands you can run

```sh
codehub --help
```

Available subcommands are the following:

1. `createcluster`: Used for creating a new CodeHub deployment and its
   associated cloud resources. Requires a cluster name using the option `-n <name>`
   or `--name <name>` (up to 14 alphanumeric symbols) and accepts the name of an admin user for CodeHub
   using the option `-a <admin>` or `--admin <admin>`. The `--admin` option can
   be supplied multiple times to create multiple admin users. For more
   information about this subcommand run:

   ```sh
   codehub createcluster --help
   ```

2. `deletecluster`: Used for deleting a CodeHub deployment and its associated
   cloud resources. Requires a cluster name using the option `-n <name>` or
   `--name <name>`. For more information about this subcommand run:

   ```sh
   codehub deletecluster --help
   ```

3. `getip`: Used for getting the IP of the entrypoint for a CodeHub deployment.
   Requires a cluster name using the option `-n <name>` or `--name <name>`. For
   more information about this subcommand run:

   ```sh
   codehub getip --help
   ```

4. `scalecluster`: Used for manually changing the node pool size and the down
   scaling behaviour of the autoscaler. Requires a cluster name using the option
   `-n <name>` or `--name <name>` and a number of nodes using the option
   `--nodes <num of nodes>`. Also accepts the `--down` flag to
   specify that the autoscaler should be able to scale down to 0. For more
   information about this subcommand run:

   ```sh
   codehub scalecluster --help
   ```

5. `upgradecluster`: Used to change the cluster and Kubernetes configuration of
   a CodeHub deployment. Requires a cluster name using the option `-n <name>` or
   `--name <name>`. Also accepts the option `--https <hostname>` to set up https
   for hostname `<hostname>`, `--client-id <client id>` and `--client-secret
<client secret>` to enable GitHub OAuth2 authentication, `-a <admin>` or
   `--admin <admin>` to set new admins. For more information about this subcommand run:

   ```sh
   codehub upgradecluster --help
   ```

Further configuration is done by modifying the YAML files in the
`dscampus/templates` folder.

### Example

Create a cluster named `examplecluster` with admin users `admin1` and `admin2`
using the command

```sh
codehub createcluster --name examplecluster --admin admin1 --admin admin2
```

Once the deployment is complete the IP of the entrypoint will be printed to
terminal. At this point you can go to that IP and login as either `admin1` or
`admin2` without a password to test the deployment.

To add https support to the deployment use

```sh
codehub upgradecluster --name examplecluster \
                              --admin admin1 \
                              --admin admin2 \
                              --https example.hostname.com
```

This will deploy a Let's Encrypt tls certificate valid for the hostname
`example.hostname.com`.

To add GitHub OAuth2 authentication using a GitHub OAuth app with client id
`<client id>` and client secret `<client secret>` use the command

```sh
codehub upgradecluster --name examplecluster \
                             --admin admin1 \
                             --admin admin2 \
                             --https example.hostname.com \
                             --client-id <client id> \
                             --client-secret <client secret>
```

Delete the deployment and associated resources using the command

```sh
codehub deletecluster --name examplecluster
```

### Checking GitHub usernames

There is a script for checking if a list of GitHub usernames exist and report
the ones that do not.

To use it, a GitHub access token is required and there is a limit of 6000
requests per hour. The user list needs to be separated by commas.

```sh
./check_github_users.sh <GITHUB_ACCESS_TOKEN> "user1, user2, ..."
```

### Notable issues

Sometimes the SSL certificate does not generate properly, this can usually be
fixed by restarting the load balancer: `kubectl -n jhub delete pod autohttps-<id>`

## Development

### Issues and project

GitHub Issues are used to create and track issues and feature requests for the
repository.

### Branches

There are two main branches:

- `develop`: Development branch. Changes to the repository are frequently merged
  into the `develop` branch by pull requests from temporary branches after
  review.
- `acceptance`: Branch for accepting features to be merged into master. Changes in the develop branch are merged into the
  `acceptance` branch by pull requests in order to thoroughly check features and feature changes.
- `master`: The current release of the repository. Can only be changes by
  merging a pull request from the `acceptance` branch after review.

Temporary branches conform to the following naming convention:

- `bugfix/XYZ`: Designated for bugfixes.
- `feature/XYZ`: Designated for addition of new features.
- `refactor/XYZ`: Designated for refactoring work.
- `docs/XYZ`: Designated for updates to the documentation.

`XYZ` should be descriptive enough to identify what the changes relate to.

### Workflow

Use the following workflow when solving an issue:

1. Make sure you are on the `develop` branch and that you have pulled all the
   latest changes to your local git repository.
2. Create a new temporary branch from the `develop` branch following the above
   naming convention using e.g.

   ```sh
   git switch -c feature/XYZ
   ```

3. Make and commit your changes to the temporary branch.
4. Push your temporary branch to the GitHub repository.
5. Open a pull request to merge the changes from your temporary branch into the
   `develop` branch. Make sure to request at least one reviewer and mention
   which issue will be closed by this pull request.
6. After the changes have been accepted by the reviewer, merge the changes and
   delete the temporary branch after merging.

When preparing for a release use the following workflow:

1. Make sure all intended changes are merged into `develop`.
2. Create a pull request to merge changes from `develop` into `acceptance` with all
   current developers as reviewers.
3. Merge the changes after the review is accepted.
4. Test the current state of the repository thoroughly to make sure everything
   works as intended. If any issues are found make the changes to the `develop`
   branch and repeat step 2.
5. Create a pull request to merge `acceptance` into `master` with all current
   developers as reviewers.
6. Merge the changes after the review is accepted.
7. Create a release on GitHub named `vX.Y.Z` according to semantic versioning
   and tag the corresponding commit with the release tag.
8. Merge the release tag back into `develop` for continued development.

### Continuous integration

The project has continuous integration set up in the form of automatic linting
with `flake8` using GitHub actions. Linting will be run on every push and pull
request. To run the tests locally before pushing changes to the repository, run
the following:

```sh
flake8 .
```
