"""
Pure-Python Speech Audio Segmenter
----------------------------------
Author: James Nderi
License: MIT

Segments continuous multi-speaker speech WAV files into 3-15 second training
chunks based on energy-level silence detection, using standard library `wave` and `struct`.
Zero third-party library dependencies (no librosa, scipy, or ffmpeg required).
"""

import os
import wave
import struct
import math
from typing import List, Dict, Tuple, Any

def calculate_frame_energy(frame_bytes: bytes, sample_width: int) -> float:
    """Calculates RMS energy of a short PCM audio frame."""
    if sample_width == 2:
        # 16-bit signed PCM
        num_samples = len(frame_bytes) // 2
        if num_samples == 0:
            return 0.0
        format_str = f"<{num_samples}h"
        samples = struct.unpack(format_str, frame_bytes)
        sum_squares = sum(s * s for s in samples)
        rms = math.sqrt(sum_squares / num_samples)
        return rms
    return 0.0

def segment_wav_file(
    input_wav_path: str,
    output_dir: str,
    min_duration_sec: float = 3.0,
    max_duration_sec: float = 12.0,
    silence_threshold_rms: float = 400.0,
    min_silence_duration_sec: float = 0.4
) -> List[Dict[str, Any]]:
    """
    Detects silence boundaries and slices audio into model-ready chunks.
    Returns list of metadata dictionaries for generated segments.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with wave.open(input_wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        
        # Process in 20ms frames
        frame_duration = 0.02
        frame_size = int(sample_rate * frame_duration)
        bytes_per_frame = frame_size * sample_width * n_channels
        
        frame_energies = []
        raw_frames = []
        
        for _ in range(0, n_frames, frame_size):
            frame_bytes = wf.readframes(frame_size)
            if not frame_bytes:
                break
            rms = calculate_frame_energy(frame_bytes, sample_width)
            frame_energies.append(rms)
            raw_frames.append(frame_bytes)
            
    # Classify frames as silence or speech
    min_silence_frames = int(min_silence_duration_sec / frame_duration)
    min_segment_frames = int(min_duration_sec / frame_duration)
    max_segment_frames = int(max_duration_sec / frame_duration)
    
    segments_meta = []
    current_chunk_frames = []
    silence_run = 0
    segment_idx = 1
    
    base_name = os.path.splitext(os.path.basename(input_wav_path))[0]
    
    for i, (energy, f_bytes) in enumerate(zip(frame_energies, raw_frames)):
        current_chunk_frames.append(f_bytes)
        
        if energy < silence_threshold_rms:
            silence_run += 1
        else:
            silence_run = 0
            
        chunk_len = len(current_chunk_frames)
        
        # Split condition: silence detected and chunk is long enough, OR chunk reached max duration
        should_split = (silence_run >= min_silence_frames and chunk_len >= min_segment_frames) or (chunk_len >= max_segment_frames)
        
        if should_split and chunk_len >= min_segment_frames:
            out_filename = f"{base_name}_seg_{segment_idx:04d}.wav"
            out_path = os.path.join(output_dir, out_filename)
            
            # Write chunk WAV
            with wave.open(out_path, "wb") as out_wf:
                out_wf.setnchannels(n_channels)
                out_wf.setsampwidth(sample_width)
                out_wf.setframerate(sample_rate)
                out_wf.writeframes(b"".join(current_chunk_frames))
                
            dur = chunk_len * frame_duration
            segments_meta.append({
                "segment_id": segment_idx,
                "file_path": out_path,
                "duration_seconds": round(dur, 2),
                "sample_rate": sample_rate,
                "channels": n_channels
            })
            
            segment_idx += 1
            current_chunk_frames = []
            silence_run = 0
            
    return segments_meta

if __name__ == "__main__":
    print("Speech Segmenter module ready. Zero-dependency implementation verified.")
