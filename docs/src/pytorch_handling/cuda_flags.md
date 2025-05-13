# CUDA Flags

In order to simplify writing CUDA kernels, the PyTorch C++ library enables several compiler flags:

- Using CUDA architectures of detected GPUs
- Enabling `__host__ __device__` lambda functions, e.g., with thrust/CUB algorithms
- Enabling relaxed `constexpr` rules to reuse, e.g., `std::clamp` in kernels and `__device__` functions
- Suppressing some noisy warnings

However, the PyTorch C++ library provides these flags by modifying the (old-school) [``CUDA_NVCC_FLAGS``](<inv:cmake.org#module/FindCUDA>) variable. Although CMake will pick up the variable, the modifications are **only** visible in the directory (and subdirectory) scope(s) where PyTorch has been found by [``find_package``](<inv:cmake.org#command/find_package>). This may lead to compiler errors for depending targets in parent or sibling directories when finding PyTorch with the ``GLOBAL`` option enabled, as this promotes **only** the respective targets to all scopes but leaves the variables modifications in the calling scope.


Charonload automatically detects the modified compile flags and attaches them as an `INTERFACE` property to the CUDA target of the PyTorch C++ library, such that they will be correctly propagated to any linking target.
