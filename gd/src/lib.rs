/// Implementation of _gd accelerator module
/// Requires nightly-rust or development rust version

use base64;

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn urlsafe_b64encode(py: Python, bytes: &[u8]) -> PyResult<PyObject> {
    Ok(PyBytes::new(py, base64::encode_config(bytes, base64::URL_SAFE).as_bytes()).to_object(py))
}

#[pyfunction]
fn urlsafe_b64decode(py: Python, bytes: &[u8]) -> PyResult<PyObject> {
    Ok(PyBytes::new(py, &base64::decode_config(bytes, base64::URL_SAFE).unwrap()).to_object(py))
}

/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add("__doc__", "Implementation of parser accelerator module, written in Rust.")?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    module.add_wrapped(wrap_pyfunction!(urlsafe_b64encode))?;
    module.add_wrapped(wrap_pyfunction!(urlsafe_b64decode))?;
    // return nothing
    Ok(())
}
