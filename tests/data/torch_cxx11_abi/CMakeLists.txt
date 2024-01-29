cmake_minimum_required(VERSION 3.27)

project(torch_common_shared LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

    # External interface library
    add_library(external_interface INTERFACE)

    target_compile_definitions(external_interface INTERFACE EXTERNAL_INTERFACE)

    # External library with alias
    add_library(external_string_lib SHARED)

    target_sources(external_string_lib PRIVATE external_string_lib.cpp)
    target_compile_features(external_string_lib PUBLIC cxx_std_17)
    target_include_directories(external_string_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

    # External library
    add_library(aliased_external_string_lib SHARED)
    add_library(namespace::aliased_external_string_lib ALIAS aliased_external_string_lib)

    target_sources(aliased_external_string_lib PRIVATE aliased_external_string_lib.cpp)
    target_compile_features(aliased_external_string_lib PUBLIC cxx_std_17)
    target_include_directories(aliased_external_string_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

    # There are further linked elements that should be checked against but are already implicitly included (by Torch):
    # - Absolute path to library
    # - Linker flags
    # - Generator expressions

    # Library already linking to Torch
    charonload_add_torch_library(torch_cxx11_abi SHARED)

    target_sources(torch_cxx11_abi PRIVATE two_times_cpu.cpp)
    target_link_libraries(torch_cxx11_abi PRIVATE external_string_lib
                                                  namespace::aliased_external_string_lib
                                                  external_interface)

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_cxx11_abi)
endif()
