#pragma once

#include <ATen/core/Tensor.h>
#include <string>

at::Tensor
two_times(const at::Tensor& input);

std::string
numel_to_string(const at::Tensor& input);

std::string
numel_to_string_aliased(const at::Tensor& input);
