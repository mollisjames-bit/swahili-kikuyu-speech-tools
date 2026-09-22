"""
Unit Tests for Swahili and Kikuyu Speech Tools
"""

import unittest
import os
import wave
import struct
import tempfile
import sys

# Ensure package is on sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from swahili_speech.phonetics import text_to_phonemes, normalize_text
from swahili_speech.segmenter import segment_wav_file

class TestPhonetics(unittest.TestCase):
    def test_swahili_digraphs(self):
        # Test ng', ch, sh, th
        text = "ng'ombe chakula shule thelathini"
        phonemes = "".join(text_to_phonemes(text, "sw"))
        self.assertIn("ŋ", phonemes)
        self.assertIn("tʃ", phonemes)
        self.assertIn("ʃ", phonemes)
        self.assertIn("θ", phonemes)

    def test_kikuyu_vowels(self):
        # Test Kikuyu special vowels ĩ and ũ
        text = "mũndũ kĩrĩra"
        phonemes = "".join(text_to_phonemes(text, "ki"))
        # In our mapping, ũ -> o, ĩ -> e
        self.assertIn("moⁿdo", phonemes)
        self.assertIn("kerera", phonemes)

class TestSegmenter(unittest.TestCase):
    def test_segment_synthetic_wav(self):
        # Create a synthetic 16kHz 16-bit mono WAV with speech and silence
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "test_audio.wav")
            sample_rate = 16000
            
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                
                # 4 seconds tone (speech), 1 second silence, 4 seconds tone
                speech_frames_1 = struct.pack("<64000h", *([8000] * 64000))
                silence_frames = struct.pack("<16000h", *([0] * 16000))
                speech_frames_2 = struct.pack("<64000h", *([8000] * 64000))
                
                wf.writeframes(speech_frames_1 + silence_frames + speech_frames_2)
                
            out_dir = os.path.join(tmpdir, "segments")
            segments = segment_wav_file(wav_path, out_dir, min_duration_sec=2.0, silence_threshold_rms=200.0)
            
            self.assertGreaterEqual(len(segments), 1)
            for seg in segments:
                self.assertTrue(os.path.exists(seg["file_path"]))
                self.assertGreater(seg["duration_seconds"], 0.0)

if __name__ == "__main__":
    unittest.main()
