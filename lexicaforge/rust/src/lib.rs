use std::collections::HashMap;
use std::sync::Arc;
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use unicode_segmentation::UnicodeSegmentation;
use unicode_normalization::UnicodeNormalization;

#[derive(Error, Debug)]
pub enum LexicaError {
    #[error("Invalid UTF-8 sequence")]
    InvalidUtf8,
    #[error("Regex compilation error: {0}")]
    RegexError(#[from] regex::Error),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// Result type for the library
pub type Result<T> = std::result::Result<T, LexicaError>;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StringStats {
    pub char_count: usize,
    pub word_count: usize,
    pub unique_chars: usize,
    pub unique_words: usize,
    pub char_frequencies: HashMap<char, usize>,
    pub word_frequencies: HashMap<String, usize>,
}

/// Performance-optimized string statistics calculation
#[pyo3::pyfunction]
pub fn calculate_string_stats(text: &str) -> Result<StringStats> {
    let chars: Vec<char> = text.chars().collect();
    let words: Vec<String> = text.unicode_words().map(String::from).collect();
    
    let char_frequencies = chars.par_iter()
        .fold_with(HashMap::new(), |mut acc, &c| {
            *acc.entry(c).or_insert(0) += 1;
            acc
        })
        .reduce_with(|mut a, b| {
            for (k, v) in b {
                *a.entry(k).or_insert(0) += v;
            }
            a
        })
        .unwrap_or_default();
    
    let word_frequencies = words.par_iter()
        .fold_with(HashMap::new(), |mut acc, word| {
            *acc.entry(word.clone()).or_insert(0) += 1;
            acc
        })
        .reduce_with(|mut a, b| {
            for (k, v) in b {
                *a.entry(k).or_insert(0) += v;
            }
            a
        })
        .unwrap_or_default();
    
    Ok(StringStats {
        char_count: chars.len(),
        word_count: words.len(),
        unique_chars: char_frequencies.len(),
        unique_words: word_frequencies.len(),
        char_frequencies,
        word_frequencies,
    })
}

/// Fast string similarity calculation using Levenshtein distance
#[pyo3::pyfunction]
pub fn levenshtein_distance(s1: &str, s2: &str) -> usize {
    let s1_chars: Vec<char> = s1.chars().collect();
    let s2_chars: Vec<char> = s2.chars().collect();
    
    let mut matrix = vec![vec![0; s2_chars.len() + 1]; s1_chars.len() + 1];
    
    for i in 0..=s1_chars.len() {
        matrix[i][0] = i;
    }
    
    for j in 0..=s2_chars.len() {
        matrix[0][j] = j;
    }
    
    for i in 0..s1_chars.len() {
        for j in 0..s2_chars.len() {
            let cost = if s1_chars[i] == s2_chars[j] { 0 } else { 1 };
            matrix[i + 1][j + 1] = (matrix[i][j + 1] + 1)
                .min(matrix[i + 1][j] + 1)
                .min(matrix[i][j] + cost);
        }
    }
    
    matrix[s1_chars.len()][s2_chars.len()]
}

/// Fast string normalization for comparison
#[pyo3::pyfunction]
pub fn normalize_string(s: &str) -> String {
    s.nfd()
        .filter(|c| !c.is_combining_mark())
        .collect::<String>()
        .to_lowercase()
}

/// Efficient pattern matching using Aho-Corasick algorithm
#[pyo3::pyfunction]
pub fn find_patterns(text: &str, patterns: Vec<String>) -> HashMap<String, Vec<usize>> {
    let automaton = aho_corasick::AhoCorasick::new(patterns.iter().map(|s| s.as_str()));
    let mut matches = HashMap::new();
    
    for mat in automaton.find_iter(text) {
        let pattern = patterns[mat.pattern()].clone();
        matches.entry(pattern)
            .or_insert_with(Vec::new)
            .push(mat.start());
    }
    
    matches
}

/// Parallel text processing for large datasets
#[pyo3::pyfunction]
pub fn process_text_batch(texts: Vec<String>) -> Vec<StringStats> {
    texts.par_iter()
        .map(|text| calculate_string_stats(text))
        .filter_map(Result::ok)
        .collect()
}

/// Fast string tokenization with custom delimiters
#[pyo3::pyfunction]
pub fn tokenize(text: &str, delimiters: &str) -> Vec<String> {
    let pattern = Regex::new(&format!("[{}]+", regex::escape(delimiters))).unwrap();
    pattern.split(text)
        .filter(|s| !s.is_empty())
        .map(String::from)
        .collect()
}

/// Initialize the Python module
#[pymodule]
fn lexicaforge_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_string_stats, m)?)?;
    m.add_function(wrap_pyfunction!(levenshtein_distance, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_string, m)?)?;
    m.add_function(wrap_pyfunction!(find_patterns, m)?)?;
    m.add_function(wrap_pyfunction!(process_text_batch, m)?)?;
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    Ok(())
} 