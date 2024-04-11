# UCS Base image with packages

This variant of the base image does include on purpose the packages file, so
that the usage of Apt does yield a reproducible results as long as there is no
call to `apt-get update` or similar made.


## Building

```sh
docker build --platform linux/amd64 . -t ucs-base-with-packages
```
