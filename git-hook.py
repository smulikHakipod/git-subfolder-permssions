#!/usr/bin/python3

import sys
from subprocess import Popen, PIPE
import subprocess
import os

GIT_PATH = os.environ.get("GIT_PATH")
REPO_PATH = os.environ.get("REPO_PATH")
GIT_FILTER_PATH = os.environ.get("GIT_FILTER_PATH")
GH_USERNAME = os.environ.get("GH_USERNAME")
# write a tee command that passes both stdin and stdout to a file
with open('/tmp/git-params.txt', 'ab') as log:
    args = [GIT_PATH]
    args.extend(sys.argv[1:])
    log.write(b"\nENV\n")
    log.write(bytes(str(os.environ), 'utf-8'))
    log.write(b"\nCOMMAND\n")
    log.write(bytes(str(args), 'utf-8'))
    log.write(b"\nCWD\n")
    log.write(bytes(str(os.getcwd()), 'utf-8'))
    log.write(b"\nSTDIN\n")
    allowedRevList = []
    fullStdin = b''
    if args[1] == 'pack-objects':
        if '--filter=sparse:oid=main:.gitfilterspec' not in args and '--filter=blob:none' not in args:
            #print("ERROR: You must use --filter=sparse:oid=main:.gitfilterspec --filter=blob:none when using git-filter-branch")
            #exit(5)
            args.append('--filter=sparse:oid=main:.gitfilterspec')
            #pass
            
        revList = subprocess.run([GIT_PATH, 'rev-list', '--all', '--objects'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        #log.write(revList.stdout)  

        for line in revList.stdout.decode('utf-8').splitlines():
            splittedLine = line.split(' ')
            gitFilterSpec = open(os.path.join('../', GIT_FILTER_PATH), 'rb')
            firstLine = gitFilterSpec.readline()
            if firstLine.startswith(b'#Allowed Users:'):
                allowedUsers = [u.strip() for u in firstLine.split(b'#Allowed Users: ')[1].split(b';')]
                if GH_USERNAME.encode('utf-8') not in allowedUsers:
                    print("ERROR: You are not allowed to access this repo")
                    exit(5)
            else:
                print("ERROR: You must specify allowed users in the first line of the .gitfilterspec file")
                exit(5)
            

            if len(splittedLine) >= 2:
                for spec in gitFilterSpec:
                    specStr = spec.decode('utf-8').strip().strip('\n')
                    #log.write(f"\n CMP {splittedLine[1]} {specStr} \n".encode('utf-8'))
                    # this is probably bugged
                    if splittedLine[1].startswith(specStr):
                        allowedRevList.append(splittedLine[0])
            else:
                allowedRevList.append(splittedLine[0])
        #log.write(bytes(str(allowedRevList), 'utf-8'))  

    proc = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    while True:
        chunk = sys.stdin.buffer.read(1024)
        if not chunk:
            break

        log.write(chunk)
        fullStdin += chunk
        proc.stdin.write(chunk)
        proc.stdin.flush()
    proc.stdin.close()
    if args[1] == 'pack-objects':
        for line in fullStdin.decode('utf-8').splitlines():
            if line not in allowedRevList and line != '--not' and line != '':
                log.write(b"\nACCESS DENIED!!\n")
                log.write(bytes(str(line), 'utf-8'))
                exit(5)

    log.write(b"\nSTDOUT\n")
    while True:
        chunk = proc.stdout.read(1024)
        if not chunk:
            break
        log.write(chunk)
        sys.stdout.buffer.write(chunk)


    proc.wait()

