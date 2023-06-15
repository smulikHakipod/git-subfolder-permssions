"""Modify HTTP query parameters."""
from mitmproxy import http
import json
from bs4 import BeautifulSoup
from contextlib import redirect_stdout
import os 
import urllib
import requests
import re

GITHUB_URL = 'github.com'
REPO_ORG_NAME = os.environ.get("REPO_PATH").strip('/')
REPO_URL = f'https://{GITHUB_URL}/{REPO_ORG_NAME}'

def is_repo_url(url):
    return urllib.parse.urlparse(url).path in ['/' + REPO_ORG_NAME, '/' + REPO_ORG_NAME + '/']

def get_current_github_username(cookies):
    

    res = requests.get(f'https://{GITHUB_URL}', cookies=cookies)

    soup = BeautifulSoup(res.text, 'html.parser')
    userLogin = soup.find("meta", {"name": "user-login"})

    if not userLogin:
        return None
    return userLogin['content']

GIT_FILTER_PATH = os.environ.get("GIT_FILTER_PATH")

def get_allowed_folders():
    gitFilterSpec = open(GIT_FILTER_PATH, 'rb')
    files = []
    for l in gitFilterSpec:
        files.append(l.decode('utf-8').strip().strip('\n').strip('/'))
    return files

def get_allowed_users():
    gitFilterSpec = open(GIT_FILTER_PATH, 'rb')
    firstLine = gitFilterSpec.readline()
    if firstLine.startswith(b'#Allowed Users:'):
        return [u.decode('utf-8').strip() for u in firstLine.split(b'#Allowed Users: ')[1].split(b';')]
    else:
        raise "ERROR: You must specify allowed users in the first line of the .gitfilterspec file"

def is_folder_allowed(allowedFolders, url):
    services = ['tree', 'blob', 'raw']
    for service in services:
        for f in allowedFolders:
            if (url.startswith(f'{REPO_URL}/{service}/') and re.match(f'{re.escape(REPO_URL)}/{service}/[^/]+/{f}(.*)', url)):
                return True
    return False

def request(flow: http.HTTPFlow) -> None:
    
    if (is_repo_url(flow.request.url)
        #or flow.request.url.startswith('https://github.com/notifications/647633462/watch_subscription') 
        or flow.request.url.startswith(f'{REPO_URL}/show_partial') 
        #or flow.request.url.startswith(f'{REPO_URL}/commit')
        #or flow.request.url.startswith(f'{REPO_URL}/pull')
        or flow.request.url.startswith(f'{REPO_URL}/security/overall-count')
        or is_folder_allowed(get_allowed_folders(), flow.request.url)

        ):

        ghUsername = get_current_github_username(dict(flow.request.cookies.items()))
        print("gh username", ghUsername)
        if ghUsername not in get_allowed_users():
            return
    
        with open('/app/cookies.json', 'r') as f:
            cookies = json.load(f)
            flow.request.cookies = [(item['name'], item['value']) for item in cookies]


def response(flow: http.HTTPFlow) -> None:
    if is_repo_url(flow.request.url):
        print("got private repo")
        soup = BeautifulSoup(flow.response.get_text(), 'html.parser')
        for d in soup.select('div.Box-row.Box-row--focus-gray.py-2.d-flex.position-relative.js-navigation-item'):
            print("found nav item")
            box_str = ''
            for t in d.select('a.js-navigation-open')[0].findAll(string=True, recursive=True):
                t = str(t)
                if (t == '\n' or len(t.strip()) == 0):
                    continue
                box_str = t.strip()
            if box_str in get_allowed_folders():
                continue
            
            print("hiding dir", box_str)
            d.clear()
            d.unwrap()

        flow.response.text = soup.prettify()