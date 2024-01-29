cmake_minimum_required(VERSION 3.27)

project(torch_common_shared LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

    charonload_add_torch_library(torch_common_shared SHARED)

    target_sources(torch_common_shared PRIVATE two_times_cpu.cpp)

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_common_shared)
endif()
