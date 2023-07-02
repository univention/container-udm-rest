# UDM Rest API joinscript tools

This image provides utilities which help to replicate the UDM related operations
of joinscripts.

The intended usage is in CI pipelines to automatically extract the needed UDM
objects from existing join scripts, so that the data does not have to be
maintained in two places.


## Status - Experimental

The tooling is not perfect, it's barely doing enough to get the data out of the
portal joinscript. Using this in other cases will most likely need improvements
to this tooling as well.


## Example usage

Start a `python3` interpreter:

```shell
docker compose run --rm -it api-tools bash
```

```shell
export OUT_FILENAME=/tmp/udm-objects.yaml
./33univention-portal.inst
cat /tmp/udm-objects.yaml
```

Be aware that you will have to make the joinscript available, either by having a
copy in the sources or by mounting in additional volumes. In the example above
the file `33univention-portal.inst` has been manually copied into the place
where the container has been started from.


## Development

The easiest way to work on the sources is to run the container via `docker
compose` so that the sources are mounted into the container. Then the
environment variable `PATH` has to be modified, so that the right commands are
executed.

Note that the example below has mounted the sources of the univention portal
into the container as well. You will have to tweak the file
`docker-compose.overrides.yaml` for this.

```shell
source ./docker/udm-rest-api-joinscript-tools/dev-fixup-path.sh
./wu/univention-portal/33univention-portal.inst
```
