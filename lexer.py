import re
from tokens import *
from token_class import Token
from constants import *
from error_class import *
from position_class import *
import syntax

# LEXER CLASS

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
        self.identifier_pattern = re.compile(rf'^[{LETTER_A}][{ALPHA_NUM}_]{{0,14}}$')

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        errors = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in LETTER_A:
                isIDNTFR = True
                word = ''
                while self.current_char is not None and self.current_char in ALPHA_NUM or self.current_char == '_':
                    word += self.current_char
                    self.advance()

                # LETTER A
                if word[0] == 'a' and len(word) >= 2:
                    if word[1] == 'l' and len(word) >= 3:
                        if word[2] == 't':
                            if len(word) == 3:
                                if self.current_char != None and self.current_char in DELIM1:
                                    tokens.append(Token(self.pos.ln + 1, TT_ALT, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                            else:
                                if word[3] == 'h' and len(word) >= 5:
                                    if word[4] == 'e' and len(word) >= 6:
                                        if word[5] == 'o' and len(word) == 6:
                                            if self.current_char != None and self.current_char in DELIM2:
                                                tokens.append(Token(self.pos.ln + 1, TT_ALTHEO,word))
                                                isIDNTFR = False
                                            else:
                                                errors.append(LexicalError(self.pos.ln + 1, word))
                                                isIDNTFR = False
                    elif word[1] == 'n' and len(word) >= 3:
                        if word[2] == 'c' and len(word) >= 4:
                            if word[3] == 'h' and len(word) >= 5:
                                if word[4] == 'o' and len(word) >= 6:
                                    if word[5] == 'r' and len(word) == 6:
                                        if self.current_char != None and self.current_char in DELIM2:
                                            tokens.append(Token(self.pos.ln + 1, TT_ANCHOR,word))
                                            isIDNTFR = False
                                        else:
                                            errors.append(LexicalError(self.pos.ln + 1, word))
                                            isIDNTFR = False
                        elif word[2] == 'd' and len(word) == 3:
                            if self.current_char == ' ':
                                tokens.append(Token(self.pos.ln + 1, TT_AND, word))
                                isIDNTFR = False
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, word))
                                isIDNTFR = False

                # LETTER B
                if word[0] == 'b' and len(word) >= 2:
                    if word[1] == 'u' and len(word) >= 3:
                        if word[2] == 'l'and len(word) >= 4:
                            if word[3] == 'l' and len(word) == 4:
                                if self.current_char == ' ':
                                    tokens.append(Token(self.pos.ln + 1, TT_BULL, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER C
                if word[0] == 'c' and len(word) >= 2:
                    if word[1] == 'h' and len(word) >= 3:
                        if word[2] == 'e' and len(word) >= 4:
                            if word[3] == 's' and len(word) >= 5:
                                if word[4] == 't' and len(word) == 5:
                                    if self.current_char == ' ':
                                        tokens.append(Token(self.pos.ln + 1, TT_CHEST, word))
                                        isIDNTFR = False
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False
                    if word[1] == 'a' and len(word) >= 3:
                        if word[2] == 'p' and len(word) >= 4:
                            if word[3] == 't' and len(word) >= 5:
                                if word[4] == 'a' and len(word) >= 6:
                                    if word[5] == 'i' and len(word) >= 7:
                                        if word[6] == 'n' and len(word) == 7:
                                            if self.current_char != None and self.current_char in DELIM2:
                                                tokens.append(Token(self.pos.ln + 1, TT_CAPTAIN, word))
                                                isIDNTFR = False
                                            else:
                                                errors.append(LexicalError(self.pos.ln + 1, word))
                                                isIDNTFR = False

                # LETTER D
                if word[0] == 'd' and len(word) >= 2:
                    if word[1] == 'a' and len(word) >= 3:
                        if word[2] == 'g' and len(word) >= 4:
                            if word[3] == 'g' and len(word) >= 5:
                                if word[4] == 'e' and len(word) >= 6:
                                    if word[5] == 'r' and len(word) == 6:
                                        if self.current_char != None and self.current_char in DELIM14:
                                            tokens.append(Token(self.pos.ln + 1, TT_DAGGER, word))
                                            isIDNTFR = False
                                        else:
                                            errors.append(LexicalError(self.pos.ln + 1, word))
                                            isIDNTFR = False
                    elif word[1] == 'o' and len(word) >= 3:
                        if word[2] == 'f' and len(word) >= 4:
                            if word[3] == 'f' and len(word) >= 5:
                                if word[4] == 'y' and len(word) == 5:
                                    if self.current_char == ' ':
                                        tokens.append(Token(self.pos.ln + 1, TT_DOFFY, word))
                                        isIDNTFR = False   
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False                 

                # LETTER F
                if word[0] == 'f' and len(word) >= 2:
                    if word[1] == 'i' and len(word) >= 3:
                        if word[2] == 'r' and len(word) >= 4:
                            if word[3] == 'e' and len(word) == 4:
                                if self.current_char != None and self.current_char in DELIM2:
                                    tokens.append(Token(self.pos.ln + 1, TT_FIRE, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                    elif word[1] == 'l' and len(word) >= 3:
                        if word[2] == 'e' and len(word) >= 4:
                            if word[3] == 'e' and len(word) >= 5:
                                if word[4] == 't' and len(word) == 5:
                                    if self.current_char == ' ':
                                        tokens.append(Token(self.pos.ln + 1, TT_FLEET, word))
                                        isIDNTFR = False
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False
                    elif word[1] == 'o' and len(word) >= 3:
                        if word[2] == 'u' and len(word) >= 4:
                            if word[3] == 'r' and len(word) == 4:
                                if self.current_char != None and self.current_char in DELIM2:
                                    tokens.append(Token(self.pos.ln + 1, TT_FOUR, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER H
                if word[0] == 'h' and len(word) >= 2:
                    if word[1] == 'e' and len(word) >= 3:
                        if word[2] == 'l' and len(word) >= 4:
                            if word[3] == 'm' and len(word) == 4:
                                if self.current_char != None and self.current_char in DELIM2:
                                    tokens.append(Token(self.pos.ln + 1, TT_HELM, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                    elif word[1] == 'o' and len(word) >= 3:
                        if word[2] == 'm' and len(word) >= 4:
                            if word[3] == 'e' and len(word) == 4: 
                                if self.current_char != None and self.current_char in DELIM2:
                                    tokens.append(Token(self.pos.ln + 1, TT_HOME, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER L
                if word[0] == 'l' and len(word) >= 2:
                    if word[1] == 'e' and len(word) >= 3:
                        if word[2] == 'a' and len(word) >= 4:
                            if word[3] == 'k' and len(word) == 4:
                                if self.current_char == ';':
                                    tokens.append(Token(self.pos.ln + 1, TT_LEAK, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                        elif word[2] == 'n' and len(word) == 3:
                            if self.current_char == '(':
                                tokens.append(Token(self.pos.ln + 1, TT_LEN, word))
                                isIDNTFR = False
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, word))
                                isIDNTFR = False
                    elif word[1] == 'o' and len(word) >= 3:
                        if word[2] == 'a' and len(word) >= 4:
                            if word[3] == 'd' and len(word) == 4:
                                if self.current_char == '(':
                                    tokens.append(Token(self.pos.ln + 1, TT_LOAD, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                        elif word[2] == 'y' and len(word) >= 4:
                            if word[3] == 'a' and len(word) >= 5: 
                                if word[4] == 'l' and len(word) == 5: 
                                    if self.current_char == ' ':
                                        tokens.append(Token(self.pos.ln + 1, TT_LOYAL, word))
                                        isIDNTFR = False
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False

                # LETTER N
                if word[0] == 'n' and len(word) >= 2:
                    if word[1] == 'a' and len(word) >= 3:
                        if word[2] == 'y' and len(word) == 3:
                            if self.current_char == ' ':
                                tokens.append(Token(self.pos.ln + 1, TT_NAY, word))
                                isIDNTFR = False
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, word))
                                isIDNTFR = False
                
                # LETTER O
                if word[0] == 'o' and len(word) >= 2:
                    if word[1] == 'f' and len(word) >= 3:
                        if word[2] == 'f' and len(word) >= 4:
                            if word[3] == 'b' and len(word) >= 5:
                                if word[4] == 'o' and len(word) >= 6:
                                    if word[5] == 'a' and len(word) >= 7:
                                        if word[6] == 'r' and len(word) >= 8:
                                            if word[7] == 'd' and len(word) == 8:
                                                tokens.append(Token(self.pos.ln + 1, TT_OFFBOARD, word))
                                                isIDNTFR = False
                    elif word[1] == 'n' and len(word) >= 3:
                        if word[2] == 'b' and len(word) >= 4:
                            if word[3] == 'o' and len(word) >= 5:
                                if word[4] == 'a' and len(word) >= 6:
                                    if word[5] == 'r' and len(word) >= 7:
                                        if word[6] == 'd' and len(word) == 7:
                                            if self.current_char != None and self.current_char in DELIM4:
                                                tokens.append(Token(self.pos.ln + 1, TT_ONBOARD, word))
                                                isIDNTFR = False
                                            else:
                                                errors.append(LexicalError(self.pos.ln + 1, word))
                                                isIDNTFR = False
                    elif word[1] == 'r' and len(word) >= 3:
                        if word[2] == 'o' and len(word) == 3:
                            if self.current_char == ' ':
                                tokens.append(Token(self.pos.ln + 1, TT_ORO, word))
                                isIDNTFR = False
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, word))
                                isIDNTFR = False
                
                # LETTER P
                if word[0] == 'p' and len(word) >= 2:
                    if word[1] == 'a' and len(word) >= 3:
                        if word[2] == 's' and len(word) >= 4:
                            if word[3] == 's' and len(word) == 4:
                                if self.current_char == ';':
                                    tokens.append(Token(self.pos.ln + 1, TT_PASS, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                    elif word[1] == 'i' and len(word) >= 3:
                        if word[2] == 'n' and len(word) >= 4:
                            if word[3] == 't' and len(word) == 4:
                                if self.current_char == ' ':
                                    tokens.append(Token(self.pos.ln + 1, TT_PINT, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER R
                if word[0] == 'r' and len(word) >= 2:
                    if word[1] == 'e' and len(word) >= 3:
                        if word[2] == 'a' and len(word) >= 4:
                            if word[3] == 'l' and len(word) == 4:
                                if self.current_char != None and self.current_char in DELIM18:
                                    tokens.append(Token(self.pos.ln + 1, TT_REAL, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                
                # LETTER S
                if word[0] == 's' and len(word) >= 2:
                    if word[1] == 'a' and len(word) >= 3:
                        if word[2] == 'i' and len(word) >= 4:
                            if word[3] == 'l' and len(word) == 4:
                                if self.current_char == ';':
                                    tokens.append(Token(self.pos.ln + 1, TT_SAIL, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False
                
                # LETTER T
                if word[0] == 't' and len(word) >= 2:
                    if word[1] == 'h' and len(word) >= 3:
                        if word[2] == 'e' and len(word) >= 4:
                            if word[3] == 'o' and len(word) == 4:
                                if self.current_char != None and self.current_char in DELIM2:
                                    tokens.append(Token(self.pos.ln + 1, TT_THEO, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER U
                if word[0] == 'u' and len(word) >= 2:
                    if word[1] == 's' and len(word) >= 3:
                        if word[2] == 'o' and len(word) >= 4:
                            if word[3] == 'p' and len(word) >= 5:
                                if word[4] == 'p' and len(word) == 5:
                                    if self.current_char != None and self.current_char in DELIM18:
                                        tokens.append(Token(self.pos.ln + 1, TT_USOPP, word))
                                        isIDNTFR = False
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False

                # LETTER V
                if word[0] == 'v' and len(word) >= 2:
                    if word[1] == 'o' and len(word) >= 3:
                        if word[2] == 'i' and len(word) >= 4:
                            if word[3] == 'd' and len(word) == 4:
                                if self.current_char == ' ':
                                    tokens.append(Token(self.pos.ln + 1, TT_VOID, word))
                                    isIDNTFR = False
                                else:
                                    errors.append(LexicalError(self.pos.ln + 1, word))
                                    isIDNTFR = False

                # LETTER W
                if word[0] == 'w' and len(word) >= 2:
                    if word[1] == 'h' and len(word) >= 3:
                        if word[2] == 'a' and len(word) >= 4:
                            if word[3] == 'l' and len(word) >= 5:
                                if word[4] == 'e' and len(word) == 5:
                                    if self.current_char != None and self.current_char in DELIM2:
                                        tokens.append(Token(self.pos.ln + 1, TT_WHALE, word))
                                        isIDNTFR = False
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, word))
                                        isIDNTFR = False
                
                # IDENTIFIER
                if self.identifier_pattern.match(word):
                    if isIDNTFR and self.current_char != None and self.current_char in DELIMID:
                        tokens.append(Token(self.pos.ln + 1, TT_IDTFR, word))
                    elif isIDNTFR:
                        errors.append(LexicalError(self.pos.ln + 1, word))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, word))
            elif self.current_char == '+':
                self.advance()
                if self.current_char == '+':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM13:
                        tokens.append(Token(self.pos.ln + 1, TT_INCR, '++'))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "++"))
                elif self.current_char != None and self.current_char in DELIM6:
                    tokens.append(Token(self.pos.ln + 1, TT_PLUS, '+'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "+"))
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '-':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM13:
                        tokens.append(Token(self.pos.ln + 1, TT_DECR, '--'))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "--"))
                elif self.current_char != None and self.current_char in DELIM15:
                    tokens.append(Token(self.pos.ln + 1, TT_MINUS, '-'))
                elif self.current_char in NUMERIC:
                    num_str = '-'
                    dot_count = 0
                    if self.current_char in NUM:
                        num_str += self.current_char
                        self.advance()
                        while self.current_char in NUMERIC and len(num_str) != 14:
                            num_str += self.current_char
                            self.advance()
                        if self.current_char in DELIM10:
                            tokens.append(Token(self.pos.ln + 1, TT_PINT_LIT, num_str))
                        elif self.current_char == ".":
                            num_str += self.current_char
                            dot_count+=1
                            self.advance()
                            if self.current_char in NUMERIC:
                                num_str += self.current_char
                                self.advance()
                                for i in range(7):
                                    if self.current_char in NUMERIC and i < 6:
                                        num_str += self.current_char
                                        self.advance()
                                    elif self.current_char in DELIM10 and i == 6:
                                        tokens.append(Token(self.pos.ln + 1, TT_FLEET_LIT, num_str))
                                        break
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, num_str))
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, num_str))
                        else:
                            errors.append(LexicalError(self.pos.ln + 1, num_str))
                    elif self.current_char == '0':
                        num_str += self.current_char
                        self.advance()
                        if self.current_char in DELIM10:
                            tokens.append(Token(self.pos.ln + 1, TT_PINT_LIT, '0'))
                        elif self.current_char == ".":
                            num_str += self.current_char
                            dot_count+=1
                            self.advance()
                            if self.current_char in NUMERIC:
                                num_str += self.current_char
                                self.advance()
                                for i in range(7):
                                    if self.current_char in NUMERIC and i < 6:
                                        num_str += self.current_char
                                        self.advance()
                                    elif self.current_char in DELIM10 and i == 6:
                                        tokens.append(Token(self.pos.ln + 1, TT_FLEET_LIT, float(num_str)))
                                    else:
                                        errors.append(LexicalError(self.pos.ln + 1, num_str))
                            else:
                                errors.append(LexicalError(self.pos.ln + 1, num_str))
                        else:
                            errors.append(LexicalError(self.pos.ln + 1, num_str))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "-"))
            elif self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM5:
                        tokens.append(Token(self.pos.ln + 1, TT_EXPONENT, '**'))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "**"))
                elif self.current_char != None and self.current_char in DELIM5:
                    tokens.append(Token(self.pos.ln + 1, TT_MUL, '*'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "*"))
            elif self.current_char == '/':
                self.advance()
                if self.current_char == '/':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM5:
                        tokens.append(Token(self.pos.ln + 1, TT_FDIV, '//'))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "//"))
                elif self.current_char != None and self.current_char in DELIM5:
                    tokens.append(Token(self.pos.ln + 1, TT_DIV, '/'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "/"))
            elif self.current_char == '%':
                self.advance()
                if self.current_char != None and self.current_char in DELIM5:
                    tokens.append(Token(self.pos.ln + 1, TT_MOD, '%'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "%"))
            elif self.current_char == '(':
                self.advance()
                if self.current_char != None and self.current_char in DELIM16:
                    tokens.append(Token(self.pos.ln + 1, TT_LPAREN, '('))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "("))
            elif self.current_char == ')':
                self.advance()
                if self.current_char != None and self.current_char in DELIM7:
                    tokens.append(Token(self.pos.ln + 1, TT_RPAREN, ')'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, ")"))
            elif self.current_char == '{':
                self.advance()
                if self.current_char != None and self.current_char in DELIM17:
                    tokens.append(Token(self.pos.ln + 1, TT_LBRACKET, '{'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "{"))
            elif self.current_char == '}':
                self.advance()
                if self.current_char != None and self.current_char in DELIM4:
                    tokens.append(Token(self.pos.ln + 1, TT_RBRACKET, '}'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "}"))
            elif self.current_char == '[':
                self.advance()
                if self.current_char != None and self.current_char in DELIM6:
                    tokens.append(Token(self.pos.ln + 1, TT_LSBRACKET, '['))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "["))
            elif self.current_char == ']':
                self.advance()
                if self.current_char != None and self.current_char in DELIM7:
                    tokens.append(Token(self.pos.ln + 1, TT_RSBRACKET, ']'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "]"))
            elif self.current_char == ';':
                tokens.append(Token(self.pos.ln + 1, TT_SMCLN, ';'))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(self.pos.ln + 1, TT_CLN, ':'))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(self.pos.ln + 1, TT_COMMA, ','))
                self.advance()
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    if self.current_char in DELIM6:
                        tokens.append(Token(self.pos.ln + 1, TT_EQUAL, '=='))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "=="))
                elif self.current_char in DELIM6:
                    tokens.append(Token(self.pos.ln + 1, TT_ASSIGN, '='))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "="))
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM6:
                        tokens.append(Token(self.pos.ln + 1, TT_NOTEQUAL, '!='))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "!="))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "!"))                    
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM6:
                        tokens.append(Token(self.pos.ln + 1, TT_LEQUAL, '<='))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, "<="))
                elif self.current_char != None and self.current_char in DELIM9:
                    tokens.append(Token(self.pos.ln + 1, TT_LTHAN, '<'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, "<"))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    if self.current_char != None and self.current_char in DELIM6:
                        tokens.append(Token(self.pos.ln + 1, TT_GEQUAL, '>='))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, ">="))
                elif self.current_char != None and self.current_char in DELIM9:
                    tokens.append(Token(self.pos.ln + 1, TT_GTHAN, '>'))
                else:
                    errors.append(LexicalError(self.pos.ln + 1, ">"))
            elif self.current_char == '"':
                string = ''
                escape = False
                isValidString = False
                self.advance() 

                while self.current_char is not None:
                    if escape:
                        if self.current_char == 'n':
                            string += '\n'
                        else:
                            string += self.current_char
                        escape = False
                    elif self.current_char == '\\':
                        escape = True
                    elif self.current_char == '"':
                        self.advance()
                        tokens.append(Token(self.pos.ln + 1, TT_DOFFY_LIT, '"' + string + '"')) 
                        isValidString = True
                        break
                    else:
                        string += self.current_char
                    self.advance()
                
                if isValidString == False:
                    errors.append(LexicalError(self.pos.ln + 1, string))
            elif self.current_char == "`":
                string = ''
                escape = False
                isValidString = False
                self.advance() 

                while self.current_char is not None:
                    if escape:
                        if self.current_char == 'n':
                            string += '\n'
                        else:
                            string += self.current_char
                        escape = False
                    elif self.current_char == '\\':
                        escape = True
                    elif self.current_char == "`":
                        self.advance()
                        tokens.append(Token(self.pos.ln + 1, TT_DOFFY_LIT, "`" + string + "`")) 
                        isValidString = True
                        break
                    else:
                        string += self.current_char
                    self.advance()
                
                if isValidString == False:
                    errors.append(LexicalError(self.pos.ln + 1, string))
            elif self.current_char in NUMERIC:
                num_str = ''
                dot_count = 0
                if self.current_char in NUM:
                    num_str += self.current_char
                    self.advance()
                    while self.current_char in NUMERIC and len(num_str) != 14:
                        num_str += self.current_char
                        self.advance()
                    if self.current_char in DELIM10:
                        tokens.append(Token(self.pos.ln + 1, TT_PINT_LIT, int(num_str)))
                    elif self.current_char == ".":
                        num_str += self.current_char
                        dot_count+=1
                        self.advance()
                        if self.current_char in NUMERIC:
                            num_str += self.current_char
                            isValidNum = False
                            self.advance()
                            for i in range(7):
                                if self.current_char in NUMERIC and i < 6:
                                    num_str += self.current_char
                                    self.advance()
                                elif self.current_char in DELIM10 and i == 6:
                                    tokens.append(Token(self.pos.ln + 1, TT_FLEET_LIT, float(num_str)))
                                    isValidNum = True
                                    break
                            if not isValidNum:
                                errors.append(LexicalError(self.pos.ln + 1, num_str))
                        else:
                            errors.append(LexicalError(self.pos.ln + 1, num_str))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, num_str))
                elif self.current_char == '0':
                    num_str += self.current_char
                    self.advance()
                    if self.current_char in DELIM10:
                        tokens.append(Token(self.pos.ln + 1, TT_PINT_LIT, '0'))
                    elif self.current_char == ".":
                        num_str += self.current_char
                        dot_count+=1
                        self.advance()
                        if self.current_char in NUMERIC:
                            num_str += self.current_char
                            isValidNum = False
                            self.advance()
                            for i in range(7):
                                if self.current_char in NUMERIC and i < 6:
                                    num_str += self.current_char
                                    self.advance()
                                elif self.current_char in DELIM10 and i == 6:
                                    tokens.append(Token(self.pos.ln + 1, TT_FLEET_LIT, float(num_str)))
                                    isValidNum = True
                                    break
                            if not isValidNum:
                                errors.append(LexicalError(self.pos.ln + 1, num_str))
                        else:
                            errors.append(LexicalError(self.pos.ln + 1, num_str))
                    else:
                        errors.append(LexicalError(self.pos.ln + 1, num_str))
            elif self.current_char == '#':
                comment_value = '#'
                self.advance()
                if self.current_char == '#':
                    while self.current_char is not None:
                        if self.current_char == "#":
                            comment_value += self.current_char
                            self.advance()
                            if self.current_char == "#":
                                comment_value += self.current_char
                                tokens.append(Token(self.pos.ln + 1, TT_MLCOMMENT, comment_value))
                                break
                            else:
                                comment_value += self.current_char
                                self.advance()
                        else:
                            comment_value += self.current_char
                            self.advance()
                else:
                    while self.current_char is not None and self.current_char != '\n':
                        comment_value += self.current_char
                        self.advance()
                    tokens.append(Token(self.pos.ln + 1, TT_SLCOMMENT, comment_value))
                self.advance() 
            elif self.current_char == '\n':
                self.advance()
            else: 
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                errors.append(LexicalError(self.pos.ln + 1, char))

        return tokens, errors

# (run)

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

def analyze_text(input_text):
    result, error = run('<stdin>', input_text)
    return result, error