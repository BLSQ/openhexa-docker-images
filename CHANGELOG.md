# Changelog

## [1.7.3](https://github.com/BLSQ/openhexa-docker-images/compare/1.7.2...1.7.3) (2025-03-03)


### Release

* 1.7.3 ([79f331a](https://github.com/BLSQ/openhexa-docker-images/commit/79f331ac1fde1dc500f6966f9154f92238d813ff))
* 1.7.3 ([e526bcd](https://github.com/BLSQ/openhexa-docker-images/commit/e526bcd61680e378450bd678859fbbf428ac658e))
* 1.7.3 ([11bf446](https://github.com/BLSQ/openhexa-docker-images/commit/11bf446b356fbaa4166e10d22126a822c87e487c))

## [1.7.2](https://github.com/BLSQ/openhexa-docker-images/compare/1.7.1...1.7.2) (2025-02-27)


### Bug Fixes

* Try to use binaries to install cran packages (instead of building them from source ([36a376c](https://github.com/BLSQ/openhexa-docker-images/commit/36a376c23c2a045dd6cd265903250ba470af7619))

## [1.7.1](https://github.com/BLSQ/openhexa-docker-images/compare/1.7.0...1.7.1) (2025-02-25)


### Miscellaneous Chores

* **release:** Release v1.7.1 ([0918d71](https://github.com/BLSQ/openhexa-docker-images/commit/0918d7137500af332d6b2d8e830cd130e202991f))

## [1.7.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.6.2...1.7.0) (2025-02-24)


### Features

* **Blsq:** update blsq image ([#65](https://github.com/BLSQ/openhexa-docker-images/issues/65)) ([75e0c98](https://github.com/BLSQ/openhexa-docker-images/commit/75e0c983b9248ed6fc183876b5c9878d3a536a7f))


### Bug Fixes

* Also set conda ownership to jovyan in the blsq image ([a3da822](https://github.com/BLSQ/openhexa-docker-images/commit/a3da8228c2bedd10eb8d2c184fc8ea3b07302b27))
* **blsq-r:** Conda reports a problem when installing 3 deps. Commenting them for now ([5ea171f](https://github.com/BLSQ/openhexa-docker-images/commit/5ea171f439f107d2459dbef0cfd0fb5d4f035fe5))
* chown /opt/conda to jovyan ([8dd88b1](https://github.com/BLSQ/openhexa-docker-images/commit/8dd88b17d1c47f8e78c648e2fc8ad2549a5a1c11))
* **R:** XML deps were missing in order to install "malariaAtlas" ([#70](https://github.com/BLSQ/openhexa-docker-images/issues/70)) ([0b832b0](https://github.com/BLSQ/openhexa-docker-images/commit/0b832b030e28e6528adfc1f6dc93c79850f6f506))

## [1.6.2](https://github.com/BLSQ/openhexa-docker-images/compare/1.6.1...1.6.2) (2024-12-16)


### Bug Fixes

* **Conda:** Install all conda packages with non-root user ([ae34cdf](https://github.com/BLSQ/openhexa-docker-images/commit/ae34cdf1b765f1f766c8c273afea574eeb49b131))
* **pip:** Do not install deps in user space ([39cf14d](https://github.com/BLSQ/openhexa-docker-images/commit/39cf14d231937d9d1e303d3642a71923dc206588))

## [1.6.1](https://github.com/BLSQ/openhexa-docker-images/compare/1.6.0...1.6.1) (2024-12-16)


### Bug Fixes

* **requirements:** Install packages in user space ([6debe51](https://github.com/BLSQ/openhexa-docker-images/commit/6debe51e4340c08877b82da6d11fe61a4a9552f5))

## [1.6.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.5.0...1.6.0) (2024-12-09)


### Features

* update openhexa.sdk & openhexa.toolbox ([52f993f](https://github.com/BLSQ/openhexa-docker-images/commit/52f993f92537a8141ce58106e4218eb153f46fc9))


### Bug Fixes

* Add bioconda as a channel to use ([#64](https://github.com/BLSQ/openhexa-docker-images/issues/64)) ([9d0c4ca](https://github.com/BLSQ/openhexa-docker-images/commit/9d0c4cae87f7a719796c0928b279211cc1639cee))

## [1.5.0](https://github.com/BLSQ/openhexa-docker-images/compare/1.4.6...1.5.0) (2024-12-02)


### Features

* **Blsq:** add ruff linter to blsq image ([#60](https://github.com/BLSQ/openhexa-docker-images/issues/60)) ([bccf4ba](https://github.com/BLSQ/openhexa-docker-images/commit/bccf4baa56fafd64393a9ed76f24f096e5e19adb))
* **Docker:** create a custom R image ([#57](https://github.com/BLSQ/openhexa-docker-images/issues/57)) ([63dae52](https://github.com/BLSQ/openhexa-docker-images/commit/63dae522c214c6d535b84655f8e37a89738aa965))

## [1.4.6](https://github.com/BLSQ/openhexa-docker-images/compare/1.4.5...1.4.6) (2024-11-20)


### Bug Fixes

* set the USER for the blsq image; remove g+w on the wrap_up.py & merge install.packages together ([456febf](https://github.com/BLSQ/openhexa-docker-images/commit/456febf65c7a6397a77c62d5ce1566ca7633ccaf))

## [1.4.5](https://github.com/BLSQ/openhexa-docker-images/compare/1.4.4...1.4.5) (2024-11-15)


### Miscellaneous Chores

* Release 1.4.5 ([9df8117](https://github.com/BLSQ/openhexa-docker-images/commit/9df81172454bce133d437ff270aa9eb4b50e5d47))

## [1.4.4](https://github.com/BLSQ/openhexa-docker-images/compare/1.4.3...1.4.4) (2024-10-16)


### Bug Fixes

* **FS:** Change owner of the /home/hexa/workspace folder to jovyan since it's created as root from K8S ([#54](https://github.com/BLSQ/openhexa-docker-images/issues/54)) ([9bb8936](https://github.com/BLSQ/openhexa-docker-images/commit/9bb89362f898ca7f0c6434f756916919932e697a))
* **fuse:** Workspace directory was not writeable by the user ([68abc78](https://github.com/BLSQ/openhexa-docker-images/commit/68abc782e937a0228f7c3fdf679533519614585e))
* **Pipelines:** print exception traceback ([#56](https://github.com/BLSQ/openhexa-docker-images/issues/56)) ([a13ac4d](https://github.com/BLSQ/openhexa-docker-images/commit/a13ac4d88312a53860432075e4bd5e6e483384f0))

## [1.4.3](https://github.com/BLSQ/openhexa-docker-images/compare/v1.4.2...1.4.3) (2024-09-05)


### Bug Fixes

* Try to fix release-please to generate tags without v ([96f2fcd](https://github.com/BLSQ/openhexa-docker-images/commit/96f2fcd9f52919d6722207ed9e26af41e6878c35))

## [1.4.2](https://github.com/BLSQ/openhexa-docker-images/compare/v1.4.1...v1.4.2) (2024-09-05)


### Bug Fixes

* Put back the include-v-in-tag ([055d28f](https://github.com/BLSQ/openhexa-docker-images/commit/055d28f96bff48effee1056aa470a8a09a9d6230))
* Remove the 'v' in front the tag (temporary solution the time release-please works as expected) ([98ccbb7](https://github.com/BLSQ/openhexa-docker-images/commit/98ccbb77ed717cdacde389d1449096d371573602))
* set the 'simple' release-type & remove include-v-in-tag that has 'false' as the default ([42fc5d6](https://github.com/BLSQ/openhexa-docker-images/commit/42fc5d6ef898132ec3f587a9c4b863ef07fb971b))

## [1.4.1](https://github.com/BLSQ/openhexa-docker-images/compare/v1.4.0...v1.4.1) (2024-09-05)


### Bug Fixes

* **ci:** Fix release-please configuration ([691b2ff](https://github.com/BLSQ/openhexa-docker-images/commit/691b2fff5edd42061e174b22152aa7c136246cc7))

## [1.4.0](https://github.com/BLSQ/openhexa-docker-images/compare/v1.3.9...v1.4.0) (2024-09-03)


### Miscellaneous Chores

* release 1.4.0 ([7554d1a](https://github.com/BLSQ/openhexa-docker-images/commit/7554d1ab09e739e0cc67a03dd5de8860398553e5))

## [1.3.9](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.8...v1.3.9) (2024-08-22)


### Bug Fixes

* **docker:** Build images using the default docker driver ([f4dfbed](https://github.com/BLSQ/openhexa-docker-images/commit/f4dfbedc63fc9e2a2a3d3d570c8b5aefe331ab5f))
* **docker:** load the base image in docker ([a48f704](https://github.com/BLSQ/openhexa-docker-images/commit/a48f7042f0072aec67fc929a8d20d5079690d4d9))
* **Notebook:** point to workspace directory as root directory ([#41](https://github.com/BLSQ/openhexa-docker-images/issues/41)) ([b7c8fd9](https://github.com/BLSQ/openhexa-docker-images/commit/b7c8fd9c73ff46344c7b06b77abbbcbc11ad313c))
* try to disable docker cache to not have awscli in the image ([#47](https://github.com/BLSQ/openhexa-docker-images/issues/47)) ([c023ef2](https://github.com/BLSQ/openhexa-docker-images/commit/c023ef22672ba0a97bcf8da7811c83137b5c8f7e))
* use the local registry (try at least) ([b80b116](https://github.com/BLSQ/openhexa-docker-images/commit/b80b116d1207438d7e3372086df76bd9b3c0c1a4))

## [1.3.8](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.7...1.3.8) (2024-06-25)


### Miscellaneous

* Add renovate.json ([#35](https://github.com/BLSQ/openhexa-docker-images/issues/35)) ([8a85f78](https://github.com/BLSQ/openhexa-docker-images/commit/8a85f78087f7caa16c2abf4d98644e46b00c389e))
* **deps:** update actions/checkout action to v4 ([#36](https://github.com/BLSQ/openhexa-docker-images/issues/36)) ([b6befe2](https://github.com/BLSQ/openhexa-docker-images/commit/b6befe24cfd8f1efa59c020ea603a0a0911e7f1b))
* **deps:** update docker/build-push-action action to v6 ([#38](https://github.com/BLSQ/openhexa-docker-images/issues/38)) ([c81065b](https://github.com/BLSQ/openhexa-docker-images/commit/c81065b44ede5394bfc0a9c6467212d61c8d3d0c))

## [1.3.7](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.6...1.3.7) (2024-06-25)


### Bug Fixes

* **SDK:** Upgrade openehxa.sdk to latest version to fix connections ([3ff4db5](https://github.com/BLSQ/openhexa-docker-images/commit/3ff4db5deb79bdcae55f7fed53d4971c049cdb9f))

## [1.3.6](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.5...1.3.6) (2024-06-24)


### Bug Fixes

* **Dockerfile:** use conda for internal ([#32](https://github.com/BLSQ/openhexa-docker-images/issues/32)) ([8811841](https://github.com/BLSQ/openhexa-docker-images/commit/8811841dd8872f6453720b8b7d7cc8dfd82a4628))

## [1.3.5](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.4...1.3.5) (2024-06-14)


### Miscellaneous

* Move libraries from base to the others ([#31](https://github.com/BLSQ/openhexa-docker-images/issues/31)) ([3ad0d01](https://github.com/BLSQ/openhexa-docker-images/commit/3ad0d0104c6b65172567147558d85b440608b15b))
* Release 1.3.5 ([43049ed](https://github.com/BLSQ/openhexa-docker-images/commit/43049edcdb37d924b5f8ac7cc89c41a4fbc50533))

## [1.3.4](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.3...1.3.4) (2024-06-10)


### Bug Fixes

* Use conda instead of pip to install requirements.txt ([dc2f430](https://github.com/BLSQ/openhexa-docker-images/commit/dc2f4309e1826f33e080eb30948e583abd37c284))

## [1.3.3](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.2...1.3.3) (2024-06-05)


### Bug Fixes

* **Pipeline:** Try..catch around the pipeline execution to catch all errors that can occur and exit the program with an error ([fc0da2a](https://github.com/BLSQ/openhexa-docker-images/commit/fc0da2a3bdf380fc65ff6a252f0eb394db3e8849))
* The pipeline job is not stopped in case of error ([#27](https://github.com/BLSQ/openhexa-docker-images/issues/27)) ([1ee95b8](https://github.com/BLSQ/openhexa-docker-images/commit/1ee95b812cfabc941ce0b000a61a60633519f129))


### Miscellaneous

* Add a wildcard for the patch number of openhexa.toolbox ([3d13ef9](https://github.com/BLSQ/openhexa-docker-images/commit/3d13ef94fea6098cc37a683de5d2449839c7cf8f))
* Removing the fuse unmount (done by the system) ([9c57eb6](https://github.com/BLSQ/openhexa-docker-images/commit/9c57eb6c0b9da690bfd6d59246d4f3911d5ceab5))

## [1.3.2](https://github.com/BLSQ/openhexa-docker-images/compare/1.3.1...1.3.2) (2024-05-28)


### Bug Fixes

* Set PYTHONUNBUFFERED to send to stdout & stderr directly ([3041386](https://github.com/BLSQ/openhexa-docker-images/commit/30413863015a2640f565f48479dd5c47f8cda66e))

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
