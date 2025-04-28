<?php

namespace LexicaForge;

use PHPUnit\Framework\TestCase;

class LexicaForgeTest extends TestCase {
    private $nlp;

    protected function setUp(): void {
        $this->nlp = new LexicaForge();
    }

    public function testTokenize() {
        $text = "Hello World! This is a test.";
        $tokens = $this->nlp->tokenize($text);
        
        $this->assertCount(6, $tokens);
        $this->assertEquals("hello", $tokens[0]);
        $this->assertEquals("world!", $tokens[1]);
        $this->assertEquals("this", $tokens[2]);
        $this->assertEquals("is", $tokens[3]);
        $this->assertEquals("a", $tokens[4]);
        $this->assertEquals("test.", $tokens[5]);
    }

    public function testTokenizeEmptyString() {
        $text = "";
        $tokens = $this->nlp->tokenize($text);
        $this->assertEmpty($tokens);
    }

    public function testExtractEntities() {
        $text = "John works at Google and Mary is at Microsoft";
        $entities = $this->nlp->extractEntities($text);
        
        $this->assertCount(4, $entities);
        $this->assertContains("John", $entities);
        $this->assertContains("Google", $entities);
        $this->assertContains("Mary", $entities);
        $this->assertContains("Microsoft", $entities);
    }

    public function testExtractEntitiesNoMatches() {
        $text = "this is a test without proper nouns";
        $entities = $this->nlp->extractEntities($text);
        $this->assertEmpty($entities);
    }

    public function testCalculateSimilarity() {
        $text1 = "Hello World";
        $text2 = "Hello Universe";
        $similarity = $this->nlp->calculateSimilarity($text1, $text2);
        
        $this->assertEqualsWithDelta(0.5, $similarity, 0.001);
    }

    public function testCalculateSimilarityIdentical() {
        $text = "Hello World";
        $similarity = $this->nlp->calculateSimilarity($text, $text);
        $this->assertEqualsWithDelta(1.0, $similarity, 0.001);
    }

    public function testCalculateSimilarityNoCommon() {
        $text1 = "Hello World";
        $text2 = "Goodbye Universe";
        $similarity = $this->nlp->calculateSimilarity($text1, $text2);
        $this->assertEqualsWithDelta(0.0, $similarity, 0.001);
    }

    public function testCacheFunctionality() {
        $text = "Test caching";
        
        // First call should compute
        $tokens1 = $this->nlp->tokenize($text);
        
        // Second call should use cache
        $tokens2 = $this->nlp->tokenize($text);
        
        $this->assertSame($tokens1, $tokens2);
    }
} 