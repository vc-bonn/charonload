cmake_minimum_required(VERSION 3.27)

project(torch_colliding_binding_cmake_target LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    add_library(${TORCH_EXTENSION_NAME} STATIC)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE two_times_cpu.cpp)
    target_compile_features(${TORCH_EXTENSION_NAME} PRIVATE cxx_std_17)
endif()
