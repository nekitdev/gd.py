/// Implementation of _gd accelerator module
/// Requires nightly-rust or dev rust
/// DO NOT COMPILE YET

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


#[pyfunction]
/// Show current version of the _gd library
fn get_version() -> PyResult<String> {
    let version = "0.1.0".to_string();
    Ok(version)
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(py: Python, module: &PyModule) -> PyResult<()> {
    // add all functions
    module.add_wrapped(wrap_pyfunction!(get_version))?;
    // return nothing
    Ok(())
}
