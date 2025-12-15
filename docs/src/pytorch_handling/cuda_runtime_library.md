# CUDA Runtime Library

Writing CUDA kernel usually involves calling several utility functions (e.g. for setting devices, synchronizing kernels, etc.), which are provided by the CUDA toolkit via the CUDA runtime Library (cudart). Depending on the use case and the type of library or C++/CUDA extension being developed, there are two candidates of cudart to consider:

- **Shared** cudart, which is typically a reasonable default and is provided via the [``CUDA::cudart``](<inv:cmake.org#module/FindCUDAToolkit>) CMake target
- **Static** cudart, which is provided by the [``CUDA::cudart_static``](<inv:cmake.org#module/FindCUDAToolkit>) CMake target

It is important to note that these two variants are inherently incompatible with each other, so only one should be chosen. The PyTorch C++ library explicitly links against cudart, but the exact choice of variant is not determined in advance and may change between versions or in the future. On the other hand, CMake automatically adds cudart to the list of linked libraries for a target if the target contains CUDA sources. The actual variant to be used can be controlled via the [`CUDA_RUNTIME_LIBRARY`](<inv:cmake.org#prop_tgt/CUDA_RUNTIME_LIBRARY>) target property, which defaults to match the target type (i.e. [``CUDA::cudart_static``](<inv:cmake.org#module/FindCUDAToolkit>) for **static** libraries, and [``CUDA::cudart``](<inv:cmake.org#module/FindCUDAToolkit>) for **shared** libraries). As a result, more sophisticated projects may accidentally result in linking both variants and could thus run into linker errors.

CharonLoad automatically detects the cudart variant used by PyTorch and sets the [`CUDA_RUNTIME_LIBRARY`](<inv:cmake.org#prop_tgt/CUDA_RUNTIME_LIBRARY>) target property accordingly, transitively scans for all dependencies, and patches each of the respective CMake targets where the cudart target differs from the expected variant.
