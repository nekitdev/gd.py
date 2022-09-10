use pyo3::PyResult;
use pyo3::marker::Python;
use pyo3::types::{PyBytes, PyModule};
use pyo3::{pyfunction as py_function, pymodule as py_module, wrap_pyfunction as wrap_py_function};

pub mod utils;


#[py_function(text_signature = "(data: bytes, key: bytes)")]
fn cyclic_xor<'p>(python: Python<'p>, mut data: Vec<u8>, key: &[u8]) -> PyResult<&'p PyBytes> {
    utils::cyclic_xor_in_place(&mut data, key);

    Ok(PyBytes::new(python, &data))
}


#[py_function(text_signature = "(data: bytes, key: int)")]
fn xor<'p>(python: Python<'p>, mut data: Vec<u8>, key: u8) -> PyResult<&'p PyBytes> {
    utils::xor_in_place(&mut data, key);

    Ok(PyBytes::new(python, &data))
}


#[py_module]
fn _gd(_python: Python, module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_py_function!(cyclic_xor, module)?)?;
    module.add_function(wrap_py_function!(xor, module)?)?;

    Ok(())
}
