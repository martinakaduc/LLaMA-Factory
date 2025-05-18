export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export DISABLE_VERSION_CHECK=1
llamafactory-cli train configs/gemma3-12b-it_lora_sft_1.yaml
llamafactory-cli export configs/merge_lora/gemma3-12b-it_lora_sft_1.yaml