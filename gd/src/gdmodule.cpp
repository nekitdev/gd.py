#include <Python.h>

/*
    This is an accelerator module for gd.py library.
    (Empty for now, implementation soon)
*/

const char* version = "0.1";

PyObject* get_version(PyObject *self) {
    return PyUnicode_FromString(version);
}

// Methods definiton
static PyMethodDef gd_methods[] = {
    {"get_version", (PyCFunction) get_version, METH_NOARGS, "Get current version of _gd extension."},
    // Terminate the array with an object containing nulls.
    {nullptr, nullptr, 0, nullptr}
};

// Module definition
static PyModuleDef gd_module = {
    PyModuleDef_HEAD_INIT,
    "_gd",
    "Accelerator module for parsing level strings in gd.py",
    0,
    gd_methods
};

// Init _gd
PyMODINIT_FUNC PyInit__gd() {
    return PyModule_Create(&gd_module);
}
