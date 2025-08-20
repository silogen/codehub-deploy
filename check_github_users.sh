#!/bin/bash
Usernames=$2

IFS=',' # Properly set IFS

for user in $Usernames; do
    res=$(curl --write-out "%{response_code}" \
               --silent --output /dev/null \
               -H "Authorization: token $1" \
               "https://api.github.com/users/$user")
    if [ "$res" != "200" ]; then
        echo "$res $user"
    fi
done
