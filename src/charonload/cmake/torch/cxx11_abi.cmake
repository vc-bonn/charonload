function(charonload_detect_cxx11_abi)
    if(DEFINED CACHE{CHARONLOAD_TORCH_CXX11_ABI})
        return()
    endif()

    charonload_message(CHECK_START "Detecting C++11 ABI version of Torch ...")
    execute_process(COMMAND ${Python_EXECUTABLE} "-c" "
import platform

import torch

if platform.system() == \"Linux\":
    print(int(torch.compiled_with_cxx11_abi()))
"
                    OUTPUT_VARIABLE DETECTION_RESULT
                    ERROR_VARIABLE PYTHON_ERROR
                    ECHO_ERROR_VARIABLE
                    OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(NOT DETECTION_RESULT STREQUAL "")
        set(CHARONLOAD_TORCH_CXX11_ABI ${DETECTION_RESULT} CACHE STRING "C++11 ABI version used to compile Torch")
        charonload_message(CHECK_PASS "done (C++11 ABI=${CHARONLOAD_TORCH_CXX11_ABI})")
    else()
        set(CHARONLOAD_TORCH_CXX11_ABI "NOTFOUND" CACHE STRING "C++11 ABI version used to compile Torch")
        charonload_message(CHECK_FAIL "done")
    endif()
endfunction()
