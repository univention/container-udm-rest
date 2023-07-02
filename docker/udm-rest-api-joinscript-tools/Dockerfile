ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-ucs-base/ucs-base-dev-504
ARG UCS_BASE_IMAGE_TAG=latest

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

# TODO: See https://git.knut.univention.de/univention/ucs/-/merge_requests/820
RUN ucs-dev-add-branch.sh jbornhold-udm-rest-client \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest-client=10.* \
      python3-yaml=3.* \
      univention-config=15.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY bin/* /usr/local/bin/

COPY bin/fake.sh /usr/local/bin/die
COPY bin/fake.sh /usr/local/bin/joinscript_init
COPY bin/fake.sh /usr/local/bin/nc
COPY bin/fake.sh /usr/local/bin/systemctl
COPY bin/fake.sh /usr/local/bin/ucs_registerLDAPExtension
COPY bin/fake.sh /usr/local/bin/umc_init
COPY bin/fake.sh /usr/local/bin/umc_operation_create
COPY bin/fake.sh /usr/local/bin/univention-portal
