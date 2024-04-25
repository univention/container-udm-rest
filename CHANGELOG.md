# Changelog

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
