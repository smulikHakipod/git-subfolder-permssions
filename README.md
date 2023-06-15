
# GIT Subfolder Permssions

** This much more of a POC than a finished projetc. Many things are missing, and there are probably some security issues. Use on your own resonsiblity **

The aim of this project is to expose only certain subfolders of a GIT project,
usually to external collborators. 

The project keeps the looks and feel of Github, with almost no change the Github UI + CLI, it just filter out the directories the user does not have permssion to.

The user can keep using its own Github username, password or token, without having to use custom ones. 

The project is based on some kind of HTTP reverse proxy for the Github web interface, and somekind of Git hooks to force [partial clone](https://docs.gitlab.com/ee/topics/git/partial_clone.html) and allow only certain subfolders to be accessed. 

## Getting Started

### Requirments
* You would need docker installed.
* You would need a Github user that would act as a "bot" for the external users, and will read/write/create PRs on their behalf. On this user you would need to have the username + password + [github persoanl access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). For testing purposes you can use your own Github user.
* For production usecases, you would probably need DNS + TLS certificate, something like `git.your-domain.com`. For local testing it's not needed.

### Instructions

* In your private repo you would need to explain which users are allowed to access the reduced set of directories. 

Create a file named `.gitfilterspec` and put something like the following in it:

```
#Allowed Users: sosefe;some_more_usernames
/frontend
/README.md
/.gitfilterspec
```

This example basically tells Git Subfolder Permssions project that the external users `sosefe` or `some_more_usernames` **will only** have permssions for the `frontend` folder (and the other files showed in the example). Please pay attention to put the
`/.gitfilterspec` itself as well here, regardless to your included directories. 

** Those users must not have permssions to the Github repo, those permissions will be handled by Github Subfolder Permssions project. ** If you put those users on the Github private repo maintainer list, it will make no effect, as those users will have full access anyway, so don't do that. 

* You would then need to the Github Subfolder Project

Please pay attention to all the arguments and replace them with the details relevant to you.

In Unix like systems: `#Allowed Users` section.

```
GIT_SERVER_NAME=127.0.0.1 GIT_TOKEN=<ghp_..... Github personal token of the user> GIT_USERNAME=<github username (no email)> GIT_PASSWORD=<github-passsword e.g 1234567> REPO_PATH=<repo path e.g smulikHakipod/test_private_repo> docker-compose up
```

You then can go to `https://127.0.0.1/` and login to your "guest"/"external"/"weak" Github account that does not have permssions. And then you can observe that you can surf to "https://127.0.0.1/private_github_org/private_github_repo" and only get access to allowed directories in the repo, and not all the directories in the repo.


For CLI:
`
git clone --sparse --filter=sparse:oid=main:.gitfilterspec https://some_github_username@127.0.0.1/private_github_org/private_github_repo && cd private_github_repo && git config --local core.sparsecheckout true && git show main:.gitfilterspec >> .git/info/sparse-checkout && git checkout
`

and that's it, you have paritally cloned repository. You can pull, push, commit etc. If the user will try to access a folder he cannot (he wont be able to really know, as we alreay hide it, but if he being smartass) then he will get blocked. 

### For production
* Change GIT_SERVER_NAME according to your domain DNS.
* Modify apache-selfsigned.(key/crt) according your TLS key of the domain in GIT_SERVER_NAME from above
