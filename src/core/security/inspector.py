import ast
import re

try:
    import esprima
    _HAS_ESPRIMA = True
except ImportError:
    _HAS_ESPRIMA = False

try:
    import javalang
    _HAS_JAVALANG = True
except ImportError:
    _HAS_JAVALANG = False

# ── Python Whitelist ──
PYTHON_ALLOWED_MODULES = {
    'math', 'cmath', 'collections', 'itertools', 'functools',
    'heapq', 'bisect', 'decimal', 'fractions', 'string',
    'sys', 'copy', 'operator', 'typing', 'dataclasses',
    'enum', 'abc', 'array', 'queue', 'statistics',
    'random', 'datetime', 'time', 'io', 'textwrap',
    'numbers', 'contextlib', 'pprint', 'struct', 'hashlib',
    'base64', 'binascii', 'unicodedata', 'calendar', 'zlib',
    're', 'json', 'sortedcontainers',
}

PYTHON_BLOCKED_CALLS = {
    'eval', 'exec', 'compile', '__import__', 'open',
    'globals', 'locals', 'breakpoint', 'getattr', 'setattr',
    'delattr', 'vars',
}

def inspect_python(code):
    violations = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"safe": True, "violations": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split('.')[0]
                if root not in PYTHON_ALLOWED_MODULES:
                    violations.append(f"Import '{alias.name}' is not whitelisted")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split('.')[0]
                if root not in PYTHON_ALLOWED_MODULES:
                    violations.append(f"Import from '{node.module}' is not whitelisted")
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in PYTHON_BLOCKED_CALLS:
                violations.append(f"Call to '{node.func.id}()' is not allowed")
                
    return {"safe": len(violations) == 0, "violations": violations}

# ── JavaScript Whitelist ──
JS_BLOCKED_REQUIRES = {
    'fs', 'child_process', 'net', 'http', 'https', 'dgram',
    'os', 'vm', 'cluster', 'worker_threads', 'path',
    'tls', 'dns', 'readline', 'repl', 'v8', 'inspector',
    'perf_hooks', 'async_hooks', 'trace_events', 'crypto',
}

def _walk_esprima(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk_esprima(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_esprima(item)

def inspect_javascript(code):
    if not _HAS_ESPRIMA:
        return {"safe": True, "violations": []}
        
    violations = []
    try:
        tree = esprima.parseScript(code).toDict()
    except Exception:
        return {"safe": True, "violations": []}

    for node in _walk_esprima(tree):
        if not isinstance(node, dict) or 'type' not in node:
            continue
            
        if node['type'] == 'CallExpression':
            callee = node.get('callee', {})
            if callee.get('type') == 'Identifier' and callee.get('name') == 'require':
                args = node.get('arguments', [])
                if args and args[0].get('type') == 'Literal':
                    mod = args[0].get('value', '')
                    if mod in JS_BLOCKED_REQUIRES or mod not in ('', None):
                        violations.append(f"require('{mod}') is not whitelisted")
            
            if callee.get('type') == 'Identifier' and callee.get('name') in ('eval', 'Function'):
                violations.append(f"{callee.get('name')}() is not allowed")
                
        if node['type'] == 'MemberExpression':
            obj = node.get('object', {})
            prop = node.get('property', {})
            if obj.get('name') == 'process' and prop.get('name') in ('env', 'exit', 'kill', 'pid', 'cwd'):
                violations.append(f"process.{prop.get('name')} is not allowed")
                
    return {"safe": len(violations) == 0, "violations": violations}

# ── Java Whitelist ──
JAVA_ALLOWED_PACKAGES = {'java.util', 'java.lang', 'java.math', 'java.text', 'java.time'}
JAVA_ALLOWED_IO_CLASSES = {
    'java.io.BufferedReader', 'java.io.InputStreamReader', 'java.io.PrintWriter',
    'java.io.IOException', 'java.io.StreamTokenizer', 'java.io.OutputStream',
    'java.io.InputStream', 'java.io.StringReader', 'java.io.StringWriter',
    'java.io.ByteArrayInputStream', 'java.io.ByteArrayOutputStream',
}

def inspect_java(code):
    if not _HAS_JAVALANG:
        return {"safe": True, "violations": []}
        
    violations = []
    try:
        tree = javalang.parse.parse(code)
    except Exception:
        return {"safe": True, "violations": []}

    for imp in (tree.imports or []):
        clean = imp.path.rstrip('.*').rstrip('.')
        is_allowed = clean in JAVA_ALLOWED_IO_CLASSES
        if not is_allowed:
            for pkg in JAVA_ALLOWED_PACKAGES:
                if clean == pkg or clean.startswith(pkg + '.'):
                    is_allowed = True
                    break
        
        if not is_allowed:
            violations.append(f"Import '{imp.path}' is not whitelisted")

    for _, node in tree.filter(javalang.tree.MethodInvocation):
        if node.qualifier == 'Runtime' or (node.member == 'exec' and node.qualifier):
            violations.append("Runtime.exec() is not allowed")
        if node.qualifier == 'System' and node.member in ('exit', 'getenv', 'getProperty'):
            violations.append(f"System.{node.member}() is not allowed")

    for _, node in tree.filter(javalang.tree.ClassCreator):
        type_name = node.type.name if node.type else ''
        blocked_classes = (
            'ProcessBuilder', 'File', 'FileInputStream', 'FileOutputStream', 
            'FileReader', 'FileWriter', 'Socket', 'ServerSocket', 
            'URL', 'HttpURLConnection', 'DatagramSocket'
        )
        if type_name in blocked_classes:
            violations.append(f"new {type_name}() is not allowed")
            
    return {"safe": len(violations) == 0, "violations": violations}

# ── C / C++ Whitelist ──
C_CPP_ALLOWED_HEADERS = {
    'stdio.h', 'stdlib.h', 'string.h', 'math.h', 'ctype.h', 'limits.h', 
    'float.h', 'stddef.h', 'stdbool.h', 'stdint.h', 'assert.h', 'errno.h', 
    'time.h', 'stdarg.h', 'inttypes.h', 'wchar.h', 'wctype.h', 'complex.h', 
    'tgmath.h', 'iso646.h',
    'iostream', 'iomanip', 'sstream', 'string', 'vector', 'list', 'deque', 
    'array', 'forward_list', 'stack', 'queue', 'set', 'map', 'priority_queue', 
    'unordered_set', 'unordered_map', 'bitset', 'tuple', 'utility', 
    'optional', 'variant', 'any', 'algorithm', 'numeric', 'functional', 
    'iterator', 'memory', 'regex', 'initializer_list', 'type_traits', 
    'typeinfo', 'exception', 'stdexcept', 'random', 'chrono', 'valarray', 
    'complex', 'span',
    'climits', 'cmath', 'cstring', 'cstdlib', 'cstdio', 'cctype', 
    'cassert', 'cerrno', 'cfloat', 'cstddef', 'cstdint', 'ctime', 
    'cwchar', 'cwctype',
}

def inspect_c_cpp(code):
    violations = []
    for match in re.finditer(r'#\s*include\s*[<"]([^>"]+)[>"]', code):
        header = match.group(1)
        if header not in C_CPP_ALLOWED_HEADERS:
            violations.append(f"#include <{header}> is not whitelisted")
    return {"safe": len(violations) == 0, "violations": violations}

INSPECTORS = {
    "python": inspect_python,
    "javascript": inspect_javascript,
    "c": inspect_c_cpp,
    "cpp": inspect_c_cpp,
    "java": inspect_java,
}
