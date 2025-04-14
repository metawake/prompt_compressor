import json
from pathlib import Path
from prompt_compressor.core.compressor import PromptCompressor
import spacy

def calculate_entity_preservation(original_text, compressed_text, nlp):
    """Calculate what percentage of named entities were preserved"""
    original_doc = nlp(original_text)
    compressed_doc = nlp(compressed_text)
    
    # Extract original entities
    original_entities = set()
    for ent in original_doc.ents:
        original_entities.add(ent.text.lower())
    
    # Extract preserved entities
    preserved_entities = set()
    for ent in compressed_doc.ents:
        preserved_entities.add(ent.text.lower())
    
    # Calculate preservation ratio
    total_entities = len(original_entities)
    preserved_count = sum(1 for ent in original_entities if ent in preserved_entities)
    
    preservation_ratio = (preserved_count / total_entities * 100) if total_entities > 0 else 100
    return preservation_ratio, original_entities, preserved_entities

def test_basic_replacements():
    """Test basic compression replacements"""
    compressor = PromptCompressor(rules_file="rules.yaml")
    nlp = spacy.load("en_core_web_sm")
    
    test_cases = [
        ("Could you explain how this works?", "explain how this works?"),
        ("I would like to learn more about this topic.", "learn more about this topic."),
        ("I'm working on a project that needs optimization.", "I'm working on a project needing optimization."),
        ("The system's performance hasn't been great.", "The system's performance hasn't been great."),
        ("We're going to implement a new feature.", "We're implementing a new feature.")
    ]
    
    print("\nBasic Replacement Tests:")
    print("-" * 50)
    
    for original, expected in test_cases:
        result = compressor.analyze_prompt(original)
        preservation_ratio, orig_ents, preserved_ents = calculate_entity_preservation(
            original, result['compressed_text'], nlp
        )
        print(f"\nOriginal ({result['original_tokens']} tokens): {original}")
        print(f"Compressed ({result['compressed_tokens']} tokens): {result['compressed_text']}")
        print(f"Compression ratio: {result['compression_ratio']:.2f}%")
        print(f"Entity preservation: {preservation_ratio:.2f}%")
        if orig_ents:
            print(f"Original entities: {', '.join(orig_ents)}")
            print(f"Preserved entities: {', '.join(preserved_ents)}")

def analyze_prompts(prompts_file="sample_prompts.txt"):
    """Analyze compression for a set of prompts"""
    compressor = PromptCompressor(rules_file="rules.yaml")
    nlp = spacy.load("en_core_web_sm")
    
    with open(prompts_file, 'r') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    total_original = 0
    total_compressed = 0
    total_saved = 0
    total_entity_preservation = 0
    compression_results = []
    
    for prompt in prompts:
        result = compressor.analyze_prompt(prompt)
        preservation_ratio, orig_ents, preserved_ents = calculate_entity_preservation(
            prompt, result['compressed_text'], nlp
        )
        
        total_original += result['original_tokens']
        total_compressed += result['compressed_tokens']
        total_saved += (result['original_tokens'] - result['compressed_tokens'])
        total_entity_preservation += preservation_ratio
        
        result['entity_preservation'] = preservation_ratio
        result['original_entities'] = list(orig_ents)
        result['preserved_entities'] = list(preserved_ents)
        compression_results.append(result)
    
    # Sort by compression ratio
    compression_results.sort(key=lambda x: x['compression_ratio'], reverse=True)
    
    # Calculate averages
    avg_compression = (total_saved / total_original * 100) if total_original > 0 else 0
    avg_entity_preservation = total_entity_preservation / len(prompts) if prompts else 0
    
    print(f"\nAnalyzed {len(prompts)} prompts:")
    print(f"Total original tokens: {total_original}")
    print(f"Total compressed tokens: {total_compressed}")
    print(f"Average compression ratio: {avg_compression:.2f}%")
    print(f"Average entity preservation: {avg_entity_preservation:.2f}%")
    print(f"Total tokens saved: {total_saved}")
    
    print("\nTop 5 most compressed prompts:")
    print("-" * 50)
    for result in compression_results[:5]:
        print(f"\nOriginal ({result['original_tokens']} tokens): {result['original_text']}")
        print(f"Compressed ({result['compressed_tokens']} tokens): {result['compressed_text']}")
        print(f"Compression ratio: {result['compression_ratio']:.2f}%")
        print(f"Entity preservation: {result['entity_preservation']:.2f}%")
        if result['original_entities']:
            print(f"Original entities: {', '.join(result['original_entities'])}")
            print(f"Preserved entities: {', '.join(result['preserved_entities'])}")
    
    print("\nBottom 5 least compressed prompts:")
    print("-" * 50)
    for result in compression_results[-5:]:
        print(f"\nOriginal ({result['original_tokens']} tokens): {result['original_text']}")
        print(f"Compressed ({result['compressed_tokens']} tokens): {result['compressed_text']}")
        print(f"Compression ratio: {result['compression_ratio']:.2f}%")
        print(f"Entity preservation: {result['entity_preservation']:.2f}%")
        if result['original_entities']:
            print(f"Original entities: {', '.join(result['original_entities'])}")
            print(f"Preserved entities: {', '.join(result['preserved_entities'])}")

def main():
    # Run basic replacement tests
    test_basic_replacements()
    
    # Analyze general prompts
    print("\nGeneral Prompts Compression Report:")
    print("=" * 50)
    analyze_prompts()

if __name__ == "__main__":
    main() 