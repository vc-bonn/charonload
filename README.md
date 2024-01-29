<!-- start readme -->

# CharonLoad

<!---
<p align="center">
-->
<img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-blue"/>
<a href="https://github.com/psf/black">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/>
</a>
<a href="https://numpydoc.readthedocs.io/en/latest/format.html">
    <img alt="Style: numpy" src="https://img.shields.io/badge/%20style-numpy-459db9.svg"/>
</a>
<a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
</a>
<!---
</p>
-->

## Features

CharonLoad is a bridge between Python code and rapidly developed custom C++/CUDA extensions to make writing **high-performance research code** with *PyTorch* easy:

- PyTorch C++ API detection and linking
- Automatic just-in-time (JIT) compilation of the C++/CUDA part
- Cached incremental builds and automatic clean builds
- Full power of CMake for handling C++ dependencies
- Python stub file generation for syntax highlighting and auto-completion in VS Code
- Interactive mixed Python/C++ debugging support in VS Code via *Python C++ Debugger* extension

CharonLoad reduces the burden to start writing and experimenting with custom GPU kernels in PyTorch by getting complex boilerplate code and common pitfalls out of your way. Developing C++/CUDA code with CharonLoad feels similar to writing Python scripts and lets you follow the same familiar workflow.


## Installation

CharonLoad requires **Python >=3.8** and can be installed from **source** (after cloning the repository):

```sh
python -m pip install --editable ".[dev]"
```


## Quick Start

CharonLoad only requires minimal changes to existing projects. In particular, a small configuration of the C++/CUDA project is added in the Python part while the CMake and C++ part should adopt some predefined functions:

- `<your_project>/main.py`
  
    ```python
    # Add configuration somewhere at the top of the project
    import charonload

    # Set optional path to stub directory, by default "typings" relative to the project root in VS Code
    VSCODE_STUBS_DIRECTORY = pathlib.Path(__file__).parent / "typings"

    charonload.module_config["my_cpp_cuda_ext"] = charonload.Config(
        # All paths must be absolute
        project_directory=pathlib.Path(__file__).parent / "<my_cpp_cuda_ext>",
        build_directory="optional/build/directory/for/caching",
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    # From now on, "my_cpp_cuda_ext" can be used in this module and any other imported module
    import other_module
    # ...
    ```

- `<your_project>/other_module.py`
  
    ```python
    # This import compiles and loads the C++/CUDA extension just-in-time (JIT)
    import my_cpp_cuda_ext

    # All defined bindings of "my_cpp_cuda_ext" can now be used ...
    # This will have proper syntax highlighting and auto-completion in VS Code if stubs are generated
    print(my_cpp_cuda_ext.some_function())
    ```

- `<your_project>/<my_cpp_cuda_ext>/CMakeLists.txt`
  
    ```cmake
    find_package(charonload)

    if(charonload_FOUND)
        charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

        # Add source files containing Python bindings, etc.
        target_sources(${TORCH_EXTENSION_NAME} PRIVATE src/<my_bindings>.cpp)

        # Add further properties to the target, e.g. link against other libraries, etc.
        # ...
    endif()
    ```

- ``<your_project>/<my_cpp_cuda_ext>/src/<my_bindings>.cpp``

    ```cpp
    #include <torch/python.h>

    PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
    {
        // Define some bindings which can take PyTorch tensors as input and output.
        // ...
        m.def("some_function", &some_function, "Documentation of some_function");
    }
    ```


## Contributing

If you would like to contribute to CharonLoad, you can find more information in the Contributing guide.


## License

MIT


## Contact

Patrick Stotko - <a href="mailto:stotko@cs.uni-bonn.de">stotko@cs.uni-bonn.de</a><br/>

<!-- end readme -->
