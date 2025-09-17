import re
from enum import Enum
from typing import List, NamedTuple

class TokenType(Enum):
    # Keywords
    PLAY = 'PLAY'
    TEMPO = 'TEMPO'
    VOLUME = 'VOLUME'
    INSTRUMENT = 'INSTRUMENT'
    DURATION = 'DURATION'
    REPEAT = 'REPEAT'
    CHORD = 'CHORD'
    REST = 'REST'
    
    # Notes
    NOTE = 'NOTE'
    
    # Literals
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    
    # Operators and Punctuation
    EQUALS = '='
    SEMICOLON = ';'
    COMMA = ','
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    LBRACKET = '['
    RBRACKET = ']'
    
    # Special
    NEWLINE = 'NEWLINE'
    EOF = 'EOF'
    INVALID = 'INVALID'

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class MusicLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Define token patterns
        self.token_patterns = [
            (r'#.*', None),  # Comments
            (r'\n', TokenType.NEWLINE),
            (r'\s+', None),  # Whitespace
            (r'\bPLAY\b', TokenType.PLAY),
            (r'\bTEMPO\b', TokenType.TEMPO),
            (r'\bVOLUME\b', TokenType.VOLUME),
            (r'\bINSTRUMENT\b', TokenType.INSTRUMENT),
            (r'\bDURATION\b', TokenType.DURATION),
            (r'\bREPEAT\b', TokenType.REPEAT),
            (r'\bCHORD\b', TokenType.CHORD),
            (r'\bREST\b', TokenType.REST),
            (r'\b[A-G][#b]?[0-9]\b', TokenType.NOTE),  # Notes like C4, F#3, Bb2
            (r'\d+\.?\d*', TokenType.NUMBER),
            (r'"[^"]*"', TokenType.STRING),
            (r'=', TokenType.EQUALS),
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
        ]
        
        self.compiled_patterns = [(re.compile(pattern), token_type) 
                                 for pattern, token_type in self.token_patterns]
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            match_found = False
            
            for pattern, token_type in self.compiled_patterns:
                match = pattern.match(self.text, self.pos)
                if match:
                    value = match.group(0)
                    
                    if token_type is not None:  # Skip comments and whitespace
                        if token_type == TokenType.NEWLINE:
                            self.tokens.append(Token(token_type, value, self.line, self.column))
                            self.line += 1
                            self.column = 1
                        else:
                            self.tokens.append(Token(token_type, value, self.line, self.column))
                            self.column += len(value)
                    else:
                        if value == '\n':
                            self.line += 1
                            self.column = 1
                        else:
                            self.column += len(value)
                    
                    self.pos = match.end()
                    match_found = True
                    break
            
            if not match_found:
                # Invalid character
                char = self.text[self.pos]
                self.tokens.append(Token(TokenType.INVALID, char, self.line, self.column))
                self.pos += 1
                self.column += 1
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
