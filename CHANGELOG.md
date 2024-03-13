# Changelog

## [1.0.1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v1.0.0...v1.0.1) (2024-03-13)


### Bug Fixes

* better logging readonly filesystem patch ([e6ce2f3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e6ce2f36dd6ceed5f569274770837ae5fae87253))

## [1.0.0](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/compare/v0.8.0...v1.0.0) (2024-03-11)


### ⚠ BREAKING CHANGES

* **helm:** BSI-compliant deployment

### Features

* **helm:** BSI-compliant deployment ([2cb90ad](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2cb90ad527e05e440b7e5d2dfa63ccb74b45a62c))


### Bug Fixes

* apply updateStrategy if configured ([1f4a444](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1f4a4445deb0ff76b965b37c7479daf2e633f478))
* attempt to get the pipeline-based test to work ([d155c3e](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/d155c3e1f19db2f0c49102f66055ada17382b6a1))
* cleanup values ([6aa3113](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/6aa31137179f495fc955d28b31f4c57c61f56476))
* create app user ([8cc93f2](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/8cc93f28d558724ab4d09b60cab41bdb8040d2a9))
* fix ldap.conf syntax ([733bdf6](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/733bdf6600204273777f89ceb7fc3e2df52093bc))
* **helm:** Avoid setting resources by default. ([2ddb203](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2ddb203e799137ad858b0fd474e077b9b30f55e3))
* **helm:** Consistent handling of secrets and the base64 encoding ([e582ce3](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/e582ce3a25c2266be8759689ee4a83b3183aa704))
* **helm:** remove udm-rest-api debug sidecar ([1670715](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/16707153577825e223d67f7e0d0060beba81692a))
* **helm:** Use the "latest" image by default ([9f7935a](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/9f7935a818722b61648878c4a9985f1a9f593c02))
* make resources for init containers adjustable via values ([db920f5](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/db920f5b2112e8c5a0feb70ac08a4119f82e68c9))
* removed istio and config ([1438e21](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1438e2152010de3868cf45fe91dba174c9dd2cdc))
* renamed incorrenct key updateStrategy to strategy ([2d0daeb](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/2d0daebc8f72d1bf799e33711edc4ea512160a0a))
* **udm-rest-api:** logging read only filesystem ([37f40d1](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/37f40d1725a6225832e2f9dd02c9dee030d25be7))
* **udm-rest-api:** remove chown calls for /dev/stdout file in preparation for read-only root filesystem ([1c569f4](https://git.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/commit/1c569f4773ba1b15f0a5a7c52d9f0b98e36c6805))

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
