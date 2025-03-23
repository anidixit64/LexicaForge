use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;
use rayon::prelude::*;
use lazy_static::lazy_static;
use regex::Regex;

/// Custom error type for parser operations
#[derive(Error, Debug)]
pub enum ParserError {
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    #[error("Processing error: {0}")]
    ProcessingError(String),
}

/// Represents a parsed morpheme with its properties
#[derive(Debug, Serialize, Deserialize)]
struct Morpheme {
    text: String,
    morpheme_type: String,
    position: usize,
    length: usize,
}

/// Represents a parsed word with its morphological analysis
#[derive(Debug, Serialize, Deserialize)]
struct ParsedWord {
    original: String,
    normalized: String,
    morphemes: Vec<Morpheme>,
    confidence: f64,
}

/// Python class for the high-performance parser
#[pyclass]
struct RustParser {
    prefix_patterns: HashMap<String, String>,
    suffix_patterns: HashMap<String, String>,
}

#[pymethods]
impl RustParser {
    #[new]
    fn new() -> PyResult<Self> {
        Ok(RustParser {
            prefix_patterns: HashMap::new(),
            suffix_patterns: HashMap::new(),
        })
    }

    /// Initialize patterns from Python dictionaries
    #[pyo3(text_signature = "($self, prefixes, suffixes)")]
    fn initialize_patterns(&mut self, prefixes: &PyDict, suffixes: &PyDict) -> PyResult<()> {
        self.prefix_patterns.clear();
        self.suffix_patterns.clear();

        for (key, value) in prefixes.iter() {
            let k: String = key.extract()?;
            let v: String = value.extract()?;
            self.prefix_patterns.insert(k, v);
        }

        for (key, value) in suffixes.iter() {
            let k: String = key.extract()?;
            let v: String = value.extract()?;
            self.suffix_patterns.insert(k, v);
        }

        Ok(())
    }

    /// Batch process a list of words in parallel
    #[pyo3(text_signature = "($self, words)")]
    fn batch_process<'py>(&self, py: Python<'py>, words: &PyList) -> PyResult<&'py PyList> {
        let words_vec: Vec<String> = words.extract()?;
        
        // Process words in parallel using rayon
        let results: Vec<ParsedWord> = words_vec.par_iter()
            .map(|word| self.process_single_word(word))
            .collect();

        // Convert results to Python objects
        let py_results = PyList::empty(py);
        for result in results {
            let dict = PyDict::new(py);
            dict.set_item("original", result.original)?;
            dict.set_item("normalized", result.normalized)?;
            dict.set_item("confidence", result.confidence)?;
            
            let morphemes = PyList::empty(py);
            for m in result.morphemes {
                let m_dict = PyDict::new(py);
                m_dict.set_item("text", m.text)?;
                m_dict.set_item("type", m.morpheme_type)?;
                m_dict.set_item("position", m.position)?;
                m_dict.set_item("length", m.length)?;
                morphemes.append(m_dict)?;
            }
            dict.set_item("morphemes", morphemes)?;
            
            py_results.append(dict)?;
        }

        Ok(py_results)
    }

    /// Process a single word with optimized Rust implementation
    fn process_single_word(&self, word: &str) -> ParsedWord {
        let normalized = word.to_lowercase();
        let mut morphemes = Vec::new();
        let mut confidence = 1.0;

        // Find prefixes
        for (pattern, meaning) in &self.prefix_patterns {
            if let Some(pos) = normalized.find(pattern) {
                if pos == 0 {  // Only consider prefix at start
                    morphemes.push(Morpheme {
                        text: pattern.clone(),
                        morpheme_type: "prefix".to_string(),
                        position: 0,
                        length: pattern.len(),
                    });
                    confidence *= 0.9;  // Adjust confidence
                    break;
                }
            }
        }

        // Find suffixes
        for (pattern, meaning) in &self.suffix_patterns {
            if let Some(pos) = normalized.rfind(pattern) {
                if pos + pattern.len() == normalized.len() {  // Only consider suffix at end
                    morphemes.push(Morpheme {
                        text: pattern.clone(),
                        morpheme_type: "suffix".to_string(),
                        position: pos,
                        length: pattern.len(),
                    });
                    confidence *= 0.9;  // Adjust confidence
                    break;
                }
            }
        }

        // Extract root
        let root_start = morphemes.iter()
            .find(|m| m.morpheme_type == "prefix")
            .map_or(0, |m| m.position + m.length);
            
        let root_end = morphemes.iter()
            .find(|m| m.morpheme_type == "suffix")
            .map_or(normalized.len(), |m| m.position);

        if root_start < root_end {
            morphemes.push(Morpheme {
                text: normalized[root_start..root_end].to_string(),
                morpheme_type: "root".to_string(),
                position: root_start,
                length: root_end - root_start,
            });
        }

        ParsedWord {
            original: word.to_string(),
            normalized,
            morphemes,
            confidence,
        }
    }
}

/// Create the Python module
#[pymodule]
fn lexicaforge_parser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustParser>()?;
    Ok(())
} 