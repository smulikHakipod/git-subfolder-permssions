#!/bin/bash
GIT_FOLDER=/app/git-repo
REPO_HOSTNAME=github.com

set -x
set -e

if [ $# -ne 3 ]; then
    echo "Usage: $0 <username> <api_key> <repo>"
    exit 1
fi

if [ ! -d "$GIT_FOLDER/$3" ] ; then
    git clone https://$1:$2@$REPO_HOSTNAME/$3 $GIT_FOLDER/$3
fi

cd $GIT_FOLDER/$3

git config --local uploadpack.allowfilter true
git config http.receivepack true
git config receive.denyCurrentBranch updateInstead

while true; do
    git fetch --all
    git pull
    git push -u --branches
    sleep 60
done

