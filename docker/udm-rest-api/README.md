# Readme


## `dockpin` experiment


### Generate lock files

```sh
# Generate the lock file for the build stage
~/go/bin/dockpin apt pin --base-image base-v1

# Generate the lock file for the final stage
~/go/bin/dockpin apt pin --base-image base-v1 -s dockpin-apt-final.pkgs -p dockpin-apt-final.lock
```


## Handling individual packages

The URL of the package has to be discovered, this should be done based on Apt,
e.g. as follows:

```sh
apt-get download --print-uris univention-directory-manager-rest | sed s/\ .*$//
```

Based on this URL a simple download via tooling like `curl`, `wget` or others
can be made.
