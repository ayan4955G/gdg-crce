# Re:Learn — Programming Misconception Taxonomy

## 1. Overview
The taxonomy models 10 fundamental cognitive hurdles encountered in introductory Python programming (`P001` through `P010`). Each concept maps concrete AST structural patterns, runtime symptoms, and counterexample strategies.

| ID | Misconception Name | Core Concept | Distinguishing Anti-Pattern |
|---|---|---|---|
| **P001** | Variable Assignment Confusion | Variables | Left-hand expression assignment (`x + 1 = y`) or symmetric state coupling assumption |
| **P002** | Variable Scope Confusion | Functions & Scope | Accessing local variables after activation frame destruction |
| **P003** | Loop Boundary / Off-by-One | Loops | Treating exclusive bounds `range(start, stop)` as inclusive intervals `[start, stop]` |
| **P004** | Loop Condition Misunderstanding | Loops | Assuming mid-body termination instead of header evaluation |
| **P005** | Conditional Logic Misunderstanding | Conditionals | Using independent `if` statements assuming mutually exclusive `if-elif-else` branches |
| **P006** | Boolean Operator Misunderstanding | Conditionals & Booleans | Natural language formulation: `x == 1 or 2` (truthy constant) |
| **P007** | Return vs Print Confusion | Functions & Scope | Void function terminating in `print()`, assigning `None` to caller expressions |
| **P008** | Parameter vs Argument Confusion | Functions & Scope | Forcing argument variable names to match formal parameter definitions |
| **P009** | List/Array Indexing Misunderstanding | Lists & Indexing | Confusing 1-based ordinal position with 0-based indices or element value with index |
| **P010** | Mutable State / Reference Confusion | Data Structures | Believing list assignment (`b = a`) creates an isolated deep copy |
