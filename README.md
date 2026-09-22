# Swahili & Kikuyu Speech Tools (`swahili-kikuyu-speech-tools`)

An open-source, zero-dependency Python toolset for audio segmentation, phonetic grapheme-to-phoneme (G2P) alignment, and linguistic data quality auditing for low-resource East African languages: **Standard Kiswahili** and **Kikuyu (Gĩkũyũ)**.

Supported under the digital commons framework for the Next Generation Internet (NGI).

---

## Key Features

1. **Rule-Based Grapheme-to-Phoneme (G2P) Engine:**
   - Accurate phonetic mapping for standard Kiswahili (5 cardinal vowels, prenasalized stops `mb`, `nd`, `ng'`, `nj`, voiceless fricatives `dh`, `th`, `gh`).
   - Phonetic transcription for Kikuyu (7 phonemic vowels `a, e, i, o, u, ĩ, ũ`, labialized velars `gw`, `kw`, prenasalized consonants).
2. **Pure Python Audio Segmentation:**
   - Standard library `wave` module processing (no `ffmpeg` or `librosa` installation required).
   - Energy-based silence detection and chunking into 5–15 second training segments suitable for Whisper and Kaldi ASR models.
3. **Dataset Manifest Generator:**
   - Generates standardized JSON / TSV manifests (`audio_filepath`, `text_norm`, `phonemes`, `duration`, `speaker_id`).

---

## Installation

```bash
git clone https://github.com/jamesnderi/swahili-kikuyu-speech-tools.git
cd swahili-kikuyu-speech-tools
pip install -e .
```

---

## Usage Example

### 1. Grapheme-to-Phoneme Conversion
```python
from swahili_speech.phonetics import text_to_phonemes

# Swahili
sw_text = "Habari za asubuhi na karibu sana"
print(text_to_phonemes(sw_text, lang="sw"))
# Output: ['h', 'a', 'b', 'a', 'r', 'i', ' ', 'z', 'a', ' ', 'a', 's', 'u', 'b', 'u', 'h', 'i', ' ', 'n', 'a', ' ', 'k', 'a', 'r', 'i', 'b', 'u', ' ', 's', 'a', 'n', 'a']

# Kikuyu
ki_text = "Mũgambo wa rũrĩrĩ rũitũ"
print(text_to_phonemes(ki_text, lang="ki"))
```

### 2. Audio Segmentation
```python
from swahili_speech.segmenter import segment_wav_file

segments = segment_wav_file("input_interview.wav", output_dir="output_chunks/", min_duration=3.0, max_duration=12.0)
print(f"Extracted {len(segments)} training segments.")
```

---

## License

Released under the **MIT License**. Free for commercial and non-commercial research, dataset creation, and model training.
