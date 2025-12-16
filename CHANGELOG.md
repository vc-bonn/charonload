# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.3.0] - 2025-12-16

### Added

- Select cudart library specified by PyTorch [@stotko](https://github.com/stotko) ([\#74](https://github.com/vc-bonn/charonload/pull/74))

### Removed

- Drop Python 3.9 support [@stotko](https://github.com/stotko) ([\#66](https://github.com/vc-bonn/charonload/pull/66))

### Fixed

- Fix kernel synchronization in tests [@stotko](https://github.com/stotko) ([\#73](https://github.com/vc-bonn/charonload/pull/73))


## [0.2.1] - 2025-06-07

### Fixed

- Fix propagation of PyTorch CUDA flags for multiple archs [@stotko](https://github.com/stotko) ([\#59](https://github.com/vc-bonn/charonload/pull/59))


## [0.2.0] - 2025-05-13

### Added

- Propagate PyTorch CUDA flags via CMake target [@stotko](https://github.com/stotko) ([\#57](https://github.com/vc-bonn/charonload/pull/57))
- Document JIT compiling and PyTorch handling behavior [@stotko](https://github.com/stotko) ([\#56](https://github.com/vc-bonn/charonload/pull/56))
- Support global configuration overrides with environment variables [@stotko](https://github.com/stotko) ([\#55](https://github.com/vc-bonn/charonload/pull/55))
- Add Python 3.13 support [@stotko](https://github.com/stotko) ([\#47](https://github.com/vc-bonn/charonload/pull/47))

### Changed

- Also clean if torch version has changed [@stotko](https://github.com/stotko) ([\#53](https://github.com/vc-bonn/charonload/pull/53))
- Use extension name when determining default build directory [@stotko](https://github.com/stotko) ([\#49](https://github.com/vc-bonn/charonload/pull/49))
- Defer resolving configurations until inserted into dict [@stotko](https://github.com/stotko) ([\#48](https://github.com/vc-bonn/charonload/pull/48))

### Removed

- Drop Python 3.8 support [@stotko](https://github.com/stotko) ([\#46](https://github.com/vc-bonn/charonload/pull/46))


## [0.1.4] - 2024-11-08

### Fixed

- Handle single file stubs in skip condition [@stotko](https://github.com/stotko) ([\#44](https://github.com/vc-bonn/charonload/pull/44))
- Consider all installations paths for exclusion [@stotko](https://github.com/stotko) ([\#43](https://github.com/vc-bonn/charonload/pull/43))


## [0.1.3] - 2024-10-21

### Added

- Print summary of modifications in clean and import steps [@stotko](https://github.com/stotko) ([\#40](https://github.com/vc-bonn/charonload/pull/40))

### Fixed

- Ignore relative paths in collected DLL directories [@stotko](https://github.com/stotko) ([\#39](https://github.com/vc-bonn/charonload/pull/39))
- Skip passing empty arguments to stub generation [@stotko](https://github.com/stotko) ([\#38](https://github.com/vc-bonn/charonload/pull/38))


## [0.1.2] - 2024-07-29

### Added

- Raise user warning when PyTorch is not yet imported [@stotko](https://github.com/stotko) ([\#35](https://github.com/vc-bonn/charonload/pull/35))
- Log step progress in verbose mode [@stotko](https://github.com/stotko) ([\#32](https://github.com/vc-bonn/charonload/pull/32))
- Add support for colored compiler logs on Unix [@stotko](https://github.com/stotko) ([\#27](https://github.com/vc-bonn/charonload/pull/27))

### Changed

- Honor PATH variable on Windows for DLL search [@stotko](https://github.com/stotko) ([\#36](https://github.com/vc-bonn/charonload/pull/36))
- Prefer default directories in config for installed projects [@stotko](https://github.com/stotko) ([\#33](https://github.com/vc-bonn/charonload/pull/33))
- Perform clean only for incompatible versions [@stotko](https://github.com/stotko) ([\#30](https://github.com/vc-bonn/charonload/pull/30))


## [0.1.1] - 2024-02-21

### Added

- Create `.gitignore` file for build directory [@stotko](https://github.com/stotko) ([\#22](https://github.com/vc-bonn/charonload/pull/22))

### Changed

- Print unformatted step logs in verbose mode [@stotko](https://github.com/stotko) ([\#20](https://github.com/vc-bonn/charonload/pull/20))
- Enforce modern `|` notation for unions in docs [@stotko](https://github.com/stotko) ([\#19](https://github.com/vc-bonn/charonload/pull/19))

### Fixed

- Fix CMake error with `CUDA_ARCHITECTURES` and old policy scope [@stotko](https://github.com/stotko) ([\#23](https://github.com/vc-bonn/charonload/pull/23))


## [0.1.0] - 2024-02-06

- Initial version

[0.3.0]: https://github.com/vc-bonn/charonload/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/vc-bonn/charonload/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/vc-bonn/charonload/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/vc-bonn/charonload/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/vc-bonn/charonload/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/vc-bonn/charonload/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/vc-bonn/charonload/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/vc-bonn/charonload/releases/tag/v0.1.0
