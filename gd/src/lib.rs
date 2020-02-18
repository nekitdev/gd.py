/// Implementation of _gd accelerator module
/// Requires nightly-rust or dev rust
/// DO NOT COMPILE

use std::collections::HashMap;

use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyFloat, PyList, PyAny, PyTuple};
use pyo3::wrap_pyfunction;


#[pyfunction]
fn split_to_map(
    py: Python,
    string: String,
    separator: String
) -> HashMap<String, String> {
    let mut iter = string.split(separator);
    let mut data = HashMap::new();
    while let (
        Some(key), Some(value)
    ) = (iter.next(), iter.next()) {
        data.insert(key, value);
    }
    return data.into_py_dict(py)?;
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_wrapped(wrap_pyfunction!(split_to_map));
    module.add("__doc__", "Implementation of parser accelerator module, written in Rust.");
    // return nothing
    Ok(())
}
