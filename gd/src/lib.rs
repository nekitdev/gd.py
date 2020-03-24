/// Implementation of _gd accelerator module
/// Requires nightly-rust or development rust version

use pyo3::prelude::*;
// use pyo3::wrap_pyfunction;

/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add("__doc__", "Implementation of parser accelerator module, written in Rust.")?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    // return nothing
    Ok(())
}
