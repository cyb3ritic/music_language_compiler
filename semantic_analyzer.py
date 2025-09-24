from typing import List, Set
from parser import *
from symbol_table import SymbolTable
import re

class SemanticError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        if line and column:
            super().__init__(f"Semantic error at line {line}, column {column}: {message}")
        else:
            super().__init__(f"Semantic error: {message}")

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.valid_instruments = ['sine', 'square', 'triangle', 'sawtooth', 'piano']
        self.note_pattern = re.compile(r'^[A-G][#b]?[0-9]$')
    
    def analyze(self, ast: Program) -> SymbolTable:
        """Analyze AST and return symbol table"""
        try:
            self.visit_program(ast)
        except SemanticError as e:
            self.errors.append(str(e))
        
        if self.errors:
            error_msg = '; '.join(self.errors)
            raise SemanticError(f"Semantic errors found: {error_msg}")
        
        return self.symbol_table
    
    def add_error(self, message: str, node: ASTNode = None):
        """Add error with optional location info"""
        error = SemanticError(message)
        self.errors.append(str(error))
    
    def visit_program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, stmt: ASTNode):
        """Visit statement node"""
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
        else:
            self.add_error(f"Unknown statement type: {type(stmt)}", stmt)
    
    def visit_tempo_statement(self, stmt: TempoStatement):
        """Validate tempo statement"""
        if stmt.bpm <= 0 or stmt.bpm > 300:
            self.add_error(f"Invalid tempo: {stmt.bpm}. Must be between 1 and 300 BPM.", stmt)
        else:
            self.symbol_table.set_value('tempo', stmt.bpm)
    
    def visit_volume_statement(self, stmt: VolumeStatement):
        """Validate volume statement"""
        if stmt.level < 0 or stmt.level > 1:
            self.add_error(f"Invalid volume: {stmt.level}. Must be between 0.0 and 1.0.", stmt)
        else:
            self.symbol_table.set_value('volume', stmt.level)
    
    def visit_instrument_statement(self, stmt: InstrumentStatement):
        """Validate instrument statement"""
        if stmt.name not in self.valid_instruments:
            self.add_error(
                f"Invalid instrument: '{stmt.name}'. Valid instruments: {self.valid_instruments}", 
                stmt
            )
        else:
            self.symbol_table.set_value('instrument', stmt.name)
    
    def visit_play_statement(self, stmt: PlayStatement):
        """Validate play statement"""
        if not stmt.notes:
            self.add_error("Play statement must have at least one note", stmt)
            return
        
        for note in stmt.notes:
            if not self.is_valid_note(note):
                self.add_error(f"Invalid note: '{note}'", stmt)
        
        if stmt.duration is not None and stmt.duration <= 0:
            self.add_error(f"Invalid duration: {stmt.duration}. Must be positive.", stmt)
    
    def visit_chord_statement(self, stmt: ChordStatement):
        """Validate chord statement"""
        if len(stmt.notes) < 2:
            self.add_error("Chord must contain at least 2 notes.", stmt)
            return
        
        if len(stmt.notes) > 6:
            self.add_error("Chord cannot contain more than 6 notes.", stmt)
        
        for note in stmt.notes:
            if not self.is_valid_note(note):
                self.add_error(f"Invalid note in chord: '{note}'", stmt)
        
        # Check for duplicate notes
        unique_notes = set(stmt.notes)
        if len(unique_notes) != len(stmt.notes):
            self.add_error("Chord contains duplicate notes", stmt)
        
        if stmt.duration is not None and stmt.duration <= 0:
            self.add_error(f"Invalid chord duration: {stmt.duration}. Must be positive.", stmt)
    
    def visit_rest_statement(self, stmt: RestStatement):
        """Validate rest statement"""
        if stmt.duration <= 0:
            self.add_error(f"Invalid rest duration: {stmt.duration}. Must be positive.", stmt)
        
        if stmt.duration > 16:  # Reasonable upper limit
            self.add_error(f"Rest duration too long: {stmt.duration}. Maximum is 16 beats.", stmt)
    
    def visit_repeat_statement(self, stmt: RepeatStatement):
        """Validate repeat statement"""
        if stmt.times <= 0:
            self.add_error(f"Invalid repeat count: {stmt.times}. Must be positive.", stmt)
        elif stmt.times > 100:  # Reasonable upper limit
            self.add_error(f"Repeat count too high: {stmt.times}. Maximum is 100.", stmt)
        
        if not stmt.statements:
            self.add_error("Repeat block cannot be empty", stmt)
        
        # Recursively validate statements in repeat block
        for sub_stmt in stmt.statements:
            self.visit_statement(sub_stmt)
    
    def is_valid_note(self, note: str) -> bool:
        """Validate note format (e.g., C4, F#3, Bb2)"""
        if not self.note_pattern.match(note):
            return False
        
        # Extract octave and validate range
        octave = int(note[-1])
        if octave < 0 or octave > 8:
            return False
        
        return True
