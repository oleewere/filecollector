extern crate yaml_rust;
extern crate pyo3;

use pyo3::prelude::{Python, PyModule, PyResult, pyfunction, pymodule};
use pyo3::wrap_pyfunction;

use yaml_rust::YamlLoader;
use std::fs::File;
use std::io::prelude::*;


#[pyfunction]
fn collect(config_file: &str) {
    let mut file = File::open(config_file).expect("Unable to open file");
    let mut contents = String::new();

    file.read_to_string(&mut contents).expect("Unable to read file");

    let docs = YamlLoader::load_from_str(&contents).unwrap();
    let doc = &docs[0];

    println!("{:?}", doc);
}

#[pymodule]
fn filecollector(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(collect))?;
    Ok(())
}
