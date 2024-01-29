function(charonload_detect_cuda_version)
    if(DEFINED CACHE{CHARONLOAD_TORCH_CUDA_VERSION})
        return()
    endif()

    charonload_message(CHECK_START "Detecting CUDA version of Torch ...")
    execute_process(COMMAND ${Python_EXECUTABLE} "-c" "
import torch

if torch.cuda.is_available():
    print(torch.version.cuda)
"
                    OUTPUT_VARIABLE DETECTION_RESULT
                    ERROR_VARIABLE PYTHON_ERROR
                    ECHO_ERROR_VARIABLE
                    OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(NOT DETECTION_RESULT STREQUAL "")
        set(CHARONLOAD_TORCH_CUDA_VERSION ${DETECTION_RESULT} CACHE STRING "CUDA version used to compile Torch")
        charonload_message(CHECK_PASS "done (CUDA ${CHARONLOAD_TORCH_CUDA_VERSION})")
    else()
        set(CHARONLOAD_TORCH_CUDA_VERSION "NOTFOUND" CACHE STRING "CUDA version used to compile Torch")
        charonload_message(CHECK_FAIL "done")
    endif()
endfunction()
