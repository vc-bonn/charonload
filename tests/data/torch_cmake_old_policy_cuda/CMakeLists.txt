# Oldest policy version without deprecation warning for CMake 3.27
cmake_minimum_required(VERSION 3.5)

project(torch_cmake_old_policy_cuda LANGUAGES CXX CUDA)

find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp two_times_cuda.cu)
endif()
