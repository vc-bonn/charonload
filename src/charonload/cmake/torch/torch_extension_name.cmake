#[[.rst:
.. cmake:variable:: TORCH_EXTENSION_NAME

  Contains the required name of the Torch module that will later be loaded. Use this variable to generate the target
  of the bindings:

  .. code-block:: cmake

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

#]]
