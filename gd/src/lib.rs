/// Implementation of _gd accelerator module
/// Requires nightly-rust or dev rust
/// DO NOT COMPILE

use std::collections::HashMap;

use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict, PyFloat, PyList, PyAny, PyTuple};
use pyo3::wrap_pyfunction;


fn split_to_map<'a>(
    string: &'a str,
    separator: &str
) -> HashMap<&'a str, &'a str> {
    let mut iter = string.split(separator);
    let mut data = HashMap::new();
    while let (
        Some(key), Some(value)
    ) = (iter.next(), iter.next()) {
        data.insert(key, value);
    }
    return data;
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    // return nothing
    Ok(())
}
