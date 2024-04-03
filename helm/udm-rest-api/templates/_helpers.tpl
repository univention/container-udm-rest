{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions releate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
Templates defined in other Helm sub-charts are imported to be used to configure this chart.
If the value .Values.global.nubusDeployment equates to true, the defined templates are imported.
*/}}
{{- define "templates.ldapUri" -}}
{{- if .Values.global.nubusDeployment -}}
{{- $protocol := "" -}}
{{- $serviceName := "" -}}
{{- $protocol = include "nubusTemplates.ldap.protocol" . -}}
{{- if and .Values.nubusTemplates .Values.nubusTemplates.ldap .Values.nubusTemplates.ldap.serviceName -}}
{{- $serviceName = include "nubusTemplates.ldap.serviceName" . -}}
{{- else -}}
{{- $serviceName = printf "%s-ldap-server" .Release.Name -}}
{{- end -}}
{{- printf "%s://%s" $protocol $serviceName -}}
{{- else -}}
{{ required "Either .Values.udmRestApi.ldap.uri or .Values.global.ldap.uri must be set" (coalesce .Values.udmRestApi.ldap.uri .Values.global.ldap.uri) }}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "udm-rest-api.configMapUcrDefaults" -}}
    {{- $nubusDefaultConfigMapUcrDefaults := printf "%s-stack-data-ums-ucr" .Release.Name -}}
    {{- if or .Values.configMapUcrDefaults .Values.global.configMapUcrDefaults -}}
        {{- coalesce .Values.configMapUcrDefaults .Values.global.configMapUcrDefaults -}}
    {{- else if .Values.global.nubusDeployment -}}
        {{- $nubusDefaultConfigMapUcrDefaults -}}
    {{- else -}}
        {{- .Values.global.configMapUcrDefaults | required ".Values.global.configMapUcrDefaults must be defined." -}}
    {{- end -}}
{{- end -}}

{{- define "udm-rest-api.configMapUcr" -}}
    {{- $nubusDefaultConfigMapUcr := printf "%s-stack-data-ums-ucr" .Release.Name -}}
    {{- if or .Values.configMapUcr .Values.global.configMapUcr -}}
        {{- coalesce .Values.configMapUcr .Values.global.configMapUcr -}}
    {{- else if .Values.global.nubusDeployment -}}
        {{- $nubusDefaultConfigMapUcr -}}
    {{- end -}}
{{- end -}}

{{- define "udm-rest-api.configMapUcrForced" -}}
    {{- if or .Values.configMapUcrForced .Values.global.configMapUcrForced -}}
        {{- coalesce .Values.configMapUcrForced .Values.global.configMapUcrForced -}}
    {{- else if .Values.global.nubusDeployment -}}
        null
    {{- end -}}
{{- end -}}
