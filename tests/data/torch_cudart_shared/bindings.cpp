#include <torch/python.h>

#include "two_times_cuda.h"

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
    m.def("numel_times_multi_processor_count", &numel_times_multi_processor_count, "input"_a, R"(
        Get the number of elements of the given input tensor times the number of multiprocessors of the current GPU,
        by calling a function from an external library.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        The product of the number of elements and the multiprocessor count.
    )");
    m.def("numel_times_multi_processor_count_aliased", &numel_times_multi_processor_count_aliased, "input"_a, R"(
        Get the number of elements of the given input tensor times the number of multiprocessors of the current GPU,
        by calling a function from an external aliased library.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        The product of the number of elements and the multiprocessor count.
    )");
}
