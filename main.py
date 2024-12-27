import mne
import pandas as pd
import os
import logging
import argparse

# Configure logging
logging.basicConfig(
	filename='converting.log', 
	level=logging.INFO, 
	format='%(asctime)s - %(levelname)s - %(message)s'
)

def bdf2csv_data_lowspeeed(file_path, debug=False):
	"""
	Convert a BDF file to a CSV file and save only the last 14 channels in the same directory as the input file.

	Parameters:
	file_path (str): Path to the input BDF file.
	debug (bool): Whether to crop the raw data for debugging.
	"""
	try:
		# Load the BDF file and preload data
		raw = mne.io.read_raw_bdf(file_path, preload=True)

		# Crop raw for debugging if debug is True
		if debug:
			raw.crop(tmin=0, tmax=10)

		# Extract data and time indices
		data, times = raw.get_data(return_times=True)

		# Log file details
		logging.info(
			"File processed: %s, Total Channels: %d, Timepoints: %d",
			file_path, len(raw.ch_names), len(times)
		)

		# Extract the last 14 channels
		last_14_channel_indices = range(len(raw.ch_names) - 14, len(raw.ch_names))
		selected_data = data[last_14_channel_indices, :]
		selected_channel_names = [raw.ch_names[i] for i in last_14_channel_indices]

		# Create a DataFrame with time index and selected channel names
		df = pd.DataFrame(selected_data.T, columns=selected_channel_names)
		df.insert(0, "timeindex", times)

		# Determine the output CSV path
		output_csv = os.path.splitext(file_path)[0] + ("-lowspeed-debug.csv" if debug else "-lowspeed.csv")

		# Save the DataFrame to a CSV file
		df.to_csv(output_csv, index=False)

		# Log success
		logging.info("CSV file saved successfully: %s", output_csv)

		# Print DataFrame for debugging
		if debug:
			print(df.head())

	except Exception as e:
		logging.error("Error processing file %s: %s", file_path, str(e))
		print(f"An error occurred: {e}")

def bdf2csv_data(file_path, debug=False):
	"""
	Convert a BDF file to a CSV file and save it in the same directory as the input file.

	Parameters:
	file_path (str): Path to the input BDF file.
	debug (bool): Whether to crop the raw data for debugging.
	"""
	# Load the BDF file and preload data
	raw = mne.io.read_raw_bdf(file_path, preload=True)

	# Crop raw for debugging if debug is True
	if debug:
		raw.crop(tmin=0, tmax=10)

	# Extract data and time indices
	data, times = raw.get_data(return_times=True)

	# Log file details
	logging.info(
		"File processed: %s, Channels: %d, Timepoints: %d",
		file_path, len(raw.ch_names), len(times)
	)

	# Create a DataFrame with time index and channel names
	df = pd.DataFrame(data.T, columns=raw.ch_names)
	df.insert(0, "timeindex", times)

	# Determine the output CSV path
	output_csv = os.path.splitext(file_path)[0] + ("-debug.csv" if debug else ".csv")

	# Save the DataFrame to a CSV file
	df.to_csv(output_csv, index=False)

def bdf2csv_evt(file_path, debug=False):
	try:
		# Read the annotations from the BDF file
		annotations = mne.read_annotations(file_path)

		# Log the success of annotation reading
		logging.info(f"Successfully read annotations from {file_path}")

		# Convert annotations to a DataFrame
		annotations_df = annotations.to_data_frame()

		# Add raw onset values (in seconds relative to recording start)
		annotations_df['onset_raw'] = annotations.onset

		# Remove the 'onset' column
		annotations_df = annotations_df.drop(columns=['onset'])

		# Reorder columns to place 'onset_raw' as the first column
		columns_order = ['onset_raw'] + [col for col in annotations_df.columns if col != 'onset_raw']
		annotations_df = annotations_df[columns_order]

		# Determine the output CSV file path
		output_csv_path = os.path.splitext(file_path)[0] + '.csv'

		# Export the DataFrame to a CSV file
		annotations_df.to_csv(output_csv_path, index=False)

		# Log the completion
		logging.info(f"Annotations successfully saved to {output_csv_path}")

		# Print some of the output for verification
		if debug:
			print(annotations_df.head())

	except Exception as e:
		logging.error(f"Error while processing {file_path}: {e}")
		print(f"An error occurred: {e}")


def process_folders(base_folders, debug=False):
	"""
	Search for folders with prefix 'EEG_BRK' in the given directories, 
	find 'data.bdf' inside them, and convert it to CSV.

	Parameters:
	base_folders (list): List of paths to the base directories to search.
	debug (bool): Whether to crop the raw data for debugging.
	"""
	# Iterate over all base folders
	for base_folder in base_folders:
		# Iterate over all items in the base folder
		for folder_name in os.listdir(base_folder):
			# Check if the folder name starts with 'EEG_BRK'
			if folder_name.startswith("EEG_BRK"):
				folder_path = os.path.join(base_folder, folder_name)
				# Check if it is a directory
				if os.path.isdir(folder_path):
					# Check for 'data.bdf' in the directory
					data_bdf_path = os.path.join(folder_path, "data.bdf")
					if os.path.exists(data_bdf_path):
						print(f"Processing file: {data_bdf_path}")
						bdf2csv_data(data_bdf_path, debug=debug)
						bdf2csv_data_lowspeeed(data_bdf_path, debug=debug)

					# Check for 'evt.bdf' in the directory
					evt_bdf_path = os.path.join(folder_path, "evt.bdf")					
					if os.path.exists(evt_bdf_path):
						print(f"Processing file: {evt_bdf_path}")
						# bdf2csv_evt(evt_bdf_path, debug=debug)

# Example usage
if __name__ == "__main__":
	# Parse command line arguments
	parser = argparse.ArgumentParser(description="Convert BDF files to CSV.")
	parser.add_argument("--debug", action="store_true", help="Enable debug mode to crop raw data.")
	parser.add_argument("--base-folder", type=str, nargs='+', required=True, help="Base folder(s) to process.")
	args = parser.parse_args()

	# Process all EEG_BRK folders in the given base folders with optional debug mode
	process_folders(args.base_folder, debug=args.debug)
