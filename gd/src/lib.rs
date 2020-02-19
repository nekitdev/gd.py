/// Implementation of _gd accelerator module
/// Requires nightly-rust or development rust version

use std::collections::HashMap;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


#[pyfunction]
fn split_to_map(
    py: Python,
    string: String,
    separator: String
) -> PyResult<PyObject> {
    let delim: &str = &separator;
    let mut data = HashMap::new();

    let mut iter = string.split(delim);

    while let (
        Some(key), Some(value)
    ) = (iter.next(), iter.next()) {
        data.insert(key, value);
    }

    Ok(data.to_object(py))
}


/// This module is a python module implemented in Rust.
#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add("__doc__", "Implementation of parser accelerator module, written in Rust.")?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    module.add_wrapped(wrap_pyfunction!(split_to_map))?;
    // return nothing
    Ok(())
}
