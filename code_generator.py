from typing import List, Dict, Any, Optional
from parser import *
from symbol_table import SymbolTable
from dataclasses import dataclass

@dataclass
class Instruction:
    opcode: str
    operands: List[Any]
    line: int = 0
    column: int = 0
    
    def __str__(self):
        return f"{self.opcode} {' '.join(map(str, self.operands))}"

class CodeGenerationError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        if line and column:
            super().__init__(f"Code generation error at line {line}, column {column}: {message}")
        else:
            super().__init__(f"Code generation error: {message}")

class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.instructions = []
    
    def generate(self, ast: Program) -> List[Instruction]:
        """Generate code from AST"""
        self.instructions = []
        
        # Emit initial setup instructions
        self.emit('INIT')
        self.emit('SET_TEMPO', self.symbol_table.get_value('tempo'))
        self.emit('SET_VOLUME', self.symbol_table.get_value('volume'))
        self.emit('SET_INSTRUMENT', self.symbol_table.get_value('instrument'))
        
        self.visit_program(ast)
        
        # Emit cleanup instruction
        self.emit('END')
        
        return self.instructions
    
    def emit(self, opcode: str, *operands, line: int = 0, column: int = 0):
        """Emit an instruction"""
        instruction = Instruction(opcode, list(operands), line, column)
        self.instructions.append(instruction)
    
    def visit_program(self, node: Program):
        """Visit program node"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, stmt: ASTNode):
        """Visit statement node"""
        line = getattr(stmt, 'line', 0)
        column = getattr(stmt, 'column', 0)
        
        if isinstance(stmt, TempoStatement):
            self.emit('SET_TEMPO', stmt.bpm, line=line, column=column)
        elif isinstance(stmt, VolumeStatement):
            self.emit('SET_VOLUME', stmt.level, line=line, column=column)
        elif isinstance(stmt, InstrumentStatement):
            self.emit('SET_INSTRUMENT', stmt.name, line=line, column=column)
        elif isinstance(stmt, PlayStatement):
            duration = stmt.duration or self.symbol_table.get_value('duration')
            for note in stmt.notes:
                self.emit('PLAY_NOTE', note, duration, line=line, column=column)
        elif isinstance(stmt, ChordStatement):
            duration = stmt.duration or self.symbol_table.get_value('duration')
            self.emit('PLAY_CHORD', stmt.notes, duration, line=line, column=column)
        elif isinstance(stmt, RestStatement):
            self.emit('REST', stmt.duration, line=line, column=column)
        elif isinstance(stmt, RepeatStatement):
            self.emit('REPEAT_START', stmt.times, line=line, column=column)
            for sub_stmt in stmt.statements:
                self.visit_statement(sub_stmt)
            self.emit('REPEAT_END', line=line, column=column)
        else:
            raise CodeGenerationError(f"Unknown statement type: {type(stmt)}", line, column)
