#!/bin/bash

student_list=$1
gh_token=$2

awk '{print tolower($1)}' $student_list | sort -u --ignore-case > tmp && mv tmp $student_list
for name in `cat $student_list`; do
  sh check_github_users.sh $gh_token $name >> invalid_$student_list
done

awk '{print $NF}' invalid_$student_list > tmp && mv tmp invalid_$student_list

diff $student_list invalid_$student_list | awk '/^</{print $NF}' > valid_$student_list
