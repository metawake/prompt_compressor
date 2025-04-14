# Semantic Prompt Compressor

A Python library for compressing prompts while preserving their semantic meaning. This tool helps reduce token count for LLM prompts without losing important information.

## Features

- Modular, rule-based compression
- Multiple compression profiles (safe, quality)
- Configurable compression rules
- Token count reduction analysis
- Command-line interface for easy use

## Installation

```bash
pip install -e .
```

## Usage

### Command Line Interface

The package provides a CLI with two main commands: `compress` and `analyze`.

#### Basic Compression

```bash
prompt-compress compress "I am really interested in learning more about Python programming"
```

Output:
```
I'm interested in learning about Python programming
```

#### Show Compression Statistics

```bash
prompt-compress compress "I am really interested in learning more about Python programming" -s
```

Output:
```
=== Compression Statistics ===
Original tokens: 12
Compressed tokens: 9
Tokens saved: 3
Compression ratio: 25.00%
```

#### Detailed Analysis

```bash
prompt-compress compress "I am really interested in learning more about Python programming" -v
```

Output:
```
=== Compression Statistics ===
Original tokens: 12
Compressed tokens: 9
Tokens saved: 3
Compression ratio: 25.00%

=== Detailed Analysis ===
Original text: I am really interested in learning more about Python programming
Compressed text: I'm interested in learning about Python programming
```

#### Analyze Compression Opportunities

```bash
prompt-compress analyze "I am really interested in learning more about Python programming"
```

Output:
```
=== Compression Statistics ===
Original tokens: 12
Compressed tokens: 9
Tokens saved: 3
Compression ratio: 25.00%
```

#### Save Results to File

```bash
prompt-compress compress "I am really interested in learning more about Python programming" -o results.json
```

### Python API

```python
from prompt_compressor import PromptCompressor

# Initialize with default rules
compressor = PromptCompressor()

# Compress a prompt
compressed = compressor.compress("I am really interested in learning more about Python programming")

# Analyze compression
analysis = compressor.analyze_prompt("I am really interested in learning more about Python programming")
print(f"Original tokens: {analysis['original_tokens']}")
print(f"Compressed tokens: {analysis['compressed_tokens']}")
print(f"Compression ratio: {analysis['compression_ratio']:.2f}%")
```

## Compression Rules

The compression rules are defined in YAML format and can be customized. The default rules include:

- Remove fillers and greetings
- Strip unnecessary modifiers
- Collapse redundant phrases
- Preserve technical terms and entities
- Handle contractions properly

Example rules configuration:

```yaml
rule_groups:
  remove_fillers:
    enabled: true
    patterns:
      - pattern: "I am really"
        replacement: "I'm"
      - pattern: "more about"
        replacement: "about"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 