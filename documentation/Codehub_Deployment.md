# Creating a cluster for a Campus

### 1. Setting up codehub-deployment environment

#### A. Install required packages

Installing and using the `codehub` CLI requires the following:

- [git](https://www.git-scm.com)
- [conda](https://docs.conda.io/en/latest/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud)
- [opentofu](https://opentofu.org/)
- Install the `gke-gcloud-auth-plugin` gcloud component

Few things needs to be done before:

1. `gcloud auth activate-service-account --key-file secrets/gcp/service-account.json`
2. `gcloud config set project <project name>`

#### B. Install the codehub cli

I cannot install easily python 3.7.6, thus I have decided to bump the version to `python 3.9.10`. Python 3.10.X cannot be used yet as there are some problems with `grcp`.

I'm using pyenv for python version management. So, I have done the following:

```sh
pyenv install 3.9.10
pyenv local 3.9.10
python -m venv .codehub
source .codehub/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r dev_requirements.txt
pip install -e .
```

### Creating cluster

1. Create the cluster:

```sh
codehub createcluster -n <cluster-name> -r <region>
```

2. Monitoring a created cluster

```sh
gcloud container clusters list
gcloud container clusters get-credentials <cluster-name> --location=europe-north1
kubectl -n jhub get pods
```

You can also have a look at the [Kubernetes Engine Product page of your project](https://console.cloud.google.com/kubernetes/list/overview)
I see that VM instances have been created. We request by default 3 nodes, it can be seen [here](https://console.cloud.google.com/compute/instances)

3. Upgrade the cluster to allow https and use the Github OAUTH

1. **Add https**: Once the cluster is created, at the end of the stdout, you will see an IP address. You need to link this IP address to a DNS record.

1. **Github OAUTH**: To create a new OAuth app on GitHub, visit the following: [https://github.com/settings/developers](https://github.com/settings/developers) > Oauth apps > New OAuth App.
   There, you will need to provide information about your app, its name, homepage URL and callback URL. For details see [https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) .
   Ensure that the callback URL points to the hub of your deployment as it is responsible for handling the authentication of users to the JupyterHub. The logo of the app can be found in the `assets` folder of the `codehub-deployment` repository. Once you have provided all this information, you can generate a client secret for your app. Please save the client secret in a secure place as it is only visible once.

1. Upgrade the cluster with the OAuth app and the dns record to you JupyterHub. In the example below, I have the following client id: `1234` and client secret: `4321` To upgrade the `codehubdev` cluster, I will run the following command:

```sh
codehub upgradecluster -n codehubdevOld --https developer.codehub.company.ai --client-id 1234 --client-secret 4321 --admin admin --admin my-github-user
```

Be sure to add all admins to this command including the `admin` user. A set of pods will be created and updated including the `autohttps-x-x` and `hub-x-x` pods.

You have now an up and running cluster.
