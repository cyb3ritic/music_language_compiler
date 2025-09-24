# Music Language Compiler

This project is a complete compiler for a custom, text-based music description language. It parses source files written in this language, analyzes them, and synthesizes the output into a `.wav` audio file.

The compiler is built in Python and demonstrates the classic stages of compilation:
1.  **Lexical Analysis**: Converts the source code into a stream of tokens.
2.  **Syntax Analysis**: Parses the tokens to build an Abstract Syntax Tree (AST).
3.  **Semantic Analysis**: Validates the AST for correctness (e.g., valid note names, correct types).
4.  **Code Generation**: Traverses the AST to produce a linear sequence of audio instructions.
5.  **Audio Synthesis**: Generates raw audio data (PCM waves) based on the instructions.
6.  **Output Generation**: Writes the audio data to a `.wav` file.

## Features

*   Define tempo, volume, and instrument.
*   Play individual notes (e.g., `C4`, `F#5`, `Bb3`).
*   Play chords with multiple notes.
*   Insert rests (silence).
*   Supported instruments: `sine`, `square`, `triangle`, `sawtooth`, `piano`.
*   Verbose mode for detailed compilation logging.

## Project Structure

```
.
├── main.py                # Main compiler driver and command-line interface
├── lexer.py               # Lexical analyzer (Tokenizer)
├── parser.py              # Syntax analyzer (Parser)
├── semantic_analyzer.py   # Semantic analyzer
├── code_generator.py      # Generates intermediate instructions
├── audio_synthesizer.py   # Synthesizes audio from instructions
├── symbol_table.py        # Data structure for managing symbols
├── requirements.txt       # Project dependencies
├── *.mus                  # Example source files for the music language
└── .gitignore             # Git ignore file
```

## Getting Started

### Prerequisites

*   Python 3.x
*   pip

### Installation

1.  **Set up a virtual environment:**
    ```sh
    python -m venv music_venv
    source music_venv/bin/activate  # On Windows, use `music_venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

You can compile a `.mus` file using the `main.py` script. The only required argument is the input file path.

```sh
python main.py <input_file.mus> [output_file.wav]
```

### Examples

1.  **Compile `hbd.mus` to `hbd.wav`:**
    ```sh
    python main.py hbd.mus
    ```
    This will generate an audio file named `hbd.wav` in the project directory.

2.  **Compile with a specific output file name:**
    ```sh
    python main.py example_advanced.mus my_song.wav
    ```

3.  **Compile in verbose mode for more details:**
    ```sh
    python main.py --verbose hbd.mus
    ```

## Music Language Syntax

Here is a quick overview of the language syntax.

```
// Set the tempo in beats per minute
Tempo: 120

// Set the master volume (0-100)
Volume: 80

// Set the instrument
Instrument: piano

// Play single notes. Format: NoteName[#b]Octave:Duration
// Duration is a fraction of a whole note (e.g., 1/4, 1/8)
Play C4: 1/4
Play G#5: 1/8

// Play a chord (multiple notes at once)
Chord {G4, B4, D5}: 1/2

// Insert a rest (silence)
Rest: 1/4
```
