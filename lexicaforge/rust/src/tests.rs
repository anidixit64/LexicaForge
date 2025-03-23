#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_calculate_string_stats() {
        let text = "Hello, world!";
        let stats = calculate_string_stats(text).unwrap();
        
        assert_eq!(stats.char_count, 13);
        assert_eq!(stats.word_count, 2);
        assert_eq!(stats.unique_chars, 10);
        assert_eq!(stats.unique_words, 2);
        
        let mut expected_chars = HashMap::new();
        expected_chars.insert('H', 1);
        expected_chars.insert('e', 1);
        expected_chars.insert('l', 3);
        expected_chars.insert('o', 2);
        expected_chars.insert(',', 1);
        expected_chars.insert(' ', 1);
        expected_chars.insert('w', 1);
        expected_chars.insert('r', 1);
        expected_chars.insert('d', 1);
        expected_chars.insert('!', 1);
        
        assert_eq!(stats.char_frequencies, expected_chars);
        
        let mut expected_words = HashMap::new();
        expected_words.insert("Hello".to_string(), 1);
        expected_words.insert("world".to_string(), 1);
        
        assert_eq!(stats.word_frequencies, expected_words);
    }

    #[test]
    fn test_levenshtein_distance() {
        assert_eq!(levenshtein_distance("kitten", "sitting"), 3);
        assert_eq!(levenshtein_distance("saturday", "sunday"), 3);
        assert_eq!(levenshtein_distance("", ""), 0);
        assert_eq!(levenshtein_distance("", "abc"), 3);
        assert_eq!(levenshtein_distance("abc", ""), 3);
    }

    #[test]
    fn test_normalize_string() {
        assert_eq!(normalize_string("Hello, World!"), "hello, world!");
        assert_eq!(normalize_string("café"), "cafe");
        assert_eq!(normalize_string("über"), "uber");
        assert_eq!(normalize_string(""), "");
    }

    #[test]
    fn test_find_patterns() {
        let text = "The quick brown fox jumps over the lazy dog";
        let patterns = vec!["the".to_string(), "fox".to_string(), "dog".to_string()];
        
        let matches = find_patterns(text, patterns);
        
        let mut expected = HashMap::new();
        expected.insert("the".to_string(), vec![0, 31]);
        expected.insert("fox".to_string(), vec![16]);
        expected.insert("dog".to_string(), vec![40]);
        
        assert_eq!(matches, expected);
    }

    #[test]
    fn test_process_text_batch() {
        let texts = vec![
            "Hello, world!".to_string(),
            "Testing 123".to_string(),
            "Another test".to_string(),
        ];
        
        let results = process_text_batch(texts);
        
        assert_eq!(results.len(), 3);
        assert_eq!(results[0].word_count, 2);
        assert_eq!(results[1].word_count, 2);
        assert_eq!(results[2].word_count, 2);
    }

    #[test]
    fn test_tokenize() {
        assert_eq!(
            tokenize("Hello, world!", ", "),
            vec!["Hello", "world!"]
        );
        
        assert_eq!(
            tokenize("one-two-three", "-"),
            vec!["one", "two", "three"]
        );
        
        assert_eq!(
            tokenize("a.b.c", "."),
            vec!["a", "b", "c"]
        );
        
        assert_eq!(
            tokenize("", ","),
            Vec::<String>::new()
        );
    }

    #[test]
    fn test_error_handling() {
        // Test invalid UTF-8 handling
        let invalid_text = unsafe { std::str::from_utf8_unchecked(&[0xFF, 0xFF]) };
        assert!(calculate_string_stats(invalid_text).is_err());
    }
} 