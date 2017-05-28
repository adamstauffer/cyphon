# Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/). This project adheres to [Semantic Versioning](http://semver.org/).

<a name="Unreleased"></a>
## [Unreleased]

<a name="1.1.3"></a>
## [1.1.3](https://github.com/dunbarcyber/cyphon/compare/1.1.2...1.1.3) (2017-05-27)

### Added

- **categories:** added REST API endpoint for Categories ([360dc56](https://github.com/dunbarcyber/cyphon/commit/360dc56))
- **docs:** added email tutorial ([d8fd982](https://github.com/dunbarcyber/cyphon/commit/d8fd982))
- **docs:** added Logstash tutorial ([69769f9](https://github.com/dunbarcyber/cyphon/commit/69769f9), [1c56516](https://github.com/dunbarcyber/cyphon/commit/1c56516))
- **docs:** added minimum system requirements ([d00b95](https://github.com/dunbarcyber/cyphon/commit/d00b95))

### Fixed

- **.gitignore:** fixed directory for Cyphon settings ([e863c4a](https://github.com/dunbarcyber/cyphon/commit/e863c4a))
- **bottler.bottles:** fixed bug with EmbeddedDocumentFields ([6fd70f5](https://github.com/dunbarcyber/cyphon/commit/6fd70f5))
- **docs:** updated instructions for Elasticsearch data directory ([03c3446](https://github.com/dunbarcyber/cyphon/commit/03c3446))

<a name="1.1.2"></a>
## [1.1.2](https://github.com/dunbarcyber/cyphon/compare/1.1.1...1.1.2) (2017-05-16)

### Fixed

- **sifter.mungers:** modified `Munger.process()` to avoid errors when processing mail ([84f8871](https://github.com/dunbarcyber/cyphon/commit/84f8871))

<a name="1.1.1"></a>
## [1.1.1](https://github.com/dunbarcyber/cyphon/compare/1.1.0...1.1.1) (2017-05-16)

### Fixed

- **alerts:** modified `Alert.save()` so that `location` and `content_date` are added the Alert to even if the Alert already has `data`, and a `title` with a default value is refreshed ([a37d9eb](https://github.com/dunbarcyber/cyphon/commit/a37d9eb))
- **alerts:** `Alert.saved_data` is no longer cached ([9fdba5d](https://github.com/dunbarcyber/cyphon/commit/9fdba5d))
- **engines.elasticsearch.engine:** Elasticsearch indexes are refreshed prior to searching by id ([65d72e2](https://github.com/dunbarcyber/cyphon/commit/65d72e2))
- **watchdogs:** Watchdogs pass data directly to Muzzles instead of fetching saved data, avoiding race condition in Logstash ([7c5a53d](https://github.com/dunbarcyber/cyphon/commit/7c5a53d))

<a name="1.1.0"></a>
## [1.1.0](https://github.com/dunbarcyber/cyphon/compare/1.0.3...1.1.0) (2017-05-14)

### Added

- **cyphon.documents:** added `DocumentOj` class for handling document references ([d701762](https://github.com/dunbarcyber/cyphon/commit/d701762))
- **receiver.receiver:** added RabbitMQ queue consumers for DataChutes, Watchdogs, and Monitors ([d701762](https://github.com/dunbarcyber/cyphon/commit/d701762))
- **target.followees:** added `get_by_natural_key()` method for Followees, Accounts, LegalNames, and Aliases ([0f8f3b8](https://github.com/dunbarcyber/cyphon/commit/0f8f3b8))
- **target.locations:** added `get_by_natural_key()` method for Locations ([2b5199d](https://github.com/dunbarcyber/cyphon/commit/2b5199d))
- **target.searchterms:** added `get_by_natural_key()` method for SearchTerms ([813c1ca](https://github.com/dunbarcyber/cyphon/commit/813c1ca))

### Fixed

- **sifter.condensers:** removed extra inline Fitting form ([10f53ce](https://github.com/dunbarcyber/cyphon/commit/10f53ce))
- **sifter.logsifter:** fixed "Test this rule" tool on LogRule admin page ([751d55b](https://github.com/dunbarcyber/cyphon/commit/751d55b))

<a name="1.0.3"></a>
## [1.0.3](https://github.com/dunbarcyber/cyphon/compare/1.0.2...1.0.3) (2017-05-14)

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
- **responder.actions.filters:** fixed ActionFilterBackend to allow access to Actions associated with public Passports ([952464b](https://github.com/dunbarcyber/cyphon/commit/952464b))

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
