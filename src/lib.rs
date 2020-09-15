use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;

pub mod utils;


#[pyfunction]
fn cyclic_xor<'p>(py: Python<'p>, data: &[u8], key: &[u8]) -> PyResult<&'p PyBytes> {
    Ok(PyBytes::new(py, &utils::cyclic_xor(data, key)))
}


#[pyfunction]
fn xor<'p>(py: Python<'p>, data: &[u8], key: u8) -> PyResult<&'p PyBytes> {
    Ok(PyBytes::new(py, &utils::xor(data, key)))
}


#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_wrapped(wrap_pyfunction!(cyclic_xor))?;
    module.add_wrapped(wrap_pyfunction!(xor))?;

    Ok(())
}
