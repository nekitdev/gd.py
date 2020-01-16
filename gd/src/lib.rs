/// Implementation of _gd accelerator module
/// DO NOT COMPILE YET

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


#[pyfunction]
/// Show current version of the _gd library
fn get_version() -> PyResult(String) {
    let VERSION = "0.1.0";
    VERSION
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn string_sum(py: Python, module: &PyModule) -> PyResult<()> {
    module.add_wrapped(wrap_pyfunction!(get_version))?;
    Ok(())
}
