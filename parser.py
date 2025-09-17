from typing import List, Optional, Any, Dict
from lexer import Token, TokenType, MusicLexer
from dataclasses import dataclass

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class PlayStatement(ASTNode):
    notes: List[str]
    duration: Optional[float] = None

@dataclass
class TempoStatement(ASTNode):
    bpm: float

@dataclass
class VolumeStatement(ASTNode):
    level: float

@dataclass
class InstrumentStatement(ASTNode):
    name: str

@dataclass
class ChordStatement(ASTNode):
    notes: List[str]
    duration: Optional[float] = None

@dataclass
class RestStatement(ASTNode):
    duration: float

@dataclass
class RepeatStatement(ASTNode):
    times: int
    statements: List[ASTNode]

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
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        if self.current_token.type != token_type:
            raise ParseError(f"Expected {token_type.value}, got {self.current_token.type.value}", 
                           self.current_token)
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
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
            raise ParseError(f"Unexpected token: {self.current_token.type.value}", self.current_token)
    
    def parse_play_statement(self) -> PlayStatement:
        self.expect(TokenType.PLAY)
        
        notes = []
        duration = None
        
        if self.current_token.type == TokenType.NOTE:
            notes.append(self.current_token.value)
            self.advance()
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.NOTE:
                    notes.append(self.current_token.value)
                    self.advance()
        
        # Check for duration
        if self.current_token.type == TokenType.DURATION:
            self.advance()
            self.expect(TokenType.EQUALS)
            duration_token = self.expect(TokenType.NUMBER)
            duration = float(duration_token.value)
        
        self.expect(TokenType.SEMICOLON)
        return PlayStatement(notes, duration)
    
    def parse_tempo_statement(self) -> TempoStatement:
        self.expect(TokenType.TEMPO)
        self.expect(TokenType.EQUALS)
        bpm_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return TempoStatement(float(bpm_token.value))
    
    def parse_volume_statement(self) -> VolumeStatement:
        self.expect(TokenType.VOLUME)
        self.expect(TokenType.EQUALS)
        volume_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return VolumeStatement(float(volume_token.value))
    
    def parse_instrument_statement(self) -> InstrumentStatement:
        self.expect(TokenType.INSTRUMENT)
        self.expect(TokenType.EQUALS)
        instrument_token = self.expect(TokenType.STRING)
        self.expect(TokenType.SEMICOLON)
        return InstrumentStatement(instrument_token.value.strip('"'))
    
    def parse_chord_statement(self) -> ChordStatement:
        self.expect(TokenType.CHORD)
        self.expect(TokenType.LBRACKET)
        
        notes = []
        if self.current_token.type == TokenType.NOTE:
            notes.append(self.current_token.value)
            self.advance()
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.NOTE:
                    notes.append(self.current_token.value)
                    self.advance()
        
        self.expect(TokenType.RBRACKET)
        
        duration = None
        if self.current_token.type == TokenType.DURATION:
            self.advance()
            self.expect(TokenType.EQUALS)
            duration_token = self.expect(TokenType.NUMBER)
            duration = float(duration_token.value)
        
        self.expect(TokenType.SEMICOLON)
        return ChordStatement(notes, duration)
    
    def parse_rest_statement(self) -> RestStatement:
        self.expect(TokenType.REST)
        self.expect(TokenType.EQUALS)
        duration_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SEMICOLON)
        return RestStatement(float(duration_token.value))
    
    def parse_repeat_statement(self) -> RepeatStatement:
        self.expect(TokenType.REPEAT)
        times_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.LBRACE)
        
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            if self.current_token.type == TokenType.RBRACE:
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return RepeatStatement(int(times_token.value), statements)
