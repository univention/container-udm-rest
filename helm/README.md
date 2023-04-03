
# Helm charts for the UDM REST API


## Installing

Copy the `*.example` files and adjust them for the current environment.

Install the charts with
`helm install <parameters> udm-rest-api ./udm-rest-api`

Add custom values with the
`--values linter_values.yaml`
parameter.

Add the certificate file with `--set-file udmRestApi.caCertFile=ca.crt`

See
`linter_values.yaml`
files for important values.

Other changeable parameters can be found in the `values.yaml`
files of the respective project-directories.

Add a namespace-parameter to install avoid using the `default`-namespace.
I.e. `--namespace poco`

### Example

```
helm install \
  --namespace poco \
  --values linter_values.yaml \
  --set-file udmRestApi.caCertFile=ca.crt \
  udm-rest-api \
  ./udm-rest-api
```

## Uninstalling

To uninstall the chart with the release name `udm-rest-api`:

```console
helm uninstall udm-rest-api
```

## General helm hints

See the templated output with `helm template ./udm-rest-api/`

Remove the api-chart with `helm --namespace poco uninstall udm-rest-api`


## General kubectl hints

Show status of the replica-set with `kubectl --namespace poco describe ReplicaSet`

Show installed Services with `kubectl --namespace poco get service`

Show running pods with `kubectl --namespace poco get pods`

Show endpoints with `kubectl --namespace poco get endpoints`

Show deployments with `kubectl --namespace poco get deployments`
