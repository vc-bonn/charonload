cmake_minimum_required(VERSION 3.27)

project(torch_cxx_standard LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp two_times_cpu.cpp)
endif()
