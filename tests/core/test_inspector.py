import pytest
from src.core.security.inspector import (
    inspect_python,
    inspect_javascript,
    inspect_java,
    inspect_c_cpp
)

def test_inspect_python_safe():
    code = """
import math
from collections import defaultdict

def solve():
    return math.sqrt(16)
"""
    result = inspect_python(code)
    assert result["safe"] is True
    assert len(result["violations"]) == 0

def test_inspect_python_unsafe_module():
    code = """
import os
"""
    result = inspect_python(code)
    assert result["safe"] is False
    assert "Import 'os' is not whitelisted" in result["violations"]

def test_inspect_python_unsafe_call():
    code = "eval('print(1)')"
    result = inspect_python(code)
    assert result["safe"] is False
    assert "Call to 'eval()' is not allowed" in result["violations"]

def test_inspect_javascript_safe():
    code = """
const x = 10;
console.log(Math.max(x, 20));
"""
    result = inspect_javascript(code)
    assert result["safe"] is True

def test_inspect_javascript_unsafe_require():
    code = "const fs = require('fs');"
    result = inspect_javascript(code)
    assert result["safe"] is False
    assert any("fs" in v for v in result["violations"])

def test_inspect_javascript_unsafe_eval():
    code = "eval('1+1');"
    result = inspect_javascript(code)
    assert result["safe"] is False
    assert any("eval" in v for v in result["violations"])

def test_inspect_java_safe():
    code = """
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
    result = inspect_java(code)
    assert result["safe"] is True

def test_inspect_java_unsafe_import():
    code = """
import java.io.File;
"""
    result = inspect_java(code)
    assert result["safe"] is False
    assert any("java.io.File" in v for v in result["violations"])

def test_inspect_java_unsafe_runtime():
    code = """
public class Main {
    public static void main(String[] args) {
        Runtime.getRuntime().exec("sh");
    }
}
"""
    result = inspect_java(code)
    assert result["safe"] is False
    assert "Runtime.exec() is not allowed" in result["violations"]

def test_inspect_c_cpp_safe():
    code = """
#include <stdio.h>
#include <iostream>

int main() {
    return 0;
}
"""
    result = inspect_c_cpp(code)
    assert result["safe"] is True

def test_inspect_c_cpp_unsafe():
    code = """
#include <unistd.h>
"""
    result = inspect_c_cpp(code)
    assert result["safe"] is False
    assert any("unistd.h" in v for v in result["violations"])
