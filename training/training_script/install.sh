conda install pytorch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 pytorch-cuda=12.1 -c pytorch -c nvidia
conda install "xformers<0.0.26" -c xformers
pip install fire transformers datasets sentencepiece "huggingface[cli]" wandb fire 
pip install "trl<0.9.0" peft accelerate bitsandbytes