
# Helm charts for the UDM REST API


## Usage

Copy the `*.example` files and adjust them for the current environment.

Install the charts with
`helm install <parameters> udm-rest-api ./udm-rest-api`

Add custom values with the
`--values values-udm-rest-api.yaml`
parameter.
See
`values-udm-rest-api.yaml.example`
files for important values.
Other changeable parameters can be found in the `values.yaml`
files of the respective project-directories.

Add a namespace-parameter to install avoid using the `default`-namespace.
I.e. `--namespace poco`


## General helm hints

See the templated output with `helm template ./udm-rest-api/`

Remove the api-chart with `helm --namespace poco uninstall udm-rest-api`


## General kubectl hints

Show status of the replica-set with `kubectl --namespace poco describe ReplicaSet`

Show installed Services with `kubectl --namespace poco get service`

Show running pods with `kubectl --namespace poco get pods`

Show endpoints with `kubectl --namespace poco get endpoints`

Show deployments with `kubectl --namespace poco get deployments`


## Documenting the Helm charts


The documentation of the helm charts is generated mainly out of two places:

- `values.yaml` contains the documentation of the supported configuration
  options.

- `README.md.gotmpl` is the template to generate the `README.md` file, it does
  contain additional prose documentation.

As a generator the tool `helm-docs` is in use. We support two main local usage scenarios:

- `helm-docs` runs it locally. Needs a local installation first.

- `docker compose run helm-docs` allows to use a pre-defined docker container in
  which `helm-docs` is available. Can be used in the folder `/docker` in this
  repository.
