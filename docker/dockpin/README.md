# Utility `dockpin`

This folder defines a utility container image which is based on the Univention
base image and does include the utility `dockpin`, so that this tool can be used
to lock Apt based dependencies.


## Status - EXPERIMENTAL

This image is serving an experiment.

If it should be intended for usage then it must be moved into a more appropriate
place like the repository of the ucs based image.


## Known issues

* Our base image does log to `stdout` currently. This leads to `dockpin` failing.
  There is a change which makes it work in this MR:
  <https://git.knut.univention.de/univention/components/ucs-base-image/-/merge_requests/53>

## Usage

The main idea is to allow to use `dockpin` together with the Univention sources
in an easy way:

```sh
~/go/bin/dockpin apt pin --base-image gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-506
```

Compare the README of `dockpin` itself:
<https://github.com/Jille/dockpin/blob/master/README.md>
