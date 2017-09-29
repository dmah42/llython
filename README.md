# llython
LLVM IR generation for Python

Uses llvmlite to generate LLVM IR from the Python AST.

## Example
```python
c = 42
b = 64
a = b
```

Generates

```
; ModuleID = "example/assign.py"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define void @"module_fn"() 
{
top-level:
  %"c" = alloca double
  store double 0x4045000000000000, double* %"c"
  %"b" = alloca double
  store double 0x4050000000000000, double* %"b"
  %"b.1" = load double, double* %"b"
  %"a" = alloca double
  store double %"b.1", double* %"a"
}
```
