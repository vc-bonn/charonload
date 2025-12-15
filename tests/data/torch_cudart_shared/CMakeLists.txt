cmake_minimum_required(VERSION 3.27)

project(torch_cudart_shared LANGUAGES CXX CUDA)

find_package(charonload)

find_package(CUDAToolkit REQUIRED)

if(charonload_FOUND)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

    # External interface library
    add_library(external_interface INTERFACE)

    target_compile_definitions(external_interface INTERFACE EXTERNAL_INTERFACE)

    # External library with alias
    add_library(external_cudart_lib SHARED)

    target_sources(external_cudart_lib PRIVATE external_cudart_lib.cpp)
    target_include_directories(external_cudart_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
    target_link_libraries(external_cudart_lib PRIVATE CUDA::cudart)

    # External library
    add_library(aliased_external_cudart_lib SHARED)
    add_library(namespace::aliased_external_cudart_lib ALIAS aliased_external_cudart_lib)

    target_sources(aliased_external_cudart_lib PRIVATE aliased_external_cudart_lib.cpp)
    target_include_directories(aliased_external_cudart_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
    target_link_libraries(aliased_external_cudart_lib PRIVATE CUDA::cudart)

    # Library already linking to Torch
    charonload_add_torch_library(torch_cudart_shared SHARED)

    target_sources(torch_cudart_shared PRIVATE two_times_cuda.cu)
    target_link_libraries(torch_cudart_shared PRIVATE external_cudart_lib
                                                      namespace::aliased_external_cudart_lib
                                                      external_interface)

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_cudart_shared)
endif()
