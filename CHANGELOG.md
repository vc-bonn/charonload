# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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

[0.1.1]: https://github.com/vc-bonn/charonload/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/vc-bonn/charonload/releases/tag/v0.1.0
