cmake_minimum_required(VERSION 3.27)

project(charonload)

if(PROJECT_IS_TOP_LEVEL)
    message(FATAL_ERROR "charonload cannot be built directly.\n"
    "Use this CMake file only via \"add_subdirectory\" or the \"FetchContent\" module to make charonload available in C++-only projects without JIT compilation.")
endif()


list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/src/charonload")

find_package(charonload REQUIRED GLOBAL)


set(MODIFIED_CMAKE_VARIABLES
    # Set by Caffe2/public/cuda.cmake as part of TorchConfig.cmake
    "CMAKE_CUDA_FLAGS"
    "CMAKE_CUDA_FLAGS_DEBUG"
    "CMAKE_CUDA_FLAGS_MINSIZEREL"
    "CMAKE_CUDA_FLAGS_RELEASE"
    "CMAKE_CUDA_FLAGS_RELWITHDEBINFO"
)

foreach(var IN LISTS MODIFIED_CMAKE_VARIABLES)
    set(${var} ${${var}} PARENT_SCOPE)
endforeach()
