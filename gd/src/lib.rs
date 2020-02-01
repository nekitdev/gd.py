/// Implementation of _gd accelerator module
/// Requires nightly-rust or dev rust
/// DO NOT COMPILE YET

use std::collections::HashMap;

use pyo3::prelude::*;
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


#[pyfunction]
/// Split a string into python dict
/// split('1:1:2:2') -> {'1': '1', '2': '2'}
fn split(string: &'a str, delim: &'a str) -> PyDict<String, String> {
    Ok(split_to_map(string, delim).into_py_dict())
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(py: Python, module: &PyModule) -> PyResult<()> {
    // add all functions
    module.add_wrapped(wrap_pyfunction!(split))?;
    // return nothing
    Ok(())
}
