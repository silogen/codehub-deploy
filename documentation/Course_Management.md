# Managing a codehub cluster

There are 3 main repositories for managing the cluster

1. `codehub-deployment` - campus platform management, infrastructure
2. `ds-capus-redesign` - Material for the DS Campus, from where we distribute the course
3. `codehub-notebook-env` - handling the campus

## Adding users

1. Get the list of users and their github usernames from the Program Manager (Maria Colell).
2. Check the validity of the Github accounts
   a. Copy and paste all of the usernames to a `.txt` file, e.g. `<campus_name>_students.txt`, `ads17_students.txt`.
   b. Then proceed with the categorisation of the list of IDs into two categories; valid and invalid:

```shell
sh check_students.sh <campus_name>_student.txt <your-gh-access-token>
```

The above script generates two text files: `valid_<campus_name>_list.txt` and `invalid_<campus_name>_list.txt`. For invalid IDs, discuss with the course manager to request the updated student ID.

To check individual IDs you can use the following command:

```shell
sh check_github_users.sh <your-gh-access-token> <student-github-id>
```

3. Add the valid student github IDs to the hub either from the UI or by using the helm upgrade cluster command.

```sh
cat valid_ads15_students.txt
```

to get the accounts and add on the UI

OR

Add the participants to the `hub/config.yaml` under the `allowed_users:` tag and run an upgrade of the release.

```sh
helm upgrade --cleanup-on-fail \
  jhub <your-latest-deployment-absolute-path>/helm/helm-chart \
  --namespace jhub \
  --values <your-latest-deployment-absolute-path>/hub/config.yaml
```

A new release of the hub has now been created.

# Uploading the Course Content and Distributing the weekly Assignments

## Uploading the Course Content

Once all of the users have been added, **start all servers** on the JupyterHub Control panel (if there are multiple pages make sure to go to the next one and **start all servers** there as well).

1. Make sure that all of the servers have been started.
2. Become the admin user and start a terminal.
3. If it is the first time (at the start of a course) run : `cds init`
4. Clone the repository that contains all of the course's content.

````sh
git clone https://github.com/combient/enablement-ads.git
cp -R ds-campus-redesigned/Platform_Material/Assignments/* course/source/
cp -R ds-campus-redesigned/Data/* Data/
cp -R ds-campus-redesigned/Platform_Material/Self_Study_Material/ Self_Study_Material/
```

Note: Make sure that the Data folders has the right permissions (if it's `root root`, then change those by running `chown -R jovyan Data`, and run the `cp` command again).

5. Distribute the Data to the students.

```sh
cds send Data
````

6. Make sure that the students have permission to access the directories containing the course materials.

7. Change the ownership of the folders that contain the course materials from `root` to `jovyan`.

```sh
sudo su
cd /efs/home
vi list_users.txt
```

paste the list of student usernames to the `list_users.txt` file. Then run

```sh
for n in `cat list_students.txt`; do chown -R jovyan /efs/home/$n; done
```

Check that the user owning the folders is now `jovyan`. Access one of the servers that corresponds to a student at random and ensure that the content of the Data, Supplementary_Notebooks_for_Modules and Self_Study_Material is now visible.

## Distributing the Weekly Assignments and Reading Materials

Every week the students receive a weekly assignment that they have to submit and the relevant reading materials. We usually distribute the assignment the Wednesday before the week that the assignment refers to. Similarly with the Reading Materials.

To generate, release and distribute the Assignment and Reading Materials of the week run:

```sh
cds assignment generate $Assignment
cds assignment release $Assignment
cds assignment distribute $Assignment
cds send Self_Study_Material/$Module
```

In one of the servers make sure that the corresponding assignment and reading materials have been made available.

## Uploading the compressed Data

At the end of the campus, the users are provided with a zip file containing the data.
To zip the data folder:

```sh
sudo su
apt-get install zip
zip -r data.zip Data
```

and then send the zipped data to the users:

```
cds send data.zip
```

## For late admissions

If a new user get admitted after the above steps have been completed follow the instructions below to repeat the process for the single user:

Start the user's server. Add the following code in a script called `add_new_user.sh`:

```sh
#!/bin/bash
Assignments=$2
Modules=$3

echo "Distributing Data to $1"
cds send Data -u $1

IFS=,
for Assignment, Module in $Assignments, $Modules;
do
    echo "Distribute $Assignment to $1"
    cds assignment distribute $Assignment -u $1
    echo "Distributing Self Study Materials to $1"
    cds send Self_Study_Material/$Module -u $1
done
```

Run the script:

`sh add_new_user.sh dummy_user Assignment1,Assignment2 Module1,Module2`

(Note: Define the list of assignments as comma separated values (without a whitespace))

Finally, give the newly added user persmissions to access the course materils:

```sh
sudo su
cd /efs/home
chown -R jovyan /efs/home/<username>
```
