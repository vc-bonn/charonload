<h1 align="center">CharonLoad</h1>

<!-- start readme -->

<p align="center">
<a href="https://pypi.python.org/pypi/charonload">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/charonload">
</a>
<a href="https://pypi.python.org/pypi/charonload">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/charonload">
</a>
<a href="https://github.com/vc-bonn/charonload/blob/main/LICENSE">
    <img alt="GitHub License" src="https://img.shields.io/github/license/vc-bonn/charonload"/>
</a>
<a href="https://github.com/vc-bonn/charonload/actions/workflows/tests.yml">
    <img alt="Tests" src="https://github.com/vc-bonn/charonload/actions/workflows/tests.yml/badge.svg">
</a>
<a href="https://github.com/vc-bonn/charonload/actions/workflows/lint.yml">
    <img alt="Lint" src="https://github.com/vc-bonn/charonload/actions/workflows/lint.yml/badge.svg">
</a>
<a href="https://vc-bonn.github.io/charonload">
    <img alt="Documentation" src="https://img.shields.io/badge/docs-Latest-green.svg"/>
</a>
</p>


CharonLoad is a bridge between Python code and rapidly developed custom C++/CUDA extensions to make writing **high-performance research code** with *PyTorch* easy:

- 🔥 PyTorch C++ API detection and linking
- 🔨 Automatic just-in-time (JIT) compilation of the C++/CUDA part
- 📦 Cached incremental builds and automatic clean builds
- 🔗 Full power of CMake for handling C++ dependencies
- ⌨️ Python stub file generation for syntax highlighting and auto-completion in VS Code
- 🐛 Interactive mixed Python/C++ debugging support in VS Code via *Python C++ Debugger* extension

CharonLoad reduces the burden to start writing and experimenting with custom GPU kernels in PyTorch by getting complex boilerplate code and common pitfalls out of your way. Developing C++/CUDA code with CharonLoad feels similar to writing Python scripts and lets you follow the same familiar workflow.


## Installation

CharonLoad requires **Python >=3.8** and can be installed from PyPI:

```sh
pip install charonload
```


## Quick Start

CharonLoad only requires minimal changes to existing projects. In particular, a small configuration of the C++/CUDA project is added in the Python part while the CMake and C++ part should adopt some predefined functions:

- `<your_project>/main.py`
  
    ```python
    import charonload

    VSCODE_STUBS_DIRECTORY = pathlib.Path(__file__).parent / "typings"

    charonload.module_config["my_cpp_cuda_ext"] = charonload.Config(
        project_directory=pathlib.Path(__file__).parent / "<my_cpp_cuda_ext>",
        build_directory="custom/build/directory",  # optional
        stubs_directory=VSCODE_STUBS_DIRECTORY,  # optional
    )

    import other_module
    ```

- `<your_project>/other_module.py`
  
    ```python
    import my_cpp_cuda_ext  # JIT compiles and loads the extension

    tensor_from_ext = my_cpp_cuda_ext.generate_tensor()
    ```

- `<your_project>/<my_cpp_cuda_ext>/CMakeLists.txt`
  
    ```cmake
    find_package(charonload)

    if(charonload_FOUND)
        charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

        target_sources(${TORCH_EXTENSION_NAME} PRIVATE src/<my_bindings>.cpp)
        # Further properties, e.g. link against other 3rd-party libraries, etc.
        # ...
    endif()
    ```

- ``<your_project>/<my_cpp_cuda_ext>/src/<my_bindings>.cpp``

    ```cpp
    #include <torch/python.h>

    torch::Tensor generate_tensor();  // Implemented somewhere in <my_cpp_cuda_ext>

    PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
    {
        m.def("generate_tensor", &generate_tensor, "Optional Python docstring");
    }
    ```


## Contributing

If you would like to contribute to CharonLoad, you can find more information in the [Contributing](https://vc-bonn.github.io/charonload/src/contributing.html) guide.


## License

MIT


## Contact

Patrick Stotko - <a href="mailto:stotko@cs.uni-bonn.de">stotko@cs.uni-bonn.de</a><br/>

<!-- end readme -->
