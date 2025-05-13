# Disclaimer - Work in progress

The repository you are looking into is work in progress.

It contains proof of concept and preview builds in development created in context of the [openDesk](https://gitlab.opencode.de/bmi/opendesk/info) project.

The repository's content provides you with first insights into the containerized cloud IAM from Univention, derived from the UCS appliance.

# UDM-REST API container

## Getting Started

### BYOL: Bring Your Own LDAP

Check out the [LDAP container](https://git.knut.univention.de/univention/customers/dataport/upx/container-ldap) in a separate folder.
Follow the instructions from the LDAP repository to initialize the server.

Then copy the provided `.env.udm-rest-api.example` to `.env.udm-rest-api`
and customize it if needed:
  - Ensure that the `LDAP_BASE_DN` matches in both containers.
  - Place the `LDAP_CN_ADMIN_PW` in a new file `secret/machine.secret`.

Start the container:

    docker compose up --detach


### Use with UCS VM

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

## Access via Browser

Point your browser to <http://localhost:9979/udm/> and enjoy!

There is also an OpenAPI interface available: <http://localhost:9979/udm/schema/>.

## Configuration

### LDAP

You need to configure `LDAP_HOST`, `LDAP_PORT` and `LDAP_BASE_DN` with
the settings of your LDAP directory server.

The variable `LDAP_HOST_DN` should be set to the DN
of the UDM REST API's "machine account".
The corresponding password of this account should be placed
in a text file at `/run/secrets/machine_secret` (recommended for production),
or passed in the `MACHINE_SECRET` environment (only for testing).

The variable `AUTHORIZED_DOMAIN_ADMINS` should point to a DN
which contains a group with a list of users which may access the UDM REST API.

Upon requests (which need HTTP Authorization)
the UDM REST API will try to authenticate first using the machine account
and check that the username provided in the request is part of the group
(i.e. listed in `memberUid` key)
configured in `AUTHORIZED_DOMAIN_ADMINS`.
After checking authentication and authorization
it will create an LDAP connection bound to the given user.

### TLS

In order to use TLS with the LDAP server
you will need to set `TLS_REQCERT=demand`
and provide a CA certificate in PEM format at `/run/secrets/ca_cert`.

Should you prefer not using TLS
then set `TLS_REQCERT=never`
and do not provide any CA certificates.

## Linting

You can run the pre-commit checker as follows:
```bash
docker compose run --rm pre-commit
```

## Tests

[See the `tests` README for instructions on how to run the tests](./tests/README.md)

## Implementation Status

### UDM Modules

The list of modules on the front page is generated [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-rest/src/univention/admin/rest/module.py#L2116).
A scan of the modules present in the file-system happens [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-modules/modules/univention/admin/modules.py#L121).

Currently supported are the default Univention UDM modules
which are installed in `/usr/lib/python3/dist-packages/univention/admin/handlers/`,
with these exceptions:
  - *AppCenter:* \
    The handler is part of the package `univention-management-console-module-appcenter`,
    but it is unclear whether installing it makes sense in the containerized context.
  - *Portal:* \
    To be clarified. I do not know how the handler is installed in UCS... ¯\\_(ツ)_/¯
