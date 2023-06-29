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
call-joinscript.sh 33univention-portal.inst
cat /tmp/udm-objects.yaml
```
