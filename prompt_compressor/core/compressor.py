from typing import Dict, List, Any, Optional, Union
import re
import yaml
import tiktoken
from pathlib import Path
import spacy

class PromptCompressor:
    """Compresses prompts while preserving semantic meaning"""
    
    def __init__(self, rules_file=None):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.rules = self._load_rules(rules_file) if rules_file else {}
        self.placeholder_counter = 0
        self.placeholders = {}
        
        # Load Spacy model for advanced compression
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading Spacy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Common contractions to preserve
        self.contractions = {
            "I'm": "I_am", "I've": "I_have", "I'll": "I_will", "I'd": "I_would",
            "you're": "you_are", "you've": "you_have", "you'll": "you_will",
            "he's": "he_is", "she's": "she_is", "it's": "it_is",
            "we're": "we_are", "we've": "we_have", "we'll": "we_will",
            "they're": "they_are", "they've": "they_have", "they'll": "they_will",
            "that's": "that_is", "what's": "what_is", "where's": "where_is",
            "don't": "do_not", "won't": "will_not", "can't": "cannot",
            "shouldn't": "should_not", "wouldn't": "would_not", "couldn't": "could_not",
            "hasn't": "has_not", "haven't": "have_not", "hadn't": "had_not"
        }
    
    def _load_rules(self, rules_file):
        if not rules_file:
            return {}
        with open(rules_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _preserve_entities(self, text):
        # Reset placeholders for each new compression
        self.placeholders = {}
        self.placeholder_counter = 0
        
        # First preserve contractions
        for contraction, replacement in self.contractions.items():
            # Use word boundaries to ensure we match whole words only
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', replacement, text)
        
        # Preserve quoted text and technical terms
        def replace_with_placeholder(match):
            self.placeholder_counter += 1
            placeholder = f"PLACEHOLDER_{self.placeholder_counter}"
            self.placeholders[placeholder] = match.group(0)
            return placeholder
        
        # Preserve quoted text
        text = re.sub(r'"[^"]*"', replace_with_placeholder, text)
        text = re.sub(r"'[^']*'", replace_with_placeholder, text)
        
        return text

    def _restore_entities(self, text):
        # Restore placeholders
        for placeholder, original in self.placeholders.items():
            text = text.replace(placeholder, original)
            
        # Restore contractions
        for contraction, replacement in self.contractions.items():
            # Use word boundaries to ensure we match whole words only
            text = re.sub(r'\b' + re.escape(replacement) + r'\b', contraction, text)
            
        return text

    def _apply_rules(self, text, rule_group):
        """Apply compression rules from a specific rule group to the text."""
        if not self.rules.get('rule_groups', {}).get(rule_group, {}).get('enabled', False):
            return text

        patterns = self.rules.get('rule_groups', {}).get(rule_group, {}).get('patterns', [])
        
        for pattern_obj in patterns:
            pattern = pattern_obj.get('pattern', '')
            replacement = pattern_obj.get('replacement', '')
            
            if not pattern:
                continue
                
            # Handle regex patterns (those starting with \)
            if pattern.startswith('\\'):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            else:
                # For literal patterns, escape special characters and make case insensitive
                escaped_pattern = re.escape(pattern)
                text = re.sub(f'\\b{escaped_pattern}\\b', replacement, text, flags=re.IGNORECASE)
        
        return text.strip()

    def _spacy_compress(self, text: str) -> str:
        """Apply Spacy-based compression rules while preserving important information"""
        # First, preserve contractions and compound words
        text = self._preserve_entities(text)
        
        # Check if this is a question
        is_question = text.strip().endswith('?')
        
        doc = self.nlp(text)
        compressed_tokens = []
        sentences = list(doc.sents)
        
        for i, sent in enumerate(sentences):
            # Process each sentence
            tokens_to_keep = []
            important_entities = set()
            compound_words = set()
            question_words = set()
            
            # First pass: Identify important entities, compounds, and question words
            for token in sent:
                # Keep all named entities
                if token.ent_type_:
                    important_entities.add(token.text)
                    # Also keep the entity's immediate context
                    for child in token.children:
                        if child.dep_ in ['amod', 'compound', 'nummod']:
                            important_entities.add(child.text)
                
                # Identify and preserve compound words
                if token.dep_ == 'compound':
                    compound = f"{token.text} {token.head.text}"
                    compound_words.add(compound)
                    important_entities.add(token.text)
                    important_entities.add(token.head.text)
                
                # Preserve hyphenated compounds
                if '-' in token.text and len(token.text.split('-')) == 2:
                    compound_words.add(token.text)
                    important_entities.add(token.text)
                
                # Identify question words and their context
                if token.text.lower() in ['how', 'what', 'when', 'where', 'why', 'who', 'which']:
                    question_words.add(token.text)
                    # Keep the question word's context
                    for child in token.children:
                        if child.dep_ in ['attr', 'acomp', 'dobj']:
                            question_words.add(child.text)
            
            # Second pass: Process tokens with entity awareness
            for token in sent:
                # Always keep important entities and their context
                if token.text in important_entities or token.text in question_words:
                    tokens_to_keep.append(token.text)
                    continue
                
                # Keep numbers and measurements
                if token.like_num or token.text.replace('.', '').isdigit():
                    tokens_to_keep.append(token.text)
                    continue
                
                # Keep technical terms and compounds
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    (any(c.isupper() for c in token.text) or 
                     any(compound.startswith(token.text) for compound in compound_words)) and 
                    len(token.text) > 1):
                    tokens_to_keep.append(token.text)
                    continue
                
                # Skip unnecessary modifiers only if they're not part of important phrases
                if (token.pos_ in ['ADV'] and 
                    token.dep_ in ['advmod'] and 
                    not any(child.text in important_entities for child in token.children)):
                    if not any(child.dep_ in ['neg'] for child in token.children):
                        continue
                
                # Skip redundant determiners only if they're not part of important phrases
                if (token.pos_ == 'DET' and 
                    token.dep_ == 'det' and 
                    len(list(token.head.children)) > 1 and
                    token.head.text not in important_entities):
                    continue
                
                # Keep content words and important grammatical roles
                if (token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN'] or  # Content words
                    token.dep_ in ['nsubj', 'dobj', 'pobj', 'attr', 'acomp'] or  # Important roles
                    token.ent_type_):  # Named entities
                    tokens_to_keep.append(token.text)
                elif token.pos_ in ['PRON', 'AUX', 'ADP', 'CCONJ']:  # Keep function words
                    tokens_to_keep.append(token.text)
            
            if tokens_to_keep:
                # Add sentence end only if it's a complete sentence
                if any(token.pos_ in ['VERB'] for token in sent):
                    compressed_tokens.extend(tokens_to_keep)
                    # Preserve question mark if original was a question and this is the last sentence
                    if is_question and i == len(sentences) - 1:
                        compressed_tokens.append('?')
                    else:
                        compressed_tokens.append('.')
        
        # Join tokens and clean up
        compressed = ' '.join(compressed_tokens)
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        # Fix punctuation spacing - remove spaces before punctuation
        compressed = re.sub(r'\s+([.,!?])', r'\1', compressed)
        
        # Calculate compression ratio
        original_tokens = len(self.encoding.encode(text))
        compressed_tokens = len(self.encoding.encode(compressed))
        compression_ratio = (original_tokens - compressed_tokens) / original_tokens * 100
        
        # If compression is high (>15%), apply additional entity preservation
        if compression_ratio > 15:
            # Preserve more entity types
            doc = self.nlp(compressed)
            preserved_tokens = []
            
            for token in doc:
                # Keep more entity types
                if (token.ent_type_ in ['ORG', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW'] or
                    token.pos_ in ['NOUN', 'PROPN'] and any(c.isupper() for c in token.text)):
                    preserved_tokens.append(token.text)
                else:
                    preserved_tokens.append(token.text)
            
            compressed = ' '.join(preserved_tokens)
            # Fix punctuation spacing again after entity preservation
            compressed = re.sub(r'\s+([.,!?])', r'\1', compressed)
        
        # Restore contractions and other preserved entities
        compressed = self._restore_entities(compressed)
        
        return compressed

    def compress(self, text):
        """Compress the input text using all enabled rule groups."""
        if not text:
            return text
        
        # First pass: Apply regex-based rules
        compressed = text
        rule_groups = [
            'remove_greetings',
            'remove_fillers',
            'strip_modifiers',
            'collapse_phrases',
            'punctuation_compression',
            'sentence_compression'
        ]
        
        for group in rule_groups:
            compressed = self._apply_rules(compressed, group)
        
        # Second pass: Apply Spacy-based compression
        compressed = self._spacy_compress(compressed)
        
        # Ensure we don't return empty strings
        if not compressed.strip():
            return text
        
        # Clean up any extra whitespace
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        return compressed

    def analyze_prompt(self, text):
        if not text or not text.strip():
            return {
                'original_text': text,
                'compressed_text': text,
                'original_tokens': 0,
                'compressed_tokens': 0,
                'compression_ratio': 0
            }
            
        compressed = self.compress(text)
        
        # Count tokens using tiktoken
        original_tokens = len(self.encoding.encode(text))
        compressed_tokens = len(self.encoding.encode(compressed))
        
        # Calculate compression ratio
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = (tokens_saved / original_tokens) * 100 if original_tokens > 0 else 0
        
        return {
            'original_text': text,
            'compressed_text': compressed,
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'compression_ratio': compression_ratio
        } 