from os import system
import os
from tokens import *
from token_class import Token
from constants import *
from error_class import *
from position_class import *

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def analyze(self, tokens):
        temp_tokens = []
        found_onboard = False
        for token in tokens:
            if token.type == TT_ONBOARD:
                found_onboard = True
            if found_onboard:
                temp_tokens.append(token)
            if token.type == TT_OFFBOARD:
                break
        tokens = [token for token in temp_tokens if token.type not in [TT_SLCOMMENT, TT_MLCOMMENT]]
        grouped_tokens = group_tokens_by_line(tokens)
        for line_number, line_tokens in grouped_tokens.items():
            line_type = analyze_line(line_tokens)
            if line_type == "SINGLE_VARIABLE_DECLARATION":
                variable_name = line_tokens[1].value
                variable_type = line_tokens[0].type
                if variable_name in self.symbol_table:
                    self.errors.append(f"Redeclaration Error: Variable '{variable_name}' is already declared. (line {line_number})")
                else:
                    self.symbol_table[variable_name] = {"type": variable_type, "function": False}
            elif line_type == "MULTIPLE_VARIABLE_DECLARATION":
                variable_type = line_tokens[0].type
                i = 2  
                while i < len(line_tokens):
                    if line_tokens[i].type == TT_ASSIGN:
                        variable_name = line_tokens[i - 1].value 
                        if variable_name in self.symbol_table:
                            self.errors.append(f"Redeclaration Error: Variable '{variable_name}' is already declared. (line {line_number})")
                        else:
                            self.symbol_table[variable_name] = {"type": variable_type, "function": False}
                    i += 1
            print(f"Line {line_number} has type: {line_type}")
        print(self.symbol_table)
        if self.errors:
            for error in self.errors:
                print(error)
        else:
            print("Semantic analysis successful")

def analyze(tokens):
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.analyze(tokens)

def group_tokens_by_line(tokens):
    grouped_tokens = {}
    for token in tokens:
        line_number = token.line_number
        if line_number not in grouped_tokens:
            grouped_tokens[line_number] = []
        grouped_tokens[line_number].append(token)
    return grouped_tokens

def analyze_line(tokens):
    if len(tokens) == 1 and tokens[0].type == TT_ONBOARD:
        return "ONBOARD_STATEMENT"
    elif len(tokens) == 1 and tokens[0].type == TT_OFFBOARD:
        return "OFFBOARD_STATEMENT"
    elif tokens[0].type == TT_LOYAL:
        return "LOYAL_STATEMENT"
    elif tokens[0].type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL] and tokens[2].type == TT_ASSIGN:
        assign_count = sum(1 for token in tokens if token.type == TT_ASSIGN)
        if assign_count > 1:
            return "MULTIPLE_VARIABLE_DECLARATION"
        else:
            return "SINGLE_VARIABLE_DECLARATION"
    elif tokens[0].type == TT_IDTFR and tokens[1].type == TT_ASSIGN:
        return "VARIABLE_ASSIGNMENT"
    elif tokens[0].type == TT_CAPTAIN:
        return "CAPTAIN_DEFINITION"
    elif len(tokens) == 1 and tokens[0].type == TT_LBRACKET:
        return "START_BLOCK"
    elif len(tokens) == 1 and tokens[0].type == TT_RBRACKET:
        return "END_BLOCK"
    else: 
        return "SOME_OTHER_TYPE"
    pass

tokens = [
    Token(1, 'ONBOARD', 'onboard'),
    Token(2, 'PINT', 'pint'),
    Token(2, 'IDENTIFIER', 'g'),
    Token(2, '=', '='),
    Token(2, 'PINT LIT', '1'),
    Token(2, ';', ';'),
    Token(3, 'PINT', 'pint'),
    Token(3, 'IDENTIFIER', 'h'),
    Token(3, '=', '='),
    Token(3, 'PINT LIT', '2'),
    Token(3, ',', ','),
    Token(3, 'IDENTIFIER', 'a'),
    Token(3, '=', '='),
    Token(3, 'PINT LIT', '2'),
    Token(3, ';', ';'),
    Token(4, 'CAPTAIN', 'captain'),
    Token(4, '(', '('),
    Token(4, ')', ')'),
    Token(4, '{', '{'),
    Token(5, 'IDENTIFIER', 'g'),
    Token(5, '=', '='),
    Token(5, 'DOFFY LIT', "hello"),
    Token(5, ';', ';'),
    Token(6, '}', '}'),
    Token(7, 'OFFBOARD', 'offboard')
]

analyze(tokens)