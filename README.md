# Mini LLVM Compiler

This is a small experiment I built to better understand how compilers work internally.

The program parses simple arithmetic expressions and generates LLVM IR using the Python LLVM bindings (llvmlite). The goal was mainly to explore the basic compiler pipeline and how source code can be transformed into an intermediate representation.

## What it does

The compiler currently supports simple arithmetic expressions with:

- integers
- +, -, *, /
- parentheses

Example input:

3 + 4 * 5

The program tokenizes the input, builds a small AST using a recursive descent parser, and then generates LLVM IR.

## Compiler Pipeline

The implementation roughly follows this flow:

source code  
→ tokens (lexer)  
→ AST (parser)  
→ LLVM IR generation

## Running

Install dependencies:

pip install -r requirements.txt

Run:

python mini_compiler.py

Then enter an expression when prompted.

## Why I built this

I wanted to experiment with the structure of a compiler and understand how parsing and intermediate representations work before exploring larger compiler infrastructures like LLVM.

## Possible Extensions

Some things I might try next:

- variables and a symbol table
- simple optimizations like constant folding
- more language constructs
