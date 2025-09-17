from typing import List, Dict, Any
from parser import *
from symbol_table import SymbolTable
from dataclasses import dataclass

@dataclass
class Instruction:
    opcode: str
    operands: List[Any]

class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.instructions = []
    
    def generate(self, ast: Program) -> List[Instruction]:
        self.visit_program(ast)
        return self.instructions
    
    def emit(self, opcode: str, *operands):
        self.instructions.append(Instruction(opcode, list(operands)))
    
    def visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, stmt: ASTNode):
        if isinstance(stmt, TempoStatement):
            self.emit('SET_TEMPO', stmt.bpm)
        elif isinstance(stmt, VolumeStatement):
            self.emit('SET_VOLUME', stmt.level)
        elif isinstance(stmt, InstrumentStatement):
            self.emit('SET_INSTRUMENT', stmt.name)
        elif isinstance(stmt, PlayStatement):
            duration = stmt.duration or self.symbol_table.get_value('duration')
            for note in stmt.notes:
                self.emit('PLAY_NOTE', note, duration)
        elif isinstance(stmt, ChordStatement):
            duration = stmt.duration or self.symbol_table.get_value('duration')
            self.emit('PLAY_CHORD', stmt.notes, duration)
        elif isinstance(stmt, RestStatement):
            self.emit('REST', stmt.duration)
        elif isinstance(stmt, RepeatStatement):
            self.emit('REPEAT_START', stmt.times)
            for sub_stmt in stmt.statements:
                self.visit_statement(sub_stmt)
            self.emit('REPEAT_END')
