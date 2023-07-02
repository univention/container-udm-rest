ARG BASE_IMAGE_TAG=latest
ARG BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/udm-rest-api-python-client:${BASE_IMAGE_TAG}

ARG PORTAL_UDM_EXTENSIONS_TAG=latest
ARG PORTAL_UDM_EXTENSIONS_IMAGE=gitregistry.knut.univention.de/univention/components/univention-portal/portal-udm-extensions:${PORTAL_UDM_EXTENSIONS_TAG}


# hadolint ignore=DL3006
FROM ${PORTAL_UDM_EXTENSIONS_IMAGE} AS portal-udm-extensions


# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

WORKDIR /
RUN mkdir /join-data

COPY --from=portal-udm-extensions /udm/join-data/* /join-data/
COPY command.sh /

CMD ["/command.sh"]
