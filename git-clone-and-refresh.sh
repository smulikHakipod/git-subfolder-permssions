#!/bin/bash
GIT_FOLDER=/app/git-repo
REPO_HOSTNAME=github.com

set -x
set -e

if [ $# -ne 3 ]; then
    echo "Usage: $0 <username> <api_key> <repo>"
    exit 1
fi


htpasswd -b -c .htpasswd $1 $2


if [ ! -d "$GIT_FOLDER" ] ; then
    git clone https://$1:$2@$REPO_HOSTNAME/$3 $GIT_FOLDER/$3
fi

cd $GIT_FOLDER/$3
git config --local uploadpack.allowfilter true
while true; do
    git fetch --all
    git pull
    sleep 60
done

