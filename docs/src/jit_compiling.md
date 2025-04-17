# JIT Compiling

CharonLoad executes the following steps to JIT compile the C++/CUDA extension:

## 1. (Optional) Clean

Removes any existing old files in the [build directory](#ResolvedConfig.full_build_directory). This optional step can be controlled by setting the [``clean_build``](#ResolvedConfig.clean_build) flag of <project:#ResolvedConfig>.

In addition, cleaning is **automatically** performed if at least one of these conditions are fulfilled:
- CMake Configure step *failed*.
- CharonLoad version used in previous run is *incompatible* with current version.  
  (Same minor version, e.g. 0.3.X is considered incompatible to 0.4.Y.)
- PyTorch version has *changed* since the previous run.


## 2. Initialize

Prepares internal state and places ``.gitignore`` into [build directory](#ResolvedConfig.full_build_directory) to minimize noise.


## 3. CMake Configure

Runs CMake on the specified [project directory](#ResolvedConfig.full_project_directory). Additional arguments to the command can be passed via [``cmake_options``](#ResolvedConfig.cmake_options) of <project:#ResolvedConfig>.

Skipped automatically if CMake configuration has not changed from previous run.


## 4. Build

Performs parallel compilation of the configured project. If project source files have not changed between runs, the underlying native build tool usually skips unnecessary compilations on its own.


## 5. (Optional) Stub Generation

Analyzes the compiled C++/CUDA extension and generates Python stub files. This is useful to enable syntax highlighting and auto-completion of the bindings in VS Code. This optional step can be enabled by specifying the [stubs directory](#ResolvedConfig.full_stubs_directory) of <project:#ResolvedConfig>.

Skipped automatically if the compiled extension file has not changed from a previous run, i.e. the build step did not alter the file.


## 6. Import Path

Extends Python's module search paths with the location of the compiled extension to enable ``import`` calls to it. On Windows, the DLL search paths are also extended by the list of shared/dynamic libraries to which the extension links.
