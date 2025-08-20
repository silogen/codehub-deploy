### Checklist for Deploying a Cluster for a New Cohort

1. Create a cluster with name <cohort_name> using the `codehub` cli (`codehub create ...`).
2. Check the status of the cluster using the gcp cli `gcloud`. It should be "Running".
3. Fetch the ip address assigned to the cluster using the `codehub` cli (`codehub getip ... `).
4. Create a GitHub OATH app and generate a client secret.
5. Ask the DNS administrator to bind the cluster's ip to the given https. Upgrade the cluster and add all admins users, https and the client id and secret from the OATH app using the `codehub` cli (`codehub upgrade ...`).
6. Validate all GitHub usernames using the script `check_students.sh`.
7. Locate the deployment snapshot in the deployments folder and navigate to the `config.yaml` file in the `hub` folder. Add all valid GitHub usernames under the `allowed_users` tag.
8. Update the cluster by running the `helm upgrade ... ` command, which add all of the listed users.
9. Access the cluster from the browser and login using your GitHub username.
10. Start the admin server and start a terminal window.
11. Verify that the `cds` cli is installed by running the command `which cds`.
12. Navigate to the admin page of the control panel and start all the servers. Go back to the terminal and initialise `cds` by running `cds init`.
13. Clone the repository that has the contents of the given course.
14. Copy the contents of the repository in the respective directories (`course/source`, etc.)
15. Distribute the `Data`, `Learning Materials 1`, `Assignment 1`.
16. Create a `.txt` file that lists all of the student usernames.
17. Give the students read permissions to the files by changing the ownership of the files `root -> jovyan`.
18. Start a user's server at random and verify that you can see the distributed resources.

You have now completed the setup for the new cohort!
