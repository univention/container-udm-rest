#!/usr/bin/python3
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import base64
import hashlib
import json
import os
import ssl
import urllib.error
import urllib.request


def api_request(method, path, body=None):
    host = os.environ['KUBERNETES_SERVICE_HOST']
    port = os.environ.get('KUBERNETES_SERVICE_PORT_HTTPS', '443')
    token = open('/var/run/secrets/kubernetes.io/serviceaccount/token').read().strip()
    ca = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    if path.startswith('apps/'):
        path = path.removeprefix('apps/')
        prefix = f'/apis/apps/v1/namespaces/{os.environ["UDM_AUTHORIZATION_NAMESPACE"]}'
    else:
        prefix = f'/api/v1/namespaces/{os.environ["UDM_AUTHORIZATION_NAMESPACE"]}'
    url = f'https://{host}:{port}{prefix}/{path}'
    request = urllib.request.Request(
        url,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method=method,
    )
    context = ssl.create_default_context(cafile=ca)
    try:
        with urllib.request.urlopen(request, context=context) as response:  # nosec B310
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return error.code, None
        raise


def main():
    archive = open(os.environ['UDM_AUTHORIZATION_ARCHIVE'], 'rb').read()
    digest = hashlib.sha256(archive).hexdigest()
    name = os.environ['UDM_AUTHORIZATION_CONFIGMAP']
    namespace = os.environ['UDM_AUTHORIZATION_NAMESPACE']
    key = os.environ.get('UDM_AUTHORIZATION_CONFIGMAP_KEY', 'udm-policies.tar.gz')
    configmap = {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app.kubernetes.io/component': 'udm-authorization'},
            'annotations': {'udm-authorization.univention.de/sha256': digest},
        },
        'binaryData': {key: base64.b64encode(archive).decode('ascii')},
    }

    status, current = api_request('GET', f'configmaps/{name}')
    if status == 200 and current.get('metadata', {}).get('annotations', {}).get('udm-authorization.univention.de/sha256') == digest:
        return
    if status == 200:
        configmap['metadata']['resourceVersion'] = current['metadata']['resourceVersion']
        api_request('PUT', f'configmaps/{name}', configmap)
    elif status == 404:
        api_request('POST', 'configmaps', configmap)
    else:
        raise RuntimeError(f'Unexpected ConfigMap status: {status}')

    deployment = os.environ['UDM_AUTHORIZATION_GUARDIAN_DEPLOYMENT']
    patch = {
        'metadata': {
            'annotations': {
                'udm-authorization.univention.de/sha256': digest,
            },
        },
        'spec': {'template': {'metadata': {'annotations': {'udm-authorization.univention.de/sha256': digest}}}},
    }
    api_request('PATCH', f'apps/deployments/{deployment}', patch)


if __name__ == '__main__':
    main()
