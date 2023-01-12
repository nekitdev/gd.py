use core::mem::size_of;

use pyo3::{
    Py, PyResult, Python,
    exceptions::PyValueError,
    types::{PyAny, PyBytes, PyModule},
};

use pyo3::{pyclass as py_class, pymethods as py_methods, pymodule as py_module};


macro_rules! unary_tuple {
    ($item: expr) => {
        ($item,)
    };
}


const READ: &'static str = "read";
const WRITE: &'static str = "write";
const VALUE: &'static str = "value";

const UNKNOWN_BYTE_ORDER: &'static str = "unknown byte order";
const NOT_ENOUGH_DATA: &'static str = "not enough data";


#[py_class]
enum ByteOrder {
    Little,
    Big,
}


const DEFAULT_BYTE_ORDER: ByteOrder = ByteOrder::Little;


impl ByteOrder {
    fn try_from_string(string: &str) -> PyResult<Self> {
        match string {
            "<" => Ok(Self::Little),
            ">" => Ok(Self::Big),
            _ => Err(PyValueError::new_err(UNKNOWN_BYTE_ORDER)),
        }
    }
}


#[py_class]
struct Converter {
    order: Option<Py<PyAny>>,
}


#[py_methods]
impl Converter {
    #[new]
    fn new(order: Option<Py<PyAny>>) -> Self {
        Self { order }
    }

    fn convert(&self, python: Python<'_>) -> PyResult<ByteOrder> {
        match &self.order {
            Some(order) => {
                let value = order.getattr(python, VALUE)?;
                ByteOrder::try_from_string(value.extract(python)?)
            },
            None => Ok(DEFAULT_BYTE_ORDER),
        }
    }
}


#[py_class(module = "_gd")]
struct Reader {
    reader: Py<PyAny>,
    order: ByteOrder,
}


#[py_methods]
impl Reader {
    #[new]
    fn new(python: Python<'_>, reader: Py<PyAny>, order: Option<Py<PyAny>>) -> PyResult<Self> {
        let order = Converter::new(order).convert(python)?;

        Ok(Self { reader, order })
    }

    fn read_u8(&self, python: Python<'_>) -> PyResult<u8> {
        let data = self.read_vector(python, size_of::<u8>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(u8::from_le_bytes(array)),
            ByteOrder::Big => Ok(u8::from_be_bytes(array)),
        }
    }

    fn read_u16(&self, python: Python<'_>) -> PyResult<u16> {
        let data = self.read_vector(python, size_of::<u16>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(u16::from_le_bytes(array)),
            ByteOrder::Big => Ok(u16::from_be_bytes(array)),
        }
    }

    fn read_u32(&self, python: Python<'_>) -> PyResult<u32> {
        let data = self.read_vector(python, size_of::<u32>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(u32::from_le_bytes(array)),
            ByteOrder::Big => Ok(u32::from_be_bytes(array)),
        }
    }

    fn read_u64(&self, python: Python<'_>) -> PyResult<u64> {
        let data = self.read_vector(python, size_of::<u64>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(u64::from_le_bytes(array)),
            ByteOrder::Big => Ok(u64::from_be_bytes(array)),
        }
    }

    fn read_i8(&self, python: Python<'_>) -> PyResult<i8> {
        let data = self.read_vector(python, size_of::<i8>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(i8::from_le_bytes(array)),
            ByteOrder::Big => Ok(i8::from_be_bytes(array)),
        }
    }

    fn read_i16(&self, python: Python<'_>) -> PyResult<i16> {
        let data = self.read_vector(python, size_of::<i16>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(i16::from_le_bytes(array)),
            ByteOrder::Big => Ok(i16::from_be_bytes(array)),
        }
    }

    fn read_i32(&self, python: Python<'_>) -> PyResult<i32> {
        let data = self.read_vector(python, size_of::<i32>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(i32::from_le_bytes(array)),
            ByteOrder::Big => Ok(i32::from_be_bytes(array)),
        }
    }

    fn read_i64(&self, python: Python<'_>) -> PyResult<i64> {
        let data = self.read_vector(python, size_of::<i64>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(i64::from_le_bytes(array)),
            ByteOrder::Big => Ok(i64::from_be_bytes(array)),
        }
    }

    fn read_f32(&self, python: Python<'_>) -> PyResult<f32> {
        let data = self.read_vector(python, size_of::<f32>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(f32::from_le_bytes(array)),
            ByteOrder::Big => Ok(f32::from_be_bytes(array)),
        }
    }

    fn read_f64(&self, python: Python<'_>) -> PyResult<f64> {
        let data = self.read_vector(python, size_of::<f64>())?;

        let array = data.try_into().map_err(|_| PyValueError::new_err(NOT_ENOUGH_DATA))?;

        match self.order {
            ByteOrder::Little => Ok(f64::from_le_bytes(array)),
            ByteOrder::Big => Ok(f64::from_be_bytes(array)),
        }
    }

    fn read_vector(&self, python: Python<'_>, size: usize) -> PyResult<Vec<u8>> {
        let data = self.read(python, size)?;

        Ok(data.extract(python)?)
    }

    fn read(&self, python: Python<'_>, size: usize) -> PyResult<Py<PyBytes>> {
        let data = self.reader.call_method1(python, READ, unary_tuple!(size))?;

        Ok(data.extract(python)?)
    }
}


#[py_class(module = "_gd")]
struct Writer {
    writer: Py<PyAny>,
    order: ByteOrder,
}


#[py_methods]
impl Writer {
    #[new]
    fn new(python: Python<'_>, writer: Py<PyAny>, order: Option<Py<PyAny>>) -> PyResult<Self> {
        let order = Converter::new(order).convert(python)?;

        Ok(Self { writer, order })
    }

    fn write_u8(&self, python: Python<'_>, value: u8) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_u16(&self, python: Python<'_>, value: u16) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_u32(&self, python: Python<'_>, value: u32) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_u64(&self, python: Python<'_>, value: u64) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_i8(&self, python: Python<'_>, value: i8) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_i16(&self, python: Python<'_>, value: i16) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_i32(&self, python: Python<'_>, value: i32) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_i64(&self, python: Python<'_>, value: i64) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_f32(&self, python: Python<'_>, value: f32) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_f64(&self, python: Python<'_>, value: f64) -> PyResult<()> {
        let array = match self.order {
            ByteOrder::Little => value.to_le_bytes(),
            ByteOrder::Big => value.to_be_bytes(),
        };

        self.write_slice(python, &array)
    }

    fn write_slice(&self, python: Python<'_>, slice: &[u8]) -> PyResult<()> {
        self.write(python, PyBytes::new(python, slice))
    }

    fn write<'py>(&self, python: Python<'py>, data: &'py PyBytes) -> PyResult<()> {
        self.writer.call_method1(python, WRITE, unary_tuple!(data))?;

        Ok(())
    }
}


#[py_module]
fn _gd<'py>(_python: Python<'py>, module: &'py PyModule) -> PyResult<()> {
    module.add_class::<Reader>()?;
    module.add_class::<Writer>()?;

    Ok(())
}
