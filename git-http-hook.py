#!/usr/bin/python3
import os
import sys
from subprocess import Popen, PIPE
import subprocess
import requests
from pathlib import Path

GIT_HTTP_PATH = os.environ.get("GIT_HTTP_PATH")

args = [GIT_HTTP_PATH]
args.extend(sys.argv[1:])




fullStdin = b''

#open('/tmp/git-params-http.txt', 'wb').write(bytes(str(os.environ), 'utf-8'))

allowedUsers = []
currentUserName = ''
if not os.environ.get("HTTP_AUTHORIZATION"):
    sys.stdout.write('Status: 401 Forbidden\r\n')
    sys.stdout.write('WWW-Authenticate: Basic realm="Github"\r\n\r\n')
    exit(5)
else:
    currentUserRaw = requests.get('https://api.github.com/user', headers={ 'Authorization': os.environ.get("HTTP_AUTHORIZATION"), 'X-Github-Api-Version': '2022-11-28', 'Accept': 'application/vnd.github+json'})
    if currentUserRaw.status_code != 200:
        #open('/tmp/git-params-http.txt', 'ab').write(str(currentUserRaw.text).encode('utf-8'))
        sys.stdout.write('Status: 401 Forbidden\r\n\r\n')
        exit(5)
    projectRoot = os.environ.get("GIT_PROJECT_ROOT")
    pathInfoNorm = os.environ.get('PATH_INFO').split(os.path.sep)
    
    repoPath = os.path.join(projectRoot, pathInfoNorm[1], pathInfoNorm[2])
    for l in open(os.path.join(repoPath, '.gitfilterspec'), 'r').read().splitlines():
        if l.startswith('#Allowed Users:'):
            l = l[len('#Allowed Users:'):].strip()
            allowedUsers = l.split(';')
            break

    currentUserName = currentUserRaw.json()['login']
    if currentUserName not in allowedUsers:
        #open('/tmp/git-params-http.txt', 'ab').write(str(allowedUsers).encode('utf-8'))
        #open('/tmp/git-params-http.txt', 'ab').write(currentUserRaw.json()['login'].encode('utf-8'))
        #pass
        sys.stdout.write('Status: 401 Forbidden\r\n\r\n')
        exit(5)
    
myEnv = os.environ.copy()
myEnv['GH_USERNAME'] = currentUserName

proc = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=myEnv)


while True:
    chunk = sys.stdin.buffer.read(1024)
    if not chunk:
        break

    fullStdin += chunk
    proc.stdin.write(chunk)
    proc.stdin.flush()
proc.stdin.close()


#open('/tmp/git-params-http.txt', 'ab').write(fullStdin)


while True:
    chunk = proc.stdout.read(1024)
    if not chunk:
        break
    sys.stdout.buffer.write(chunk)