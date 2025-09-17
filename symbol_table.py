from typing import Dict, Any, Optional

class Symbol:
    def __init__(self, name: str, symbol_type: str, value: Any = None):
        self.name = name
        self.type = symbol_type
        self.value = value

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.defaults = {
            'tempo': 120.0,
            'volume': 0.5,
            'instrument': 'sine',
            'duration': 1.0
        }
    
    def define(self, name: str, symbol_type: str, value: Any = None):
        self.symbols[name] = Symbol(name, symbol_type, value)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    
    def get_value(self, name: str, default: Any = None) -> Any:
        symbol = self.lookup(name)
        if symbol:
            return symbol.value
        return self.defaults.get(name, default)
    
    def set_value(self, name: str, value: Any):
        if name in self.symbols:
            self.symbols[name].value = value
        else:
            self.define(name, 'variable', value)
