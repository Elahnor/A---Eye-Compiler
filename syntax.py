from os import system
import os
from tokens import *
from token_class import Token
from constants import *
from error_class import *
from position_class import *


class SyntaxAnalyzer:
    def __init__(self, tokens):
        self.temp_tokens = []
        found_onboard = False
        for token in tokens:
            if token.type == TT_ONBOARD:
                found_onboard = True
            if found_onboard:
                self.temp_tokens.append(token)
            if token.type == TT_OFFBOARD:
                break
        self.tokens = [token for token in self.temp_tokens if token.type not in [TT_SLCOMMENT, TT_MLCOMMENT]]
        self.current_token_idx = 0
        self.current_token = self.tokens[self.current_token_idx] if self.tokens else None
        self.errors = []
        self.subcnt = 0
        self.in_global = True

    def advance(self):
        self.current_token_idx += 1
        if self.current_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.current_token_idx]
            return True
        else:
            self.current_token = None
            return False

    def consume(self, expected_types):
        if self.current_token is not None:
            if self.current_token.type in expected_types:
                return self.advance()
            else:
                expected_types_str = ', '.join(expected_types)
                if not self.errors:
                    self.errors.append(f"Expected one of {expected_types_str}, found {self.current_token.type} in line {self.current_token.line_number}")
                return False
        else: 
            expected_types_str = ', '.join(expected_types)
            if not self.errors:
                self.errors.append(f"Expected one of {expected_types_str}, found none")
            return False

    def peek(self):
        next_token_idx = self.current_token_idx + 1
        if next_token_idx < len(self.tokens):
            return self.tokens[next_token_idx]
        else:
            return None

    def peek2(self):
        next_token_idx = self.current_token_idx + 2
        if next_token_idx < len(self.tokens):
            return self.tokens[next_token_idx]
        else:
            return None

    def peek_next_token(self, token_type):
        next_token_idx = self.current_token_idx
        while next_token_idx < len(self.tokens) and self.tokens[next_token_idx].type != token_type:
            next_token_idx += 1
            if next_token_idx < len(self.tokens) and self.tokens[next_token_idx].type == token_type:
                if next_token_idx + 1 < len(self.tokens): return self.tokens[next_token_idx + 1]
        return None

    def is_relational_or_logical_comp(self):
        left_curly_bracket_idx = self.current_token_idx + 1
        relevant_tokens = []
        while left_curly_bracket_idx < len(self.tokens) and self.tokens[left_curly_bracket_idx].type != TT_LBRACKET:
            left_curly_bracket_idx += 1
        relevant_tokens = self.tokens[self.current_token_idx + 1:left_curly_bracket_idx]
        for token in relevant_tokens:
            if token.type in [TT_AND, TT_ORO]:
                return True
        return False

    def parse(self):
        self.program()
        if self.current_token is not None:
            if not self.errors:
                self.errors.append("Unexpected tokens found after end of program")

        return self.errors

    # 1 {“onboard”}
    def program(self):
        if not self.consume([TT_ONBOARD]):return
        self.globall()
        self.in_global = False
        self.sub_function()
        if not self.consume([TT_CAPTAIN]):return
        if not self.consume([TT_LPAREN]):return
        if not self.consume([TT_RPAREN]):return
        if not self.consume([TT_LBRACKET]):return
        self.statement()
        if self.current_token.type == TT_HOME:
            self.home()
        if not self.consume([TT_RBRACKET]):return
        if not self.consume([TT_OFFBOARD]):return

    # 2 {“pint”, “fleet”, “doffy”, “bull”, “loyal”, λ}
    # 3 {“pint”, “fleet”, “doffy”, “bull”, “loyal”}
    # 4 {“void”, “pint”, “fleet”, “doffy”, “bull”, “loyal”, “captain”}
    def globall(self):
        if self.current_token.type in [TT_CAPTAIN, TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL,TT_LOYAL, TT_VOID]:
            while (self.peek2() is not None and self.peek2().type == TT_ASSIGN) or self.current_token.type == TT_LOYAL:
                self.global_init()
                if self.current_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_SMCLN]:
                    if not self.consume([TT_SMCLN]):return
                else:
                    if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_SMCLN]):return
        else:
            if not self.consume([TT_CAPTAIN, TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL,TT_LOYAL]):return

    # 5 {“pint”, “fleet”, “doffy”, “bull”}
    # 6 {“loyal”}
    def global_init(self):
        if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL]:
            if self.current_token.type == TT_LOYAL:
                self.loyal_init()
            else:
                self.var_dec()
                if not self.consume([TT_ASSIGN]):return
                self.global_val()
                self.global_init_tail()
        else:
            if not self.consume([TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL]):return
            
    def global_init_tail(self):
        if self.current_token.type in [TT_COMMA, TT_SMCLN]:
            if self.current_token.type == TT_COMMA:
                self.next2_global()
        else:
            if not self.consume([TT_COMMA, TT_SMCLN]):return
            
    def next2_global(self):
        if self.current_token.type in [TT_COMMA, TT_SMCLN]:
            if self.current_token.type == TT_COMMA:
                if not self.consume([TT_COMMA]):return
                self.var_assign_global()
                self.next2_global()
        else:
            if not self.consume([TT_COMMA, TT_SMCLN]):return

    # 47 {IDENTIFIER}
    def var_assign(self):
        if not self.consume([TT_IDTFR]):return
        if self.current_token.type == TT_LSBRACKET:
            self.index()
        if not self.consume([TT_ASSIGN]):return
        self.value()

    # 7 {“loyal”}
    def loyal_init(self):
        if not self.consume([TT_LOYAL]):return
        self.var_dec()
        if not self.consume([TT_ASSIGN]):return
        self.global_val()

    # 8 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “(“}
    # 9 {“[“}
    # 158 {IDENTIFIER}
    def global_val(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]:
            if self.current_token.type == TT_LSBRACKET:
                if self.peek_next_token(TT_RSBRACKET) is not None and self.peek_next_token(TT_RSBRACKET).type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                    self.global_array()
                else:
                    self.global_math()
            elif self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type in [TT_LSBRACKET, TT_SMCLN]:
                if not self.consume([TT_IDTFR]):return
                self.index()
            elif self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type not in [TT_LSBRACKET, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                if not self.consume([TT_IDTFR]):return
                if not self.consume([TT_LSBRACKET, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return
            else:
                self.literal()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]):return
    
    def global_val2(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]:
            if self.current_token.type == TT_LSBRACKET:
                self.global_array()
            elif self.current_token.type == TT_IDTFR:
                if not self.consume([TT_IDTFR]):return
                self.index()
            else:
                self.literal2()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]):return

    # 10 {PINT_LIT, FLEET_LIT}
    # 13 {DOFFY_LIT}
    # 14 {BULL_LIT} 
    # 18 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “(“, “[“}
    def literal(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]:
            if self.peek() is not None and self.peek().type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_LPAREN] or self.in_global == False:
                if self.current_token.type == TT_LPAREN: 
                    if not self.consume([TT_LPAREN]):return
                    self.global_math()
                    if not self.consume([TT_RPAREN]):return
                    if self.current_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]: 
                        self.mos()
                        self.global_math_tail()
                elif self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT]:
                    self.num_value()
                elif self.current_token.type == TT_IDTFR:
                    if not self.consume([TT_IDTFR]):return
                    if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return
                else: 
                    if not self.consume([TT_DOFFY_LIT, TT_USOPP, TT_REAL]):return
            else: 
                if self.current_token.type == TT_LPAREN: 
                    if not self.consume([TT_LPAREN]):return
                    self.global_math()
                    if not self.consume([TT_RPAREN]):return
                    if self.current_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]: 
                        self.mos()
                        self.global_math_tail()
                else: 
                    self.global_math()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]):return

    def literal2(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]:
            if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT]:
                self.num_value()
            elif self.current_token.type == TT_IDTFR:
                if not self.consume([TT_IDTFR]):return
                if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return
            else: 
                if not self.consume([TT_DOFFY_LIT, TT_USOPP, TT_REAL]):return
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_USOPP, TT_REAL, TT_IDTFR, TT_LPAREN, TT_LSBRACKET]):return

    # 11 {PINT_LIT}
    # 12 {FLEET_LIT}
    def num_value(self):
        if not self.consume([TT_PINT_LIT,TT_FLEET_LIT]):return

    # 15 {“[“}
    def global_array(self):
        if not self.consume([TT_LSBRACKET]):return
        self.global_val()
        if self.current_token.type == TT_COMMA:
            self.next_global_val()
        if not self.consume([TT_RSBRACKET]):return

    # 16 {“,“}
    # 17 {“]”}
    def next_global_val(self):
        if not self.consume([TT_COMMA]):return
        self.global_val()
        if self.current_token.type == TT_COMMA:
            self.next_global_val()

    # 19 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “(“, “[“}
    def global_math(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_LPAREN, TT_LSBRACKET]:
            self.global_math_head()
            self.mos()
            self.global_math_tail()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_LPAREN, TT_LSBRACKET]):return

    # 20 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “[“}
    # 21 {IDENTIFIER}
    # 22 {“(“}
    def global_math_head(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_LSBRACKET, TT_IDTFR, TT_LPAREN]:
            if self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                if not self.consume([TT_IDTFR]):return
            elif self.current_token.type == TT_LPAREN:
                if not self.consume([TT_LPAREN]):return
                self.global_math()
                if not self.consume([TT_RPAREN]):return
            else:
                self.global_val2()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_LSBRACKET, TT_IDTFR, TT_LPAREN]):return

    # 23 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “(“, “[“}
    def global_math_tail(self):
        self.global_val()

    # 24 {“pint”, “fleet”, “doffy”, “bull”}
    def var_init(self):
        if self.current_token.type in [TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]:
            self.var_dec()
            if not self.consume([TT_ASSIGN]):return
            self.value()
            if self.current_token.type in [TT_COMMA, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                if self.current_token.type == TT_COMMA:
                    self.var_init_tail()
            else:
                if not self.consume([TT_COMMA, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return
        else:
            if not self.consume([TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]):return

    # 25 {“pint”, “fleet”, “doffy”, “bull”}
    def var_dec(self):
        if self.current_token.type in [TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]:
            self.d_type()
            if not self.consume([TT_IDTFR]):return
        else:
            if not self.consume([TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]):return
        
    # 26 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “(“}
    # 27 {IDENTIFIER}
    # 33 {“(“, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “len”, “load”, “[“}
    # 34 {IDENTIFIER, “len”, “load”}
    # 35 {“[“} fix
    def value(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP] and self.peek() is not None and self.peek().type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                self.literal()
            elif self.current_token.type in [TT_IDTFR] and self.peek() is not None and self.peek().type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_LPAREN]:
                if self.peek().type == TT_LSBRACKET and self.peek_next_token(TT_RSBRACKET) is not None and self.peek_next_token(TT_RSBRACKET).type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                    if not self.consume([TT_IDTFR]):return
                    self.index()
                elif self.peek().type != TT_LSBRACKET:
                    if not self.consume([TT_IDTFR]):return
                    self.index()
                else:
                    self.math_operation()
            elif self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD] and self.peek() is not None and self.peek().type == TT_LPAREN:
                if self.peek_next_token(TT_RPAREN) is not None and self.peek_next_token(TT_RPAREN).type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                    self.func_call()
                elif self.peek_next_token(TT_RPAREN) == None:
                    self.func_call()
                else:
                    self.math_operation()
            elif self.current_token.type in [TT_LSBRACKET]:
                if self.peek_next_token(TT_RSBRACKET) is not None and self.peek_next_token(TT_RSBRACKET).type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                    self.array()
                elif self.peek_next_token(TT_RSBRACKET) == None:
                    self.array()
                else:
                    self.math_operation()
            else:
                if self.current_token.type == TT_LPAREN: 
                    if not self.consume([TT_LPAREN]):return
                    self.math_operation()
                    if not self.consume([TT_RPAREN]):return
                    if self.current_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]: 
                        self.mos()
                        self.math_tail()
                else:
                    self.math_operation()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    def math_head_val(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP]:
                self.literal()
            elif self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD] and self.peek() is not None and self.peek().type == TT_LPAREN:
                self.func_call()
            elif self.current_token.type in [TT_IDTFR]:
                if not self.consume([TT_IDTFR]):return
                self.index()
            elif self.current_token.type in [TT_LSBRACKET]:
                self.array()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # 28 {“[“, λ}
    # 29 {“[“}
    # 32 {“,”, “;”, “]”, “:”, “+”, “-”, “*”, ”/”, “%”, “**”, “//”, “)”, “[”, “<”, “>”, “<=”, “>=”, “==”, “!=”, “oro”, “and”}
    def index(self):
        if self.current_token.type in [TT_LSBRACKET, TT_COMMA, TT_SMCLN, TT_RSBRACKET, TT_CLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_RPAREN, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_ORO, TT_AND]:
            if self.current_token.type == TT_LSBRACKET:
                if not self.consume([TT_LSBRACKET]):return
                self.indexer()
                if not self.consume([TT_RSBRACKET]):return
                if self.current_token.type == TT_LSBRACKET:
                    self.index()
        else:
            if not self.consume([TT_LSBRACKET, TT_COMMA, TT_SMCLN, TT_RSBRACKET, TT_CLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_RPAREN, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_ORO, TT_AND]):return

    # 30
    # 31
    def indexer(self):
        if not self.consume([TT_IDTFR, TT_PINT_LIT]):return

    # def value2(self):
    #     if self.current_token.type in [TT_LPAREN, TT_USOPP, TT_REAL, TT_DOFFY_LIT, TT_LSBRACKET, TT_PINT_LIT, TT_FLEET_LIT, TT_IDTFR, TT_LEN, TT_LOAD]: 
    #         if self.current_token.type == TT_LPAREN:
    #             self.math_operation()
    #         else:
    #             if self.current_token.type in [TT_USOPP, TT_REAL, TT_DOFFY_LIT]: 
    #                 if self.current_token.type == TT_DOFFY_LIT:
    #                     while self.current_token.type == TT_DOFFY_LIT:
    #                         if not self.consume([TT_DOFFY_LIT]):return
    #                         if self.current_token.type == TT_PLUS and self.peek().type == TT_DOFFY_LIT:
    #                             if not self.consume([TT_PLUS]):return
    #                         else:
    #                             break
    #                 else:
    #                     if not self.consume([TT_USOPP, TT_REAL]):return
    #             else:
    #                 if self.current_token.type != TT_LSBRACKET:
    #                     if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT]:
    #                         self.num_value()
    #                         if self.current_token.type in [TT_RPAREN, TT_COMMA, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_CLN, TT_RSBRACKET]: 
    #                             if self.current_token.type not in [TT_COMMA, TT_SMCLN, TT_RPAREN, TT_CLN, TT_RSBRACKET]:
    #                                 self.mos()
    #                                 self.math_tail()
    #                         else:
    #                             if not self.consume([TT_COMMA, TT_SMCLN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_CLN, TT_RSBRACKET]):return
    #                     elif self.current_token.type == TT_IDTFR:
    #                         if not self.consume([TT_IDTFR]):return
    #                         if self.current_token.type not in [TT_COMMA, TT_SMCLN, TT_RPAREN, TT_CLN, TT_RSBRACKET]:
    #                             if self.current_token.type != TT_LSBRACKET:
    #                                 if self.current_token.type == TT_LPAREN:
    #                                     if not self.consume([TT_LPAREN]):return
    #                                     self.arguments()
    #                                     if not self.consume([TT_RPAREN]):return
    #                                 if self.current_token.type not in [TT_COMMA, TT_SMCLN, TT_RPAREN]:
    #                                     self.mos()
    #                                     self.math_tail()
    #                             else:
    #                                 self.index()
    #                                 if self.current_token.type == TT_LPAREN:
    #                                     if not self.consume([TT_LPAREN]):return
    #                                     self.arguments()
    #                                     if not self.consume([TT_RPAREN]):return
    #                                 if self.current_token.type not in [TT_COMMA, TT_SMCLN, TT_RPAREN]:
    #                                     self.mos()
    #                                     self.math_tail()
    #                     elif self.current_token.type in [TT_LEN, TT_LOAD]:
    #                         self.func_call()
    #                 else:
    #                     self.array()
    #     else:
    #         if not self.consume([TT_LPAREN, TT_USOPP, TT_REAL, TT_DOFFY_LIT, TT_LSBRACKET, TT_PINT_LIT, TT_FLEET_LIT, TT_IDTFR, TT_LEN, TT_LOAD]):return

    # 36 {“(“, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “len”, “load”, “[“}
    def math_operation(self):
        if self.current_token.type in [TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]:
            self.math_head()
            self.mos()
            self.math_tail()
        else:
            if not self.consume([TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # 37 {“(“}
    # 38 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “(“, “len”, “load”, “[“}
    def math_head(self):
        if self.current_token.type in [TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]:
            if self.current_token.type == TT_LPAREN:
                if not self.consume([TT_LPAREN]):return
                self.math_operation()
                if not self.consume([TT_RPAREN]):return
            else:
                self.math_head_val()
        else:
            if not self.consume([TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    def math_head2(self):
        if self.current_token.type in [TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]:
            if self.current_token.type == TT_LPAREN:
                if not self.consume([TT_LPAREN]):return
                self.math_operation()
                if not self.consume([TT_RPAREN]):return
                if self.current_token.type in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]: 
                    self.mos()
                    self.math_tail()
            else:
                self.value()
        else:
            if not self.consume([TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # 39 {“(“, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “len”, “load”, “[“}
    def math_tail(self):
        if self.current_token.type in [TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]:         
            self.math_head2()
        else:
            if not self.consume([TT_LPAREN, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # 40 {“[“}
    def array(self):
        if not self.consume([TT_LSBRACKET]):return
        self.value()
        self.next_value()
        if not self.consume([TT_RSBRACKET]):return

    # 41 {“,“}
    # 42 {“]”}
    def next_value(self):
        if self.current_token.type in [TT_COMMA, TT_RSBRACKET]:
            if self.current_token.type == TT_COMMA:
                if not self.consume([TT_COMMA]):return
                self.value()
                self.next_value()
        else:
            if not self.consume([TT_COMMA, TT_RSBRACKET]):return

    # 43 {“,” , λ}
    # 44 {“;”}
    def var_init_tail(self):
        if self.current_token.type in [TT_COMMA, TT_SMCLN]:
            if self.current_token.type == TT_COMMA:
                self.next2()
        else:
            if not self.consume([TT_COMMA, TT_SMCLN]):return
        
    # 45 {“,”}
    # 46 {“;”}
    def next2(self):
        if self.current_token.type in [TT_COMMA, TT_SMCLN]:
            if self.current_token.type == TT_COMMA:
                if not self.consume([TT_COMMA]):return
                self.var_assign()
                self.next2()
        else:
            if not self.consume([TT_COMMA, TT_SMCLN]):return

    # 47 {IDENTIFIER}
    def var_assign_global(self):
        if not self.consume([TT_IDTFR]):return
        if self.current_token.type == TT_LSBRACKET:
            self.index()
        if not self.consume([TT_ASSIGN]):return
        self.global_val()

    # 48 {“pint”}
    # 49 {“fleet”}
    # 50 {“bull”}
    # 51 {“doffy”}
    def d_type(self):
        if not self.consume([TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]):return

    # 52 {“pint”, “fleet”, “doffy”, “bull”}
    # 53 {“loyal”}
    # 54 {IDENTIFIER}
    def var_statement(self):
        if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR]: 
            if self.current_token.type in [TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]:
                self.var_init()
            elif self.current_token.type == TT_LOYAL:
                self.loyal_init()
            elif self.current_token.type == TT_IDTFR:
                self.var_assign()
        else:
            if not self.consume([TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR]):return

    # 55 {"theo"}
    def if_statement(self):
        if not self.consume([TT_THEO]):return
        self.conditional()

    # 56 {“(“}
    def conditional(self):
        if not self.consume([TT_LPAREN]):return
        self.condition()
        if self.current_token.type == TT_RPAREN:
            if not self.consume([TT_RPAREN]):return
        else:
            if not self.consume([TT_RPAREN, TT_AND, TT_ORO]):return
        if not self.consume([TT_LBRACKET]):return
        self.statement()
        self.home()
        if not self.consume([TT_RBRACKET]):return
        if self.current_token.type == TT_ALTHEO:
            self.else_if_statement()
        if self.current_token.type == TT_ALT:
            self.else_statement()    

    # 57 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, “nay”, “(“, “len”, “load”, “[“}
    # 58 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “nay”, λ, “(“, “len”, “load”, “[“}
    # 59 {BULL_LIT}
    def condition(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET, TT_REAL, TT_USOPP]:
            if self.current_token.type in [TT_REAL, TT_USOPP, TT_IDTFR] and self.peek() is not None and self.peek().type == TT_RPAREN:
                if not self.consume([TT_REAL, TT_USOPP, TT_IDTFR]):return
            elif self.is_relational_or_logical_comp() == True or self.current_token.type == TT_NAY:
                self.logical_op()
            else:
                self.relational_comp()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET, TT_REAL, TT_USOPP]):return

    def condition2(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET, TT_REAL, TT_USOPP]:
            if self.current_token.type in [TT_REAL, TT_USOPP] and self.peek() is not None and self.peek().type == TT_RPAREN:
                if not self.consume([TT_REAL, TT_USOPP]):return
            else:
                self.relational_comp()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET, TT_REAL, TT_USOPP]):return

    # 60 {“altheo”, λ}
    # 61 {“altheo”}
    # 62 {“alt”, “altheo”, “pint”, “fleet”, “doffy”, “bull”, “theo”, “helm”, “four”, “whale”, IDENTIFIER, “len”, “fire”, “leak”, “sail”, “pass”, “load”}
    def else_if_statement(self):
        if self.current_token.type in [TT_ALTHEO, TT_ALT, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_LEAK, TT_SAIL, TT_PASS, TT_LOAD]:
            while self.current_token.type == TT_ALTHEO:
                if not self.consume([TT_ALTHEO]):return
                if not self.consume([TT_LPAREN]):return
                self.condition()
                if not self.consume([TT_RPAREN]):return
                if not self.consume([TT_LBRACKET]):return
                self.statement()
                self.home()
                if not self.consume([TT_RBRACKET]):return
        else:
            if not self.consume([TT_ALTHEO, TT_ALT, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_LEAK, TT_SAIL, TT_PASS, TT_LOAD]):return

    # 63 {“alt”}
    # 64 {“pint”, “fleet”, “doffy”, “bull”, “theo”, “helm”, “four”, “whale”, IDENTIFIER, “len”, “fire”, “leak”, “sail”, “pass”, “load”}
    def else_statement(self):
        if self.current_token.type in [TT_ALT, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_LEAK, TT_SAIL, TT_PASS, TT_LOAD]:
            if self.current_token.type == TT_ALT:
                if not self.consume([TT_ALT]):return
                if not self.consume([TT_LBRACKET]):return
                self.statement()
                # 154 {“}”, “home”, “leak”, “pint”, “fleet”, “doffy”, “bull”, “theo”, “helm”, “four”, “whale”, IDENTIFIER, “len”, “fire”, “leak”, “sail”, “pass”, “load”}
                if self.current_token.type in [TT_HOME, TT_RBRACKET, TT_LEAK, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_SAIL, TT_PASS, TT_LOAD]:
                    self.home()
                else:
                    if not self.consume([TT_HOME, TT_RBRACKET, TT_LEAK, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_SAIL, TT_PASS, TT_LOAD]):return
                if not self.consume([TT_RBRACKET]):return
        else:
            if not self.consume([TT_ALT, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_LEAK, TT_SAIL, TT_PASS, TT_LOAD]):return

    # 65 {“helm”}
    def switch_statement(self):
        if not self.consume([TT_HELM]):return
        if not self.consume([TT_LPAREN]):return
        if not self.consume([TT_IDTFR]):return
        if not self.consume([TT_RPAREN]):return
        if not self.consume([TT_LBRACKET]):return
        self.switch_cond()
        if not self.consume([TT_DAGGER]):return
        if not self.consume([TT_CLN]):return
        self.statement()
        if not self.consume([TT_RBRACKET]):return

    # 66 {“chest”}
    # 67 {“chest”}
    def switch_cond(self):
        if not self.consume([TT_CHEST]):return
        self.value()
        if not self.consume([TT_CLN]):return
        self.statement()
        self.leak()
        self.switch_cond_tail()

    # 68 {“leak”}
    # 69 {“dagger”, “chest”}
    def leak(self):
        if self.current_token.type in [TT_LEAK, TT_DAGGER, TT_CHEST]:
            if self.current_token.type == TT_LEAK:
                if not self.consume([TT_LEAK]):return
                if not self.consume([TT_SMCLN]):return
        else:
            if not self.consume([TT_LEAK, TT_DAGGER, TT_CHEST]):return
        
    # 70 {“chest”, λ}
    # 71 {“dagger”, “chest”}
    def switch_cond_tail(self):
        if self.current_token.type in [TT_CHEST, TT_DAGGER]:
            if self.current_token.type == TT_CHEST:
                self.switch_cond()
        else:
            if not self.consume([TT_CHEST, TT_DAGGER]):return

    # 72 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, “nay”, “(“, “len”, “load”, “[“}
    # 73 {DOFFY_LIT}
    # 74 {IDENTIFIER, real, usopp} fix
    def relational_comp(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET, TT_REAL, TT_USOPP]: 
            if self.peek2().type == TT_DOFFY_LIT and self.current_token.type != TT_DOFFY_LIT:
                self.expression()
                self.str_cop()
                if not self.consume([TT_DOFFY_LIT]):return
            elif self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET] and self.peek2() is not None and self.peek2().type not in [TT_REAL, TT_USOPP]: 
                self.expression()
                self.comparator()
                self.expression2()
            elif self.current_token.type == TT_DOFFY_LIT and self.peek2().type == TT_DOFFY_LIT:
                if not self.consume([TT_DOFFY_LIT]):return
                self.str_cop()
                if not self.consume([TT_DOFFY_LIT]):return
            elif self.current_token.type == TT_DOFFY_LIT and self.peek2().type != TT_DOFFY_LIT:
                if not self.consume([TT_DOFFY_LIT]):return
                self.str_cop()
                self.expression()
            else:
                self.bool_exp()
                self.str_cop()

    # 75 {IDENTIFIER}
    # 76 {IDENTIFIER, “len”, “load”}
    # 77 {BULL_LIT}
    def bool_exp(self):
        if self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD, TT_REAL, TT_USOPP]: 
            if self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type == TT_LPAREN: 
                self.func_call()
            elif self.current_token.type == TT_IDTFR:
                if not self.consume([TT_IDTFR]):return
            else:
                if not self.consume([TT_REAL, TT_USOPP]):return
        else:
            if not self.consume([TT_IDTFR, TT_LEN, TT_LOAD, TT_REAL, TT_USOPP]):return

    # 78 {IDENTIFIER)
    # 79 {PINT_LIT}
    # 80 {FLEET_LIT}
    # 81 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, “nay”, “(“, “len”, “load”, “[“}
    # 82 {“(“, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “len”, “load”, “[“}
    # 83 {IDENTIFIER, “len”, “load”}
    def expression(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            if self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type not in [TT_LSBRACKET, TT_LPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                if not self.consume([TT_IDTFR]):return
                # if not self.consume([TT_LSBRACKET, TT_LPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]):return
            elif self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT] and self.peek() is not None and self.peek().type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]:
                if not self.consume([TT_PINT_LIT, TT_FLEET_LIT]):return
                if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]):return
            elif self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type in [TT_LSBRACKET] and self.peek_next_token(TT_RSBRACKET) is not None and self.peek_next_token(TT_RSBRACKET).type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]:
                if not self.consume([TT_IDTFR]):return
                self.index()
            elif self.current_token.type == TT_PINT_LIT and self.peek() is not None and self.peek().type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_AND, TT_ORO]:
                if not self.consume([TT_PINT_LIT]):return
            elif self.current_token.type == TT_FLEET_LIT and self.peek() is not None and self.peek().type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_AND, TT_ORO]:
                if not self.consume([TT_FLEET_LIT]):return
            elif self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD] and self.peek() is not None and self.peek().type == TT_LPAREN and self.peek_next_token(TT_RPAREN) is not None and self.peek_next_token(TT_RPAREN).type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN]:
                self.func_call()
            elif self.is_relational_or_logical_comp() == True or self.current_token.type == TT_NAY:
                self.logical_op()
            else:
                self.math_operation()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    def expression2(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            if self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type not in [TT_LSBRACKET, TT_LPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_SMCLN]:
                if not self.consume([TT_IDTFR]):return
                if not self.consume([TT_LSBRACKET, TT_LPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN]):return
            elif self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT] and self.peek() is not None and self.peek().type not in [TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_SMCLN]:
                if not self.consume([TT_PINT_LIT, TT_FLEET_LIT]):return
                if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_AND, TT_ORO, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN]):return
            elif self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type in [TT_LSBRACKET, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_AND, TT_ORO, TT_SMCLN, TT_RPAREN]:
                if not self.consume([TT_IDTFR]):return
                self.index()
            elif self.current_token.type == TT_PINT_LIT and self.peek() is not None and self.peek().type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_AND, TT_ORO, TT_SMCLN]:
                if not self.consume([TT_PINT_LIT]):return
            elif self.current_token.type == TT_FLEET_LIT and self.peek() is not None and self.peek().type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_AND, TT_ORO, TT_SMCLN]:
                if not self.consume([TT_FLEET_LIT]):return
            elif self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD] and self.peek() is not None and self.peek().type == TT_LPAREN and self.peek_next_token(TT_RPAREN) is not None and self.peek_next_token(TT_RPAREN).type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_RPAREN, TT_SMCLN]:
                self.func_call()
            elif self.is_relational_or_logical_comp() == True or self.current_token.type == TT_NAY:
                self.logical_op()
            else:
                self.math_operation()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # def expression(self):
    #     if self.current_token.type in [TT_LPAREN, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_LEN, TT_LOAD]: 
    #         if self.current_token.type == TT_LPAREN:
    #             if not self.consume([TT_LPAREN]):return
    #             self.expression()
    #             if self.current_token.type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]: 
    #                 self.comparator()
    #                 self.expression()
    #             if not self.consume([TT_RPAREN]):return
    #         elif self.current_token.type in [TT_IDTFR]: 
    #             if not self.consume([TT_IDTFR]):return
    #             if self.current_token.type not in [TT_RPAREN]:
    #                 if self.current_token.type == TT_LPAREN:
    #                     if not self.consume([TT_LPAREN]):return
    #                     self.arguments()
    #                     if not self.consume([TT_RPAREN]):return
    #                 if self.current_token.type not in [TT_RPAREN, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_SMCLN]:
    #                     self.mos()
    #                     self.math_tail()
    #         elif self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT]: 
    #             self.num_value()
    #             if self.current_token.type in [TT_RPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV, TT_SMCLN, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_AND, TT_ORO]: 
    #                 if self.current_token.type not in [TT_RPAREN, TT_SMCLN, TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL, TT_AND, TT_ORO]:
    #                     self.mos()
    #                     self.math_tail()
    #             else:
    #                 if not self.consume([TT_RPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return
    #         elif self.current_token.typein [TT_LOAD, TT_LEN]: 
    #             self.func_call()
    #     else:
    #         if not self.consume([TT_LPAREN, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_LEN, TT_LOAD]):return   

    # 84 {“<”, “>”, “<=”, “>=”, “==”, “!=”}
    def comparator(self):
        if self.current_token.type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]: 
            self.cop()
        else:
            if not self.consume([TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]):return

    # 85 {“<”}
    # 86 {“>”}
    # 87 {“<=”}
    # 88 {“>=”}
    # 89 {“==”, “!=”}
    def cop(self):
        if self.current_token.type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]: 
            if self.current_token.type in [TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL]: 
                if not self.consume([TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL]):return
            else:
                self.str_cop()
        else:
            if not self.consume([TT_LTHAN, TT_GTHAN, TT_LEQUAL, TT_GEQUAL, TT_EQUAL, TT_NOTEQUAL]):return

    # 90 {“==”}
    # 91 {“!=”}
    def str_cop(self):
        if not self.consume([TT_EQUAL, TT_NOTEQUAL]):return

    # 92 {“+”}
    # 93 {“-”}
    # 94 {“*”}
    # 95 {“/”}
    # 96 {“%”}
    # 97 {“**”}
    # 98 {“//”}
    def mos(self):
        if not self.consume([TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return

    # 99 {“nay”, λ}
    # 100 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT “nay”, “(“, “len”, “load”, “[“}
    def logical_op(self):
        if self.current_token.type in [TT_NAY, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            if self.current_token.type == TT_NAY:
                self.not_log()
            else:
                self.mid_log()
        else: 
            if not self.consume([TT_NAY, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return
            
    # 101 {“nay”}
    def not_log(self):
        if not self.consume([TT_NAY]):return
        if not self.consume([TT_LPAREN]):return
        self.negate()
        if self.current_token.type == TT_RPAREN:
            if not self.consume([TT_RPAREN]):return
        else:
            if not self.consume([TT_RPAREN, TT_AND, TT_ORO]):return

    # 102 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, “nay”, “(“, “len”, “load”, “[“}
    # 103 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT “nay”, “(“, “len”, “load”, “[“}
    # 104 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT “nay”, “(“, “len”, “load”, “[“}
    def negate(self):
        if self.current_token.type in [TT_DOFFY_LIT, TT_LPAREN, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_LEN, TT_NAY]: 
            self.condition()
        else:
            if not self.consume([TT_DOFFY_LIT, TT_LPAREN, TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_LEN, TT_NAY]):return

    # 105 {IDENTIFIER, PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT “nay”,  “(“, “len”, “load”, “[“}
    def mid_log(self):
        if self.current_token.type in [TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]: 
            self.condition2()
            self.logical_keywords()
            self.condition()
        else:
            if not self.consume([TT_IDTFR, TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_NAY, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return
        
    # 106 {“and”}
    # 107 {“oro”}
    def logical_keywords(self):
        if not self.consume([TT_AND, TT_ORO]):return

    # 108 {“four”}
    # 109 {“whale”}
    def loop_statement(self):
        if self.current_token.type in [TT_FOUR, TT_WHALE]: 
            if self.current_token.type == TT_FOUR:
                self.for_loop()
            elif self.current_token.type == TT_WHALE:
                self.while_loop()
        else:
            if not self.consume([TT_FOUR, TT_WHALE]):return
    
    # 110 {“four”}
    def for_loop(self):
        if not self.consume([TT_FOUR]):return
        if not self.consume([TT_LPAREN]):return
        self.var_init()
        if not self.consume([TT_SMCLN]):return
        self.relational_comp()
        if not self.consume([TT_SMCLN]):return
        self.update()
        if not self.consume([TT_RPAREN]):return
        if not self.consume([TT_LBRACKET]):return
        self.statement()
        if not self.consume([TT_RBRACKET]):return

    # 111 {IDENTIFIER}
    # 112 {IDENTIFIER}
    def update(self):
        if self.current_token.type in [TT_IDTFR]: 
            if self.peek() is not None and self.peek().type == TT_ASSIGN:
                self.var_assign()
            else:
                self.unary()
        else:
            if not self.consume([TT_IDTFR]):return

    # 113 {IDENTIFIER}
    def unary(self):
        if not self.consume([TT_IDTFR]):return
        self.uop()

    # 114 {“++”}
    # 115 {“--”}
    def uop(self):
        if not self.consume([TT_INCR, TT_DECR]):return

    # 116 {“whale”}
    def while_loop(self):
        if not self.consume([TT_WHALE]):return
        if not self.consume([TT_LPAREN]):return
        self.condition()
        if not self.consume([TT_RPAREN]):return
        if not self.consume([TT_LBRACKET]):return
        self.statement()
        if not self.consume([TT_RBRACKET]):return

    # 117 {“fire”}
    def output_statement(self):
        if not self.consume([TT_FIRE]):return
        if not self.consume([TT_LPAREN]):return
        self.value()
        if self.current_token.type in [TT_RPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]: 
            if not self.consume([TT_RPAREN]):return
        else:
            if not self.consume([TT_RPAREN, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD, TT_EXPONENT, TT_FDIV]):return

    # 118 {“load”}
    def input_statement(self):
        if not self.consume([TT_LOAD]):return
        if not self.consume([TT_LPAREN]):return
        self.prompt()
        if not self.consume([TT_RPAREN]):return

    # 119 {DOFFY_LIT}
    # 120 {IDENTIFIER}
    def prompt(self):
        if not self.consume([TT_DOFFY_LIT, TT_IDTFR]):return

    # 121 {“void”, “pint”, “fleet”, “doffy”, “bull”, λ}
    # 122 {“void”, “pint”, “fleet”, “bull” ,”doffy”, “captain”}
    # 123 {“pint”, “fleet”, “doffy”, “bull”, “void”}
    def sub_function(self):
        if self.current_token.type in [TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_CAPTAIN]:
            while self.current_token.type in [TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
                self.ret_type()
                self.func_id()
                if self.subcnt == 0:
                    if not self.consume([TT_LPAREN, TT_ASSIGN]):return
                else:
                    if not self.consume([TT_LPAREN]):return
                self.parameters()
                if not self.consume([TT_RPAREN]):return
                if not self.consume([TT_LBRACKET]):return
                self.statement()
                if self.current_token.type in [TT_HOME, TT_RBRACKET, TT_LEAK, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_SAIL, TT_PASS, TT_LOAD]:
                    self.home()
                else:
                    if not self.consume([TT_HOME, TT_RBRACKET, TT_LEAK, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_IDTFR, TT_LEN, TT_FIRE, TT_SAIL, TT_PASS, TT_LOAD]):return
                if not self.consume([TT_RBRACKET]):return
                self.subcnt += 1
            if self.current_token.type not in [TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_CAPTAIN]: 
                if not self.consume([TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_CAPTAIN]):return
        else:
            if not self.consume([TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_CAPTAIN]):return

    # 124 {“void”}
    # 125 {“pint”, “fleet”, “doffy”, “bull”}
    def ret_type(self):
        if self.current_token.type in [TT_VOID, TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
            if self.current_token.type == TT_VOID:
                if not self.consume([TT_VOID]):return
            else: 
                self.d_type()
        else:
            if not self.consume([TT_VOID, TT_PINT,TT_FLEET,TT_DOFFY,TT_BULL]):return
    
    # 126 {“pint”, “fleet”, “doffy”, “bull”, λ}
    # 129 {“pint”, “fleet”, “doffy”, “bull”}
    # 130 {“)”}
    def parameters(self):
        if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_RPAREN]:
            if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL]:
                self.var_dec()
                self.next_parameters()
        else:
            if not self.consume([TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_RPAREN]):return

    # 127 {“,”}
    # 128 {“)”, “,”}
    def next_parameters(self):
        if self.current_token.type in [TT_COMMA, TT_RPAREN]:
            if self.current_token.type == TT_COMMA:
                if not self.consume([TT_COMMA]):return
                self.parameters()
        else:
            if not self.consume([TT_COMMA, TT_RPAREN]):return

    # 131 {IDENTIFIER}
    # 132 {“len”}
    # 150 {“load”}
    def func_call(self):
        if self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD]:
            if self.current_token.type == TT_IDTFR:
                self.func_id()
                if not self.consume([TT_LPAREN]):return
                self.arguments()
                if not self.consume([TT_RPAREN]):return
            elif self.current_token.type == TT_LEN:
                if not self.consume([TT_LEN]):return
                if not self.consume([TT_LPAREN]):return
                self.len_args()
                if not self.consume([TT_RPAREN]):return
            else:
                self.input_statement()
        else:
            if not self.consume([TT_IDTFR, TT_LEN, TT_LOAD]):return

    # 133 {DOFFY_LIT}
    # 134 {“[“}
    # 135 {IDENTIFIER}
    def len_args(self):
        if self.current_token.type in [TT_DOFFY_LIT, TT_LSBRACKET, TT_IDTFR]:
            if self.current_token.type == TT_DOFFY_LIT:
                if not self.consume([TT_DOFFY_LIT]):return
            elif self.current_token.type == TT_IDTFR:
                if not self.consume([TT_IDTFR]):return
            else:
                self.array()
        else:
            if not self.consume([TT_DOFFY_LIT, TT_LSBRACKET, TT_IDTFR]):return

    # 136 {IDENTIFIER}
    def func_id(self):
        if not self.consume([TT_IDTFR]):return

    # 137 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “(“, “len”, “[“, “load”}
    # 141 {“,”, “)”}
    def arguments(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LSBRACKET, TT_LOAD, TT_COMMA, TT_RPAREN]:
            if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LSBRACKET, TT_LOAD]: 
                self.argument()
                self.arguments_tail()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LSBRACKET, TT_LOAD, TT_COMMA, TT_RPAREN]):return
    
    # 138 {“,”}
    # 139 {“,”, “)”}
    def arguments_tail(self):
        if self.current_token.type in [TT_COMMA, TT_RPAREN]:
            if self.current_token.type == TT_COMMA:
                if not self.consume([TT_COMMA]):return
                self.argument()
                self.arguments_tail()
        else:
            if not self.consume([TT_COMMA, TT_RPAREN]):return

    # 140 {PINT_LIT, FLEET_LIT, DOFFY_LIT, BULL_LIT, IDENTIFIER, “(“, “len”, “load”, “[“}
    def argument(self):
        if self.current_token.type in [TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]:
            self.value()
        else:
            if not self.consume([TT_PINT_LIT, TT_FLEET_LIT, TT_DOFFY_LIT, TT_REAL, TT_USOPP, TT_IDTFR, TT_LPAREN, TT_LEN, TT_LOAD, TT_LSBRACKET]):return

    # 142 {“home”}
    # 143 {“}”}
    def home(self):
        if self.current_token.type in [TT_HOME, TT_RBRACKET]:
            if self.current_token.type == TT_HOME:
                if not self.consume([TT_HOME]):return
                if not self.consume([TT_LPAREN]):return
                self.value()
                if not self.consume([TT_RPAREN]):return
                if not self.consume([TT_SMCLN]):return
        else:
            if not self.consume([TT_HOME, TT_RBRACKET]):return

    # 144 {“pint”, “fleet”, “doffy”, “bull”, “loyal”, λ, IDENTIFIER, “theo”, “helm”, “four”, “whale”, “load”, “fire”, “len”}
    # 145 {pint, fleet, doffy, bull, loyal, IDENTIFIER}
    # 146 {“theo”}
    # 147 {“helm”}
    # 148 {“four”, “whale”}
    # 149 {IDENTIFIER, “len”, “load”}
    # 151 {“fire”}
    # 152 {IDENTIFIER}
    # 153 {“leak”, “sail”, “pass“}
    # 154 {“}”, “home”, “leak”, “pint”, “fleet”, “doffy”, “bull”, “theo”, “helm”, “four”, “whale”, IDENTIFIER, “len”, “fire”, “leak”, “sail”, “pass”, “load”}
    def statement(self):
        if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_LOAD, TT_FIRE, TT_LEN, TT_LEAK, TT_SAIL, TT_PASS, TT_RBRACKET, TT_HOME]: 
            if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR] and self.peek() is not None and self.peek().type not in [TT_INCR, TT_DECR, TT_LPAREN]: 
                if self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type not in [TT_ASSIGN, TT_LSBRACKET]:
                    if not self.consume([TT_ASSIGN, TT_LPAREN]):return
                self.var_statement()
                if not self.consume([TT_SMCLN]):return
            elif self.current_token.type == TT_THEO:
                self.if_statement()
            elif self.current_token.type == TT_HELM:
                self.switch_statement() 
            elif self.current_token.type in [TT_FOUR, TT_WHALE]: 
                self.loop_statement()
            elif self.current_token.type in [TT_IDTFR, TT_LEN, TT_LOAD] and self.peek() is not None and self.peek().type == TT_LPAREN: 
                self.func_call()
                if not self.consume([TT_SMCLN]):return
            elif self.current_token.type == TT_FIRE:
                self.output_statement()
                if not self.consume([TT_SMCLN]):return
            elif self.current_token.type == TT_IDTFR and self.peek() is not None and self.peek().type in [TT_INCR, TT_DECR]:
                self.unary()
                if not self.consume([TT_SMCLN]):return
            elif self.current_token.type in [TT_LEAK, TT_SAIL, TT_PASS]: 
                self.control()
                if not self.consume([TT_SMCLN]):return
            if self.current_token.type in [TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_LOAD, TT_FIRE, TT_LEN, TT_LEAK, TT_SAIL, TT_PASS]: 
                self.statement()
        else:
            if not self.consume([TT_PINT, TT_FLEET, TT_DOFFY, TT_BULL, TT_LOYAL, TT_IDTFR, TT_THEO, TT_HELM, TT_FOUR, TT_WHALE, TT_LOAD, TT_FIRE, TT_LEN, TT_LEAK, TT_SAIL, TT_PASS, TT_RBRACKET, TT_HOME]):return

    # 155 {“leak”}
    # 156 {“sail”}
    # 157 {“pass”}
    def control(self):
        if not self.consume([TT_LEAK, TT_SAIL, TT_PASS]):return

def analyze_syntax(tokens):
    syntax_analyzer = SyntaxAnalyzer(tokens)
    errors = syntax_analyzer.parse()
    # os.system("cls")
    if errors:
        return errors[0]     
    else:
        return "Syntax analysis successful"

# def analyze_syntax(tokens):
#     syntax_analyzer = SyntaxAnalyzer(tokens)
#     errors = syntax_analyzer.parse()
#     os.system("cls")
#     print("*------------------------------------------------------------------*")
#     if errors:
#         for error in errors:
#             print(error)
#     else:
#         print ("Syntax analysis successful")
#     print("*------------------------------------------------------------------*")

# tokens = [
#     Token(1, 'ONBOARD', 'Onboard'),
#     Token(2, 'PINT', 'pint'),
#     Token(2, 'IDENTIFIER', 'g'),
#     Token(2, 'ASSIGN', '='),
#     Token(2, 'PINT LIT', '1'), 
#     Token(2, 'SMCLN', ';'),
#     Token(3, 'DOFFY', 'doffy'),
#     Token(3, 'IDENTIFIER', 'name'),
#     Token(3, 'ASSIGN', '='),
#     Token(3, 'DOFFY LIT', 'luwesss'),
#     Token(3, 'SMCLN', ';'),
#     Token(4, 'CAPTAIN', 'captain'),
#     Token(4, 'LPAREN', '('),
#     Token(4, 'RPAREN', ')'),
#     Token(4, 'LBRACKET', '{'),
#     Token(5, 'PINT', 'pint'),
#     Token(5, 'IDENTIFIER', 'l'),
#     Token(5, 'ASSIGN', '='),
#     Token(5, 'PINT LIT', '1'),
#     Token(5, 'COMMA', ','),
#     Token(5, 'IDENTIFIER', 'll'),
#     Token(5, 'ASSIGN', '='),
#     Token(5, 'PINT LIT', '2'),
#     Token(5, 'SMCLN', ';'),
#     Token(6, 'RBRACKET', '}'),
#     Token(7, 'OFFBOARD', 'Offboard'),
# ]

# analyze_syntax(tokens)