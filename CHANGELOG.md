# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/). This project adheres to [Semantic Versioning](http://semver.org/).


<a name="Unreleased"></a>
## [Unreleased]

### Added

- **bottler:** added `get_by_natural_key()` method for BottleFields and LabelFields ([68c2a15](https://github.com/dunbarcyber/cyphon/commit/68c2a15))
- **contexts:** added `get_by_natural_key()` method for Contexts and ContextFields ([09ff0b8](https://github.com/dunbarcyber/cyphon/commit/09ff0b8))
- **entrypoints:** added conditional for loading example fixtures ([a0efa1f](https://github.com/dunbarcyber/cyphon/commit/a0efa1f))
- **watchdogs:** added `get_by_natural_key()` method for Triggers ([8312713](https://github.com/dunbarcyber/cyphon/commit/8312713))

### Changed

- **cyphon.tests.functional_tests:** enabled functional tests to run in a Selenium 3 Docker container ([fe170cc](https://github.com/dunbarcyber/cyphon/commit/fe170cc))
- **docs:** replaced install instructions for Docker Engine with those for Docker Community Edition ([4aa080c](https://github.com/dunbarcyber/cyphon/commit/4aa080c))

### Fixed

- **cyphon.dashboard:** added Protocols and Constance to admin dashboard ([ee34361](https://github.com/dunbarcyber/cyphon/commit/ee34361), [0cbbb15](https://github.com/dunbarcyber/cyphon/commit/0cbbb15))

### Removed

- **fixtures:** removed default fixtures, since these are provided in [Cyphondock](https://github.com/dunbarcyber/cyphondock/) ([ba25363](https://github.com/dunbarcyber/cyphon/commit/ba25363))

### Security

* **entrypoints**: Celery beat and worker are now run without superuser privileges ([8f18b42](https://github.com/dunbarcyber/cyphon/commit/8f18b42))


<a name="1.0.2"></a>
## [1.0.2](https://github.com/dunbarcyber/cyphon/compare/1.0.1...1.0.2) (2017-04-07)

### Added

- **docs:** added CHANGELOG ([baf76ae](https://github.com/dunbarcyber/cyphon/commit/baf76ae))

### Changed

- **docs:** changed AUTHORS to markdown ([beb0d87](https://github.com/dunbarcyber/cyphon/commit/beb0d87))

### Fixed

- **contexts:** fixed issue with ContextFilters handling nested fields ([ac58553](https://github.com/dunbarcyber/cyphon/commit/ac58553))
- **cyphon.settings:** applied fix for [django-filter issue #562](https://github.com/carltongibson/django-filter/issues/562) ([7f09009](https://github.com/dunbarcyber/cyphon/commit/7f09009))
- **engine.mongodb.engine:** fixed issue with MongoDB queries ([ea1b043](https://github.com/dunbarcyber/cyphon/commit/ea1b043))
- **watchdogs:** fixed issue with Muzzles handling nested fields ([fe30e75](https://github.com/dunbarcyber/cyphon/commit/fe30e75))


<a name="1.0.1"></a>
## [1.0.1](https://github.com/dunbarcyber/cyphon/compare/1.0.0...1.0.1) (2017-04-05)

### Changed

- **docs:** added disclaimer to securing-cyphon.txt ([39e2d65](https://github.com/dunbarcyber/cyphon/commit/39e2d65), [4cdc5e2](https://github.com/dunbarcyber/cyphon/commit/4cdc5e2), [c811257](https://github.com/dunbarcyber/cyphon/commit/c811257), [b1722c3](https://github.com/dunbarcyber/cyphon/commit/b1722c3))
- **docs:** updated favicon ([14ab3ff](https://github.com/dunbarcyber/cyphon/commit/14ab3ff))

### Fixed

- **docs:** deleted obsolete appuser docs ([ea3e5f3](https://github.com/dunbarcyber/cyphon/commit/ea3e5f3))
- **query.reservoirqueries.reservoirqueries:** fixed bug affecting Followee-based Filters ([b6a8fd9](https://github.com/dunbarcyber/cyphon/commit/b6a8fd9))

<a name="1.0.0"></a>
## [1.0.0](https://github.com/dunbarcyber/cyphon/releases/tag/1.0.0) (2017-04-04)
