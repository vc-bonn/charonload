# C++11 ABI

:::{admonition} Hint
:class: hint

This behavior is exclusive to Linux and the GCC compiler.
:::

On Linux, the default C++ compiler is typically set to GCC. With the release of GCC 5 in 2017, its standard library introduced several [breaking ABI (Application Binary Interface) changes](https://gcc.gnu.org/wiki/Cxx11AbiCompatibility) between C++11 (and future standards) and C++98. While this may look irrelevant these days, PyTorch is built with great compatibility in mind such that even recent versions support Python's `manylinux2014` platform ([PEP 599](https://peps.python.org/pep-0599/)) which requires compatibility with GCC 4.8.

This, in turn, means that the PyTorch C++ library must adhere to and compile against the **old CXX11 ABI**. Consequently, projects linking against PyTorch also need to specify the respective compiler flag `_GLIBCXX_USE_CXX11_ABI=0`. This even extends to **all** other 3rd-party dependencies and often needs manual adjustment to their CMake scripts. Not meeting these requirements will lead to strange linker errors containing the mangled names of the incompatible C++ standard library classes. 

CharonLoad automatically detects the CXX11 ABI flag used in PyTorch, transitively scans for all dependencies, and patches each of the respective CMake targets to make use of the ABI flag.


:::{admonition} Note
:class: note

Future versions of PyTorch, starting with [PyTorch 2.7](https://github.com/pytorch/pytorch/issues/149044), will switch to the **new CXX11 ABI**. Thus, compilation will work without CharonLoad's target patching.
:::
