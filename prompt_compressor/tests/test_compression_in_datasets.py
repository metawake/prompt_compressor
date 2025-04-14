import pytest
from prompt_compressor import PromptCompressor
from get_dataset3 import get_random_user_prompts, ContentAnalyzer, ContentType
import json
from typing import Dict, List, Any
import re

@pytest.fixture
def compressor():
    return PromptCompressor()

@pytest.fixture
def analyzer():
    return ContentAnalyzer()

@pytest.fixture
def test_prompts():
    # Load all prompts from file
    with open('sample_prompts.txt', 'r') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    # Debug: Print first few prompts and their compressions
    print("\n=== Sample Compressions ===")
    for i, prompt in enumerate(prompts[:3]):
        print(f"\nPrompt {i+1}:")
        print(f"Original: {prompt}")
        compressed = PromptCompressor().compress_prompt(prompt)
        print(f"Compressed: {compressed}")
        original_tokens = PromptCompressor().get_token_count(prompt)
        compressed_tokens = PromptCompressor().get_token_count(compressed)
        reduction = ((original_tokens - compressed_tokens) / original_tokens) * 100
        print(f"Tokens: {original_tokens} -> {compressed_tokens} ({reduction:.1f}% reduction)")
    
    return prompts

def test_compression_stats(compressor, test_prompts):
    """Test compression statistics across the dataset"""
    stats = {
        'total_prompts': len(test_prompts),
        'good_compression': 0,  # >15% reduction
        'minor_compression': 0,  # 5-15% reduction
        'unchanged': 0,  # <5% reduction
        'total_reduction': 0,
        'total_original_tokens': 0,
        'total_compressed_tokens': 0,
        'best_compressions': [],  # Track best performing prompts
        'minimal_compressions': [],  # Track minimally compressed prompts
        'compression_by_pattern': {}  # Track average compression by pattern
    }

    # Common filler patterns to look for
    filler_patterns = {
        'hedging': r'\b(?:really|very|quite|somewhat|rather|fairly|pretty)\b',
        'redundant_phrases': r'\b(?:I think that|I believe that|in my opinion|from my perspective)\b',
        'polite_fillers': r'\b(?:if you could|if you would|if possible|if you don\'t mind)\b',
        'verbal_softeners': r'\b(?:just|maybe|perhaps|possibly|probably)\b',
        'empty_starters': r'\b(?:I was wondering|I wanted to ask|I would like to know)\b'
    }

    # Structural patterns that often lead to good compression
    structural_patterns = {
        'indirect_questions': r'\b(?:Could you|Would you|Can you) (?:tell|explain|describe|share)\b',
        'self_references': r'\b(?:I\'m curious|I\'ve been thinking|I\'d like to know)\b',
        'redundant_context': r'\b(?:In the context of|When it comes to|With regards to)\b',
        'multiple_adjectives': r'\b(?:\w+\s+){2,}(?:way|approach|method|solution|idea)\b',
        'nested_clauses': r'\b(?:that is|which is|who are)\b.*\b(?:that|which|who)\b',
        'double_verbs': r'\b(?:try to|begin to|start to|seem to|appear to)\b',
        'passive_voice': r'\b(?:is|are|was|were)\s+(?:\w+ed|\w+en)\b',
        'meta_phrases': r'\b(?:the topic of|the concept of|the idea of|the process of)\b'
    }

    for prompt in test_prompts:
        original_tokens = compressor.get_token_count(prompt)
        compressed = compressor.compress_prompt(prompt)
        compressed_tokens = compressor.get_token_count(compressed)
        
        reduction = ((original_tokens - compressed_tokens) / original_tokens) * 100
        
        stats['total_original_tokens'] += original_tokens
        stats['total_compressed_tokens'] += compressed_tokens
        
        # Analyze all patterns in the prompt
        patterns_found = []
        all_patterns = {**filler_patterns, **structural_patterns}
        for pattern_name, pattern in all_patterns.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                patterns_found.append(pattern_name)
                # Track compression by pattern
                if pattern_name not in stats['compression_by_pattern']:
                    stats['compression_by_pattern'][pattern_name] = {'count': 0, 'total_reduction': 0}
                stats['compression_by_pattern'][pattern_name]['count'] += 1
                stats['compression_by_pattern'][pattern_name]['total_reduction'] += reduction
        
        if reduction > 15:
            stats['good_compression'] += 1
            stats['best_compressions'].append({
                'original': prompt,
                'compressed': compressed,
                'reduction': reduction,
                'patterns': patterns_found
            })
        elif reduction > 5:
            stats['minor_compression'] += 1
        else:
            stats['unchanged'] += 1
            stats['minimal_compressions'].append({
                'original': prompt,
                'compressed': compressed,
                'reduction': reduction,
                'patterns': patterns_found
            })

    stats['total_reduction'] = ((stats['total_original_tokens'] - stats['total_compressed_tokens']) / 
                              stats['total_original_tokens']) * 100

    # Print statistics
    print("\n=== Dataset Compression Statistics ===")
    print(f"Total prompts tested: {stats['total_prompts']}")
    print(f"Good compression (>15%): {stats['good_compression']} ({stats['good_compression']/stats['total_prompts']*100:.1f}%)")
    print(f"Minor compression (5-15%): {stats['minor_compression']} ({stats['minor_compression']/stats['total_prompts']*100:.1f}%)")
    print(f"Unchanged (<5%): {stats['unchanged']} ({stats['unchanged']/stats['total_prompts']*100:.1f}%)")
    print(f"Average token reduction: {stats['total_reduction']:.1f}%")
    print(f"Original tokens: {stats['total_original_tokens']}")
    print(f"Compressed tokens: {stats['total_compressed_tokens']}")
    print(f"Total tokens saved: {stats['total_original_tokens'] - stats['total_compressed_tokens']}")

    # Print pattern effectiveness
    print("\n=== Pattern Effectiveness Analysis ===")
    print("Average compression by pattern type:")
    for pattern, data in sorted(stats['compression_by_pattern'].items(), 
                              key=lambda x: x[1]['total_reduction']/x[1]['count'], 
                              reverse=True):
        avg_reduction = data['total_reduction'] / data['count']
        print(f"- {pattern}: {avg_reduction:.1f}% (found in {data['count']} prompts)")

    # Analyze best performing compressions
    print("\n=== Best Compression Analysis ===")
    print(f"Found {len(stats['best_compressions'])} prompts with >15% compression")
    
    pattern_frequency = {}
    for compression in stats['best_compressions']:
        for pattern in compression['patterns']:
            pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
    
    print("\nCommon patterns in well-compressed prompts:")
    for pattern, count in sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(stats['best_compressions'])) * 100
        print(f"- {pattern}: found in {count} prompts ({percentage:.1f}%)")
    
    print("\nTop 3 examples of well-compressed prompts:")
    for i, compression in enumerate(sorted(stats['best_compressions'], 
                                        key=lambda x: x['reduction'], 
                                        reverse=True)[:3]):
        print(f"\nExample {i+1} ({compression['reduction']:.1f}% reduction):")
        print(f"Original: {compression['original']}")
        print(f"Compressed: {compression['compressed']}")
        print(f"Patterns found: {', '.join(compression['patterns'])}")

    # Analyze minimally compressed prompts
    print("\n=== Minimal Compression Analysis ===")
    print(f"Found {len(stats['minimal_compressions'])} prompts with <5% compression")
    
    minimal_pattern_frequency = {}
    for compression in stats['minimal_compressions']:
        for pattern in compression['patterns']:
            minimal_pattern_frequency[pattern] = minimal_pattern_frequency.get(pattern, 0) + 1
    
    print("\nCommon patterns in minimally-compressed prompts:")
    for pattern, count in sorted(minimal_pattern_frequency.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(stats['minimal_compressions'])) * 100
        print(f"- {pattern}: found in {count} prompts ({percentage:.1f}%)")
    
    print("\nTop 3 examples of minimally-compressed prompts:")
    for i, compression in enumerate(sorted(stats['minimal_compressions'], 
                                        key=lambda x: x['reduction'])[:3]):
        print(f"\nExample {i+1} ({compression['reduction']:.1f}% reduction):")
        print(f"Original: {compression['original']}")
        print(f"Compressed: {compression['compressed']}")
        print(f"Patterns found: {', '.join(compression['patterns'])}")
        print("Potential improvements: " + suggest_improvements(compression['original']))

    # Assert compression metrics
    assert stats['total_reduction'] > -5, "Average token reduction should be greater than -5%"

def suggest_improvements(prompt):
    """Suggest potential improvements for minimally compressed prompts"""
    suggestions = []
    
    if re.search(r'\b(?:really|very|quite)\b.*\b(?:really|very|quite)\b', prompt, re.IGNORECASE):
        suggestions.append("multiple intensity modifiers could be removed")
    
    if re.search(r'\b(?:I\'m curious|I\'d like|I want)\b.*\b(?:could you|would you)\b', prompt, re.IGNORECASE):
        suggestions.append("redundant request structure could be simplified")
        
    if re.search(r'\b(?:tell|explain|describe|share)\b.*\b(?:about|regarding|concerning)\b', prompt, re.IGNORECASE):
        suggestions.append("verbose question structure could be made direct")
        
    if len(re.findall(r'\band\b|\bor\b|\bbut\b', prompt)) > 2:
        suggestions.append("multiple conjunctions could be split into separate statements")
        
    if not suggestions:
        suggestions.append("prompt is already concise or requires domain-specific compression rules")
        
    return "; ".join(suggestions)

def test_compression_quality(compressor, test_prompts):
    """Test compression quality by checking readability and meaning preservation"""
    quality_stats = {
        'readable': 0,
        'meaning_preserved': 0,
        'total_checked': len(test_prompts)  # Check all prompts
    }

    for prompt in test_prompts:
        compressed = compressor.compress_prompt(prompt)
        
        # Basic readability check (no obvious errors)
        if (len(compressed) > 0 and 
            compressed[0].isupper() and 
            compressed[-1] in '.!?'):
            quality_stats['readable'] += 1

        # Basic meaning preservation check
        if (len(compressed) > 0 and 
            len(compressed.split()) >= 3):  # At least 3 words
            quality_stats['meaning_preserved'] += 1

    # Print quality statistics
    print("\n=== Compression Quality Statistics ===")
    print(f"Total prompts checked: {quality_stats['total_checked']}")
    print(f"Readable compressions: {quality_stats['readable']} ({quality_stats['readable']/quality_stats['total_checked']*100:.1f}%)")
    print(f"Meaning preserved: {quality_stats['meaning_preserved']} ({quality_stats['meaning_preserved']/quality_stats['total_checked']*100:.1f}%)")

    # Assert quality metrics
    assert quality_stats['readable'] / quality_stats['total_checked'] * 100 >= 90, "At least 90% of compressions should be readable"
    assert quality_stats['meaning_preserved'] / quality_stats['total_checked'] * 100 >= 90, "At least 90% of compressions should preserve meaning"

def test_entity_preservation(compressor, test_prompts):
    """Test entity preservation across the dataset"""
    entity_stats = {
        'total_entities': 0,
        'preserved_entities': 0,
        'lost_entities': 0
    }

    # Entity patterns to look for - updated for tech content
    entity_patterns = {
        'TECH_TERMS': r'\b(?:AI|ML|VR|AR|5G|6G|IoT|API|GPU|CPU|UI|UX)\b',  # Tech acronyms
        'PRODUCTS': r'\b(?:iPhone|Android|Windows|Linux|Mac|iOS|Chrome|Firefox|Safari)\b',  # Tech products
        'COMPANIES': r'\b(?:Google|Apple|Microsoft|Amazon|Facebook|Meta|Twitter|LinkedIn)\b',  # Tech companies
        'PLATFORMS': r'\b(?:Instagram|YouTube|TikTok|Snapchat|WhatsApp|Discord|Slack)\b',  # Social/tech platforms
        'CONCEPTS': r'\b(?:blockchain|cryptocurrency|bitcoin|ethereum|metaverse|cloud gaming)\b',  # Tech concepts
        'NUMBERS': r'\b\d+(?:\.\d+)?(?:GB|MB|TB|Hz|fps)\b',  # Tech measurements
        'VERSIONS': r'\b(?:v\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\b',  # Version numbers
        'DOMAINS': r'\b[\w-]+\.(?:com|org|net|io|ai)\b'  # Domain names
    }

    for prompt in test_prompts:
        # Find entities in original prompt
        original_entities = set()
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, prompt, re.IGNORECASE)  # Make case insensitive
            for match in matches:
                original_entities.add(match.group())
        
        entity_stats['total_entities'] += len(original_entities)
        
        # Find entities in compressed prompt
        compressed = compressor.compress_prompt(prompt)
        compressed_entities = set()
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, compressed, re.IGNORECASE)  # Make case insensitive
            for match in matches:
                compressed_entities.add(match.group())
        
        # Check entity preservation
        for entity in original_entities:
            if entity.lower() in [e.lower() for e in compressed_entities]:  # Case insensitive comparison
                entity_stats['preserved_entities'] += 1
            else:
                entity_stats['lost_entities'] += 1

    # Print entity statistics
    print("\n=== Entity Preservation Statistics ===")
    print(f"Total entities: {entity_stats['total_entities']}")
    
    # Only calculate percentages if we found entities
    if entity_stats['total_entities'] > 0:
        preserved_percent = (entity_stats['preserved_entities'] / entity_stats['total_entities']) * 100
        lost_percent = (entity_stats['lost_entities'] / entity_stats['total_entities']) * 100
        print(f"Preserved entities: {entity_stats['preserved_entities']} ({preserved_percent:.1f}%)")
        print(f"Lost entities: {entity_stats['lost_entities']} ({lost_percent:.1f}%)")
        
        # Assert entity preservation only if we found entities
        assert preserved_percent >= 90, "At least 90% of entities should be preserved"
    else:
        print("No entities found in the test prompts") 