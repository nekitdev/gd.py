use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;

pub mod utils;


/// Apply XOR cipher to ``stream`` with ``key``.
/// Applying this operation twice decodes ``stream`` back to the initial state.
///
/// Parameters
/// ----------
/// stream: :class:`bytes`
///     Data to apply XOR on.
///
/// key: :class:`int`
///     Key to use. Type ``u8`` (or ``byte``) should be used, in ``[0; 255]`` range.
///
/// Returns
/// -------
/// :class:`bytes`
///     Data after XOR applied.
#[pyfunction]
fn cyclic_xor<'p>(py: Python<'p>, data: Vec<u8>, key: &[u8]) -> PyResult<&'p PyBytes> {
    utils::cyclic_xor_inplace(&mut data, key);

    Ok(PyBytes::new(py, &data))
}


/// Apply cyclic XOR cipher to ``stream`` with ``key``.
/// Applying this operation twice decodes ``stream`` back to the initial state.
///
/// Parameters
/// ----------
/// stream: :class:`bytes`
///     Data to apply XOR on.
///
/// key: :class:`bytes`
///     Key to use. It is cycled and zipped with ``stream``.
///
/// Returns
/// -------
/// :class:`bytes`
///     Data after XOR applied.
#[pyfunction]
fn xor<'p>(py: Python<'p>, data: Vec<u8>, key: u8) -> PyResult<&'p PyBytes> {
    utils::xor_inplace(&mut data, key);

    Ok(PyBytes::new(py, &data))
}


#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add_wrapped(wrap_pyfunction!(cyclic_xor))?;
    module.add_wrapped(wrap_pyfunction!(xor))?;

    Ok(())
}
