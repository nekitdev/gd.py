/// Implementation of _gd memory manipulation module
/// Requires nightly-rust or development rust version

use std;
use std::io::Error;


#[cfg(windows)]
extern crate winapi;

use winapi::{
    ctypes::*,
    shared::minwindef::*,
    um::{
        consoleapi::*, libloaderapi::*, memoryapi::*,
        processthreadsapi::*, winnt::*, winsock2::*, winuser::*,
    },
};


use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


#[inline]
pub unsafe fn write_process_memory(
    proc_handle: HANDLE,
    address: LPVOID,
    buffer: &[u8],
) -> Result<(), Error> {
    if WriteProcessMemory(
        proc_handle,
        address,
        buffer.as_ptr() as LPVOID,
        buffer.len(),
        std::ptr::null_mut(),
    ) != 0 {
        Ok(())
    } else {
        Err(Error::last_os_error())
    }
}


#[inline]
pub unsafe fn virtual_protect(
    address: LPVOID, size: usize, protection_flags: u32
) -> Result<u32, Error> {
    let mut old_protect: u32 = 0;
    if VirtualProtect(address, size, protection_flags, &mut old_protect) != 0 {
        Ok(old_protect)
    } else {
        Err(Error::last_os_error())
    }
}


unsafe fn hook(address: usize, callback: usize) -> Result<(), Error> {
    println!("Address is {}, while callback is {}", address, callback);
    let offset = callback.wrapping_sub(address).wrapping_sub(5);
    let op = &[0xE9];  // jmp

    let old = virtual_protect(address as LPVOID, 5, PAGE_EXECUTE_READWRITE)?;

    let handle = GetCurrentProcess();
    write_process_memory(handle, address as LPVOID, op)?;
    write_process_memory(handle, (address + 1) as LPVOID, &offset.to_le_bytes())?;

    virtual_protect(address as LPVOID, 5, old)?;
    Ok(())
}


#[pymodule]
fn _gd(_py: Python, module: &PyModule) -> PyResult<()> {
    module.add("__doc__", "Implementation of memory manipulation module, written in Rust.")?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    // return nothing
    Ok(())
}
