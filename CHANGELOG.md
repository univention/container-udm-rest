# Changelog

## [0.39.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.39.0...v0.39.1) (2025-07-18)


### Bug Fixes

* add missing python3-univention-authorization dependency ([87a8609](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/87a86098fc8d730fdaa8fb8fd9c77b56533a439f)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.39.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.38.0...v0.39.0) (2025-07-18)


### Features

* update wait-for-dependency to 0.35.0 ([3791e42](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/3791e42e69b927615109cebcb8168d707d22978b)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.38.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.37.1...v0.38.0) (2025-07-16)


### Features

* update ucs-base to 5.2.2-build.20250714 ([584ef94](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/584ef945bcddbb69009aa206e32befc5494bc3c0)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.37.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.37.0...v0.37.1) (2025-07-02)


### Bug Fixes

* Configure resources in wait-for-ldap init container ([464f528](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/464f52889ac042818e2d40af4131ccec4fc85aa3)), closes [univention/dev/internal/team-nubus#1303](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1303)

## [0.37.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.36.0...v0.37.0) (2025-06-30)


### Features

* add wait-for-ldap initContainer to uoid job ([ba31455](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/ba3145579b8c1981406eb8d318f0627e3338947a)), closes [univention/dev/internal/team-nubus#1303](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1303)

## [0.36.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.35.4...v0.36.0) (2025-06-27)


### Features

* Change values structure to match the ldap client structure ([b0dd835](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/b0dd83547c9f7dbe0ad86e4c187061744f4ba468)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)


### Bug Fixes

* Avoid setting a value for imagePullPolicy by default ([9d8f125](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/9d8f12597ed763ed92f0842f7f6e68c41df2106e)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Handling of annotations and labels in udm-rest-api chart ([99286d2](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/99286d2f8512b4335ec39a1fe7354078de0bb6f1)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Remove comments from linter values ([b3b9d5d](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/b3b9d5d476fc82c287cfe67da8495107be487b38)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Use ldap base dn in default of "ldap.bindDn" ([3bfe76b](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/3bfe76b4062beb0085cf1721ba46e7d40a2e7e22)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)

## [0.35.4](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.35.3...v0.35.4) (2025-06-25)


### Bug Fixes

* removed obsolete test-connection ([79c1cea](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/79c1cea79e5122f666e40ffd033d8c5be718822f)), closes [univention/dev/internal/team-nubus#1246](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1246)

## [0.35.3](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.35.2...v0.35.3) (2025-06-23)


### Bug Fixes

* use default cluster ingress class if not defined ([39cbd7a](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/39cbd7a8d0546f2d91ea12d59508c066d8449627)), closes [univention/dev/internal/team-nubus#1134](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1134)

## [0.35.2](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.35.1...v0.35.2) (2025-06-18)


### Bug Fixes

* bump umc-base-image version ([3f1f5ce](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/3f1f5ced984dd8ce67c8e1c0a4ec9677a37789a2)), closes [univention/dev/internal/team-nubus#1263](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1263)

## [0.35.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.35.0...v0.35.1) (2025-06-18)


### Bug Fixes

* bump umc-base-image version ([1cc68d3](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/1cc68d3a60a8dae611d1979e115c63ac22f2ef53)), closes [univention/dev/internal/team-nubus#1263](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1263)

## [0.35.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.34.2...v0.35.0) (2025-06-10)


### Features

* updated ucs-base-image to 0.18.1-build-2025-05-29 ([3eb341c](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/3eb341c9f0f1cb326a4e8607137d6992083af849)), closes [univention/dev/internal/team-nubus#1220](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1220)

## [0.34.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.34.1...v0.34.2) (2025-06-06)


### Bug Fixes

* Correct defaults for image registry and pull policy in value file ([6b1619c](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/6b1619cc076015d99191d481d4170b8dd51bf144)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Correct handling of parameter imagePullSecrets ([ff2efaf](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/ff2efaf702c77942ee08d0bb0eed236fc0f68558)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Use correct value for image pull policy in job for object identifier update ([949f514](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/949f5148482f853f05269f4c8acba08bd154a124)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)

## [0.34.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.34.0...v0.34.1) (2025-06-02)


### Bug Fixes

* additional annotations should not be quoted ([b37ad94](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/b37ad944c3d2dc5337e362cba456c425b4cc024d)), closes [univention/dev/internal/team-nubus#1170](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1170)

## [0.34.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.33.0...v0.34.0) (2025-05-16)


### Features

* Update base image to include univentionObjectIdentifier changes from upstream ([f2af7d9](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f2af7d97ac8ec5e331174fde52e99e83a8551193)), closes [univention/dev/internal/team-nubus#1143](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1143)

## [0.33.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.32.1...v0.33.0) (2025-05-15)


### Features

* add blocklist_clean_expired to UDM rest api client ([c4815d4](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c4815d42890093fd2f21ba91298743f6523e450e))
* refactor blocklist cleanup job ([99aff4e](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/99aff4edfde9dbce307e65d5727f0f5ca77e1d55))

## [0.32.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.32.0...v0.32.1) (2025-05-15)


### Bug Fixes

* disable ingress affinity ([02a601b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/02a601bcf075031f70b0896479a1a7acddd0edce)), closes [univention/dev/internal/team-nubus#1121](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1121)

## [0.32.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.31.0...v0.32.0) (2025-05-12)


### Features

* Generate univentionObjectIdentifier for existing objects ([ed2f95a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/ed2f95a68170d7f0eb672f40309bd29b4f78d991)), closes [univention/dev/internal/team-nubus#1157](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1157)


### Bug Fixes

* Apply review suggestions from Johannes L. ([b35f7be](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/b35f7be1185fcb971eb590bd469a83fed13b60fc)), closes [univention/dev/internal/team-nubus#1157](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1157)
* **pre-commit:** Removed old formatters, upgraded Ruff to v0.11.8 ([6e0b3f2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/6e0b3f2a5e9f7c7d896169f6e906d62f69bf0da9)), closes [univention/dev/internal/team-nubus#1157](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1157)

## [0.31.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.30.1...v0.31.0) (2025-05-11)


### Features

* move and upgrade ucs-base-image to 0.17.3-build-2025-05-11 ([74a82d7](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/74a82d7edee2171abe41cede56e81a636a8c1fa1))

## [0.30.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.30.0...v0.30.1) (2025-05-10)


### Bug Fixes

* add missing env to ldap-server in docker-compose.yaml ([1dcf535](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1dcf535ab2ccf242b16452d757442cd58dcb04df))
* move addlicense pre-commit hook ([db2482a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/db2482aa454bd1700368cbff428d400e36bec641))
* move docker-services ([3ca1f79](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/3ca1f793f2b66ff5b4f461b675e4cd4a99c7d88d))
* update common-ci to main ([2b35e7d](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2b35e7df25e6e4f77aab5e22f7e4be159000fd10))

## [0.30.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.29.2...v0.30.0) (2025-04-29)


### Features

* Bump ucs-base-image version ([71d47db](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/71d47dbc7324f08812594641651796bc4c3c545e)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)

## [0.29.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.29.1...v0.29.2) (2025-04-10)


### Bug Fixes

* make copy calls in container init more robust ([8e84bc1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8e84bc162f42ae16162d533c6eb5bad7d1c4a589)), closes [univention/dev/internal/team-nubus#1079](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1079)

## [0.29.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.29.0...v0.29.1) (2025-03-28)


### Bug Fixes

* kyverno ([381481a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/381481a73be4681db613f0dadb2823641c848a15))

## [0.29.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.28.2...v0.29.0) (2025-02-26)


### Features

* Bump ucs-base-image to use released apt sources ([b138fa2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/b138fa24800de2a944fcfcca2f61f115c442e596))

## [0.28.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.28.1...v0.28.2) (2025-02-10)


### Bug Fixes

* set plugin mounts to read-only ([46ab263](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/46ab26348064c4cd547836a1bf383ea288dd1da3))

## [0.28.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.28.0...v0.28.1) (2025-02-10)


### Bug Fixes

* add .kyverno to helmignore ([f88167b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f88167b0ded23798756d17cfb6b3888a8f974d8e))

## [0.28.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.27.0...v0.28.0) (2024-12-20)


### Features

* upgrade UCS base image to 2024-12-12 ([1abe348](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1abe348254994f8da2cec4b105b6126516029cfb))

## [0.27.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.26.1...v0.27.0) (2024-12-11)


### Features

* Adjust to changes in ldap-server version 0.29.0 ([7b5ed6d](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/7b5ed6d2b5aa983991db95d8f02b2c131a5ded33))
* Update base image to version 0.13.3-build-2024-12-05 ([2923396](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2923396bdeb35fbf13201d0098559e021e7281e1))


### Bug Fixes

* Comment out "ldap.auth.existingSecret.keyMapping" in default values ([6de0dd2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/6de0dd25c451ac5ca6545a3f703e006b48877564))

## [0.26.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.26.0...v0.26.1) (2024-11-24)


### Bug Fixes

* add a systemExtension to the linter_values.yaml file ([de9223a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/de9223a4a233606d5d052b916f5f0018a99571f7))

## [0.26.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.25.1...v0.26.0) (2024-11-14)


### Features

* migrate secrets ([c230028](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c23002894816b36c2107151c7c702a463372d3b5))


### Bug Fixes

* support indirection in secrets to enable deduplication in the umbrella chart ([876f4ac](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/876f4acf4fbd27d2aa1113749a9cd38fbb9614a5))

## [0.25.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.25.0...v0.25.1) (2024-10-09)


### Bug Fixes

* fix ingress path configuration ([2b13f22](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2b13f228041aba5e3c710f2e9dc035c7dabb89e1))

## [0.25.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.24.0...v0.25.0) (2024-09-26)


### Features

* **ci:** enable malware scanning, disable sbom generation ([84c90ea](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/84c90eab0a24b2deaf894043d367f3377d39c5db))

## [0.24.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.23.0...v0.24.0) (2024-09-13)


### Features

* update UCS base image to 2024-09-09 ([b0dad61](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/b0dad615e654cbee6fe3bfbae6cf10b55ab77176))

## [0.23.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.22.0...v0.23.0) (2024-09-11)


### Features

* **udm-rest-api:** Headless service ([28334b7](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/28334b7872bec161a5094388696ac11b557bbaeb))


### Bug Fixes

* **udm-rest-api:** Set port to 9979 ([9def8ff](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/9def8ffceb7bc632618cf94bb411304ce6c81b68))

## [0.22.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.21.0...v0.22.0) (2024-08-28)


### Features

* unify UCR configuration ([e6ff454](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e6ff4543c28e658833d0f2b159f7a9a1c14137ab))

## [0.21.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.20.0...v0.21.0) (2024-08-21)


### Features

* **udm-rest-api:** Add certManager template for ingress ([119abd6](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/119abd609dec861dca8a77d30b0eee8c5bee84bb))

## [0.20.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.19.0...v0.20.0) (2024-07-17)


### Features

* Remove packages "python3-yaml" and "python3-jinja2" ([46c2760](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/46c2760b3505dfaacd5900cf700034114a39df9d))
* Update base image to version 0.13.1-build-2024-07-04 ([f2573c7](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f2573c75df8518addf6860ffd5db728a4e3086b5))

## [0.19.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.18.0...v0.19.0) (2024-07-09)


### Features

* adjust ingress configuration to support Nubus deployment without stack-gateway or centralized ingress configuration ([0ba6901](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/0ba69010bd736aa223732c8cb6c4bf6c80572018))

## [0.18.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.17.4...v0.18.0) (2024-07-05)


### Features

* Configure extensions through values ([d040180](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d04018075177f61856207a57a6175e9a055240f6))

## [0.17.4](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.17.3...v0.17.4) (2024-07-04)


### Bug Fixes

* remove LDAP index for App Center attribute ([7d5db71](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/7d5db71977f46de894e04dc10be2200784cc07d6))

## [0.17.3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.17.2...v0.17.3) (2024-07-02)


### Bug Fixes

* typo (oxPlugin imagePullPolicy) ([88b4edc](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/88b4edc6fa36ee867e1e923de5c9bb191c2135e0))

## [0.17.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.17.1...v0.17.2) (2024-07-01)


### Bug Fixes

* set log level to INFO ([4f27cf8](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/4f27cf8157765a558cc3cb9ac8c96d73c4415d6c))

## [0.17.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.17.0...v0.17.1) (2024-07-01)


### Bug Fixes

* update common-ci to handle external images in chart ([22b1e95](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/22b1e954c025c27a5971f88ec49d088927311e1d))

## [0.17.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.16.0...v0.17.0) (2024-06-28)


### Features

* load extensions into udm-rest-api ([d2f90a6](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d2f90a69756c881db9aa853c3ef1388bdfac1bfe))

## [0.16.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.15.0...v0.16.0) (2024-06-27)


### Features

* Update ox-connector extensions ([36176da](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/36176daca2430f3cf7883d08d99b3d8c282a8967))

## [0.15.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.14.1...v0.15.0) (2024-06-25)


### Features

* Update base image to be based on 5.2-0 ([8d6b865](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8d6b865e4523f17701444bf37c66deb625c55878))

## [0.14.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.14.0...v0.14.1) (2024-06-25)


### Bug Fixes

* activate ldap controls in uldap.py in the test ucr conf ([9e11fbf](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/9e11fbf2195028ea725e6360e451ef6b66da28df))
* bump ucs-base to 5.0-8 ([530f649](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/530f649bd0b9c94ad07e8a1212703a55faaa7cee))

## [0.14.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.13.2...v0.14.0) (2024-06-19)


### Features

* Adjust to refactored image name "portal-extension" from "protal-udm-extensions" ([d037686](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d037686df848d9cc6c48dbc7bdc136b444c2bf16))
* Adjust to refactored structure of "portal-extension" ([4519815](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/45198154bac0b7c82c8f1fe46020fc1eb841041e))
* Update the portal-extensions version to 0.26.0 ([db63e82](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/db63e82e97f7e7582e6e5135c2e98c917b004667))

## [0.13.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.13.1...v0.13.2) (2024-05-28)


### Bug Fixes

* Add additional Ingress annotation for nginx-ingress ([f572303](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f572303c237fd67860d1ea86e7f687f83b3e2b22))

## [0.13.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.13.0...v0.13.1) (2024-05-23)


### Bug Fixes

* use global registry ([c878f4f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c878f4f8a94567114152ee1fbab182e75b36b721))

## [0.13.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.12.0...v0.13.0) (2024-05-20)


### Features

* support for templating of global.configMapUcr ([0dafd78](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/0dafd78944792ef83f4fa38adb6b8c9093e85904))

## [0.12.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.11.2...v0.12.0) (2024-05-07)


### Features

* Update base image to be based on 5.0-7 ([c3f3179](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c3f3179771e79a385957f8f1d61a8b8bef10db23))


### Bug Fixes

* Drop logging related patch after upstream integration ([3787224](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/3787224ec5cdb971d3d20547601a667f314482ae))

## [0.11.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.11.1...v0.11.2) (2024-05-07)


### Bug Fixes

* **ci:** harbor helm value substitution ([a0de33b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a0de33b95e541ef64ff0271e56a64fae4bfd9914))

## [0.11.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.11.0...v0.11.1) (2024-05-06)


### Bug Fixes

* drop trivy container security scanning ([72c2160](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/72c21603ceb512efa124deca9038243a7b6da50b))

## [0.11.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.10.0...v0.11.0) (2024-04-25)


### Features

* add nubusTemplates.udmRestApi.uri ([8280ddf](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8280ddfaceab25598028e8d99fa7727f7854984d))
* changes to support the refactored umbrella values in a nubus deployment ([3ccc01e](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/3ccc01efa079a52aba773ff7fe3bdd04a86f5212))
* export nubusTemplates.udmRestApi.host and nubusTemplates.udmRestApi.port ([09c0c99](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/09c0c997f00804d921b4d18a4c81b383bbc52b27))


### Bug Fixes

* configMapForced default value ([d3acf62](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d3acf62a2a373c701ab3bfb50cf27e699ed952c3))
* re-adding configmap checksum, fixing some linter complaints ([a3cfc58](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a3cfc584c62461f972d0ef8b3c32a92c78ead40b))

## [0.10.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.9.3...v0.10.0) (2024-04-19)


### Features

* Avoid calling "apt-get update" in the build stage ([a0887fb](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a0887fb50d53c8e64c4065a5ae5c670b5b995c7d))
* Avoid calls to "apt-get update" in final stage and debug builds ([a48c75f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a48c75f7c74700a654c4e76eab82ee32199a8181))
* Build client image based on fixed packages set ([e44093e](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e44093ee88d8257ffa87dfc7632c9b01d0e5084c))
* fixup ([1b0ebb9](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1b0ebb9ebcacfbe9ea42abf7539f8a7ed26b0878))
* Use a date based tag of the base image ([4d9400b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/4d9400bd80fd13eeab69ae205ae0e94f7f382464))

## [0.9.3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.9.2...v0.9.3) (2024-04-15)


### Bug Fixes

* update openDesk pointer ([e0ea5db](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e0ea5dbf9645c8e1f23a0832f3ad16e33ad9279d))

## [0.9.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.9.1...v0.9.2) (2024-03-27)


### Bug Fixes

* **ci:** update common-ci from v1.16.2 to v1.25.0 ([e00c842](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e00c8421831da18bfd008f5123091c7623ec1e3d))

## [0.9.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.9.0...v0.9.1) (2024-03-20)


### Bug Fixes

* Set "global.imageRegistry" to correct default value ([55d5f16](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/55d5f1659c78147a4418c7e4de2a0ceb066fb72c))
* Set default image tag to "latest" ([7d458c2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/7d458c202f94e065d8d7e3c0b4f22513490cc8b8))
* Uncomment "registry" to have it captured into the readme ([dfe734b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/dfe734b82f590c5dac1cec6e9d3f720249799e49))

## [0.9.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.8.0...v0.9.0) (2024-03-13)


### Features

* **helm:** BSI-compliant deployment ([08b4c97](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/08b4c977986a5bb3ee7e0aaa308b877d477d683e))


### Bug Fixes

* apply updateStrategy if configured ([7dc439f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/7dc439fcea78109652ffa86f204c80f7b3bc5888))
* attempt to get the pipeline-based test to work ([501b9ef](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/501b9ef7dcfd1934d5599413bb2c3fee1cd3df7f))
* better logging readonly filesystem patch ([4c2092c](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/4c2092cee2cc9f0893329aba02bd3a8ddc9235ff))
* cleanup values ([c429464](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c4294649ddedfd870e3d61c72d59be3613fae2e0))
* create app user ([72316d9](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/72316d98eb9451eae690134b88f059a4572c27e5))
* fix ldap.conf syntax ([0d3502d](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/0d3502d06a79532b9b917968bc9d99ce69d2cf9e))
* **helm:** Avoid setting resources by default. ([475c77b](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/475c77b58102945d997b6b2c0b29e33956da7bbb))
* **helm:** Consistent handling of secrets and the base64 encoding ([f31099d](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f31099dec02577cb3e47c5fcea4fecfac56d6949))
* **helm:** remove udm-rest-api debug sidecar ([5165e37](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/5165e376da93f1409af8d92c194d833f7566f514))
* **helm:** Use the "latest" image by default ([37f604c](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/37f604c7377f36f1d6b5d91bff0aa25698cb47a9))
* make resources for init containers adjustable via values ([ef1b0f9](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/ef1b0f9267b0126d58bda579093609af61e5bdea))
* removed istio and config ([f160e33](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/f160e33e8583eb513483a745baf0ad110497b43b))
* renamed incorrenct key updateStrategy to strategy ([8f141d1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8f141d1d748bf57230fe694da95dabfa157f9918))
* **udm-rest-api:** logging read only filesystem ([5979281](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/597928156f4b070f8fc8d7ab9c10c62140535f8e))
* **udm-rest-api:** remove chown calls for /dev/stdout file in preparation for read-only root filesystem ([5a30d0f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/5a30d0fb07e926588c0356cfa619034ddacff5b3))

## [0.8.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.7.2...v0.8.0) (2024-03-07)


### Features

* **cli:** stages and cli image build ([97abc54](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/97abc542b8a33d875bcde3d45e65fd11bc94ee66))
* **udm-rest-api-python-client:** add entrypoint which is a command line interface to UDM REST API ([a0b5c41](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a0b5c4119c925a5ef489005b8a158ffa047668fd))

## [0.7.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.7.1...v0.7.2) (2024-03-07)


### Bug Fixes

* ldap ulimit needed on dev-env for kernel 6.6 and above ([8dd53ab](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8dd53abc38f661ab69f1625dab2f7a7758662ede))
* **udm-rest-api:** remove upstreamed patch ([18bc22a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/18bc22a5b7e2267e101ee9ef814aa01b36b9bf71))

## [0.7.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.7.0...v0.7.1) (2024-01-30)


### Bug Fixes

* **helm:** Add missed annotation "nginx.org/proxy-buffers" ([791d65f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/791d65f5fb93ace3c559d47ab26fbc82020d3fc4))

## [0.7.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.6.0...v0.7.0) (2024-01-22)


### Features

* Reduce default delay of the probes in the Helm chart ([5197e4e](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/5197e4ee570d0fd305abd997614368a9e6eff306))


### Bug Fixes

* **helm:** Avoid setting resources by default. ([d972d7c](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d972d7c0d88ec492a18bc647e1c54fda65239c7a))
* **helm:** Consistent handling of secrets and the base64 encoding ([e0b486d](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e0b486dc7a50623ce4db4b3d3003b1e731fd4d7f))
* **helm:** Remove "image.tag" configuration from "linter_values.yaml" ([625fd13](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/625fd13639baa5033c9c32fe683c201b57d571cb))
* **helm:** Use the "latest" image by default ([df29123](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/df29123e44a7f008bac91c585d92396e0d72f70e))

## [0.6.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.5.2...v0.6.0) (2024-01-18)


### Features

* **ci:** add debian update check jobs for scheduled pipeline ([d354a86](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d354a8666d0c6e13e46084d3307bf04467387f91))


### Bug Fixes

* **deps:** add renovate.json ([b9989ba](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/b9989baf3e4655276629f87481011f71629015de))

## [0.5.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.5.1...v0.5.2) (2023-12-28)


### Bug Fixes

* **licensing/ci:** add spdx license headers, add license header checking with common-ci v1.13.x, updated pre-commit-config.yaml ([c6b4d90](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c6b4d90bc66d0130bbdf00ab25ddb4b4a4e4697e))

## [0.5.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.5.0...v0.5.1) (2023-12-21)


### Bug Fixes

* **docker:** update ucs-base from 5.0-5 to 5.0-6 ([bccbecb](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/bccbecb57eeef7f40b68d28dca0b9778320758af))

## [0.5.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.4.3...v0.5.0) (2023-12-20)


### Features

* **rest:** add guardian syntax ([1e1ac6f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1e1ac6f9b9cbb25ec520541991c98403cf90520e)), closes [univention/customers/dataport/team-souvap#342](https://git.knut.univention.de/univention/customers/dataport/team-souvap/issues/342)

## [0.4.3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.4.2...v0.4.3) (2023-12-18)


### Bug Fixes

* **ci:** add Helm chart signing and publishing to souvap via OCI, common-ci 1.12.x ([41ad179](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/41ad1791896d6ffb5731de16661d267629be5a46))

## [0.4.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.4.1...v0.4.2) (2023-12-11)


### Bug Fixes

* **ci:** reference common-ci v1.11.x to push sbom and signature to souvap ([2878b13](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2878b13ada5e642bb5334015981850ff0df4be31))

## [0.4.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.4.0...v0.4.1) (2023-12-07)


### Bug Fixes

* **helm:** Fix nginx annotations regarding proxy-buffer-size ([a492641](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/a492641f9fe97cb863121d2aec673f7be1becfe6))

## [0.4.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.5...v0.4.0) (2023-12-06)


### Features

* Set image registry default via "global.imageRegistry" ([03a544a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/03a544af7067bbb236fab1cd5f596a09a3a5d5ea))
* Update to common-ci 0.6.0 ([c94ae15](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c94ae15cf4f43a4bc4bdf6e95c9cb2bb656dda4a))


### Bug Fixes

* **ingress:** Add annotation regarding the proxy_buffer_size for Nginx based ingresses ([c923514](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/c92351457d681afcc08734dc12e7f1f86934ff08))
* Move TODO comment out of the docstring ([d6b81ba](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d6b81ba2f435f8fecbbf08973311ef4358fd06d4))
* Use the knut container registry by default ([6c941ab](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/6c941ab1569fc183d06e2c282e6e76771b67e281))

## [0.3.5](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.4...v0.3.5) (2023-11-17)


### Bug Fixes

* **docker:** fix typo in udm-rest-api entrypoint ([891cfa0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/891cfa0027870e503970ae0ba5859729783c4340))

## [0.3.4](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.3...v0.3.4) (2023-11-16)


### Bug Fixes

* Pin version of "portal-udm-extensions" ([4482423](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/44824232069b66b97c30840f3510c799268f0517))

## [0.3.3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.2...v0.3.3) (2023-11-09)


### Bug Fixes

* **rest-api:** bump ox-connector dependencies for import error in syntax ([d1dbd93](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d1dbd93b737d0f57f428947212cda34326251ea2))

## [0.3.2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.1...v0.3.2) (2023-11-06)


### Bug Fixes

* **docker:** bump common-ci to build latest image ([056376f](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/056376f725eb891ac4ceb72bc795e907cbd099e1))

## [0.3.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.3.0...v0.3.1) (2023-11-03)


### Bug Fixes

* **versions:** produce version-tagged Docker images ([230f504](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/230f50429c6ef95ee502c78610282b05f21b728c))

## [0.3.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.2.0...v0.3.0) (2023-11-02)


### Features

* **rest:** ox-connector syntax, hooks, handlers and icons ([4f50d25](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/4f50d2515bd7bf947ecefe2a8fad8372a71267b0))
