# Changelog

## [1.3.1](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.0...1.3.1) (2024-05-27)


### Bug Fixes

* **pipelines:** Local pipelines run without a token or a server url ([1eb50ad](https://github.com/BLSQ/openhexa-docker-images/commit/1eb50ad7879178759225cbc2b6c2db0e7d04fe8f))


### Miscellaneous

* **Dockerfile:** Remove the cache for apt-get to not rebuild the packages ([4276831](https://github.com/BLSQ/openhexa-docker-images/commit/427683108f61d56ff3ec34f12de835d525a24e47))
* **Pipeline:** Refactor main function ([524a29d](https://github.com/BLSQ/openhexa-docker-images/commit/524a29dba5aa18185c3cc996a9781da100b32d24))

## [1.3.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.10...1.3.0) (2024-05-17)


### Features

* run notebook as pipeline ([#23](https://github.com/BLSQ/openhexa-docker-images/issues/23)) ([8eb87c6](https://github.com/BLSQ/openhexa-docker-images/commit/8eb87c6b134ab3140a132846b1c34c748b0b6389))

## [1.2.10](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.9...1.2.10) (2024-04-10)


### Miscellaneous

* Add a stub file to warn users about the home folder ([d72e488](https://github.com/BLSQ/openhexa-docker-images/commit/d72e488137341492914efc04b564b83b987dc02c))
* Add a stub file to warn users about the home folder ([#21](https://github.com/BLSQ/openhexa-docker-images/issues/21)) ([078a29a](https://github.com/BLSQ/openhexa-docker-images/commit/078a29a9e11e01579a4c6f3c27ea591a0f7dbd17))
* **docker:** Set the openhexa.sdk version to install to 0.1.* ([3cf2da8](https://github.com/BLSQ/openhexa-docker-images/commit/3cf2da832295b46a6c0297cfa3ca7afdb2ce2ca1))

## [1.2.9](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.8...1.2.9) (2024-04-09)


### Bug Fixes

* **sdk:** Update the version of the openhexa sdk used in images ([bdcc37b](https://github.com/BLSQ/openhexa-docker-images/commit/bdcc37bf5deec340767492c1ce88055e3bbb6bea))

## [1.2.8](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.7...1.2.8) (2024-04-09)


### Bug Fixes

* **BLSQ:** Wrong versions of packages for conda-forge ([a4c9724](https://github.com/BLSQ/openhexa-docker-images/commit/a4c97241a010f1ad635c5d840e687260466d09f1))

## [1.2.7](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.6...1.2.7) (2024-04-08)


### Miscellaneous

* Add labels in dockerfile for base & blsq image ([c9b839e](https://github.com/BLSQ/openhexa-docker-images/commit/c9b839e2567567ed16654ed4779a23f00ccd81ee))
* **deps:** Add connectorx, xlsx2csv, xlswriter to blsq image ([993f7cb](https://github.com/BLSQ/openhexa-docker-images/commit/993f7cbf0ddae406a48b6d30bee7bb2b601edb88))
* **deps:** Update openhexa.sdk & openhexa.toolbox ([e096c9a](https://github.com/BLSQ/openhexa-docker-images/commit/e096c9aa795d1b5882debd9df50ad37e6e2eaa25))
* format bootstrap_pipeline ([8582c1f](https://github.com/BLSQ/openhexa-docker-images/commit/8582c1f132a28be284cf348bcac0ddeb16214018))

## [1.2.6](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.5...1.2.6) (2024-02-23)


### Bug Fixes

* remove cache ([640e5c0](https://github.com/BLSQ/openhexa-docker-images/commit/640e5c0c4403fe7cd921e9511d35d9deaf784fdb))
* Use the same layer to install R & python deps ([#16](https://github.com/BLSQ/openhexa-docker-images/issues/16)) ([36e8f61](https://github.com/BLSQ/openhexa-docker-images/commit/36e8f610a20d1825efd8e3ed363ad199903a88c6))

## [1.2.5](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.4...1.2.5) (2024-02-23)


### Bug Fixes

* Add cache for local builds, use conda with mamba resolver ([c6705bc](https://github.com/BLSQ/openhexa-docker-images/commit/c6705bccb01000d08fe56c9eb10cd3993fd23d8f))
* use conda for legacy ([656be32](https://github.com/BLSQ/openhexa-docker-images/commit/656be32859739d9608caef4a3e3f9d40db06ebcd))


### Miscellaneous

* **ci:** build images also on pushes on main ([306ab19](https://github.com/BLSQ/openhexa-docker-images/commit/306ab192167fa0e25814163a75248972103843b6))
* set default tag to main ([9e1e9da](https://github.com/BLSQ/openhexa-docker-images/commit/9e1e9da8b41348e0270fd43d6a167bf6de9f257c))

## [1.2.4](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.3...1.2.4) (2024-02-22)


### Bug Fixes

* add missing python libraries ([ce6f5fe](https://github.com/BLSQ/openhexa-docker-images/commit/ce6f5fe0beef8d411b9a059d24c373ab36f75366))

## [1.2.3](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.2...1.2.3) (2024-02-22)


### Bug Fixes

* do not add link ([a54498b](https://github.com/BLSQ/openhexa-docker-images/commit/a54498b556092a8bd89b91a8e8842b20522d94ff))

## [1.2.2](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.1...1.2.2) (2024-02-22)


### Bug Fixes

* Install stringi from conda-forge ([7a41f98](https://github.com/BLSQ/openhexa-docker-images/commit/7a41f98c99b863b227b89a469d2b1a27b7b09920))

## [1.2.1](https://github.com/BLSQ/openhexa-docker-images/compare/1.2.0...1.2.1) (2024-02-21)


### Bug Fixes

* **blsq:** Add ICU developement package to handle unicode in R ([f74a067](https://github.com/BLSQ/openhexa-docker-images/commit/f74a06781b2e558e43720b2ed0d017796cf7c2e8))

## [1.2.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.1.0...1.2.0) (2024-02-20)


### Features

* **S3:** Make the base image compatible with a local hosting solution ([161e70f](https://github.com/BLSQ/openhexa-docker-images/commit/161e70f1e5c82d4de3cc5fd17cdb7113ba5dd6ce))
* Update openhexa-sdk to 0.1.37 ([0b11136](https://github.com/BLSQ/openhexa-docker-images/commit/0b1113696ec55b3818f5b5973fb0e5bf216e482c))


### Miscellaneous

* **localhosting:** Add a way to mount S3 compatible bukets ([719896e](https://github.com/BLSQ/openhexa-docker-images/commit/719896e017ac3146d4e124cc401a1944449d456d))

## [1.1.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.0.3...1.1.0) (2024-01-30)


### Features

* bump OpenHEXA SDK to 0.1.36 ([#7](https://github.com/BLSQ/openhexa-docker-images/issues/7)) ([e26ff88](https://github.com/BLSQ/openhexa-docker-images/commit/e26ff884b13d3e97718e0584021371e400fd207b))

## [1.0.3](https://github.com/BLSQ/openhexa-docker-images/compare/1.0.2...1.0.3) (2024-01-25)


### Miscellaneous

* **deps:** Update openhexa-sdk-python to 0.1.35 ([3c3e1f3](https://github.com/BLSQ/openhexa-docker-images/commit/3c3e1f3a8a03e6f9e0c6d9ae587c604160007a53))

## [1.0.2](https://github.com/BLSQ/openhexa-docker-images/compare/1.0.1...1.0.2) (2024-01-17)


### Bug Fixes

* Legacy configuration was not using the correct mounting options ([6cdfc5c](https://github.com/BLSQ/openhexa-docker-images/commit/6cdfc5c692df025365e6aea2aa6325540e5393af))

## [1.0.1](https://github.com/BLSQ/openhexa-docker-images/compare/1.0.0...1.0.1) (2024-01-17)


### Bug Fixes

* chmod on /home/jovyan crashes the server ([ef27ae7](https://github.com/BLSQ/openhexa-docker-images/commit/ef27ae76ea857f6687d4ca6cfb6e21a471dcfa96))

## 1.0.0 (2024-01-16)


### Features

* add choices in workflow ([cda0b77](https://github.com/BLSQ/openhexa-docker-images/commit/cda0b77a6caf14bd3af7f9b3a5d681d622bb6108))
* add option for latest tag in workflow ([233279c](https://github.com/BLSQ/openhexa-docker-images/commit/233279c498659197ebe1112d05b53c931b4d1e4c))
* add option for latest tag in workflow ([1856896](https://github.com/BLSQ/openhexa-docker-images/commit/18568965cfece84a76a6d474fa4e2ca048036298))
* base environment image ([68affe2](https://github.com/BLSQ/openhexa-docker-images/commit/68affe26577da248b858041122ba3de3d4f07914))
* OpenHEXA SDK & Toolbox version info ([#1](https://github.com/BLSQ/openhexa-docker-images/issues/1)) ([da9a9a7](https://github.com/BLSQ/openhexa-docker-images/commit/da9a9a77df33c8f26cf16d34a472752bcaf177d4))


### Bug Fixes

* boolean eval in workflow ([10cb5e7](https://github.com/BLSQ/openhexa-docker-images/commit/10cb5e71e4fa7412beed93635125408a0b4b0222))
* scripts & sample files ([851cd4d](https://github.com/BLSQ/openhexa-docker-images/commit/851cd4db59d2c6c04a70e7c88b2aa1e743c9b0d4))
* scripts & sample files ([d021fa4](https://github.com/BLSQ/openhexa-docker-images/commit/d021fa4434cdf04931b78991a7ebbcae31b6e175))
* scripts & sample files ([3d4c113](https://github.com/BLSQ/openhexa-docker-images/commit/3d4c11300b5f4288b0ee50e7452f84cba138505a))
* scripts & sample files ([7d5688a](https://github.com/BLSQ/openhexa-docker-images/commit/7d5688a7b255d50c6ac99e1b638a453cedf70107))
* wrong copy for hexa_scripts ([f7772d9](https://github.com/BLSQ/openhexa-docker-images/commit/f7772d930d4127afe9efea8f218a2f373c719fc2))


### Miscellaneous

* bump OpenHEXA SDK to 0.1.33 ([0998653](https://github.com/BLSQ/openhexa-docker-images/commit/0998653cfa19f7fe47917f3d7b11e522d0774378))
* rename workflow ([7f18e4d](https://github.com/BLSQ/openhexa-docker-images/commit/7f18e4db26d75d09066d4f85dd798133d6e9353f))
* update openhexa.sdk to 0.1.32 ([a41b305](https://github.com/BLSQ/openhexa-docker-images/commit/a41b305659a216690aedde041961accdab55b71d))
