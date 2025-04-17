# C++ Standard

Like many projects, the PyTorch C++ library regularly adapts its minimum required C++ standard version to newer versions in order to benefit from the respective language and standard library improvements. In the past, the C++ standard has been numped for the following releases:

- C++11 &rarr; C++14: PyTorch 1.5 (see [release announcement](https://github.com/pytorch/pytorch/releases/tag/v1.4.0))
- C++14 &rarr; C++17: PyTorch 2.1 (see [release announcement](https://github.com/pytorch/pytorch/releases/tag/v2.1.0))

Future versions may further increase the used standard to, e.g., C++20.

However, the PyTorch C++ library does not publicly expose this requirement to projects linking against it which may lead to compiler errors in the following cases:

- The project explicitly only needs a lower standard, e.g. `set(CMAKE_CXX_STANDARD 11)` for C++11
- The project relies on the default standard selected of the compiler, e.g. C++14 for MSVC

CharonLoad automatically detects the minimum required C++ standard in order to use the PyTorch C++ library and sets the corresponding [CMake Compile Feature](https://cmake.org/cmake/help/latest/manual/cmake-compile-features.7.html#requiring-language-standards).
