import os
import pickle
import numpy as np
import argparse
from sklearn.model_selection import train_test_split

def refactor_directory_structure(input_dir, output_dir, type_of_evaluation):

    label_map = {}
    current_label = 0

    X_train_data, y_train_data = [], []
    X_val_data, y_val_data = [], []
    X_test_data, y_test_data = [], []

    # Iterate through each subdirectory in the input directory
    for website_dir in os.listdir(input_dir):
        website_path = os.path.join(input_dir, website_dir)

        if os.path.isdir(website_path):
            features_file_path = os.path.join(website_path, 'features.pkl')

            if os.path.isfile(features_file_path):
                # Load the features.pkl file
                with open(features_file_path, 'rb') as f:
                    features = pickle.load(f)

                # Convert features to numpy array if it's a list
                if isinstance(features, list):
                    features = np.array(features)
                
                # Assign a label to the website if not already assigned
                if website_dir not in label_map:
                    label_map[website_dir] = current_label
                    current_label += 1

                labels = np.array([label_map[website_dir]] * features.shape[0])

                # Split the data into training, validation, and test sets
                X_temp, X_test, y_temp, y_test = train_test_split(features, labels, test_size=0.1, stratify=labels, random_state=42)
                X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1, stratify=y_temp, random_state=42)

                # Append features and labels to the respective lists
                X_train_data.append(X_train)
                y_train_data.extend(y_train)
                X_val_data.append(X_val)
                y_val_data.extend(y_val)
                X_test_data.append(X_test)
                y_test_data.extend(y_test)

    # Concatenate all features into a single numpy array
    X_train_data = np.concatenate(X_train_data, axis=0)
    y_train_data = np.array(y_train_data)
    X_val_data = np.concatenate(X_val_data, axis=0)
    y_val_data = np.array(y_val_data)
    X_test_data = np.concatenate(X_test_data, axis=0)
    y_test_data = np.array(y_test_data)

    # Shuffle the data within each set
    train_indices = np.random.permutation(X_train_data.shape[0])
    X_train_data = X_train_data[train_indices]
    y_train_data = y_train_data[train_indices]

    val_indices = np.random.permutation(X_val_data.shape[0])
    X_val_data = X_val_data[val_indices]
    y_val_data = y_val_data[val_indices]

    test_indices = np.random.permutation(X_test_data.shape[0])
    X_test_data = X_test_data[test_indices]
    y_test_data = y_test_data[test_indices]

    # Define output file paths
    X_train_output_file = os.path.join(output_dir, f'X_train_{type_of_evaluation}.pkl')
    y_train_output_file = os.path.join(output_dir, f'y_train_{type_of_evaluation}.pkl')
    X_val_output_file = os.path.join(output_dir, f'X_valid_{type_of_evaluation}.pkl')
    y_val_output_file = os.path.join(output_dir, f'y_valid_{type_of_evaluation}.pkl')
    X_test_output_file = os.path.join(output_dir, f'X_test_{type_of_evaluation}.pkl')
    y_test_output_file = os.path.join(output_dir, f'y_test_{type_of_evaluation}.pkl')

    # Save the concatenated features and labels to the output files
    with open(X_train_output_file, 'wb') as f:
        pickle.dump(X_train_data, f)

    with open(y_train_output_file, 'wb') as f:
        pickle.dump(y_train_data, f)

    with open(X_val_output_file, 'wb') as f:
        pickle.dump(X_val_data, f)

    with open(y_val_output_file, 'wb') as f:
        pickle.dump(y_val_data, f)

    with open(X_test_output_file, 'wb') as f:
        pickle.dump(X_test_data, f)

    with open(y_test_output_file, 'wb') as f:
        pickle.dump(y_test_data, f)

    print(f"Saved training X data to {X_train_output_file}")
    print(f"Saved training y data to {y_train_output_file}")
    print(f"Saved validation X data to {X_val_output_file}")
    print(f"Saved validation y data to {y_val_output_file}")
    print(f"Saved test X data to {X_test_output_file}")
    print(f"Saved test y data to {y_test_output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Refactor directory structure of network traffic data.')
    parser.add_argument('input_dir', type=str, help='Input directory containing subdirectories with features.pkl files')
    parser.add_argument('output_dir', type=str, help='Output directory to save the refactored dataset')
    parser.add_argument('type_of_evaluation', type=str, help='Type of evaluation')

    args = parser.parse_args()
    refactor_directory_structure(args.input_dir, args.output_dir, args.type_of_evaluation)
