<?php

namespace LexicaForge;

class LexicaForge {
    private $tokenCache;
    private $entityCache;
    
    public function __construct() {
        $this->tokenCache = [];
        $this->entityCache = [];
    }
    
    public function tokenize(string $text): array {
        if (isset($this->tokenCache[$text])) {
            return $this->tokenCache[$text];
        }
        
        $tokens = explode(' ', strtolower($text));
        $this->tokenCache[$text] = $tokens;
        return $tokens;
    }
    
    public function extractEntities(string $text): array {
        if (isset($this->entityCache[$text])) {
            return $this->entityCache[$text];
        }
        
        $entities = [];
        $words = explode(' ', $text);
        foreach ($words as $word) {
            if (preg_match('/^[A-Z][a-z]+$/', $word)) {
                $entities[] = $word;
            }
        }
        
        $this->entityCache[$text] = $entities;
        return $entities;
    }
    
    public function calculateSimilarity(string $text1, string $text2): float {
        $tokens1 = $this->tokenize($text1);
        $tokens2 = $this->tokenize($text2);
        
        $commonTokens = count(array_intersect($tokens1, $tokens2));
        $maxTokens = max(count($tokens1), count($tokens2));
        
        return $maxTokens > 0 ? $commonTokens / $maxTokens : 0.0;
    }
} 