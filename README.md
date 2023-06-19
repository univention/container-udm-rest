# UDM-REST API containers

## Getting Started

Use the provided Ansible script to extract all secrets from your UCS VM
and create `.env.udm-rest-api` automatically:

1. Create `ansible/inventory/hosts.yaml` based on the provided example file and insert your IP address.
2. Run the playbook:
    ```
    ansible-playbook -i ansible/inventory/hosts.yaml ansible/fetch-secrets-from-ucs-machine.yaml
    ```

Now, build and run your container:
```bash
docker compose up --detach --remove-orphans --build
```

Point your browser to http://localhost:9979/udm/ and enjoy!


## Linting

You can run the pre-commit checker as follows:
```bash
docker compose run --rm pre-commit
```


## Implementation Status

### UDM Modules

The list of modules on the front page is generated [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-rest/src/univention/admin/rest/module.py#L2116).
A scan of the modules present in the filesystem happens [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-modules/modules/univention/admin/modules.py#L121).

Currently supported are the default Univention UDM modules
which are installed in `/usr/lib/python3/dist-packages/univention/admin/handlers/`,
with these exceptions:
  - *AppCenter:* \
    The handler is part of the package `univention-management-console-module-appcenter`,
    but it is unclear whether installing it makes sense in the containerized context.
  - *Portal:* \
    To be clarified. I do not know how the handler is installed in UCS... ¯\\_(ツ)_/¯
