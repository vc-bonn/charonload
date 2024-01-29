cmake_minimum_required(VERSION 3.27)

project(torch_common_static LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(torch_common_static STATIC)

    target_sources(torch_common_static PRIVATE two_times_cpu.cpp)

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_common_static)
endif()
