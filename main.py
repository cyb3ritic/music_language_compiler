#!/usr/bin/env python3
"""
Music Language Compiler
A complete compiler that translates a custom music language into playable audio files.
"""

import sys
import argparse
from pathlib import Path

from lexer import MusicLexer
from parser import MusicParser, ParseError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator
from audio_synthesizer import AudioSynthesizer

class MusicCompiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = None
        self.code_generator = None
        self.synthesizer = None
    
    def compile_file(self, input_file: str, output_file: str = None, audio_format: str = 'mp3'):
        """Compile music language file to audio"""
        try:
            # Phase 1: Lexical Analysis
            print("Phase 1: Lexical Analysis...")
            with open(input_file, 'r') as f:
                source_code = f.read()
            
            self.lexer = MusicLexer(source_code)
            tokens = self.lexer.tokenize()
            print(f"Generated {len(tokens)} tokens")
            
            # Phase 2: Syntax Analysis (Parsing)
            print("Phase 2: Syntax Analysis...")
            self.parser = MusicParser(tokens)
            ast = self.parser.parse()
            print("Abstract Syntax Tree generated successfully")
            
            # Phase 3: Semantic Analysis
            print("Phase 3: Semantic Analysis...")
            self.semantic_analyzer = SemanticAnalyzer()
            symbol_table = self.semantic_analyzer.analyze(ast)
            print("Semantic analysis completed successfully")
            
            # Phase 4: Code Generation
            print("Phase 4: Code Generation...")
            self.code_generator = CodeGenerator(symbol_table)
            instructions = self.code_generator.generate(ast)
            print(f"Generated {len(instructions)} instructions")
            
            # Phase 5: Audio Synthesis
            print("Phase 5: Audio Synthesis...")
            self.synthesizer = AudioSynthesizer()
            audio_data = self.synthesizer.synthesize(instructions)
            
            # Phase 6: Output Generation
            print("Phase 6: Output Generation...")
            if output_file is None:
                output_file = Path(input_file).stem + f'.{audio_format}'
            
            self.synthesizer.save_audio(audio_data, output_file, audio_format)
            print(f"Compilation successful! Output: {output_file}")
            
        except (ParseError, SemanticError) as e:
            print(f"Compilation Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    
    def compile_string(self, source_code: str, output_file: str = 'output.mp3', audio_format: str = 'mp3'):
        """Compile music language string to audio"""
        try:
            # All phases as above but with string input
            print("Compiling from string...")
            
            self.lexer = MusicLexer(source_code)
            tokens = self.lexer.tokenize()
            
            self.parser = MusicParser(tokens)
            ast = self.parser.parse()
            
            self.semantic_analyzer = SemanticAnalyzer()
            symbol_table = self.semantic_analyzer.analyze(ast)
            
            self.code_generator = CodeGenerator(symbol_table)
            instructions = self.code_generator.generate(ast)
            
            self.synthesizer = AudioSynthesizer()
            audio_data = self.synthesizer.synthesize(instructions)
            
            self.synthesizer.save_audio(audio_data, output_file, audio_format)
            print(f"Compilation successful! Output: {output_file}")
            
        except (ParseError, SemanticError) as e:
            print(f"Compilation Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
        return True

def create_example_program():
    """Create an example music program"""
    example_code = """
# Example Music Program
TEMPO = 120;
VOLUME = 0.8;
INSTRUMENT = "piano";

# Play a simple melody
PLAY C4 DURATION = 1;
PLAY D4 DURATION = 1;
PLAY E4 DURATION = 1;
PLAY F4 DURATION = 1;
PLAY G4 DURATION = 2;

# Rest for 1 beat
REST = 1;

# Play a chord
CHORD [C4, E4, G4] DURATION = 2;

# Repeat a pattern
REPEAT 2 {
    PLAY A4 DURATION = 0.5;
    PLAY G4 DURATION = 0.5;
    PLAY F4 DURATION = 0.5;
    PLAY E4 DURATION = 0.5;
}

# Change instrument and play final chord
INSTRUMENT = "sine";
CHORD [C4, E4, G4, C5] DURATION = 4;
"""
    return example_code

def main():
    parser = argparse.ArgumentParser(description='Music Language Compiler')
    parser.add_argument('input_file', nargs='?', help='Input music file (.mus)')
    parser.add_argument('-o', '--output', help='Output audio file')
    parser.add_argument('-f', '--format', choices=['mp3', 'wav', 'ogg'], 
                       default='mp3', help='Output audio format')
    parser.add_argument('--example', action='store_true', 
                       help='Generate and compile an example program')
    
    args = parser.parse_args()
    
    compiler = MusicCompiler()
    
    if args.example:
        print("Generating example program...")
        example_code = create_example_program()
        
        # Save example to file
        with open('example.mus', 'w') as f:
            f.write(example_code)
        print("Example saved as 'example.mus'")
        
        # Compile example
        output_file = args.output or f'example.{args.format}'
        compiler.compile_string(example_code, output_file, args.format)
        
    elif args.input_file:
        if not Path(args.input_file).exists():
            print(f"Error: Input file '{args.input_file}' not found")
            sys.exit(1)
        
        compiler.compile_file(args.input_file, args.output, args.format)
    else:
        print("Error: No input file specified. Use --example to generate an example.")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
