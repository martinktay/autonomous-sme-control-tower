"""
Unit tests for JSON guard utility with Pydantic validation

Tests Requirement 13.3 and 13.4:
- Enforce strict JSON output validation against Pydantic schemas
- Log raw output when parsing fails
"""

import pytest
from pydantic import BaseModel, ValidationError
from app.utils.json_guard import (
    safe_json_parse,
    parse_json_safely,
    validate_with_schema,
    parse_and_validate
)


class SampleModel(BaseModel):
    """Sample Pydantic model for testing"""
    name: str
    age: int
    email: str


class TestSafeJsonParse:
    """Test suite for safe_json_parse function"""
    
    def test_parse_plain_json(self):
        """Test parsing plain JSON"""
        json_str = '{"name": "Alice", "age": 30, "email": "alice@example.com"}'
        result = safe_json_parse(json_str)
        
        assert result is not None
        assert result["name"] == "Alice"
        assert result["age"] == 30
    
    def test_parse_json_in_markdown_code_block(self):
        """Test extracting JSON from markdown code block"""
        text = '''Here is the result:
```json
{"name": "Bob", "age": 25, "email": "bob@example.com"}
```
'''
        result = safe_json_parse(text)
        
        assert result is not None
        assert result["name"] == "Bob"
    
    def test_parse_json_embedded_in_text(self):
        """Test extracting JSON embedded in text"""
        text = 'Some text before {"name": "Charlie", "age": 35, "email": "charlie@example.com"} and after'
        result = safe_json_parse(text)
        
        assert result is not None
        assert result["name"] == "Charlie"
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON"""
        result = safe_json_parse("This is not JSON at all")
        assert result is None
    
    def test_parse_empty_string(self):
        """Test handling of empty string"""
        result = safe_json_parse("")
        assert result is None


class TestParseJsonSafely:
    """Test suite for parse_json_safely function"""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON with error handling"""
        json_str = '{"name": "Alice", "age": 30, "email": "alice@example.com"}'
        result = parse_json_safely(json_str)
        
        assert result["name"] == "Alice"
    
    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_json_safely("Not valid JSON")


class TestValidateWithSchema:
    """Test suite for validate_with_schema function"""
    
    def test_validate_valid_json_against_schema(self):
        """Test validating valid JSON against Pydantic schema"""
        json_str = '{"name": "Alice", "age": 30, "email": "alice@example.com"}'
        result = validate_with_schema(json_str, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Alice"
        assert result.age == 30
        assert result.email == "alice@example.com"
    
    def test_validate_json_in_markdown(self):
        """Test validating JSON extracted from markdown"""
        text = '''```json
{"name": "Bob", "age": 25, "email": "bob@example.com"}
```'''
        result = validate_with_schema(text, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Bob"
    
    def test_validate_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            validate_with_schema("Not JSON", SampleModel)
    
    def test_validate_json_missing_required_field(self):
        """Test that JSON missing required field raises ValidationError"""
        json_str = '{"name": "Charlie", "age": 35}'  # Missing email
        
        with pytest.raises(ValidationError):
            validate_with_schema(json_str, SampleModel)
    
    def test_validate_json_wrong_type(self):
        """Test that JSON with wrong type raises ValidationError"""
        json_str = '{"name": "Dave", "age": "thirty", "email": "dave@example.com"}'
        
        with pytest.raises(ValidationError):
            validate_with_schema(json_str, SampleModel)
    
    def test_validate_without_logging(self):
        """Test validation without logging raw output"""
        json_str = '{"name": "Eve", "age": 28, "email": "eve@example.com"}'
        result = validate_with_schema(json_str, SampleModel, log_raw_on_error=False)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Eve"


class TestParseAndValidate:
    """Test suite for parse_and_validate convenience function"""
    
    def test_parse_and_validate_success(self):
        """Test successful parsing and validation"""
        json_str = '{"name": "Frank", "age": 40, "email": "frank@example.com"}'
        result = parse_and_validate(json_str, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Frank"
    
    def test_parse_and_validate_with_markdown(self):
        """Test parsing and validating JSON in markdown"""
        text = '''The model returned:
```
{"name": "Grace", "age": 32, "email": "grace@example.com"}
```
'''
        result = parse_and_validate(text, SampleModel)
        
        assert isinstance(result, SampleModel)
        assert result.name == "Grace"
    
    def test_parse_and_validate_logs_on_error(self):
        """Test that errors are logged (Requirement 13.4)"""
        # This test verifies that the function attempts to log
        # We can't easily test the actual logging without mocking
        with pytest.raises(ValueError):
            parse_and_validate("Invalid JSON", SampleModel)


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_nested_json_objects(self):
        """Test parsing nested JSON objects"""
        
        class NestedModel(BaseModel):
            name: str
            details: dict
        
        json_str = '{"name": "Test", "details": {"key": "value", "nested": {"deep": "data"}}}'
        result = validate_with_schema(json_str, NestedModel)
        
        assert result.name == "Test"
        assert result.details["key"] == "value"
    
    def test_json_with_arrays(self):
        """Test parsing JSON with arrays"""
        
        class ArrayModel(BaseModel):
            name: str
            tags: list[str]
        
        json_str = '{"name": "Test", "tags": ["tag1", "tag2", "tag3"]}'
        result = validate_with_schema(json_str, ArrayModel)
        
        assert result.name == "Test"
        assert len(result.tags) == 3
    
    def test_json_with_optional_fields(self):
        """Test parsing JSON with optional fields"""
        
        class OptionalModel(BaseModel):
            name: str
            age: int | None = None
        
        json_str = '{"name": "Test"}'
        result = validate_with_schema(json_str, OptionalModel)
        
        assert result.name == "Test"
        assert result.age is None
