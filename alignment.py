from math import e
import os
import pandas as pd
from bisect import bisect_right

song_list = [
	"10.wav", "9.wav", "12.wav", "11.wav", "14.wav", "13.wav", "16.wav", "15.wav",
	"3.wav", "4.wav", "1.wav", "2.wav", "7.wav", "8.wav", "5.wav", "6.wav",
	"19.wav", "20.wav", "17.wav", "18.wav"
]
song_pos = [-30, 38, 108, 176, 247, 315, 383, 460, 527, 597, 666, 737, 809, 875, 947, 1018, 1088, 1152, 1224, 1298]
song_duration=60


def get_music_idx(music_pos):
	# Use binary search to find the potential starting position
	idx = bisect_right(song_pos, music_pos) - 1
	
	# Check if the music position falls within the range of the identified song
	if idx >= 0 and song_pos[idx] <= music_pos < song_pos[idx] + song_duration:
		return song_list[idx]
	
	# If the position is out of range, return the default value
	return "idle"

def back_align(music_pos, onset_raw, wav_sr):
	# Reverse both dataframes
	music_pos = music_pos[::-1].reset_index(drop=True)
	onset_raw = onset_raw[::-1].reset_index(drop=True)

	result = []

	for i in range(music_pos.shape[0]):
		# Get onset_raw value
		onset_raw_value = onset_raw.at[i, 'onset_raw']
		# Calculate music position based on sample rate
		music_pos_value = music_pos.at[i, ' Frame'] / wav_sr  #TODO: need better column name, " Frame" or "Frame"
		result.append([onset_raw_value, music_pos_value, get_music_idx(music_pos_value)])

	# Convert result list to pandas DataFrame
	df_result = pd.DataFrame(result, columns=['onset_raw', 'music_pos', 'song_idx'])

	# Reverse the DataFrame back to the original order
	df_result = df_result[::-1].reset_index(drop=True)

	print(f'df_result: {df_result}')

	return df_result

def insert2evt_csv(df_result, evt_csv, file_path):
	# Read the existing CSV file
	df_large = pd.read_csv(evt_csv)

	# Merge the dataframes on 'onset_raw' column
	df_large = df_large.merge(df_result, on='onset_raw', how='left')
	df_large['music_pos'] = df_large['music_pos'].fillna('not found')

	# Print the merged dataframe
	print(df_large)

	output_csv = os.path.splitext(file_path)[0] + ("-aligned.csv")

	# Save the modified dataframe to a new CSV file
	df_large.to_csv(output_csv, index=False)  # Save as a new CSV file

def process_and_align(evt_csv_path, music_pos_path, trigger_num, wav_sr, back_align, insert2evt_csv):
	"""
	Processes the input files, filters based on TriggerNum, aligns onset times, and updates the event CSV.

	:param evt_csv_path: Path to the event CSV file
	:param music_pos_path: Path to the music position file
	:param trigger_num: Trigger number to filter data
	:param wav_sr: Sample rate in Hz
	:param back_align: Function to align music positions with onset times
	:param insert2evt_csv: Function to insert aligned data into the event CSV
	:return: None
	"""
	# Read the CSV files
	onset_raw = pd.read_csv(evt_csv_path)
	music_pos = pd.read_csv(music_pos_path)

	# Remove rows where 'TriggerNum' is NaN in music_pos
	music_pos = music_pos.dropna(subset=['TriggerNum'])

	# Filter based on TriggerNum
	onset_raw = onset_raw[onset_raw['description'] == trigger_num]
	music_pos = music_pos[music_pos['TriggerNum'] == trigger_num]

	# Align music position and onset times
	df_result = back_align(music_pos, onset_raw, wav_sr)

	# Insert the aligned data into the event CSV
	insert2evt_csv(df_result, evt_csv_path, evt_csv_path)

if __name__ == '__main__':
	# Define file paths and parameters
	music_pos = '/Users/shenyixiao/TsingHua/brain4music/forward/20240705_day5_teaching_experiment/recording_20240705-111440_sync.txt'
	evt_csv_prefix = '/Users/shenyixiao/TsingHua/brain4music/forward/20240705_day5_teaching_experiment/EEG_BRK'
	evt_csv_l =[i for i in range(2, 10, 2)]
	evt_csv_l = [evt_csv_prefix+str(e)+'/evt.csv' for e in evt_csv_l]
	print(evt_csv_l)
	trigger_num = 9
	wav_sr = 48 * 1000  # 48 kHz

	# Process and align data
	for e in evt_csv_l:
		process_and_align(e, music_pos, trigger_num, wav_sr, back_align, insert2evt_csv)