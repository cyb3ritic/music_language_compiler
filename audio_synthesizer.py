import numpy as np
from scipy.io import wavfile
import os
from typing import List, Dict, Optional
from code_generator import Instruction
import warnings

# Suppress numpy warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

class SynthesisError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class AudioSynthesizer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.tempo = 120.0  # BPM
        self.volume = 0.5
        self.instrument = 'sine'
        self.audio_data = []
        
        # Note frequencies (A4 = 440 Hz)
        self.note_frequencies = self._generate_note_frequencies()
    
    def _generate_note_frequencies(self) -> Dict[str, float]:
        """Generate frequency table for all notes"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        frequencies = {}
        
        for octave in range(0, 9):
            for i, note in enumerate(notes):
                # Calculate frequency using A4 = 440 Hz as reference
                semitones_from_a4 = (octave - 4) * 12 + (i - 9)
                frequency = 440.0 * (2 ** (semitones_from_a4 / 12))
                
                # Add both sharp and flat notation
                note_name = f"{note}{octave}"
                frequencies[note_name] = frequency
                
                # Add flat notation for sharp notes
                if '#' in note:
                    flat_note = notes[(i + 1) % 12] + 'b'
                    frequencies[f"{flat_note}{octave}"] = frequency
        
        return frequencies
    
    def synthesize(self, instructions: List[Instruction]) -> np.ndarray:
        """Synthesize audio from instructions"""
        self.audio_data = []
        repeat_stack = []
        
        i = 0
        while i < len(instructions):
            instr = instructions[i]
            
            try:
                if instr.opcode == 'INIT':
                    pass  # Initialization handled in constructor
                elif instr.opcode == 'SET_TEMPO':
                    self.tempo = max(1, min(300, float(instr.operands[0])))
                elif instr.opcode == 'SET_VOLUME':
                    self.volume = max(0, min(1, float(instr.operands[0])))
                elif instr.opcode == 'SET_INSTRUMENT':
                    self.instrument = str(instr.operands[0])
                elif instr.opcode == 'PLAY_NOTE':
                    note, duration = instr.operands
                    self._synthesize_note(str(note), float(duration))
                elif instr.opcode == 'PLAY_CHORD':
                    notes, duration = instr.operands
                    self._synthesize_chord(notes, float(duration))
                elif instr.opcode == 'REST':
                    duration = float(instr.operands[0])
                    self._add_silence(duration)
                elif instr.opcode == 'REPEAT_START':
                    times = int(float(instr.operands[0]))
                    repeat_stack.append({'times': times, 'start': i + 1, 'current': 0})
                elif instr.opcode == 'REPEAT_END':
                    if repeat_stack:
                        repeat_info = repeat_stack[-1]
                        repeat_info['current'] += 1
                        if repeat_info['current'] < repeat_info['times']:
                            i = repeat_info['start'] - 1  # Jump back to start
                        else:
                            repeat_stack.pop()
                elif instr.opcode == 'END':
                    break
                else:
                    print(f"Warning: Unknown opcode '{instr.opcode}', skipping...")
                
            except Exception as e:
                print(f"Error processing instruction '{instr}': {e}")
                # Continue with next instruction
            
            i += 1
        
        if not self.audio_data:
            print("Warning: No audio data generated")
            return np.array([])
        
        try:
            return np.concatenate(self.audio_data)
        except Exception as e:
            raise SynthesisError(f"Failed to concatenate audio data: {e}")
    
    def _synthesize_note(self, note: str, duration: float):
        """Synthesize a single note"""
        if note not in self.note_frequencies:
            print(f"Warning: Unknown note '{note}', adding silence...")
            self._add_silence(duration)
            return
        
        frequency = self.note_frequencies[note]
        samples = self._generate_tone(frequency, duration)
        if len(samples) > 0:
            self.audio_data.append(samples)
    
    def _synthesize_chord(self, notes: List[str], duration: float):
        """Synthesize a chord (multiple notes simultaneously) - FIXED VERSION"""
        if not notes:
            self._add_silence(duration)
            return
        
        valid_notes = [note for note in notes if note in self.note_frequencies]
        
        if not valid_notes:
            print(f"Warning: No valid notes in chord {notes}, adding silence...")
            self._add_silence(duration)
            return
        
        print(f"Synthesizing chord: {valid_notes} for {duration} beats")
        
        # Generate all note samples first and find the maximum length
        note_samples = []
        max_length = 0
        
        for note in valid_notes:
            frequency = self.note_frequencies[note]
            samples = self._generate_tone(frequency, duration)
            if len(samples) > 0:
                note_samples.append(samples)
                max_length = max(max_length, len(samples))
        
        if not note_samples:
            self._add_silence(duration)
            return
        
        # Create the chord by summing all notes with the same length
        chord_samples = np.zeros(max_length)
        
        for samples in note_samples:
            # Pad samples to max_length if necessary
            if len(samples) < max_length:
                padded_samples = np.zeros(max_length)
                padded_samples[:len(samples)] = samples
                samples = padded_samples
            elif len(samples) > max_length:
                # Trim if longer (shouldn't happen, but safety check)
                samples = samples[:max_length]
            
            chord_samples += samples
        
        # Normalize to prevent clipping (divide by number of notes)
        if len(note_samples) > 1:
            chord_samples = chord_samples / len(note_samples)
        
        # Apply additional scaling to keep volume reasonable
        chord_samples = chord_samples * 0.8
        
        self.audio_data.append(chord_samples)
        print(f"Chord synthesized successfully: {len(chord_samples)} samples")
    
    def _generate_tone(self, frequency: float, duration: float) -> np.ndarray:
        """Generate tone using specified instrument"""
        try:
            # Convert duration from beats to seconds
            duration_seconds = max(0.01, (duration * 60.0) / self.tempo)
            num_samples = int(self.sample_rate * duration_seconds)
            
            if num_samples <= 0:
                return np.array([])
            
            t = np.linspace(0, duration_seconds, num_samples, False)
            
            # Generate waveform based on instrument
            if self.instrument == 'sine':
                wave = np.sin(2 * np.pi * frequency * t)
            elif self.instrument == 'square':
                wave = np.sign(np.sin(2 * np.pi * frequency * t))
            elif self.instrument == 'triangle':
                wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            elif self.instrument == 'sawtooth':
                wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            elif self.instrument == 'piano':
                # Simple piano approximation using multiple harmonics
                wave = (np.sin(2 * np.pi * frequency * t) +
                       0.5 * np.sin(2 * np.pi * 2 * frequency * t) +
                       0.25 * np.sin(2 * np.pi * 3 * frequency * t))
                wave = wave / 1.75  # Normalize
            else:
                # Default to sine wave
                wave = np.sin(2 * np.pi * frequency * t)
            
            # Apply volume and envelope
            wave = wave * self.volume
            wave = self._apply_envelope(wave)
            
            return wave
            
        except Exception as e:
            print(f"Error generating tone for frequency {frequency}: {e}")
            return np.array([])
    
    def _apply_envelope(self, wave: np.ndarray) -> np.ndarray:
        """Apply ADSR envelope to prevent clicks"""
        if len(wave) == 0:
            return wave
        
        length = len(wave)
        attack_samples = min(int(0.01 * self.sample_rate), length // 10)  # 10ms attack
        release_samples = min(int(0.1 * self.sample_rate), length // 5)  # 100ms release
        
        envelope = np.ones(length)
        
        try:
            # Attack
            if attack_samples > 0:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
            
            # Release
            if release_samples > 0:
                envelope[-release_samples:] = np.linspace(
                    envelope[-release_samples], 0, release_samples
                )
            
            return wave * envelope
            
        except Exception as e:
            print(f"Error applying envelope: {e}")
            return wave
    
    def _add_silence(self, duration: float):
        """Add silence for the specified duration"""
        try:
            duration_seconds = max(0, (duration * 60.0) / self.tempo)
            num_samples = int(self.sample_rate * duration_seconds)
            
            if num_samples > 0:
                silence = np.zeros(num_samples)
                self.audio_data.append(silence)
                
        except Exception as e:
            print(f"Error adding silence: {e}")
    
    def save_audio(self, audio_data: np.ndarray, filename: str):
        """Save audio data to WAV file"""
        if len(audio_data) == 0:
            print("Warning: No audio data to save!")
            return
        
        try:
            # Ensure filename has .wav extension
            if not filename.endswith('.wav'):
                filename = filename.rsplit('.', 1)[0] + '.wav'
            
            # Normalize and convert to 16-bit
            audio_data = np.clip(audio_data, -1, 1)
            audio_16bit = (audio_data * 32767).astype(np.int16)
            
            # Save as WAV
            wavfile.write(filename, self.sample_rate, audio_16bit)
            
            print(f"Audio successfully saved as: {filename}")
            
        except Exception as e:
            raise SynthesisError(f"Failed to save audio: {e}")
