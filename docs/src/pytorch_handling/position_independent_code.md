# Position-Independent Code (PIC)

Since extension modules are dynamically loaded by the Python interpreter, their actual code will be loaded at runtime and needs to work from any address in memory, i.e. cannot use fixed addresses. While this is automatically ensured during compilation for extension modules (and shared libraries), this requirement is not needed for static libraries which will be directly linked into the executable at compile time and can, in turn, use fixed addresses.

Similar to many C++ projects, developing a C++/CUDA extension may involve the help of external 3rd-party dependencies which may be linked as **static libraries**. However, this may lead to linker errors as code from the dependency cannot be relocated to an arbitrary address.

CharonLoad automatically scans for all transitive *static* dependencies, and patches each of the respective CMake targets to enable [``POSITION_INDEPENDENT_CODE``](<inv:cmake.org#prop_tgt/POSITION_INDEPENDENT_CODE>).
