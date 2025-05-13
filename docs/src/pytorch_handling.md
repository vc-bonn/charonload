# PyTorch Handling

In addition to JIT Compiling, CharonLoad also provides native support for finding and linking against the PyTorch C++ library which is installed as part of the Python package ``torch``. To this end, the CMake function <project:#charonload_add_torch_library> is provided as a thin wrapper around [add_library()](<inv:cmake.org#command/add_library>).

However, the PyTorch C++ API comes with several non-trivial usage requirements that linking libraries must fulfill. Not meeting these requirements will lead to potentially obscure and hard-to-debug compiler and linker errors. Thus, CharonLoad automatically detects these usage requirements and adds them to the CMake target created by <project:#charonload_add_torch_library>.

In particular, the following PyTorch properties are handled:


:::::{grid} 2 2 3 3
:gutter: 3 3 4 4

::::{grid-item-card}
:link: pytorch_handling/cpp_standard
:link-type: doc

**C++ Standard**
^^^
Set minimum C++ standard for using PyTorch.

::::

::::{grid-item-card}
:link: pytorch_handling/cpp11_abi
:link-type: doc

**C++11 ABI**
^^^
Set correct C++11 ABI for linking.

::::

::::{grid-item-card}
:link: pytorch_handling/position_independent_code
:link-type: doc

**Position-Independent Code (PIC)**
^^^
Set required PIC flag for linking.

::::

::::{grid-item-card}
:link: pytorch_handling/cuda_flags
:link-type: doc

**CUDA Flags**
^^^
Set required CUDA flags for parents and siblings.

::::

:::::


```{toctree}
:hidden:

pytorch_handling/cpp_standard
pytorch_handling/cpp11_abi
pytorch_handling/position_independent_code
pytorch_handling/cuda_flags
```
