function(charonload_determine_prefix_paths)
    charonload_message(CHECK_START "Determining prefix paths used for finding dependencies ...")
    execute_process(COMMAND ${Python_EXECUTABLE} "-c" "
import pathlib
import site

# User site-packages take precedence over global site-packages
site_package_directories = [site.getusersitepackages()] if site.ENABLE_USER_SITE else []
site_package_directories.extend(site.getsitepackages())
cmake_prefix_path_list = [pathlib.Path(d).as_posix() for d in site_package_directories]

print(\";\".join(cmake_prefix_path_list))
"
                    OUTPUT_VARIABLE CHARONLOAD_PREFIX_PATH
                    ERROR_VARIABLE PYTHON_ERROR
                    ECHO_ERROR_VARIABLE
                    OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(NOT CHARONLOAD_PREFIX_PATH STREQUAL "")
        set(CHARONLOAD_PREFIX_PATH ${CHARONLOAD_PREFIX_PATH} CACHE STRING "Prefix paths used for finding dependencies")
        charonload_message(CHECK_PASS "done (${CHARONLOAD_PREFIX_PATH})")
    else()
        charonload_message(CHECK_FAIL "done")
    endif()
endfunction()
