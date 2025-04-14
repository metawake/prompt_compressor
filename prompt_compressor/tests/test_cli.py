import pytest
from typer.testing import CliRunner
from prompt_compressor.cli import app
from prompt_compressor import PromptCompressor
import json
from pathlib import Path
import tempfile
import os

runner = CliRunner()

@pytest.fixture
def sample_prompt():
    return "I'm really curious about how this works. Could you please explain it to me in a very simple way?"

@pytest.fixture
def mock_compressor(mocker):
    """Mock the PromptCompressor for CLI tests"""
    mock = mocker.Mock(spec=PromptCompressor)
    
    # Define behavior for normal prompts
    mock.compress_prompt.return_value = "compressed prompt"
    mock.get_token_count.return_value = 10
    mock.analyze_prompt.return_value = {
        'content_type': 'text',
        'token_count': 10,
        'pattern_matches': [{'pattern': 'test', 'match': 'test'}]
    }
    
    # Define behavior for empty prompts
    def compress_side_effect(text):
        return "" if not text.strip() else "compressed prompt"
    
    def token_count_side_effect(text):
        return 0 if not text.strip() else 10
    
    def analyze_side_effect(text):
        if not text.strip():
            return {
                'content_type': 'text',
                'token_count': 0,
                'pattern_matches': []
            }
        return {
            'content_type': 'text',
            'token_count': 10,
            'pattern_matches': [{'pattern': 'test', 'match': 'test'}]
        }
    
    mock.compress_prompt.side_effect = compress_side_effect
    mock.get_token_count.side_effect = token_count_side_effect
    mock.analyze_prompt.side_effect = analyze_side_effect
    
    return mock

def test_compress_basic(mock_compressor, mocker):
    """Test basic compression command"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["compress", "test prompt"])
    assert result.exit_code == 0
    assert "compressed prompt" in result.output

def test_compress_verbose(mock_compressor, mocker):
    """Test verbose compression output"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["compress", "test prompt", "--verbose"])
    assert result.exit_code == 0
    assert "Original prompt: test prompt" in result.output
    assert "Compressed prompt: compressed prompt" in result.output
    assert "Token count: 10 -> 10" in result.output

def test_compress_with_rules(mock_compressor, mocker):
    """Test compression with custom rules"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["compress", "test prompt", "--rules", "rules.yaml"])
    assert result.exit_code == 0
    mock_compressor.assert_called_once()

def test_compress_output_file(mock_compressor, mocker, tmp_path):
    """Test compression with output file"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    output_file = tmp_path / "output.json"
    result = runner.invoke(app, ["compress", "test prompt", "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()

def test_analyze_basic(mock_compressor, mocker):
    """Test basic analyze command"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["analyze", "test prompt"])
    assert result.exit_code == 0
    assert "Content type: text" in result.output
    assert "Token count: 10" in result.output

def test_analyze_with_rules(mock_compressor, mocker):
    """Test analyze with custom rules"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["analyze", "test prompt", "--rules", "rules.yaml"])
    assert result.exit_code == 0
    mock_compressor.assert_called_once()

def test_compress_error_handling(mock_compressor, mocker):
    """Test error handling in compress command"""
    mock_compressor.compress_prompt.side_effect = Exception("Test error")
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["compress", "test prompt"])
    assert result.exit_code == 1
    assert "Error" in result.output

def test_analyze_error_handling(mock_compressor, mocker):
    """Test error handling in analyze command"""
    mock_compressor.analyze_prompt.side_effect = Exception("Test error")
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["analyze", "test prompt"])
    assert result.exit_code == 1
    assert "Error" in result.output

def test_compress_empty_prompt(mock_compressor, mocker):
    """Test handling of empty prompts in compress command"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["compress", ""])
    assert result.exit_code == 0
    assert "Original prompt: (empty)" in result.output
    assert "Compressed prompt: (empty)" in result.output

def test_analyze_empty_prompt(mock_compressor, mocker):
    """Test handling of empty prompts in analyze command"""
    mocker.patch('prompt_compressor.cli.PromptCompressor', return_value=mock_compressor)
    result = runner.invoke(app, ["analyze", ""])
    assert result.exit_code == 0
    assert "Content type: text" in result.output
    assert "Token count: 0" in result.output 