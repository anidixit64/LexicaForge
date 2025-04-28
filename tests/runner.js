const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Test configuration
const config = {
    java: {
        command: 'mvn test',
        testDir: 'lexicaforge/java',
        expectedTests: 8
    },
    php: {
        command: './vendor/bin/phpunit',
        testDir: 'lexicaforge/php',
        expectedTests: 8
    },
    python: {
        command: 'pytest tests/nlp/test_lexicaforge.py -v',
        testDir: 'tests/nlp',
        expectedTests: 8
    }
};

// Debug logger
const debug = {
    log: (message) => console.log(`[DEBUG] ${message}`),
    error: (message) => console.error(`[ERROR] ${message}`),
    success: (message) => console.log(`[SUCCESS] ${message}`)
};

// Test runner class
class TestRunner {
    constructor() {
        this.results = {
            java: { passed: 0, failed: 0, total: 0 },
            php: { passed: 0, failed: 0, total: 0 },
            python: { passed: 0, failed: 0, total: 0 }
        };
    }

    async runTests() {
        debug.log('Starting test execution...');
        
        for (const [lang, config] of Object.entries(config)) {
            try {
                debug.log(`Running ${lang} tests...`);
                const output = execSync(config.command, { encoding: 'utf8' });
                
                // Parse test results
                this.parseResults(lang, output);
                
                // Check for missing tests
                this.checkMissingTests(lang);
                
            } catch (error) {
                debug.error(`Error running ${lang} tests: ${error.message}`);
                this.results[lang].failed = config.expectedTests;
            }
        }
        
        this.printSummary();
    }

    parseResults(lang, output) {
        // Java test parsing
        if (lang === 'java') {
            const passed = (output.match(/Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)/) || [0, 0, 0, 0]);
            this.results.java.passed = parseInt(passed[1]) - parseInt(passed[2]) - parseInt(passed[3]);
            this.results.java.failed = parseInt(passed[2]) + parseInt(passed[3]);
            this.results.java.total = parseInt(passed[1]);
        }
        // PHP test parsing
        else if (lang === 'php') {
            const passed = (output.match(/OK \((\d+) tests, (\d+) assertions\)/) || [0, 0, 0]);
            this.results.php.passed = parseInt(passed[1]);
            this.results.php.total = parseInt(passed[1]);
        }
        // Python test parsing
        else if (lang === 'python') {
            const passed = (output.match(/passed/) || []).length;
            const failed = (output.match(/failed/) || []).length;
            this.results.python.passed = passed;
            this.results.python.failed = failed;
            this.results.python.total = passed + failed;
        }
    }

    checkMissingTests(lang) {
        const expected = config[lang].expectedTests;
        const actual = this.results[lang].total;
        
        if (actual < expected) {
            debug.error(`${lang.toUpperCase()}: Missing ${expected - actual} tests!`);
            debug.log('Expected test cases:');
            this.printExpectedTestCases(lang);
        }
    }

    printExpectedTestCases(lang) {
        const testCases = {
            java: [
                'testTokenize',
                'testTokenizeEmptyString',
                'testExtractEntities',
                'testExtractEntitiesNoMatches',
                'testCalculateSimilarity',
                'testCalculateSimilarityIdentical',
                'testCalculateSimilarityNoCommon',
                'testCacheFunctionality'
            ],
            php: [
                'testTokenize',
                'testTokenizeEmptyString',
                'testExtractEntities',
                'testExtractEntitiesNoMatches',
                'testCalculateSimilarity',
                'testCalculateSimilarityIdentical',
                'testCalculateSimilarityNoCommon',
                'testCacheFunctionality'
            ],
            python: [
                'test_tokenize',
                'test_tokenize_empty_string',
                'test_extract_entities',
                'test_extract_entities_no_matches',
                'test_calculate_similarity',
                'test_calculate_similarity_identical',
                'test_calculate_similarity_no_common',
                'test_cache_functionality'
            ]
        };

        testCases[lang].forEach(test => {
            debug.log(`- ${test}`);
        });
    }

    printSummary() {
        console.log('\n=== Test Summary ===');
        for (const [lang, result] of Object.entries(this.results)) {
            console.log(`\n${lang.toUpperCase()}:`);
            console.log(`  Total Tests: ${result.total}`);
            console.log(`  Passed: ${result.passed}`);
            console.log(`  Failed: ${result.failed}`);
            
            if (result.total < config[lang].expectedTests) {
                console.log(`  Missing: ${config[lang].expectedTests - result.total}`);
            }
        }
    }
}

// Run the tests
const runner = new TestRunner();
runner.runTests().catch(error => {
    debug.error(`Test runner failed: ${error.message}`);
    process.exit(1);
}); 