#[[.rst:
.. cmake:command:: charonload_add_torch_library

  .. code-block:: cmake

    charonload_add_torch_library(<name> [MODULE | SHARED | STATIC])

  Creates a library target ``<name>`` with the respective type ``MODULE``, ``SHARED``, or ``STATIC``. If no type is
  provided, the default type of :doc:`add_library() <cmake.org:command/add_library>` is used. Furthermore, the
  following steps will be executed:

  1. The target ``<name>`` will automatically be linked against the following libraries:

     - Torch C++ library
     - If ``MODULE``:
        - pybind11 library (bundled within Torch)
        - Torch Python bindings

  2. If the library type is ``MODULE``, the C++ preprocessor definition ``TORCH_EXTENSION_NAME`` will be set
     to ``<name>`` in all source files of the target. This should be used to set up the bindings:

     .. code-block:: cpp

        PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
        {
            // Define some bindings ...
        }

  3. The usage requirements for PyTorch will be added to ``<name>`` and, if necessary,
     recursively to all of its dependencies:

     - C++ standard
     - C++11 ABI
     - Position-Independent Code flag

  .. admonition:: Source Files
    :class: warning

    Any additional arguments of :cmake:command:`charonload_add_torch_library` are rejected and an error will be thrown.
    This behavior is intentional and encourages to use the more modern
    :doc:`target_sources() <cmake.org:command/target_sources>` command for adding source files.

#]]


# Helper function following pybind11 and nanobind
function(charonload_set_visibility name)
    set_target_properties(${name} PROPERTIES CXX_VISIBILITY_PRESET "hidden"
                                             CUDA_VISIBILITY_PRESET "hidden")
endfunction()

function(charonload_compile_options name)
    if(MSVC)
        target_compile_options(${name} PRIVATE $<$<COMPILE_LANGUAGE:CXX>:/bigobj>)
    endif()
endfunction()

function(charonload_lto name)
    set_target_properties(${name} PROPERTIES INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
                                             INTERPROCEDURAL_OPTIMIZATION_MINSIZEREL ON)
endfunction()

function(charonload_opt_size name)
    if (MSVC)
        target_compile_options(${name} PRIVATE $<$<COMPILE_LANGUAGE:CXX>:/Os>)
    else()
        target_compile_options(${name} PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Os>)
    endif()
endfunction()

function(charonload_strip name)
    if(CMAKE_STRIP)
        add_custom_command(TARGET ${name}
                           POST_BUILD
                           COMMAND ${CMAKE_STRIP} $<TARGET_FILE:${name}>
                           VERBATIM)
    endif()
endfunction()


# Helper functions for patching
function(charonload_add_torch_cxx11_abi_compile_definition name)
    get_target_property(NAME_HAS_CXX11_ABI ${name} CHARONLOAD_HAS_CXX11_ABI)
    if(NOT ${NAME_HAS_CXX11_ABI})
        target_compile_definitions(${name} PRIVATE _GLIBCXX_USE_CXX11_ABI=${CHARONLOAD_TORCH_CXX11_ABI})
        set_target_properties(${name} PROPERTIES CHARONLOAD_HAS_CXX11_ABI ON)
        message(STATUS "Added flag _GLIBCXX_USE_CXX11_ABI=${CHARONLOAD_TORCH_CXX11_ABI} to target \"${name}\"")
    endif()
endfunction()


function(charonload_set_position_independent_code name)
    get_target_property(NAME_TYPE ${name} TYPE)
    get_target_property(NAME_PIC ${name} POSITION_INDEPENDENT_CODE)
    if(NAME_TYPE STREQUAL "STATIC_LIBRARY" AND NAME_PIC MATCHES "NOTFOUND")
        set_target_properties(${name} PROPERTIES POSITION_INDEPENDENT_CODE ON)
        message(STATUS "Set property POSITION_INDEPENDENT_CODE=ON to target \"${name}\"")
    endif()
endfunction()


function(charonload_set_torch_cxx_standard name)
    if(NOT $CACHE{CHARONLOAD_TORCH_STANDARD} STREQUAL "NOTFOUND")
        target_compile_features(${name} PUBLIC cxx_std_$CACHE{CHARONLOAD_TORCH_STANDARD})
    endif()
endfunction()


function(charonload_add_torch_library name)
    cmake_parse_arguments(arg "MODULE;SHARED;STATIC" "" "" ${ARGN})
    if(arg_UNPARSED_ARGUMENTS)
        message(STATUS "Unparsed: ${arg_UNPARSED_ARGUMENTS}")
        message(FATAL_ERROR "Invalid syntax: charonload_add_torch_library(${name} ${ARGN})")
    endif()

    if(arg_MODULE)
        set(CHARONLOAD_LIBRARY_TYPE MODULE)
    elseif(arg_SHARED)
        set(CHARONLOAD_LIBRARY_TYPE SHARED)
    elseif(arg_STATIC)
        set(CHARONLOAD_LIBRARY_TYPE STATIC)
    endif()

    if(arg_MODULE)
        if(NOT name STREQUAL TORCH_EXTENSION_NAME)
            message(FATAL_ERROR "Invalid name: charonload_add_torch_library(<name> MODULE) should be called with \${TORCH_EXTENSION_NAME}")
        endif()

        python_add_library(${name} ${CHARONLOAD_LIBRARY_TYPE} WITH_SOABI)

        target_compile_definitions(${name} PRIVATE "TORCH_EXTENSION_NAME=${name}")
        target_link_libraries(${name} PRIVATE charonload::torch_python)

        charonload_set_visibility(${name})
        charonload_compile_options(${name})
        if(NOT DEFINED CMAKE_INTERPROCEDURAL_OPTIMIZATION)  # Follow pybind11's behavior and honor global CMake settings
            charonload_lto(${name})
        endif()
        # charonload_opt_size(${name})  # Size optimization is disabled by default
        charonload_strip(${name})
    else()
        add_library(${name} ${CHARONLOAD_LIBRARY_TYPE})
    endif()

    target_link_libraries(${name} PUBLIC charonload::torch)
    set_target_properties(${name} PROPERTIES POSITION_INDEPENDENT_CODE ON)

    charonload_set_torch_cxx_standard(${name})

    # Required for charonload_patch_dependencies() and charonload_check_binding_target()
    set_target_properties(${name} PROPERTIES CHARONLOAD_IS_HANDLED_TARGET TRUE)

    if(NOT $CACHE{CHARONLOAD_TORCH_CXX11_ABI} STREQUAL "NOTFOUND")
        list(APPEND PATCH_FUNCTIONS "charonload_add_torch_cxx11_abi_compile_definition")
    endif()
    list(APPEND PATCH_FUNCTIONS "charonload_set_position_independent_code")
    cmake_language(EVAL CODE "cmake_language(DEFER DIRECTORY \"${CMAKE_SOURCE_DIR}\" CALL charonload_patch_dependencies \"${name}\" \"${PATCH_FUNCTIONS}\")")

    if(arg_MODULE)
        file(GENERATE
            OUTPUT "${CMAKE_BINARY_DIR}/charonload/$<CONFIG>/location.txt"
            CONTENT "$<TARGET_FILE:${name}>")

        file(GENERATE
            OUTPUT "${CMAKE_BINARY_DIR}/charonload/$<CONFIG>/windows_dll_directories.txt"
            CONTENT "$<TARGET_RUNTIME_DLL_DIRS:${name}>")
    endif()
endfunction()


function(charonload_collect_patchable_dependencies name output_dependency_list)
    get_target_property(DEPENDENCIES ${name} LINK_LIBRARIES)
    if(DEPENDENCIES)
        while(DEPENDENCIES)
            list(POP_FRONT DEPENDENCIES lib)

            list(FIND PROCESSED_DEPENDENCIES ${lib} lib_processed)
            if(TARGET ${lib} AND lib_processed STREQUAL "-1")
                get_target_property(LIB_IS_HANDLED_TARGET ${lib} CHARONLOAD_IS_HANDLED_TARGET)
                get_target_property(LIB_TYPE ${lib} TYPE)
                get_target_property(LIB_IMPORTED ${lib} IMPORTED)
                if(NOT LIB_IS_HANDLED_TARGET AND LIB_TYPE MATCHES "STATIC_LIBRARY|SHARED_LIBRARY|OBJECT_LIBRARY" AND NOT LIB_IMPORTED)
                    get_target_property(ACTUAL_LIB ${lib} ALIASED_TARGET)
                    if(ACTUAL_LIB)
                        list(APPEND DEPENDENCY_LIST ${ACTUAL_LIB})
                    else()
                        list(APPEND DEPENDENCY_LIST ${lib})
                    endif()
                endif()

                get_target_property(LIB_DEPENDENCIES ${lib} INTERFACE_LINK_LIBRARIES)
                if(LIB_DEPENDENCIES)
                    list(APPEND DEPENDENCIES ${LIB_DEPENDENCIES})
                endif()
                get_target_property(LIB_DEPENDENCIES ${lib} LINK_LIBRARIES)
                if(LIB_DEPENDENCIES)
                    list(APPEND DEPENDENCIES ${LIB_DEPENDENCIES})
                endif()

                list(APPEND PROCESSED_DEPENDENCIES ${lib})
            endif()
        endwhile()
    endif()

    set(${output_dependency_list} ${DEPENDENCY_LIST} PARENT_SCOPE)
endfunction()


function(charonload_patch_dependencies name patch_functions)
    if(patch_functions)
        charonload_collect_patchable_dependencies(${name} UNPATCHED_DEPENDENCIES)

        if(UNPATCHED_DEPENDENCIES)
            message(STATUS "charonload: Patching dependencies of target \"${name}\" ...")
            list(APPEND CMAKE_MESSAGE_INDENT "  ")

            foreach(func IN LISTS patch_functions)
                foreach(lib IN LISTS UNPATCHED_DEPENDENCIES)
                    cmake_language(CALL ${func} ${lib})
                endforeach()
            endforeach()

            list(POP_BACK CMAKE_MESSAGE_INDENT)
        endif()
    endif()
endfunction()
