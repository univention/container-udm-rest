# Changelog

## [0.46.4](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.46.3...v0.46.4) (2026-09-03)


### Bug Fixes

* **deps:** Update Base Image ([ec6680f](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/ec6680f7f048bc29ecc9f4a52fb6756ac9a1f428)), closes [#0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/0)

## [0.46.3](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.46.2...v0.46.3) (2026-09-03)


### Bug Fixes

* **helm:** Mount the krb5.conf at the default location to ensure it's actually picked up by the python process ([bbdb728](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/bbdb728edeabd5e3d6ad454675a226b52b9851b5)), closes [univention/dev/nubus-for-k8s/umc#14](https://git.knut.univention.de/univention/dev/nubus-for-k8s/umc/issues/14)

## [0.46.2](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.46.1...v0.46.2) (2026-08-26)


### Bug Fixes

* **deps:** Update Base Image ([b27abd5](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/b27abd509d6c064357262e5c943d3adab63b8b0c)), closes [#0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/0)
* **test:** set directory/manager/rest/server/port in UCR test config ([7522b14](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/7522b14a017c2654de7d78d860f36c63a8ca58e3)), closes [#0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/0)

## [0.46.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.46.0...v0.46.1) (2026-08-25)


### Bug Fixes

* **helm:** secret-ldap mount permissions 0400 everywhere ([6c26b4b](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/6c26b4bec4537c12567205923f4966d2cae5ba6e)), closes [univention/dev/internal/non-product-issues#121](https://git.knut.univention.de/univention/dev/internal/non-product-issues/issues/121)
* **ldap-update-univention-object-identifier:** let script fail on failures ([5ebdf90](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/5ebdf901a674cfd2c5fddccc7dbee83150c4885b)), closes [univention/dev/internal/non-product-issues#121](https://git.knut.univention.de/univention/dev/internal/non-product-issues/issues/121)

## [0.46.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.45.1...v0.46.0) (2026-08-19)


### Features

* **docker:** add writeable /etc/krb5/krb5.conf ([39bc206](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/39bc2067b5f9122a2e9482d29b2a6405e76757d8)), closes [univention/dev/nubus-for-k8s/umc#14](https://git.knut.univention.de/univention/dev/nubus-for-k8s/umc/issues/14)


### Bug Fixes

* **helm:** initContainer and volume to generate Kerberos configuration ([0ecbd03](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/0ecbd03333fa5e0ac3f81471e6fd682c6ecd7512)), closes [univention/dev/nubus-for-k8s/umc#14](https://git.knut.univention.de/univention/dev/nubus-for-k8s/umc/issues/14)

## [0.45.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.45.0...v0.45.1) (2026-07-22)


### Bug Fixes

* **deps:** Update base image ([5d6f9c4](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/5d6f9c4a92035c3a5da0a6b96a028b4166c48f40)), closes [univention/dev/internal/team-nubus#1670](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1670)

## [0.45.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.44.2...v0.45.0) (2026-07-21)


### Features

* add NT hash and Kerberos 5 Key insecure hash removal scripts ([a294c67](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/a294c67ba2615335865b17498c6393432dc21cc5)), closes [univention/dev/ucs#3651](https://git.knut.univention.de/univention/dev/ucs/issues/3651)

## [0.44.2](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.44.1...v0.44.2) (2026-07-15)


### Bug Fixes

* **helm:** improve readyness and liveness probes ([6b88e18](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/6b88e183db122cd1762eeb6c40935d40f907a7f7)), closes [univention/dev/nubus-for-k8s/udm-rest-api#21](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/21)

## [0.44.1](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.44.0...v0.44.1) (2026-07-06)


### Bug Fixes

* **deps:** Update Base Image ([f06ff2a](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/f06ff2ab207d18d18521026f0031216c17760705)), closes [#0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/0)

## [0.44.0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.43.2...v0.44.0) (2026-05-20)


### Features

* Telemetry sender ([4c7cab0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/4c7cab0e38012c01b94b2ed96388a6687eca845d)), closes [univention/dev/internal/team-nubus#1621](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1621)

## [0.43.2](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/compare/v0.43.1...v0.43.2) (2026-05-18)


### Bug Fixes

* **deps:** Update Base Image ([1abf529](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/commit/1abf5291bc0718f0e8d077fdd7511bdd76bf5af6)), closes [#0](https://git.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/issues/0)
