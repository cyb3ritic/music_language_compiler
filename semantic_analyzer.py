from typing import List
from parser import *
from symbol_table import SymbolTable

class SemanticError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, ast: Program) -> SymbolTable:
        try:
            self.visit_program(ast)
        except SemanticError as e:
            self.errors.append(str(e))
        
        if self.errors:
            raise SemanticError(f"Semantic errors found: {'; '.join(self.errors)}")
        
        return self.symbol_table
    
    def visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, stmt: ASTNode):
        if isinstance(stmt, TempoStatement):
            self.visit_tempo_statement(stmt)
        elif isinstance(stmt, VolumeStatement):
            self.visit_volume_statement(stmt)
        elif isinstance(stmt, InstrumentStatement):
            self.visit_instrument_statement(stmt)
        elif isinstance(stmt, PlayStatement):
            self.visit_play_statement(stmt)
        elif isinstance(stmt, ChordStatement):
            self.visit_chord_statement(stmt)
        elif isinstance(stmt, RestStatement):
            self.visit_rest_statement(stmt)
        elif isinstance(stmt, RepeatStatement):
            self.visit_repeat_statement(stmt)
    
    def visit_tempo_statement(self, stmt: TempoStatement):
        if stmt.bpm <= 0 or stmt.bpm > 300:
            raise SemanticError(f"Invalid tempo: {stmt.bpm}. Must be between 1 and 300 BPM.")
        self.symbol_table.set_value('tempo', stmt.bpm)
    
    def visit_volume_statement(self, stmt: VolumeStatement):
        if stmt.level < 0 or stmt.level > 1:
            raise SemanticError(f"Invalid volume: {stmt.level}. Must be between 0.0 and 1.0.")
        self.symbol_table.set_value('volume', stmt.level)
    
    def visit_instrument_statement(self, stmt: InstrumentStatement):
        valid_instruments = ['sine', 'square', 'triangle', 'sawtooth', 'piano']
        if stmt.name not in valid_instruments:
            raise SemanticError(f"Invalid instrument: {stmt.name}. Valid instruments: {valid_instruments}")
        self.symbol_table.set_value('instrument', stmt.name)
    
    def visit_play_statement(self, stmt: PlayStatement):
        for note in stmt.notes:
            if not self.is_valid_note(note):
                raise SemanticError(f"Invalid note: {note}")
        
        if stmt.duration is not None and stmt.duration <= 0:
            raise SemanticError(f"Invalid duration: {stmt.duration}. Must be positive.")
    
    def visit_chord_statement(self, stmt: ChordStatement):
        if len(stmt.notes) < 2:
            raise SemanticError("Chord must contain at least 2 notes.")
        
        for note in stmt.notes:
            if not self.is_valid_note(note):
                raise SemanticError(f"Invalid note in chord: {note}")
        
        if stmt.duration is not None and stmt.duration <= 0:
            raise SemanticError(f"Invalid chord duration: {stmt.duration}. Must be positive.")
    
    def visit_rest_statement(self, stmt: RestStatement):
        if stmt.duration <= 0:
            raise SemanticError(f"Invalid rest duration: {stmt.duration}. Must be positive.")
    
    def visit_repeat_statement(self, stmt: RepeatStatement):
        if stmt.times <= 0:
            raise SemanticError(f"Invalid repeat count: {stmt.times}. Must be positive.")
        
        for sub_stmt in stmt.statements:
            self.visit_statement(sub_stmt)
    
    def is_valid_note(self, note: str) -> bool:
        """Validate note format (e.g., C4, F#3, Bb2)"""
        import re
        pattern = r'^[A-G][#b]?[0-9]$'
        return bool(re.match(pattern, note))
