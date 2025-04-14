def test_spacy_compression():
    """Test Spacy-based compression features"""
    compressor = PromptCompressor()
    
    # Test adjective compression
    text = "The beautiful amazing wonderful view"
    compressed = compressor.compress_prompt(text)
    assert "amazing" in compressed or "wonderful" in compressed, "Should keep strongest adjective"
    assert compressed.count(" ") < text.count(" "), "Should reduce number of adjectives"
    
    # Test adverb compression
    text = "This is very really quite good"
    compressed = compressor.compress_prompt(text)
    assert "good" in compressed, "Should keep the adjective"
    assert "very" not in compressed and "really" not in compressed, "Should remove weak adverbs"
    
    # Test prepositional phrase compression
    text = "In terms of the project, with regard to the timeline"
    compressed = compressor.compress_prompt(text)
    assert "In terms of" not in compressed, "Should remove redundant prepositional phrase"
    
    # Test relative clause compression
    text = "The book that I read yesterday which was very interesting"
    compressed = compressor.compress_prompt(text)
    assert "that I read yesterday" not in compressed, "Should remove non-essential relative clause"
    
    # Test entity preservation
    text = "Apple Inc. released a new iPhone in California"
    compressed = compressor.compress_prompt(text)
    assert "Apple Inc." in compressed and "California" in compressed, "Should preserve named entities"

def test_spacy_configuration():
    """Test Spacy compression configuration options"""
    # Test disabling all Spacy compression
    compressor = PromptCompressor(spacy_config={'enabled': False})
    text = "The very beautiful amazing view"
    compressed = compressor.compress_prompt(text)
    assert compressed == text, "Should not apply any Spacy compression"
    
    # Test disabling specific features
    compressor = PromptCompressor(spacy_config={
        'compress_adjectives': False,
        'compress_adverbs': False
    })
    text = "The very beautiful amazing view"
    compressed = compressor.compress_prompt(text)
    assert "very" in compressed and "beautiful" in compressed and "amazing" in compressed, "Should preserve adjectives and adverbs"
    
    # Test entity preservation toggle
    compressor = PromptCompressor(spacy_config={'preserve_entities': False})
    text = "Apple Inc. released a new iPhone"
    compressed = compressor.compress_prompt(text)
    assert "Apple Inc." not in compressed, "Should not preserve entities when disabled"

def test_spacy_compression_quality():
    """Test the quality of Spacy-based compression"""
    compressor = PromptCompressor()
    
    # Test readability
    text = "The very beautiful amazing view that I saw yesterday was really quite spectacular"
    compressed = compressor.compress_prompt(text)
    assert compressed[0].isupper(), "Should maintain capitalization"
    assert compressed[-1] in ".!?", "Should maintain sentence ending"
    assert len(compressed.split()) >= 3, "Should maintain minimum word count"
    
    # Test meaning preservation
    text = "You must complete the task that is assigned to you"
    compressed = compressor.compress_prompt(text)
    assert "must" in compressed, "Should preserve important modal verbs"
    assert "task" in compressed, "Should preserve key nouns"
    
    # Test natural language flow
    text = "The project that we discussed yesterday needs to be completed by Friday"
    compressed = compressor.compress_prompt(text)
    assert compressed.split()[0] == "The", "Should maintain article"
    assert "needs" in compressed, "Should preserve main verb"
    assert "Friday" in compressed, "Should preserve important time reference" 