import os
import json
import sys

if __name__ == "__main__":
    first_dataset_file = sys.argv[1]
    second_dataset_file = sys.argv[2]
    if not os.path.exists(first_dataset_file):
        print(f"File {first_dataset_file} does not exist.")
        sys.exit(1)
    if not os.path.exists(second_dataset_file):
        print(f"File {second_dataset_file} does not exist.")
        sys.exit(1)
        
    num_samples = sys.argv[3]
    if not num_samples.isdigit() or int(num_samples) <= 0:
        print(f"Number of samples {num_samples} is not a valid number.")
        sys.exit(1)
        
    num_samples = int(num_samples)
    if num_samples % 2 != 0:
        print(f"Number of samples {num_samples} is not even.")
        sys.exit(1)
    
    # Read the first dataset
    with open(first_dataset_file, 'r') as f:
        first_dataset = json.load(f)
        
    # Read the second dataset
    with open(second_dataset_file, 'r') as f:
        second_dataset = json.load(f)
        
    # Remove the duplicated samples in the first dataset by the second one
    # by using "audio" as the key
    # Sample format
    # {
    #     "messages": [
    #         {
    #             "content": "<audio>Transcribe this sound into text. If the speech is disordered, please mark the words with an asterisk.",
    #             "role": "user"
    #         },
    #         {
    #             "content": "close-back-unrounded-vowel post-test dV",
    #             "role": "assistant"
    #         }
    #     ],
    #     "audios": [
    #         "UltraSuitePlus/processed-core-uxtd/core/51M/047D.mp3"
    #     ]
    # }
    
    duplicated_audios = []
    for sample in second_dataset:
        if "audios" in sample and len(sample["audios"]) > 0:
            duplicated_audios.append(sample["audios"][0][sample["audios"][0].find("/") + 1:sample["audios"][0].rfind("/")])

    # Remove the duplicated samples in the first dataset
    indexes_to_remove = []
    for i, sample in enumerate(first_dataset):
        if "audios" in sample and len(sample["audios"]) > 0:
            if sample["audios"][0][sample["audios"][0].find("/") + 1:sample["audios"][0].rfind("/")] in duplicated_audios:
                indexes_to_remove.append(i)

    indexes_to_remove.sort(reverse=True)
    for i in indexes_to_remove:
        del first_dataset[i]
    print(f"Removed {len(indexes_to_remove)} duplicated samples from the first dataset.")
    
    # Create the list of children id
    children_id = []
    is_normal = []
    for sample in first_dataset:
        if "audios" in sample and len(sample["audios"]) > 0:
            children_id.append(sample["audios"][0].split("/")[-2])
            
            if sample["audios"][0].split("/")[1] == "processed-core-uxtd":
                is_normal.append(1)
            else:
                is_normal.append(0)
                
    children_set = set(zip(children_id, is_normal))
                
    # Select half of the samples from the children that are normal and half of the samples that are disordered
    # and create a new dataset
    new_dataset = []
    normal_count = 0
    disordered_count = 0
    for child_id, is_normal in children_set:
        if is_normal == 1:
            normal_samples = [sample for sample in first_dataset if sample["audios"][0].split("/")[-2] == child_id]
            if normal_count < num_samples // 2:
                new_dataset.extend(normal_samples)
                normal_count += len(normal_samples)
        else:
            disordered_samples = [sample for sample in first_dataset if sample["audios"][0].split("/")[-2] == child_id]
            if disordered_count < num_samples //2:
                new_dataset.extend(disordered_samples)
                disordered_count += len(disordered_samples)
    
    # Save the new dataset to a file
    new_dataset_file = f"./{first_dataset_file.split('.')[0]}_final.json"
    with open(new_dataset_file, 'w') as f:
        json.dump(new_dataset, f, indent=4)
        
    # Get list of all the audio files in the new dataset
    audio_files = []
    for sample in new_dataset:
        if "audios" in sample and len(sample["audios"]) > 0:
            audio_files.append(sample["audios"][0])
    print(f"New dataset saved to {new_dataset_file}")
    
    # Save the list of audio files to a file
    audio_files_file = f"./{first_dataset_file.split('.')[0]}_audio_files.txt"
    with open(audio_files_file, 'w') as f:
        for audio_file in audio_files:
            f.write(audio_file + "\n")
    print(f"Audio files saved to {audio_files_file}")
        
    print(f"Number of normal samples: {normal_count}")
    print(f"Number of disordered samples: {disordered_count}")
    print(f"Total samples: {normal_count + disordered_count}")