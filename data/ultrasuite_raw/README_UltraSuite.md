# How to create UltraSuite dataset

```bash
git clone https://huggingface.co/datasets/SAA-Lab/UltraSuite
git clone https://huggingface.co/datasets/SAA-Lab/UltraSuitePlus
python process_data.py UltraSuite
python process_data.py UltraSuitePlus
python create_dataset.py ultrasuite.json ultrasuiteplus.json 1000
```
