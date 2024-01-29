#include <torch/python.h>

#include "two_times_cpu.h"

using namespace pybind11::literals;

#define STRINGIFY_IMPL(x) #x
#define STRINGIFY(a) STRINGIFY_IMPL(a)

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
    m.doc() = "A C++/CUDA extension module named \"" STRINGIFY(TORCH_EXTENSION_NAME) "\" that is built just-in-time.";

    m.def("two_times", &two_times, "input"_a, R"(
        Multiply the given input tensor by a factor of 2 on the CPU.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        A new tensor with the same shape and dtype as ``input`` and where each value is multiplied by 2.
    )");
    m.def("numel_to_string", &numel_to_string, "input"_a, R"(
        Get the number of elements of the given input tensor as a string, by calling a function from an external
        library.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        A string of the number of elements of ``input`.
    )");
    m.def("numel_to_string_aliased", &numel_to_string_aliased, "input"_a, R"(
        Get the number of elements of the given input tensor as a string, by calling a function from an external
        aliased library.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        A string of the number of elements of ``input`.
    )");
}
