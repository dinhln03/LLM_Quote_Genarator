# Huggingface Dataset
https://huggingface.co/datasets/dinhlnd1610/Vietnamese_Quote_Dataset_100K
# Huggingface Model(in progress)

# How to guide 
```bash
# Clone this repository and install python version 3.10
$ git clone https://github.com/dinhln03/LLM_Quote_Genarator.git
# Go into the repository
$ cd LLM_Quote_Generator
# Change API key in .env file and then
$ set -a && source .env && set +a
```
## 1. Training phase
### Download English quote dataset and translate to Vietnamese
Original quote dataset: https://github.com/ShivaliGoel/Quotes-500K

Link to download: https://drive.google.com/file/d/11MmVMc0khvB94W0zqDyUHowEEG650BSX/view?usp=drive_link
```bash
$ cd training/scripts
$ pip install -r requirements.txt
# Translate English quotes to Vietnamese using Gemini with multiple threads. Note that
# $data_path is the path to the downloaded English quote dataset, $sample_length is the number of quotes to translate,
# $start_batch is the starting batch number, $end_batch is the ending batch number, and $num_thread is the number of threads to use.
$ python translate.py main $data_path $sample_length $start_batch $end_batch $num_thread
```
### Download model
```bash
# Download google/gemma-2b model on huggingface hub and write appropriate chat template for generating quotes
$ cd training/scripts
# Install dependencies
$ sh run.sh
$ cd utils
$ python training_utils.py download_model google/gemma-2 ../../gemma-2b
```
### Training gemma-2b model
**If you have 1 GPU**, just run
```bash
$ python training/scripts/training.py
```
**If you have 1 cluster and multiple GPUs**, run Distributed Data Parallel
```bash
$ torchrun --standalone --nnodes=1 --nproc-per-node=$NUM_GPUs training.py
```
This script will help you train the model on multiple GPUs using Distributed Data Parallel (DDP) method.

## Demo
Web: 34.124.194.242.nip.io/docs

Format: `<bos>Topic<sep>Quote`

Ex: `<bos>Tình yêu<sep>Đôi mắt em`<br>   
`    <bos>Cuộc sống<sep>`