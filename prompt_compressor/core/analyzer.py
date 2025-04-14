from typing import List, Dict, Any
import re
from .types import ContentType

class ContentAnalyzer:
    """Analyzes content for compression opportunities"""
    
    def __init__(self):
        self.patterns = {
            'hedging': r'\b(?:really|very|quite|somewhat|rather|fairly|pretty)\b',
            'redundant_phrases': r'\b(?:I think that|I believe that|in my opinion|from my perspective)\b',
            'polite_fillers': r'\b(?:if you could|if you would|if possible|if you don\'t mind)\b',
            'verbal_softeners': r'\b(?:just|maybe|perhaps|possibly|probably)\b',
            'empty_starters': r'\b(?:I was wondering|I wanted to ask|I would like to know)\b'
        }
        
        self.structural_patterns = {
            'indirect_questions': r'\b(?:Could you|Would you|Can you) (?:tell|explain|describe|share)\b',
            'self_references': r'\b(?:I\'m curious|I\'ve been thinking|I\'d like to know)\b',
            'redundant_context': r'\b(?:In the context of|When it comes to|With regards to)\b',
            'multiple_adjectives': r'\b(?:\w+\s+){2,}(?:way|approach|method|solution|idea)\b',
            'nested_clauses': r'\b(?:that is|which is|who are)\b.*\b(?:that|which|who)\b',
            'double_verbs': r'\b(?:try to|begin to|start to|seem to|appear to)\b',
            'passive_voice': r'\b(?:is|are|was|were)\s+(?:\w+ed|\w+en)\b',
            'meta_phrases': r'\b(?:the topic of|the concept of|the idea of|the process of)\b'
        }
    
    def detect_content_type(self, text: str) -> ContentType:
        """Detect the type of content in the text"""
        if not text.strip():
            return ContentType.TEXT
            
        # Check for code blocks
        if re.search(r'```[\s\S]*?```', text):
            return ContentType.CODE
            
        # Check for questions
        if re.search(r'\?$', text.strip()):
            return ContentType.QUESTION
            
        # Check for commands
        if re.search(r'^[A-Za-z0-9_]+:', text.strip()):
            return ContentType.COMMAND
            
        return ContentType.TEXT
    
    def find_pattern_matches(self, text: str) -> List[Dict[str, Any]]:
        """Find all pattern matches in the text"""
        matches = []
        all_patterns = {**self.patterns, **self.structural_patterns}
        
        for pattern_name, pattern in all_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append({
                    'pattern': pattern_name,
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return matches 