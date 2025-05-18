from typing import List, Tuple
import os
import sys
import json
from tqdm import tqdm

def find_audio_json_pairs(directory: str) -> List[Tuple[str, str]]:
    """
    Find all pairs of MP3 and JSON files in the given directory and its subdirectories.
    Each pair consists of an MP3 file and its corresponding JSON file with the same base name.

    Args:
        directory: Path to the directory containing the files

    Returns:
        List of tuples where each tuple contains (mp3_path, json_path)
    """
    pairs = []

    # Walk through all directories and subdirectories
    for root, _, files in tqdm(os.walk(directory), desc="Searching for files"):
        # Get all MP3 files in current directory
        mp3_files = [f for f in files if f.endswith(".mp3")]

        for mp3_file in mp3_files:
            base_name = os.path.splitext(mp3_file)[0]
            json_file = f"{base_name}.json"

            # Check if corresponding JSON file exists in the same directory
            if json_file in files:
                mp3_path = os.path.join(root, mp3_file)
                json_path = os.path.join(root, json_file)
                pairs.append((mp3_path, json_path))

    return pairs

if __name__ == "__main__":
    dataset = sys.argv[1]
    scenario = int(sys.argv[2])
    
    assert scenario in [1, 2, 3], "Scenario ID must be 1, 2, or 3."
    
    if not os.path.exists(dataset):
        print(f"Directory {dataset} does not exist.")
        sys.exit(1)
        
    pairs = find_audio_json_pairs(dataset)
    if not pairs:
        print("No matching MP3 and JSON files found.")
        sys.exit(1)
    
    list_samples = []
    disordered_count = 0
    for mp3_path, json_path in tqdm(pairs, desc="Processing files"):
        # A sample format
        # {
        #     "messages": [
        #     {
        #         "content": "<audio>What's that sound?",
        #         "role": "user"
        #     },
        #     {
        #         "content": "It is the sound of glass shattering.",
        #         "role": "assistant"
        #     }
        #     ],
        #     "audios": [
        #     "mllm_demo_data/1.mp3"
        #     ]
        # }
        
        # Read the JSON file and extract the content
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        if json_data["answer"] == "speech_disorder":
            if scenario in [2, 3]:
                transcription = " ".join([word + "*" for word in json_data["words"]])
            else:
                transcription = " ".join(json_data["words"])
            disordered_count += 1
        else:
            transcription = " ".join(json_data["words"])
            
        list_samples.append({
            "messages": [
                {
                    "content": "<audio>Transcribe this sound into text. If the speech is disordered, please mark the words with an asterisk.",
                    "role": "user"
                },
                {
                    "content": transcription,
                    "role": "assistant"
                }
            ],
            "audios": [
                mp3_path
            ]
        })

    # Save the list of samples to a file
    json_output_path = f"./{dataset.lower()}.json"
    with open(json_output_path, 'w') as f:
        json.dump(list_samples, f, indent=4)

    print(f"Output saved to {json_output_path}")
    print(f"Number of disordered samples: {disordered_count}")
    print(f"Number of normal samples: {len(list_samples) - disordered_count}")
    print(f"Number of samples: {len(list_samples)}")