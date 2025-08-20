## Python GCP deployment instructions

This assumes you have the following installed locally:
* docker
* helm (tested with v3)
* kubectl
* gcloud

---

### 1. Set up project:

1. Create GCP project
2. Enable Kubernetes Engine
3. Enable Cloud Filestore API


### 2. Deploy

1. Create a new key on the service account `test-deploy` in the GCP project. Your JSON key-file will be automatically saved to your computer. Move it to `secrets/gcp`, rename it to `service-account.json` and authenticate your gcloud CLI with:
    ```sh
    gcloud auth activate-service-account --key-file secrets/gcp/service-account.json
    ```
2. Create and enter conda environment:
    ```sh
    conda env create -f dev_environment.yml
    conda activate codehub
    ```
3. Install CLI:
    ```sh
    pip install --editable .
    ```
4. You can now use the CLI by typing:
    1. Create cluster
        ```sh
        codehub createcluster -n <cluster-name>
        ```
    2. Upgrade cluster
        ```sh
        codehub upgradecluster -n <cluster-name>
        ```
    3. Scale cluster
        ```sh
        codehub scalecluster -n <cluster-name>
        ```
    4. Delete cluster
        ```sh
        codehub deletecluster -n <cluster-name>
        ```
    5. Delete nfs
        ```sh
        codehub deletefs -n <cluster-name>
        ```
    6. Get cluster IP
        ```sh
        codehub getip -n <cluster-name>
        ```
