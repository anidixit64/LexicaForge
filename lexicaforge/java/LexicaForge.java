package com.lexicaforge;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

public class LexicaForge {
    private Map<String, List<String>> tokenCache;
    private Map<String, List<String>> entityCache;
    
    public LexicaForge() {
        this.tokenCache = new HashMap<>();
        this.entityCache = new HashMap<>();
    }
    
    public List<String> tokenize(String text) {
        if (tokenCache.containsKey(text)) {
            return tokenCache.get(text);
        }
        
        List<String> tokens = new ArrayList<>();
        String[] words = text.split("\\s+");
        for (String word : words) {
            tokens.add(word.toLowerCase());
        }
        
        tokenCache.put(text, tokens);
        return tokens;
    }
    
    public List<String> extractEntities(String text) {
        if (entityCache.containsKey(text)) {
            return entityCache.get(text);
        }
        
        List<String> entities = new ArrayList<>();
        // Basic entity extraction implementation
        String[] words = text.split("\\s+");
        for (String word : words) {
            if (word.matches("[A-Z][a-z]+")) {
                entities.add(word);
            }
        }
        
        entityCache.put(text, entities);
        return entities;
    }
    
    public double calculateSimilarity(String text1, String text2) {
        List<String> tokens1 = tokenize(text1);
        List<String> tokens2 = tokenize(text2);
        
        int commonTokens = 0;
        for (String token : tokens1) {
            if (tokens2.contains(token)) {
                commonTokens++;
            }
        }
        
        return (double) commonTokens / Math.max(tokens1.size(), tokens2.size());
    }
} 