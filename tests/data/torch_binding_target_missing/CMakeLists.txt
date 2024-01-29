cmake_minimum_required(VERSION 3.27)

project(torch_no_binding_cmake_target LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    add_library(other_library STATIC)

    target_sources(other_library PRIVATE two_times_cpu.cpp)
    target_compile_features(other_library PRIVATE cxx_std_17)
endif()
