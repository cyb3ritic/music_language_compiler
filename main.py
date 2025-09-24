#!/usr/bin/env python3

"""
Music Language Compiler

A complete compiler that translates a custom music language into playable audio files.
Outputs only WAV format to avoid external dependencies.
"""

import sys
import argparse
import traceback
from pathlib import Path
from typing import Optional

# Import our modules
from lexer import MusicLexer, LexError
from parser import MusicParser, ParseError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator, CodeGenerationError
from audio_synthesizer import AudioSynthesizer, SynthesisError

class MusicCompiler:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = None
        self.code_generator = None
        self.synthesizer = None
    
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def compile_file(self, input_file: str, output_file: str = None) -> bool:
        """Compile music language file to audio"""
        try:
            # Validate input file
            input_path = Path(input_file)
            if not input_path.exists():
                print(f"Error: Input file '{input_file}' not found")
                return False
            
            # Read source code
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            except Exception as e:
                print(f"Error reading file '{input_file}': {e}")
                return False
            
            return self.compile_string(source_code, output_file)
            
        except Exception as e:
            print(f"Unexpected error during file compilation: {e}")
            if self.verbose:
                traceback.print_exc()
            return False
    
    def compile_string(self, source_code: str, output_file: str = 'output.wav') -> bool:
        """Compile music language string to audio"""
        try:
            # Phase 1: Lexical Analysis
            print("Phase 1: Lexical Analysis...")
            self.lexer = MusicLexer(source_code)
            tokens = self.lexer.tokenize()
            self.log(f"Generated {len(tokens)} tokens")
            
            if self.verbose:
                for token in tokens[:10]:  # Show first 10 tokens
                    print(f"  {token}")
                if len(tokens) > 10:
                    print(f"  ... and {len(tokens) - 10} more tokens")
            
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
            
            if self.verbose:
                print("Symbol table:")
                for name, symbol in symbol_table.get_all_symbols().items():
                    print(f"  {symbol}")
            
            # Phase 4: Code Generation
            print("Phase 4: Code Generation...")
            self.code_generator = CodeGenerator(symbol_table)
            instructions = self.code_generator.generate(ast)
            self.log(f"Generated {len(instructions)} instructions")
            
            if self.verbose:
                print("Generated instructions:")
                for i, instr in enumerate(instructions[:10]):  # Show first 10
                    print(f"  {i}: {instr}")
                if len(instructions) > 10:
                    print(f"  ... and {len(instructions) - 10} more instructions")
            
            # Phase 5: Audio Synthesis
            print("Phase 5: Audio Synthesis...")
            self.synthesizer = AudioSynthesizer()
            audio_data = self.synthesizer.synthesize(instructions)
            
            if len(audio_data) == 0:
                print("Warning: No audio data generated")
                return False
            
            # Phase 6: Output Generation (WAV only)
            print("Phase 6: Output Generation...")
            # Ensure output has .wav extension
            if not output_file.endswith('.wav'):
                output_file = output_file.rsplit('.', 1)[0] + '.wav'
            
            self.synthesizer.save_audio(audio_data, output_file)
            print(f"✓ Compilation successful! Output: {output_file}")
            
            return True
            
        except (LexError, ParseError, SemanticError, CodeGenerationError, SynthesisError) as e:
            print(f"Compilation Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            if self.verbose:
                traceback.print_exc()
            return False

def create_example_programs():
    """Create example music programs"""
    examples = {
        'simple': """
# "Twinkle Twinkle Little Star"
TEMPO = 100;
VOLUME = 0.8;
INSTRUMENT = "piano";

# Verse 1
PLAY C4 DURATION = 1;
PLAY C4 DURATION = 1;
PLAY G4 DURATION = 1;
PLAY G4 DURATION = 1;
PLAY A4 DURATION = 1;
PLAY A4 DURATION = 1;
PLAY G4 DURATION = 2;

PLAY F4 DURATION = 1;
PLAY F4 DURATION = 1;
PLAY E4 DURATION = 1;
PLAY E4 DURATION = 1;
PLAY D4 DURATION = 1;
PLAY D4 DURATION = 1;
PLAY C4 DURATION = 2;
""",
        
        'advanced': """
# "Für Elise" by Beethoven (Opening)
TEMPO = 80;
VOLUME = 0.7;
INSTRUMENT = "piano";

# Right hand melody
REPEAT 2 {
    PLAY E5 DURATION = 0.4;
    PLAY D#5 DURATION = 0.4;
}
PLAY E5 DURATION = 0.4;
PLAY B4 DURATION = 0.4;
PLAY D5 DURATION = 0.4;
PLAY C5 DURATION = 0.4;
PLAY A4 DURATION = 1.6;

REST = 0.4;

# Left hand accompaniment (simplified)
VOLUME = 0.5;
CHORD [A2, E3, A3] DURATION = 1.6;
CHORD [E2, G#2, E3] DURATION = 1.6;
CHORD [A2, E3, A3] DURATION = 1.6;

# Melody continues
VOLUME = 0.7;
PLAY E5 DURATION = 0.4;
PLAY D#5 DURATION = 0.4;
PLAY E5 DURATION = 0.4;
PLAY B4 DURATION = 0.4;
PLAY D5 DURATION = 0.4;
PLAY C5 DURATION = 0.4;
PLAY A4 DURATION = 1.6;
""",
        
        'demo': """
# Complete Demonstration
# This showcases all language features

# Setup
TEMPO = 100;
VOLUME = 0.75;

# Test different instruments
INSTRUMENT = "sine";
PLAY A4 DURATION = 1;

INSTRUMENT = "square";
PLAY A4 DURATION = 1;

INSTRUMENT = "triangle";
PLAY A4 DURATION = 1;

INSTRUMENT = "sawtooth";
PLAY A4 DURATION = 1;

INSTRUMENT = "piano";
PLAY A4 DURATION = 1;

REST = 1;

# Test chords with different sizes
CHORD [C4, E4] DURATION = 1;
CHORD [C4, E4, G4] DURATION = 1;
CHORD [C4, E4, G4, B4] DURATION = 1;
CHORD [C4, E4, G4, B4, D5] DURATION = 1;

REST = 1;

# Test nested repeats and tempo changes
REPEAT 2 {
    TEMPO = 120;
    PLAY C4 DURATION = 0.5;
    PLAY D4 DURATION = 0.5;
    PLAY E4 DURATION = 0.5;
    PLAY F4 DURATION = 0.5;
}

TEMPO = 80;
CHORD [C4, E4, G4, C5] DURATION = 4;
"""
    }
    
    return examples

def main():
    parser = argparse.ArgumentParser(
        description='Music Language Compiler - Transform music notation into WAV audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --example simple           # Generate simple example
  python main.py --example advanced        # Generate advanced example  
  python main.py --example demo            # Generate full demo
  python main.py song.mus                  # Compile your own file
  python main.py song.mus -o output.wav    # Specify output file
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Input music file (.mus)')
    parser.add_argument('-o', '--output', help='Output WAV file')
    parser.add_argument('--example', choices=['simple', 'advanced', 'demo'],
                       help='Generate and compile an example program')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create compiler instance
    compiler = MusicCompiler(verbose=args.verbose)
    
    if args.example:
        # Generate and compile example
        print(f"Generating '{args.example}' example program...")
        
        examples = create_example_programs()
        example_code = examples.get(args.example, examples['simple'])
        
        # Save example to file
        example_filename = f'example_{args.example}.mus'
        try:
            with open(example_filename, 'w', encoding='utf-8') as f:
                f.write(example_code)
            print(f"Example saved as '{example_filename}'")
        except Exception as e:
            print(f"Error saving example file: {e}")
            sys.exit(1)
        
        # Compile example
        output_file = args.output or f'example_{args.example}.wav'
        success = compiler.compile_string(example_code, output_file)
        
        if success:
            print(f"\n🎵 Example compilation completed successfully!")
            print(f"📁 Music file: {example_filename}")
            print(f"🔊 Audio file: {output_file}")
        else:
            print(f"\n❌ Example compilation failed!")
            sys.exit(1)
    
    elif args.input_file:
        # Compile user file
        if not Path(args.input_file).exists():
            print(f"Error: Input file '{args.input_file}' not found")
            sys.exit(1)
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            input_path = Path(args.input_file)
            output_file = input_path.stem + '.wav'
        
        success = compiler.compile_file(args.input_file, output_file)
        
        if success:
            print(f"\n🎵 Compilation completed successfully!")
            print(f"🔊 Audio file: {output_file}")
        else:
            print(f"\n❌ Compilation failed!")
            sys.exit(1)
    
    else:
        # No input provided
        print("Error: No input specified.")
        print("\nTry one of these:")
        print("  python main.py --example simple    # Generate a simple example")
        print("  python main.py --example advanced  # Generate an advanced example")
        print("  python main.py --example demo      # Generate a full demo")
        print("  python main.py your_music.mus      # Compile your own file")
        print("\nUse --help for more options.")
        sys.exit(1)

if __name__ == '__main__':
    main()
