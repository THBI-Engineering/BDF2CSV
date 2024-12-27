import numpy as np
import soundfile as sf
from pathlib import Path

# Input list of songs (mono) and their corresponding start times
song_list = [
	"9.wav", "12.wav", "11.wav", "14.wav", "13.wav", "16.wav", "15.wav",
	"3.wav", "4.wav", "1.wav", "2.wav", "7.wav", "8.wav", "5.wav", "6.wav",
	"19.wav", "20.wav", "17.wav", "18.wav"
]
song_pos = [38, 108, 176, 247, 315, 383, 460, 527, 597, 666, 737, 809, 875, 947, 1018, 1088, 1152, 1224, 1298]

# Base path for the input files
base_path = Path("MusicSti-Cropped")
song_list = [base_path / song for song in song_list]

# Output file name
output_file = "combined_songs.wav"

# Read all WAV files and ensure they have the same sample rate
sample_rate = None
songs_data = []
for file in song_list:
	data, sr = sf.read(file, dtype='int32')  # Read as int32 for higher precision
	if data.ndim > 1:
		raise ValueError(f"{file} is not mono. Please ensure all files are mono.")
	if sample_rate is None:
		sample_rate = sr
		print(f"Sample rate: {sample_rate}")
	elif sample_rate != sr:
		raise ValueError(f"Sample rate mismatch in {file}. Expected {sample_rate}, got {sr}")
	songs_data.append(data)

# Calculate insertion points for each song in terms of sample indices
song_pos_samples = [int(pos * sample_rate) for pos in song_pos]
total_duration_samples = max(start_sample + len(song) for start_sample, song in zip(song_pos_samples, songs_data))
combined_audio = np.zeros(total_duration_samples, dtype=np.int32)

# Insert each song at the specified position
for i, (start_sample, song) in enumerate(zip(song_pos_samples, songs_data)):
	end_sample = start_sample + len(song)
	if np.any(combined_audio[start_sample:end_sample] != 0):
		print(f"Warning: Overlap detected for song {song_list[i]} at {start_sample/sample_rate:.2f} seconds.")
	combined_audio[start_sample:end_sample] += song

# Write the combined audio to an output WAV file
sf.write(output_file, combined_audio, sample_rate, subtype='PCM_24')
print(f"Combined mono WAV file saved as {output_file}")
