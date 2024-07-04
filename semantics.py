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
        isInFunc = False
        isInParam = True
        param_table = {}
        func_symbol = {}
        funcName = ''
        bracketCnt = 100
        contCnt = 2
        func_info = {}
        isSkip = 0

        for token in tokens:
            if isSkip != 0:
                isSkip -= 1
            elif isInFunc:
                if contCnt != 0:
                    contCnt -= 1
                elif isInParam and token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
                    variable_name = tokens[tokens.index(token) + 1].value
                    if variable_name in param_table:
                        self.errors.append(f"Redeclaration Error: Parameter '{variable_name}' is already declared. (line {token.line_number})")
                    param_table[variable_name] = {"type": token.type, "function": False}  
                    func_info[funcName]["paramCnt"] += 1
                    param_number = func_info[funcName]["paramCnt"]
                    func_info[funcName]["param" + str(param_number) + "_type"] = token.type
                    func_info[funcName]["param" + str(param_number) + "_name"] = variable_name
                elif isInParam and token.type == TT_RPAREN:
                    isInParam = False
                elif token.type == TT_LBRACKET:
                    if bracketCnt == 100:
                        bracketCnt = 1
                    else:
                        bracketCnt += 1
                elif token.type == TT_RBRACKET:
                    bracketCnt -= 1
                    if bracketCnt == 0:
                        isInFunc = False
                        isInParam = True
                        param_table = {}
                        func_symbol = {}
                        funcName = ''
                        bracketCnt = 100
                        contCnt = 2
                elif token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
                    variable_name = tokens[tokens.index(token) + 1].value
                    if variable_name in param_table:
                        self.errors.append(f"Redeclaration Error: Parameter '{variable_name}' is already declared. (line {token.line_number})")
                    elif variable_name in func_symbol:
                        self.errors.append(f"Redeclaration Error: Variable '{variable_name}' is already declared. (line {token.line_number})")
                    func_symbol[variable_name] = {"type": token.type, "function": False}  
                elif token.type == TT_IDTFR:
                    if tokens[tokens.index(token) + 1].type == TT_ASSIGN:
                        variable_name = token.value
                        if variable_name not in func_symbol and variable_name not in param_table and variable_name not in self.symbol_table:
                            self.errors.append(f"Undeclared Variable Usage: Variable '{variable_name}' is being used before it is declared. (line {token.line_number})")
                        elif tokens[tokens.index(token) + 2].type != TT_ASSIGN:
                            if variable_name in param_table:
                                declared_symbol = param_table[variable_name]
                            elif variable_name in func_symbol:
                                declared_symbol = func_symbol[variable_name]
                            else:
                                declared_symbol = self.symbol_table.get(variable_name)

                            if declared_symbol["function"] == True:
                                self.errors.append(f"Function Assign: Can't assign a value to Function '{variable_name}'. (line {token.line_number})")
                                return self.errors
                            
                            declared_type = declared_symbol["type"]
                            
                            expected_value_types = {
                                TT_PINT: [TT_PINT_LIT],
                                TT_FLEET: [TT_PINT_LIT, TT_FLEET_LIT],
                                TT_DOFFY: TT_DOFFY_LIT,
                                TT_BULL: [TT_REAL, TT_USOPP]
                            }

                            expected_types = expected_value_types.get(declared_type)

                            if tokens[tokens.index(token) + 3].type in [TT_SMCLN, TT_COMMA]:
                                assigned_value_type = tokens[tokens.index(token) + 2].type
                                if assigned_value_type not in expected_types:
                                    self.errors.append(f"Type Mismatch: Variable '{variable_name}' is declared as '{declared_type}' but is assigned '{assigned_value_type}'. (line {token.line_number})")
                            else:
                                expression_tokens = tokens[tokens.index(token) + 2:]
                                for i, expr_token in enumerate(expression_tokens):
                                    if expr_token.type in [TT_SMCLN, TT_COMMA]:
                                        break
                                    elif expr_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_EXCLA, TT_FDIV, TT_EXPONENT, TT_LPAREN, TT_RPAREN]:
                                        continue
                                    elif expr_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP]:
                                        if expr_token.type not in expected_types:
                                            self.errors.append(f"Type Mismatch: '{expr_token.type}' found in the expression (Expected: '{expected_types}'). (line {expr_token.line_number})")
                                            break
                                    isSkip += 1
                elif token.type == TT_HOME:
                    funcType = self.symbol_table.get(funcName)["type"]

                    expected_value_types = {
                        TT_PINT: [TT_PINT_LIT, TT_PINT],
                        TT_FLEET: [TT_PINT_LIT, TT_FLEET_LIT, TT_PINT, TT_FLEET],
                        TT_DOFFY: [TT_DOFFY_LIT, TT_DOFFY],
                        TT_BULL: [TT_REAL, TT_USOPP, TT_BULL]
                    }

                    expected_types = expected_value_types.get(funcType)

                    if tokens[tokens.index(token) + 3].type in [TT_RPAREN]:
                        if tokens[tokens.index(token) + 2].type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP]:
                            assigned_value_type = tokens[tokens.index(token) + 2].type
                        elif tokens[tokens.index(token) + 2].value in param_table:
                            assigned_value_type = param_table[tokens[tokens.index(token) + 2].value]["type"]
                        elif tokens[tokens.index(token) + 2].value in func_symbol:
                            assigned_value_type = func_symbol[tokens[tokens.index(token) + 2].value]["type"]
                        elif tokens[tokens.index(token) + 2].value in self.symbol_table:
                            assigned_value_type = self.symbol_table.get(tokens[tokens.index(token) + 2].value)["type"]
                        else:
                            self.errors.append(f"Undeclared Variable Usage: Variable '{tokens[tokens.index(token) + 2].value}' is being used before it is declared. (line {token.line_number})")

                        if assigned_value_type not in expected_types:
                            self.errors.append(f"Return Type Mismatch: Function '{funcName}' has a return type of '{declared_type}' but is assigned '{assigned_value_type}'. (line {token.line_number})")
                    else:
                        expression_tokens = tokens[tokens.index(token) + 2:]
                        parCnt = 1
                        for i, expr_token in enumerate(expression_tokens):
                            if expr_token.type == TT_RPAREN:
                                parCnt -= 1
                                if parCnt == 0:
                                    break
                            elif expr_token.type == TT_LPAREN:
                                parCnt += 1
                            elif expr_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_EXCLA, TT_FDIV, TT_EXPONENT, TT_LPAREN, TT_RPAREN]:
                                continue
                            elif expr_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP]:
                                if expr_token.type not in expected_types:
                                    self.errors.append(f"Return Type Mismatch: Function '{funcName}' has a return type of '{declared_type}' but is assigned '{expr_token.type}'. (line {token.line_number})")
                                    break
                            elif expr_token.type == TT_IDTFR:
                                if expr_token.value in param_table:
                                    assigned_value_type = param_table[expr_token.value]["type"]
                                elif expr_token.value in func_symbol:
                                    assigned_value_type = func_symbol[expr_token.value]["type"]
                                elif expr_token.value in self.symbol_table:
                                    assigned_value_type = self.symbol_table.get(expr_token.value)["type"]
                                else:
                                    self.errors.append(f"Undeclared Variable Usage: Variable '{expr_token.value}' is being used before it is declared. (line {token.line_number})")

                                if assigned_value_type not in expected_types:
                                    self.errors.append(f"Return Type Mismatch: Function '{funcName}' has a return type of '{declared_type}' but is assigned '{assigned_value_type}'. (line {token.line_number})")
                            isSkip += 1
            elif token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
                if tokens[tokens.index(token) + 2].type == TT_ASSIGN:
                    variable_name = tokens[tokens.index(token) + 1].value
                    if variable_name in self.symbol_table:
                        self.errors.append(f"Redeclaration Error: Variable '{variable_name}' is already declared. (line {token.line_number})")
                    else:
                        self.symbol_table[variable_name] = {"type": token.type, "function": False}  
                elif tokens[tokens.index(token) + 2].type == TT_LPAREN:
                    function_name = tokens[tokens.index(token) + 1].value
                    if function_name in self.symbol_table:
                        self.errors.append(f"Redeclaration Error: Function '{function_name}' is already declared. (line {token.line_number})")
                    else:
                        self.symbol_table[function_name] = {"type": token.type, "function": True}  
                        func_info[function_name] = {"type": token.type, "paramCnt": 0}
                        isInFunc = True
                        funcName = function_name
            elif token.type == TT_CAPTAIN:
                if TT_CAPTAIN in self.symbol_table:
                    self.errors.append(f"Multiple Captain Declaration: Captain is already declared. (line {token.line_number})")
                self.symbol_table[TT_CAPTAIN] = {"type": TT_CAPTAIN, "function": True} 
            elif token.type == TT_IDTFR:
                if tokens[tokens.index(token) + 1].type == TT_ASSIGN:
                    variable_name = token.value
                    if variable_name not in self.symbol_table:
                        self.errors.append(f"Undeclared Variable Usage: Variable '{variable_name}' is being used before it is declared. (line {token.line_number})")
                    elif tokens[tokens.index(token) + 2].type != TT_ASSIGN: #tokens[tokens.index(token) - 1].type not in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL] and unclear
                        declared_symbol = self.symbol_table.get(variable_name)
                        if declared_symbol["function"] == True:
                            self.errors.append(f"Function Assign: Can't assign a value to Function '{variable_name}'. (line {token.line_number})")
                            return self.errors
                        declared_type = declared_symbol["type"]
                        
                        expected_value_types = {
                            TT_PINT: [TT_PINT_LIT],
                            TT_FLEET: [TT_PINT_LIT, TT_FLEET_LIT],
                            TT_DOFFY: TT_DOFFY_LIT,
                            TT_BULL: [TT_REAL, TT_USOPP]
                        }

                        expected_types = expected_value_types.get(declared_type)

                        if tokens[tokens.index(token) + 3].type in [TT_SMCLN, TT_COMMA]:
                            assigned_value_type = tokens[tokens.index(token) + 2].type
                            if assigned_value_type not in expected_types:
                                self.errors.append(f"Type Mismatch: Variable '{variable_name}' is declared as '{declared_type}' but is assigned '{assigned_value_type}'. (line {token.line_number})")
                        else:
                            expression_tokens = tokens[tokens.index(token) + 2:]
                            for i, expr_token in enumerate(expression_tokens):
                                if expr_token.type in [TT_SMCLN, TT_COMMA]:
                                        break
                                elif expr_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_EXCLA, TT_FDIV, TT_EXPONENT, TT_LPAREN, TT_RPAREN]:
                                    continue
                                elif expr_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP]:
                                    if expr_token.type not in expected_types:
                                        self.errors.append(f"Type Mismatch: '{expr_token.type}' found in the expression (Expected: '{expected_types}'). (line {expr_token.line_number})")
                                        break
                            isSkip += 1
                elif tokens[tokens.index(token) + 1].type == TT_LPAREN:
                    variable_name = token.value
                    declared_symbol = self.symbol_table.get(variable_name)
                    if declared_symbol["function"] == True:
                        param_tokens = tokens[tokens.index(token) + 2:]
                        checkedFunction = func_info[variable_name]
                        paramCnt = checkedFunction["paramCnt"]
                        checkedToken = 0
                        parCnt = 1
                        for i, param_token in enumerate(param_tokens):
                            if param_token.type == TT_RPAREN:
                                parCnt -= 1
                                if parCnt == 0:
                                    if checkedToken < paramCnt:
                                        self.errors.append(f"Insufficient Parameter: {paramCnt} expected but only {checkedToken} found for {variable_name}. Please ensure all required parameters are included. (line {token.line_number})")
                                    break
                            elif param_token.type == TT_LPAREN:
                                parCnt += 1
                            elif param_token.type in [TT_IDTFR, TT_PINT_LIT, TT_DOFFY_LIT, TT_FLEET_LIT, TT_REAL, TT_USOPP]:
                                if checkedToken < paramCnt:
                                    if param_tokens[i + 1].type in [TT_COMMA, TT_RPAREN]:
                                        currentParam = self.symbol_table.get(param_tokens[i].value)
                                        if currentParam["type"] != checkedFunction[f"param{i+1}_type"]:
                                            self.errors.append(f"Invalid Parameter: Invalid parameter {param_tokens[i].value} provided for {variable_name}. Please check the parameter and try again. (line {token.line_number})")
                                        checkedToken += 1
                                    # elif hindi single value kulang 
                                else:
                                    self.errors.append(f"Excess Parameter: {paramCnt} expected but {checkedToken} found for {variable_name}. Please remove any unnecessary parameters. (line {token.line_number})")
                            isSkip += 1
                            

        # print(self.symbol_table)
        return self.errors


# # Example usage:
# semantic_analyzer = SemanticAnalyzer()
# tokens = [
#     Token(1, 'ONBOARD', 'onboard'),
#     Token(2, 'PINT', 'pint'),
#     Token(2, 'IDENTIFIER', 'g'),
#     Token(2, '=', '='),
#     Token(2, 'PINT LIT', '1'),
#     Token(2, ';', ';'),
#     Token(4, 'CAPTAIN', 'captain'),
#     Token(4, '(', '('),
#     Token(4, ')', ')'),
#     Token(4, '{', '{'),
#     Token(5, 'IDENTIFIER', 'g'),
#     Token(5, '=', '='),
#     Token(5, 'PINT LIT', '2'),
#     Token(5, ';', ';'),
#     Token(6, '}', '}'),
#     Token(7, 'OFFBOARD', 'offboard')
# ]

# try:
#     semantic_errors = semantic_analyzer.analyze(tokens)
#     if semantic_errors:
#         print(semantic_errors[0]) 
#     else:
#         print("Semantic analysis successful")
# except SemanticError as e:
#     print(e.as_string())

def analyze(tokens):
    semantic_analyzer = SemanticAnalyzer()
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
    errors = semantic_analyzer.analyze(tokens)
    if errors:
        return errors[0]
    else:
        return "Semantic analysis successful"


# # Example usage:
# semantic_analyzer = SemanticAnalyzer()
# tokens = [
#     Token(1, 'ONBOARD', 'onboard'),
#     Token(2, 'PINT', 'pint'),
#     Token(2, 'IDENTIFIER', 'g'),
#     Token(2, '=', '='),
#     Token(2, 'PINT_LIT', '1'),
#     Token(2, ';', ';'),
#     # Token(3, 'PINT', 'pint'),
#     # Token(3, 'IDENTIFIER', 'g'),
#     # Token(3, '=', '='),
#     # Token(3, 'PINT_LIT', '1'),
#     # Token(3, ';', ';'),
#     Token(4, 'CAPTAIN', 'captain'),
#     Token(4, '(', '('),
#     Token(4, ')', ')'),
#     Token(4, '{', '{'),
#     Token(5, 'IDENTIFIER', 'g'),
#     Token(5, '=', '='),
#     Token(5, 'DOFFY LIT', "hello"),
#     # Token(5, 'PINT_LIT', '2'),
#     Token(5, ';', ';'),
#     Token(6, '}', '}'),
#     # Token(4, 'CAPTAIN', 'captain'),
#     # Token(4, '(', '('),
#     # Token(4, ')', ')'),
#     # Token(4, '{', '{'),
#     # Token(5, 'IDENTIFIER', 'g'),
#     # Token(5, '=', '='),
#     # Token(5, 'PINT_LIT', '2'),
#     # Token(5, ';', ';'),
#     # Token(6, '}', '}'),
#     Token(7, 'OFFBOARD', 'offboard')
# ]