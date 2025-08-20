#!/bin/zsh

# Check if service account file exists
if [ ! -f "/app/secrets/gcp/service-account.json" ]; then
    echo "Error: GCP service account file 'secrets/gcp/service-account.json' is missing"
    exit 1
fi

clear
utils/motd.sh

echo -e "\e[38;5;250m"
# Activate GCloud service account
gcloud config set project ${GCP_PROJECT_NAME} --quiet
gcloud auth activate-service-account --key-file /app/secrets/gcp/service-account.json --quiet
echo -e "\e[0m"

echo -e "\e[38;5;245m"
echo "---------------------------------------------------------------------------------------------------------"
echo -e "\e[0m\e[38;5;250m"
echo "You are connected to the container, and the following folders from the host are mounted: \e[0m"
echo "  ./"
echo "  ├─ codehub"
echo "  ├─ deployments"
echo "  ├─ secrets"
echo "  └─ utils"
echo ""
echo -e "Type \"\e[38;5;202mgcloud info\e[0m\" to verify the service account is activated."
echo -e "Type \"\e[38;5;202mexit\e[0m\" to quit and turn off the container."
echo ""
echo -e "To open another terminal like this, run \"\e[38;5;202m./dep.sh\e[0m\" on the host machine."
echo ""
echo -e "\e[0m\e[38;5;245m"
echo "---------------------------------------------------------------------------------------------------------"
echo -e "\e[0m"
echo ""
