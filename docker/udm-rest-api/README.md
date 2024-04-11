# Readme

## `dockpin` experiment

```sh
# Generate the lock file for the build stage
~/go/bin/dockpin apt pin --base-image base-v1

# Generate the lock file for the final stage
~/go/bin/dockpin apt pin --base-image base-v1 -s dockpin-apt-final.pkgs -p dockpin-apt-final.lock
```
