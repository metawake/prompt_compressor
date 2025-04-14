import typer
from pathlib import Path
from typing import Optional
import json
from .core.compressor import PromptCompressor

app = typer.Typer()

def print_stats(result: dict, show_verbose: bool = False):
    """Print compression statistics in a formatted way"""
    print("\n=== Compression Statistics ===")
    print(f"Original tokens: {result['original_tokens']}")
    print(f"Compressed tokens: {result['compressed_tokens']}")
    print(f"Tokens saved: {result['original_tokens'] - result['compressed_tokens']}")
    print(f"Compression ratio: {result['compression_ratio']:.2f}%")
    
    if show_verbose:
        print("\n=== Detailed Analysis ===")
        print(f"Original text: {result['original_text']}")
        print(f"Compressed text: {result['compressed_text']}")

@app.command()
def compress(
    prompt: str = typer.Argument(..., help="The prompt to compress"),
    rules_file: Optional[Path] = typer.Option(None, "--rules", "-r", help="Path to rules YAML file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to save results as JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output including original and compressed text"),
    stats: bool = typer.Option(False, "--stats", "-s", help="Show compression statistics")
):
    """Compress a prompt using semantic compression rules"""
    compressor = PromptCompressor(rules_file=str(rules_file) if rules_file else None)
    
    if not prompt.strip():
        if verbose or stats:
            print("\n=== Empty Prompt ===")
            print("Original prompt: (empty)")
            print("Compressed prompt: (empty)")
            print("Token count: 0")
            print("Reduction: 0.00%")
        if output:
            with open(output, 'w') as f:
                json.dump({
                    'original': '',
                    'compressed': '',
                    'original_tokens': 0,
                    'compressed_tokens': 0,
                    'reduction': 0.0
                }, f, indent=2)
        return
    
    result = compressor.analyze_prompt(prompt)
    compressed = result['compressed_text']
    
    # Show stats if either verbose or stats flag is set
    if verbose or stats:
        print_stats(result, show_verbose=verbose)
    else:
        # Default output is just the compressed text
        print(compressed)
    
    if output:
        with open(output, 'w') as f:
            json.dump({
                'original': prompt,
                'compressed': compressed,
                'original_tokens': result['original_tokens'],
                'compressed_tokens': result['compressed_tokens'],
                'reduction': result['compression_ratio']
            }, f, indent=2)

@app.command()
def analyze(
    prompt: str = typer.Argument(..., help="The prompt to analyze"),
    rules_file: Optional[Path] = typer.Option(None, "--rules", "-r", help="Path to rules YAML file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed analysis")
):
    """Analyze a prompt for compression opportunities"""
    compressor = PromptCompressor(rules_file=str(rules_file) if rules_file else None)
    result = compressor.analyze_prompt(prompt)
    
    print_stats(result, show_verbose=verbose)

def main():
    app() 