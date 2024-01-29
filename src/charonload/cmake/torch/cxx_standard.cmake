function(charonload_detect_torch_cxx_standard)
    if(DEFINED CACHE{CHARONLOAD_TORCH_STANDARD})
        return()
    endif()

    # Only check for C++14 and later since this is required for PyTorch 1.5+
    set(KNOWN_CXX_STANDARDS 14 17)
    if(NOT CMAKE_CUDA_COMPILER_LOADED OR CMAKE_CUDA_COMPILER_VERSION VERSION_GREATER_EQUAL 12.0)
        list(APPEND KNOWN_CXX_STANDARDS 20)
    endif()

    charonload_message(CHECK_START "Detecting minimum C++ standard for Torch ...")
    list(APPEND CMAKE_MESSAGE_INDENT "  ")
    foreach(std IN LISTS KNOWN_CXX_STANDARDS)
        charonload_message(CHECK_START "CMAKE_CXX_STANDARD: ${std}")

        try_compile(COMPILE_RESULT
                    PROJECT "torch_cxx_standard_${std}"
                    SOURCE_DIR "${charonload_DIR}/torch/cxx_standard"
                    BINARY_DIR "${CMAKE_BINARY_DIR}/charonload/torch/cxx_standard_${std}"
                    CMAKE_FLAGS
                        "-DCMAKE_MESSAGE_LOG_LEVEL=ERROR"
                        "-DCHARONLOAD_TORCH_STANDARD=${std}"
                        "-DTorch_DIR=${Torch_DIR}"
                    LOG_DESCRIPTION "Checking C++${std} standard for Torch"
        )

        if(COMPILE_RESULT)
            charonload_message(CHECK_PASS "Success")
            set(CHARONLOAD_TORCH_STANDARD ${std} CACHE STRING "Minimum C++ standard required for Torch using cxx_std_{XY}")
            break()
        else()
            charonload_message(CHECK_FAIL "Failed")
        endif()
    endforeach()
    list(POP_BACK CMAKE_MESSAGE_INDENT)

    if(CHARONLOAD_TORCH_STANDARD)
        # Already set in loop
        charonload_message(CHECK_PASS "done (C++${CHARONLOAD_TORCH_STANDARD})")
    else()
        set(CHARONLOAD_TORCH_STANDARD "NOTFOUND" CACHE STRING "Minimum C++ standard required for Torch using cxx_std_{XY}")
        charonload_message(CHECK_FAIL "done")
    endif()
endfunction()
