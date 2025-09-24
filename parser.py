from typing import List, Optional, Any, Dict
from lexer import Token, TokenType, MusicLexer
from dataclasses import dataclass, field

@dataclass
class ASTNode:
    """Base AST Node"""
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

@dataclass
class PlayStatement(ASTNode):
    notes: List[str] = field(default_factory=list)
    duration: Optional[float] = None

@dataclass
class TempoStatement(ASTNode):
    bpm: float = 0.0

@dataclass
class VolumeStatement(ASTNode):
    level: float = 0.0

@dataclass
class InstrumentStatement(ASTNode):
    name: str = ""

@dataclass
class ChordStatement(ASTNode):
    notes: List[str] = field(default_factory=list)
    duration: Optional[float] = None

@dataclass
class RestStatement(ASTNode):
    duration: float = 0.0

@dataclass
class RepeatStatement(ASTNode):
    times: int = 0
    statements: List[ASTNode] = field(default_factory=list)

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")

class MusicParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to next token"""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at tokens"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        if not self.current_token:
            raise ParseError(f"Expected {token_type.value}, got EOF", 
                           Token(TokenType.EOF, '', 0, 0))
        
        if self.current_token.type != token_type:
            raise ParseError(f"Expected {token_type.value}, got {self.current_token.type.value}",
                           self.current_token)
        
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self):
        """Skip newline tokens"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """Parse the token stream into an AST"""
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            
            if self.current_token.type == TokenType.EOF:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        if not self.current_token:
            return None
        
        if self.current_token.type == TokenType.PLAY:
            return self.parse_play_statement()
        elif self.current_token.type == TokenType.TEMPO:
            return self.parse_tempo_statement()
        elif self.current_token.type == TokenType.VOLUME:
            return self.parse_volume_statement()
        elif self.current_token.type == TokenType.INSTRUMENT:
            return self.parse_instrument_statement()
        elif self.current_token.type == TokenType.CHORD:
            return self.parse_chord_statement()
        elif self.current_token.type == TokenType.REST:
            return self.parse_rest_statement()
        elif self.current_token.type == TokenType.REPEAT:
            return self.parse_repeat_statement()
        else:
            raise ParseError(f"Unexpected token: {self.current_token.type.value}", 
                           self.current_token)
    
    def parse_play_statement(self) -> PlayStatement:
        """Parse PLAY statement"""
        self.expect(TokenType.PLAY)
        
        notes = []
        duration = None
        
        # Parse first note
        if self.current_token and self.current_token.type == TokenType.NOTE:
            notes.append(self.current_token.value)
            self.advance()
        else:
            raise ParseError("Expected note after PLAY", self.current_token or Token(TokenType.EOF, '', 0, 0))
        
        # Parse additional notes (for multiple notes in sequence)
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.NOTE:
                notes.append(self.current_token.value)
                self.advance()
            else:
                raise ParseError("Expected note after comma", self.current_token or Token(TokenType.EOF, '', 0, 0))
        
        # Parse optional duration
        if self.current_token and self.current_token.type == TokenType.DURATION:
            self.advance()
            self.expect(TokenType.EQUALS)
            duration_token = self.expect(TokenType.NUMBER)
            duration = float(duration_token.value)
        
        self.expect(TokenType.SEMICOLON)
        return PlayStatement(notes, duration)
    
    def parse_tempo_statement(self) -> TempoStatement:
        """Parse TEMPO statement"""
        self.expect(TokenType.TEMPO)
        self.expect(TokenType.EQUALS)
        bpm_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return TempoStatement(float(bpm_token.value))
    
    def parse_volume_statement(self) -> VolumeStatement:
        """Parse VOLUME statement"""
        self.expect(TokenType.VOLUME)
        self.expect(TokenType.EQUALS)
        volume_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return VolumeStatement(float(volume_token.value))
    
    def parse_instrument_statement(self) -> InstrumentStatement:
        """Parse INSTRUMENT statement"""
        self.expect(TokenType.INSTRUMENT)
        self.expect(TokenType.EQUALS)
        instrument_token = self.expect(TokenType.STRING)
        self.expect(TokenType.SEMICOLON)
        return InstrumentStatement(instrument_token.value.strip('"\''))
    
    def parse_chord_statement(self) -> ChordStatement:
        """Parse CHORD statement"""
        self.expect(TokenType.CHORD)
        self.expect(TokenType.LBRACKET)
        
        notes = []
        
        # Parse first note
        if self.current_token and self.current_token.type == TokenType.NOTE:
            notes.append(self.current_token.value)
            self.advance()
        else:
            raise ParseError("Expected note in chord", self.current_token or Token(TokenType.EOF, '', 0, 0))
        
        # Parse additional notes
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.NOTE:
                notes.append(self.current_token.value)
                self.advance()
            else:
                raise ParseError("Expected note after comma in chord", self.current_token or Token(TokenType.EOF, '', 0, 0))
        
        self.expect(TokenType.RBRACKET)
        
        # Parse optional duration
        duration = None
        if self.current_token and self.current_token.type == TokenType.DURATION:
            self.advance()
            self.expect(TokenType.EQUALS)
            duration_token = self.expect(TokenType.NUMBER)
            duration = float(duration_token.value)
        
        self.expect(TokenType.SEMICOLON)
        return ChordStatement(notes, duration)
    
    def parse_rest_statement(self) -> RestStatement:
        """Parse REST statement"""
        self.expect(TokenType.REST)
        self.expect(TokenType.EQUALS)
        duration_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return RestStatement(float(duration_token.value))
    
    def parse_repeat_statement(self) -> RepeatStatement:
        """Parse REPEAT statement"""
        self.expect(TokenType.REPEAT)
        times_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.LBRACE)
        
        statements = []
        
        while (self.current_token and 
               self.current_token.type != TokenType.RBRACE and 
               self.current_token.type != TokenType.EOF):
            
            self.skip_newlines()
            
            if not self.current_token or self.current_token.type == TokenType.RBRACE:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return RepeatStatement(int(float(times_token.value)), statements)
