# UDM Rest API

This version of the image has been modified so that it is based on a variant of
`ucs-base` which does include the package set. See [../ucs-base](../ucs-base)
regarding the modified base image.

## Building the image

First ensure that the base image has been built.

```sh
docker build --platform linux/amd64 . -t wip
```
