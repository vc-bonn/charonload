#[[.rst:
This module provides some useful functions to propagate the settings from by charonload to the user's C++ code. The
path to this module becomes automatically propagated if it is enabled. A typical example on how to use the module is
shown in the following:

.. code-block:: cmake

  find_package(charonload)

  if(charonload_FOUND)
      charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

      # Add source files containing Python bindings, etc.
      target_sources(${TORCH_EXTENSION_NAME} PRIVATE ...)

      # Add further properties to the target, e.g. link against other libraries, etc.
      # ...
  endif()

#]]

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../" ABSOLUTE)


if(CMAKE_VERSION VERSION_LESS 3.27)
    message(FATAL_ERROR "CharonLoad requires CMake 3.27+ but older version ${CMAKE_VERSION} is used instead!")
endif()
cmake_policy(VERSION 3.27)


macro(charonload_message)
    if(NOT charonload_FIND_QUIETLY)
        message(${ARGV})
    endif()
endmacro()


charonload_message(STATUS "")
charonload_message(STATUS "--------------------------- find_package(charonload) ----------------------------")
charonload_message(STATUS "")


set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Enabled by charonload" FORCE)
charonload_message(STATUS "Enabled CMAKE_EXPORT_COMPILE_COMMANDS: ${CMAKE_EXPORT_COMPILE_COMMANDS}")


include(CMakeFindDependencyMacro)

charonload_message(STATUS "Finding Python ...")
list(APPEND CMAKE_MESSAGE_INDENT "  ")

if(DEFINED CHARONLOAD_PYTHON_EXECUTABLE)
    set(Python_EXECUTABLE ${CHARONLOAD_PYTHON_EXECUTABLE})
endif()
find_dependency(Python COMPONENTS Development Interpreter)

list(POP_BACK CMAKE_MESSAGE_INDENT)


include("${CMAKE_CURRENT_LIST_DIR}/prefix_paths.cmake")
charonload_determine_prefix_paths()

list(APPEND CMAKE_PREFIX_PATH ${CHARONLOAD_PREFIX_PATH})


charonload_message(STATUS "Finding Torch ...")
list(APPEND CMAKE_MESSAGE_INDENT "  ")


# Suppress as much messages as possible when finding torch dependencies
if(charonload_FIND_QUIETLY)
    set(Caffe2_FIND_QUIETLY 1)
    set(CUDA_FIND_QUIETLY 1)
    set(CUDAToolkit_FIND_QUIETLY 1)
    set(Threads_FIND_QUIETLY 1)
    set(CUDNN_FIND_QUIETLY 1)
endif()

find_dependency(Torch)

if(Torch_FOUND)
    get_target_property(TORCH_LIBRARY_LOCATION torch LOCATION)
    get_filename_component(TORCH_LIB_SEARCH_PATH ${TORCH_LIBRARY_LOCATION} DIRECTORY)

    find_library(TORCH_PYTHON
                 NAMES "torch_python"
                 PATHS ${TORCH_LIB_SEARCH_PATH})

    if(NOT TARGET charonload::torch)
        add_library(charonload::torch INTERFACE IMPORTED)
        target_link_libraries(charonload::torch INTERFACE ${TORCH_LIBRARIES})
    endif()

    if(NOT TARGET charonload::torch_python)
        add_library(charonload::torch_python INTERFACE IMPORTED)
        target_link_libraries(charonload::torch_python INTERFACE ${TORCH_PYTHON})
    endif()
endif()

list(POP_BACK CMAKE_MESSAGE_INDENT)


include("${CMAKE_CURRENT_LIST_DIR}/torch/cxx_standard.cmake")
charonload_detect_torch_cxx_standard()

include("${CMAKE_CURRENT_LIST_DIR}/torch/cxx11_abi.cmake")
charonload_detect_cxx11_abi()

include("${CMAKE_CURRENT_LIST_DIR}/torch/cuda_version.cmake")
charonload_detect_cuda_version()


include("${CMAKE_CURRENT_LIST_DIR}/torch/add_torch_library.cmake")


charonload_message(STATUS "")
charonload_message(STATUS "-------------------------------------------------------------------------------")
charonload_message(STATUS "")


# The torch component is always found.
if(NOT charonload_FIND_COMPONENTS)
    set(charonload_FIND_COMPONENTS torch)
endif()
set(charonload_torch_FOUND TRUE)

set(charonload_ROOT_DIR "${PACKAGE_PREFIX_DIR}")

# Print a "Found charonload: ..." message in CONFIG mode although this is usually intended in MODULE mode.
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(charonload
                                  REQUIRED_VARS charonload_ROOT_DIR
                                  HANDLE_COMPONENTS)

function(charonload_check_binding_target)
    if(CHARONLOAD_JIT_COMPILE)
        get_target_property(EXTENSION_IS_HANDLED_TARGET ${TORCH_EXTENSION_NAME} CHARONLOAD_IS_HANDLED_TARGET)
        get_target_property(EXTENSION_TYPE ${TORCH_EXTENSION_NAME} TYPE)
        if(charonload_FOUND AND (NOT EXTENSION_IS_HANDLED_TARGET OR NOT EXTENSION_TYPE STREQUAL "MODULE_LIBRARY"))
            message(FATAL_ERROR "Missing python binding target: charonload_add_torch_library(<name> MODULE) has not been called.")
        endif()
    endif()
endfunction()
cmake_language(EVAL CODE "cmake_language(DEFER DIRECTORY \"${CMAKE_SOURCE_DIR}\" CALL charonload_check_binding_target)")
