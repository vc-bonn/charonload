cmake_minimum_required(VERSION 3.27)

project(torch_wrong_cmake_target LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(wrong_target_name MODULE)

    target_sources(wrong_target_name PRIVATE bindings.cpp two_times_cpu.cpp)
endif()
