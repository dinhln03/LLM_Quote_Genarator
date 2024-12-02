conda install pytorch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 pytorch-cuda=12.1 -c pytorch -c nvidia
conda install "xformers<0.0.26" -c xformers
pip install fire==0.7.0 transformers==4.46.3 datasets==3.1.0 sentencepiece==0.2.0 "huggingface[cli]" wandb==0.18.7
pip install "trl<0.9.0" peft==0.13.2 accelerate==1.1.1 bitsandbytes==0.44.1