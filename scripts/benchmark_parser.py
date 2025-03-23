"""
Benchmark script to compare Python and Rust parser implementations.
"""
import time
import random
import string
from typing import List, Callable
import statistics

from lexicaforge.nlp.morphemes.analyzer import MorphemeAnalyzer
from lexicaforge.nlp.parser import RUST_AVAILABLE


def generate_random_word(min_len: int = 3, max_len: int = 10) -> str:
    """Generate a random word-like string."""
    length = random.randint(min_len, max_len)
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_word_with_affixes() -> str:
    """Generate a word with common prefixes/suffixes."""
    prefixes = ['un', 're', 'dis', 'pre', 'post']
    suffixes = ['ing', 'ed', 'ly', 'tion', 'ment', 'ness']
    root = generate_random_word(4, 7)
    
    has_prefix = random.random() > 0.5
    has_suffix = random.random() > 0.5
    
    if has_prefix and has_suffix:
        return random.choice(prefixes) + root + random.choice(suffixes)
    elif has_prefix:
        return random.choice(prefixes) + root
    elif has_suffix:
        return root + random.choice(suffixes)
    return root


def benchmark_function(func: Callable, args: List, num_runs: int = 5) -> dict:
    """Benchmark a function over multiple runs."""
    times = []
    for _ in range(num_runs):
        start = time.time()
        func(*args)
        end = time.time()
        times.append(end - start)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times)
    }


def main():
    """Run benchmarks comparing Python and Rust implementations."""
    # Generate test data
    num_words = 10000
    words = [generate_word_with_affixes() for _ in range(num_words)]
    
    # Initialize analyzer
    analyzer = MorphemeAnalyzer()
    
    # Benchmark single word analysis
    word = "unhappiness"
    single_results = benchmark_function(analyzer.analyze, [word])
    
    # Benchmark batch processing
    batch_results = benchmark_function(
        analyzer.get_morpheme_frequency,
        [words]
    )
    
    # Print results
    print(f"Benchmarking results (using {'Rust' if RUST_AVAILABLE else 'Python'} backend):")
    print("\nSingle word analysis:")
    print(f"Mean time: {single_results['mean']:.6f} seconds")
    print(f"Median time: {single_results['median']:.6f} seconds")
    print(f"Std dev: {single_results['std_dev']:.6f} seconds")
    
    print(f"\nBatch processing ({num_words} words):")
    print(f"Mean time: {batch_results['mean']:.6f} seconds")
    print(f"Median time: {batch_results['median']:.6f} seconds")
    print(f"Std dev: {batch_results['std_dev']:.6f} seconds")
    print(f"Words per second: {num_words / batch_results['mean']:.2f}")


if __name__ == "__main__":
    main() 