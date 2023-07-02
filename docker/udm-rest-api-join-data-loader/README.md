# UDM Rest API Join Data Loader

This container is based on the `udm-rest-api-python-client` and bundles the
needed data from extensions into one image. This way the data can be initialized
once the `udm-rest-api` is available.


## Status

This is an interim solution for the SouvAP project. On the short term we bundle
the fixed set of extensions and their related LDAP data into the images at build
time. This allows us to move from the VM into the fully containerized stack,
even though the dynamic extension handling is not yet solved for the container
stack.


## Approach

The idea is, that every extension does provide its needs as a series of `YAML`
documents which describe which objects have to be present.

The utility script `project-join-data.py` from the `udm-rest-api-python-client`
is then used to apply those `YAML` documents to the running `udm-rest-api`.
