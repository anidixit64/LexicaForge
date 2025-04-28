package com.lexicaforge;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;

public class LexicaForgeTest {
    private final LexicaForge nlp = new LexicaForge();

    @Test
    public void testTokenize() {
        String text = "Hello World! This is a test.";
        List<String> tokens = nlp.tokenize(text);
        
        assertEquals(6, tokens.size());
        assertEquals("hello", tokens.get(0));
        assertEquals("world!", tokens.get(1));
        assertEquals("this", tokens.get(2));
        assertEquals("is", tokens.get(3));
        assertEquals("a", tokens.get(4));
        assertEquals("test.", tokens.get(5));
    }

    @Test
    public void testTokenizeEmptyString() {
        String text = "";
        List<String> tokens = nlp.tokenize(text);
        assertTrue(tokens.isEmpty());
    }

    @Test
    public void testExtractEntities() {
        String text = "John works at Google and Mary is at Microsoft";
        List<String> entities = nlp.extractEntities(text);
        
        assertEquals(4, entities.size());
        assertTrue(entities.contains("John"));
        assertTrue(entities.contains("Google"));
        assertTrue(entities.contains("Mary"));
        assertTrue(entities.contains("Microsoft"));
    }

    @Test
    public void testExtractEntitiesNoMatches() {
        String text = "this is a test without proper nouns";
        List<String> entities = nlp.extractEntities(text);
        assertTrue(entities.isEmpty());
    }

    @Test
    public void testCalculateSimilarity() {
        String text1 = "Hello World";
        String text2 = "Hello Universe";
        double similarity = nlp.calculateSimilarity(text1, text2);
        
        assertEquals(0.5, similarity, 0.001);
    }

    @Test
    public void testCalculateSimilarityIdentical() {
        String text = "Hello World";
        double similarity = nlp.calculateSimilarity(text, text);
        assertEquals(1.0, similarity, 0.001);
    }

    @Test
    public void testCalculateSimilarityNoCommon() {
        String text1 = "Hello World";
        String text2 = "Goodbye Universe";
        double similarity = nlp.calculateSimilarity(text1, text2);
        assertEquals(0.0, similarity, 0.001);
    }

    @Test
    public void testCacheFunctionality() {
        String text = "Test caching";
        
        // First call should compute
        List<String> tokens1 = nlp.tokenize(text);
        
        // Second call should use cache
        List<String> tokens2 = nlp.tokenize(text);
        
        assertSame(tokens1, tokens2);
    }
} 