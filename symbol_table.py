from typing import Dict, Any, Optional, Set

class Symbol:
    def __init__(self, name: str, symbol_type: str, value: Any = None):
        self.name = name
        self.type = symbol_type
        self.value = value
    
    def __str__(self):
        return f"Symbol({self.name}: {self.type} = {self.value})"
    
    def __repr__(self):
        return self.__str__()

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.defaults = {
            'tempo': 120.0,
            'volume': 0.5,
            'instrument': 'sine',
            'duration': 1.0
        }
        # Initialize with defaults
        for name, value in self.defaults.items():
            self.define(name, 'default', value)
    
    def define(self, name: str, symbol_type: str, value: Any = None):
        """Define a new symbol"""
        self.symbols[name] = Symbol(name, symbol_type, value)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol by name"""
        return self.symbols.get(name)
    
    def exists(self, name: str) -> bool:
        """Check if symbol exists"""
        return name in self.symbols
    
    def get_value(self, name: str, default: Any = None) -> Any:
        """Get symbol value with fallback to default"""
        symbol = self.lookup(name)
        if symbol:
            return symbol.value
        return self.defaults.get(name, default)
    
    def set_value(self, name: str, value: Any):
        """Set symbol value, creating if necessary"""
        if name in self.symbols:
            self.symbols[name].value = value
        else:
            self.define(name, 'variable', value)
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols"""
        return self.symbols.copy()
    
    def clear(self):
        """Clear all symbols and reset to defaults"""
        self.symbols.clear()
        for name, value in self.defaults.items():
            self.define(name, 'default', value)
