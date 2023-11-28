use pyo3::prelude::*;
use isg_4real::*;

#[pymodule]
fn dddb(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    let submodule = PyModule::new(_py, "video")?;
    submodule.add_function(wrap_pyfunction!(encode, m)?)?;
    submodule.add_function(wrap_pyfunction!(decode, m)?)?;
    m.add_submodule(submodule)?;
    Ok(())
}
