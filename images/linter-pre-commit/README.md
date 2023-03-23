# Working locally with the linting container

Building the image:

```
docker build -f docker/linter-pre-commit/Dockerfile --platform=linux/amd64 -t wip .
```

Experimenting in the container:

```
docker run -it --rm --mount type=bind,src=$PWD,dst=/work wip /bin/bash
```
