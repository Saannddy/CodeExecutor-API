import pytest
from src.core.security.sanitizer import sanitize_code

def test_sanitize_code_python_safe():
    code = """
import math
print("hello world")
"""
    result = sanitize_code("python", code)
    assert result["safe"] is True
    assert len(result["violations"]) == 0

def test_sanitize_code_python_regex_blacklist():
    code = """
import math
# A comment mentioning os.system
"""
    result = sanitize_code("python", code)
    assert result["safe"] is False
    assert any("Security policy violation prohibited code pattern detected." in v for v in result["violations"])

def test_sanitize_code_python_combined():
    code = """
import os
os.system('ls')
"""
    result = sanitize_code("python", code)
    assert result["safe"] is False
    assert any("Functionality or library not found in the allowed runtime environment." in v for v in result["violations"])
    assert any("Security policy violation prohibited code pattern detected." in v for v in result["violations"])

def test_sanitize_code_javascript_safe():
    code = """
console.log("Safe code");
"""
    result = sanitize_code("javascript", code)
    assert result["safe"] is True

def test_sanitize_code_javascript_blacklist():
    code = """
// use child_process
"""
    result = sanitize_code("javascript", code)
    assert result["safe"] is False
    assert any("Security policy violation prohibited code pattern detected." in v for v in result["violations"])

def test_sanitize_code_c_safe():
    code = """
#include <stdio.h>
int main() { printf("Hello"); return 0; }
"""
    result = sanitize_code("c", code)
    assert result["safe"] is True

def test_sanitize_code_c_blacklist():
    code = """
#include <stdio.h>
int main() {
    system("rm -rf /");
    return 0;
}
"""
    result = sanitize_code("c", code)
    assert result["safe"] is False
    assert any("Security policy violation prohibited code pattern detected." in v for v in result["violations"])

def test_sanitize_code_java_safe():
    code = """
import java.util.List;
public class Main {}
"""
    result = sanitize_code("java", code)
    assert result["safe"] is True

def test_sanitize_code_java_blacklist():
    code = """
import java.util.List;
public class Main {
    public void run() {
        ProcessBuilder builder = new ProcessBuilder();
    }
}
"""
    result = sanitize_code("java", code)
    assert result["safe"] is False
    assert any("Security policy violation prohibited code pattern detected." in v for v in result["violations"])
