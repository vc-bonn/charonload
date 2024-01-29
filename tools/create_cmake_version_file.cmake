if(NOT DEFINED CHARONLOAD_CMAKE_DIR)
    message(FATAL_ERROR "CHARONLOAD_CMAKE_DIR not defined!")
endif()

if(NOT DEFINED CHARONLOAD_VERSION)
    message(FATAL_ERROR "CHARONLOAD_VERSION not defined!")
endif()

if(NOT DEFINED CHARONLOAD_VERSION_COMPATIBILITY)
    message(FATAL_ERROR "CHARONLOAD_VERSION_COMPATIBILITY not defined!")
endif()

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CHARONLOAD_CMAKE_DIR}/charonload-config-version.cmake"
    VERSION ${CHARONLOAD_VERSION}
    COMPATIBILITY ${CHARONLOAD_VERSION_COMPATIBILITY})
