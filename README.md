<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to generate synthetic data for translating English quotes into Vietnamese using the Gemini API. The generated data serves as the foundation for fine-tuning the Gemma-2b model, enhancing its ability to produce high-quality Vietnamese quotes. The ultimate goal is to deploy the model and make it production-ready and highly scalable using Kubernetes on Google Cloud Platform (GKE) and integrate with CI-CD pipeline. This is my first project of MLOps course 1 at [FSDS](https://www.fullstackdatascience.com/). I'd like to give a big credit to my instructor [Mr. Quan Dang](https://www.linkedin.com/in/quan-dang/) for his guidance and support.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Gemini API][Gemini-logo]][Gemini-url]
* [![Unsloth][Unsloth-logo]][Unsloth-url]
* [![FastAPI][FastAPI-logo]][FastAPI-url]
* [![Docker][Docker-logo]][Docker-url]
* [![GKE][GKE-logo]][GKE-url]
* [![Ansible][Ansible-logo]][Ansible-url]
* [![Terraform][Terraform-logo]][Terraform-url]
* [![Ngnix][Ngnix-logo]][Ngnix-url]
* [![Elasticsearch][Elasticsearch-logo]][Elasticsearch-url] [![Logstash][Logstash-logo]][Logstash-url] [![Kibana][Kibana-logo]][Kibana-url]
* [![Prometheus][Prometheus-logo]][Prometheus-url] [![Grafana][Grafana-logo]][Grafana-url]
* [![Jaeger][Jaeger-logo]][Jaeger-url]
* [![Jenkins][Jenkins-logo]][Jenkins-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project. If you don't want to fine-tune the model, you can skip the <a href="#dg">data generation section</a> and <a href="#training">training section</a> and move ahead to the <a href="#readme-top">deployment section</a>. Checkout my data and model on the Huggingface hub as prequisites for the deployment phase.:
- Dataset: [dinhlnd1610/Vietnamese_Quote_Dataset_100K](https://huggingface.co/datasets/dinhlnd1610/Vietnamese_Quote_Dataset_100K)
- Model: [dinhlnd1610/gemma-2b-quote-generation-82000](https://huggingface.co/dinhlnd1610/gemma-2b-quote-generation-82000)

### Prerequisites

1. Clone the repository
   ```sh
   git clone https://github.com/dinhln03/LLM_Quote_Genarator.git
   ```
2. Cd into the project directory
   ```sh
   cd LLM_Quote_Genarator
   ```

<a id="dg"></a>

### I. Data Generation 

In this phase, we will translate the English quote to Vietnamese using Gemini Pro and.

1. Get your Gemini API key and save it in the `.env` file
   ```sh
   cd training/translate
   set -a && source .env && set +a
   ```
2. Download English quote dataset and install the required packages
   ```sh
   gdown https://drive.google.com/uc?id=11MmVMc0khvB94W0zqDyUHowEEG650BSX
   conda create -n training python=3.10 -y && conda activate training  && pip install -r requirements.txt
   ```
3. Run the Script to generate Vietnamese quotes. Data will be saved in `data` folder and log will be saved in `log` folder
   ```bash
   python run.py main \
     --data_path=$data_path \
     --sample_length=$sample_length \
     --start_batch=$start_batch \
     --end_batch=$end_batch \
     --num_thread=$num_thread
   ```
   ```bash
   # Example
   python run.py main --data_path=./data.csv --sample_length=20000 --start_batch=0 --end_batch=4000 --num_thread=5
   ```
   | Parameter | Description |
   |-----------|-------------|
   | `$data_path` | Path to the downloaded English quote dataset |
   | `$sample_length` | Number of quotes to translate |
   | `$start_batch` | Starting batch number |
   | `$end_batch` | Ending batch number |
   | `$num_thread` | Number of threads to use |

   **Key Notes:**
   - You should choose `num_thread` such that `(end_batch - start_batch + 1)` is divisible by `num_thread`.
    - Calculate `num_thread` using:
      ```sh
      num_thread = (end_batch - start_batch) // 5
      ```
4. Merge json data in folder `data` to a single json file
   ```bash
   python utils/merge_file.py 
   ```
5. Checkout the notebook to do some preprocessing data step such as: removing duplicate data point, remove toxic words,.. and push to huggingface hub. You can include more preprocessing steps such as removing more toxic words, filtering by perplexity,...

<a id="training"></a>

### II. Fine-tuning Gemma-2b model
1. Install the required packages
   ```sh
   cd training/training_scripts
   sh run.sh
   ```
2. Download google/gemma-2b model on huggingface hub and write appropriate chat template for generating quotes
   ```sh
   cd utils
   python training_utils.py download_model google/gemma-2b ../../gemma-2b
   ```
3. Fine-tune gemma-2b model on translated data produced in the previous step
   ```bash
   cd ..
   ```
   **If you have only 1 GPU**, just run
   ```bash
   export CUDA_VISIBLE_DEVICES=0
   python training.py
   ```
   **If you have 1 node and multiple GPUs**, run Distributed Data Parallel
   ```bash
   export CUDA_VISIBLE_DEVICES=1,2,...
   torchrun --standalone --nnodes=1 --nproc-per-node=$NUM_GPUs training.py
   ```
4. Login to Wandb to monitor the training process
   ![alt text](images/wandb-training.png)
   ![alt text](images/wandb-eval.png)
5. Merge the lora model with the base model. 
   ```bash
   cd utils
   python training_utils.py merge_model \
      --base_model_path=$base_model_path \
      --lora_path=$lora_model_path \
      --output_path=$output_model_path
   ```
   | Parameter | Description |
   |-----------|-------------|
   | `$base_model_path` | Path to the orginal google/gemma2b model |
   | `$lora_model_path` | Path to the fine-tuned lora adapter |
   | `$output_model_path` | Path to save the merged model |
6. Checkout the notebook to push the model to huggingface hub. 














<!-- MARKDOWN LINKS & IMAGES -->
[GKE-logo]: https://img.shields.io/badge/GKE-blue?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAk1BMVEX///9Rm/dMkulRmvatzfvY5/1Omffg7PtYmOpMkuhKl/ZCjOjk7vtJkOlrqfh1r/hzqO2mx/Ps8/z3+v6ewfI9iuj1+f5ln+thnOva6Pp7re6ryfRFlPbM4Pyix/pyrPhjpPeNu/m30fWUvvlcn/ez0vvB1/bQ4fl/tPiCsu+Lt/Caw/qLu/k3jvWyzvRppOwug+eqs0SkAAANJElEQVR4nO1ca1vqvBK1jQSaEhVKy60gAnJV2f//1520TWYm3MT3Q9PzPFnuLRQRszqXNTMpPD15eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHg4RtZtt/4Dxu2+65U/hmyz2r2+/Ae8v+6eW65X/wCSY5ALwUswfg3s/EfmvhBi8Zm4JvAbNjvGg4AVX6y4Lf8zVhyW3/XD1VdQHplj9Y+L9bHhrjoTnOkla3IBAUPu8Ig+CeZBJr4y1yTuob/mTBuoNBlwCqqHKgsyfQKIeQNjcsbEs2sW9/AiGBhI8zFWZOQO2EzTI7ZWB9+frmncRmtNnJJhrDHgy9AdGbqrYVgdCtbcbLMCV2TogmitAH5mMQW+5hzkjfXT2UJAioFAM2Zkho6xm00XfqF46sI1kxto7zhNGTSDgq8CV51+0L4oI0o0mmnEZC4IAUynJC6Rr/Fa0EPrh3wxds3mGsYvAoxnRIGqOglOSLG0DLDic+6azRUoE2JW1A4ZGPWn4WnVAIF1zIw68sXMNZ9LbDnHdZ6vHxIlJlBGWINUgMnFrnHFW3stiCjYPIhgMPBTHacapKKr6ObzponiPCe5hFmBqO9jINIviFZqdfWPv7ddU7KRvfCAuBqqH6lrMLegmeE5lGj15KVrTjaOOQYfFQAieCTYjGcSr8TiXD9JvDSqG27nHKtP6AWJ3KH+QSRCMELSwZ8Ud/PXJiWbLwFRSOQCfPD8G9Y11jdarhbJpkE9RtEWmuKZrDHA+1QqsNmA1IOlnfHvItm8uOYFyHYcwgpUG3KO3VwQmQiIS5OiFQKS5Y1JNh85JA1iDir92BoZBoF9SkiOwl9h3w2JxO2CoxJQPpQdmMmIBxgSdN44OGYscXTNrcKcW+pGq2h6cFmP2iYjxSto57rrmlyBluopSMkFMUYLMchCXAiOnM7ykaWa5S1fNWDw1l+Js+iBkoakRn1XrI+frznHIMX6xqRhUt2pHiNoQC88XnDkQQxAVVF/5/limT11v7gw3CzdtO1Y3Rfvzv206OwvUj2SMr1FsWBlwLIQ6293nNPyhooGCIv+9bVzxVjmzM4v1GVJNRaI72NiGqJktvjmOrsyMDQ6AKnDxavjHqOtEodZKJgRNQ50UOSvViHdX77nnMHJAb3Agt04cT53m2y+cDZDTQBxVi2ai/fNxa/OuaBBZxmfpFXHU6kMpJ7wwlxT2YEH6y9dnPTHyVOrqw8+F2U5i3ywGEJvVfnXZSRmXzk2u+CgJJ+WK1zMt1UA9jdvk/5TLzzMquPuskg5pDynRQI4O19f2r82POe21WzVKFfK8xczNhvvw7RgmMadHx1b3flaGEGkRQ28RHEvXzgrT7taCsmisMHVGeZlpTNM9+eUSlkyDGU02FSrTmYfa4GFjMk7SK94KXc9xjOYCvWPZtBAiPm4sla2fItkGGqGCp3JtnqR/uzlWwTUVS/yDl84Ith6gf1sIw7QGpYBKHY64JLNJJKKYMUwLhiGsjPQ5QpRDtp/kXjO3YzAkw9BAo90TLqqRAWcjUINwjCUoTzocMw+hbgIZqo8bgYapQnBMa3JSxmBMLXeFP5JGKbmKIz3pupcBoJD64ghaSoBsXAwH07mHAQMqkizOpVhdAbNZm8pEDxnGMZyr5Uk+1xA+2vJohYQB0bcrDnOH84HEYxr44xP/4BfFMpY+eUmlpJwTHvaPEeOr2B4Qqrmr7UbsbsTVmUN9WXpo+K9fFJ/c4qRjJTDY1FGL/cdwlHGg23pz9s1PyviyGnj67qNmDznzFoCilmxSvH6VFz+NYkIk3Q4NR45O0jCMe4cipzU7kgoj2jGqe7U3mN0F3jCYWCIlVbJsGtFYHTY4q/3p5OQmrFXMgxD006ZV4LUpYrbmo1oRhfoVKTHA4YxGvDUspqgpL/pxJH5aWgYhjT6LO8I+KLWfYxuDlWyFTjGBGcMlZEuS8tuJwX7AkNDkc4GNOH8o87ydCXI2WVGKbAosRnK0/bai2SDyKQgZBiaTjjAoNQuW2cb1f+mLmksR5qKM4bx5No86ceEKfFSJSlYw5vkpV9f1LcZlXzlVgTSnFcd2gyjMD1tzlaX9KeKYJVrKcOSoj5fNLTLUKwtEucQhYyIfoDjUZvhaHDopOnbhqaa8VT1Um+DfXweh1Us6tENdFBaFOtqFLtrTv4yzaZgSspQDsdPy0knTg9bs8DucpjGQ9VbDNJrDEMGLmpOW3X7XVMkbtZmEkY6Hcgz5bHNUDlXd7ZP5WhfFqv95SRK5UDJf3adYSSZ5R5wLvlrPQyfLQGk9QdoxwVDxeuYxvHoRzGZqGL0tCx81jAMz2xYOqrpNNGa6qsehkf8g8ZoZOTJLr20ShCqiAvTzqF3UkR7VQl2w4ZENOwkFoh6GK6s9oa4EnjsVYYqf25PqXLBFLTjDsOQtlHgpnk90+GVNW1gaDz02esM1UMTJQ84HLzDMApJ/mI1M5yfiR+cY6R4i+HTeJhO8eh2HBYUOeqQOZM1eelybWIEmEFnqCPxJsPWKO1dMpRXGBbSD5vjuiqsa+jWWnOopEipRo/+yPCaDYn0Q6yLVT0Mk1dh0gqNQDqM+iPDa5kmNDUq7EIFLK9rvj9em4svINuYGemV3iIekc0jm2EyKKc4txhWNSrGt9jVttE2y4lUWBtP7Lw/VNowI0Mkm+FTe/oWy9sMQ9ovqu819sA7QZSKzKMMDMMoPW2t837GULUYPyoM7zAM8bXzOi/MWH7r6sVuC8GmZk7zb1IsarYHP7UYTg+FdTdpeivTGNGoTmVe57XfVbIxeRz9yCSFkmH7reztx3sZh8fxOcNkM0pV+abKm+xnOLjJ0MSikop6t7u7WKExEH/o6iqG/VZSeGFa5Jv43zFLCMOsvy86fJlGM7XubHybYamL6tVFrWOa4p2iOWkpcL9Qpxqh25x2r2OmUaqv6BqGyWxvJqkynsyqpd9iGJb9Yv3vT9gGQidyu70hlbdaNJnpKy6nzdO4YJhMo5gMhP9Nkl8YKketUSk0sjlMU0gsGn8V1cWv/embNb8f9X5G8WA2iOjGRefwUzLc3maoHNXBZn5/JRg6Kq2Ri6zA9YS6vRySrSYZjiI5GhF+Mt7r2UZykJfUEDXVaxZm+rJSMhuGdoPxQDe5T93eKLbWSvmFbz8Vv2x2iMLbkB0XF+5nHwLIwcwIDMnZSI+Nku7h33XzpB0zf+tPovCeCdODA4JVF0UGYQzyTXXDw4O5TqgXxZerlimMwsfDKz+3zO7oepMVN5UoTt4YqEfA4gguRhiMzkwk5cmk/9khvhuCKhu5uvBrazspVsgmOJUftnTZndg0qpawQHZM7xtQPXnviGBRu5neAn3UNIylMcM4HHT1FSe9YaSlQ8rOXif/fmv/Gz8Vhe4u+2q/CNofQsuI/qrkYNgze/rTSUkxlnudYZLN4dx7r/noweH1l1tyyTYMaqDdLylGqi5bauVoD4aqCp9MjUIMOr9FYFhdv+EQX9gokmEUDqhKijI66Uv1svFhuOlXbjvej+4qhEHn6uZjbZh948iP2TcmuxZXmcjQTIEzMw3eDh+wX+Gjbk1YbiWaJHq2kQLSERbVihxZG93bQ+chfgquL2XvvwrsE63JGDqujqcOpMT+rwoIkAOX7EqUF/qQXRpoFQMoBgzFdLgs7Fg0jQ8THLqNwgL9D3yPM4lDs5tRfZn1ppOWavrTu6QsxG4KUhtLFELQRLyGT6cbY7O4M5SP2q84JaMmfPJAVpan1tiNjBZNZoU1/4FfKCOHF7ETlI0izE4xxUBeLb/kvf7vFkNnBamN5OPsY2nIDWbWSjT+RjBtykecbNcCu3vqqXTiiI76MOKha2aAT84xraBIYK3KdI36Rxs6f2ceYsdJVwGRaDoOGFD90YTuxR5RvEePFGqBlVaJSP6NoXuxRyTvgowvArORCI8xU839xUcHjfr8lrF5MyEpT0EOqe8+HIvSZd97DascEw1mVWz9DctHrWjtjTcC2280GyPGg+QKlfljDONDQz5PAZAVn1BDxhcgEeRRbddHHJW0Wo2B7jGwjMEumKrjg7EYTX//i7Vju8a0An2iSanQ9T+YbprQNF0gW+U4pcHG6awADx5yVMfTp1tYBhyCzXAiBY7VW/0ShW8NUwqN7Ln6qCETcOCgUKESd71L0Mle2iPIdgznbHQmxQxnbJPvOWojRhfXsVkTS0G5RgtyQvgmRRk3qKc4Q7YQZhp8VnSjTDIgecuEjrZDH8MMJRHlgVbjIJSFfa9bMd43rZqx8Pxt90ykC6bm04fXKMphc320RFC+8dySQbpbQwaPV1tiKVPXU/zfkHwuyo/Kr6hx0HjQDqgEGLugKGV4asKA9Be0PxaLdfAoIoLO6O3K+xSbiPbs8/lhTBGb7f8HPw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PD4+G438NLskjpFeIVwAAAABJRU5ErkJggg==
[GKE-url]: https://cloud.google.com/kubernetes-engine
[Docker-logo]: https://img.shields.io/badge/Docker-blue?logo=docker
[Docker-url]: https://www.docker.com/
[Gemini-logo]: https://img.shields.io/badge/GeminiAPI-blue?logo=googlegemini
[Gemini-url]: https://ai.google.dev/
[Unsloth-logo]: https://img.shields.io/badge/Unsloth-green?logo=data:image/jpeg;base64,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
[Unsloth-url]: https://unsloth.ai/
[FastAPI-logo]: https://img.shields.io/badge/FastAPI-009688?logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[Elasticsearch-logo]: https://img.shields.io/badge/Elasticsearch-005571?logo=elasticsearch
[Elasticsearch-url]: https://www.elastic.co/elasticsearch
[Logstash-logo]: https://img.shields.io/badge/Logstash-005571?logo=logstash
[Logstash-url]: https://www.elastic.co/logstash
[Kibana-logo]: https://img.shields.io/badge/Kibana-005571?logo=kibana
[Kibana-url]: https://www.elastic.co/kibana
[Ansible-logo]: https://img.shields.io/badge/Ansible-EE0000?logo=ansible
[Ansible-url]: https://www.ansible.com/
[Terraform-logo]: https://img.shields.io/badge/Terraform-white?logo=terraform
[Terraform-url]: https://www.terraform.io/
[Ngnix-logo]: https://img.shields.io/badge/Nginx-009639?logo=nginx
[Ngnix-url]: https://docs.nginx.com/nginx-ingress-controller/
[Prometheus-logo]: https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus
[Prometheus-url]: https://prometheus.io/
[Grafana-logo]: https://img.shields.io/badge/Grafana-F46800?logo=grafana
[Grafana-url]: https://grafana.com/
[Jaeger-logo]: https://img.shields.io/badge/Jaeger-jaeger?logo=jaeger
[Jaeger-url]: https://www.jaegertracing.io/
[Jenkins-logo]: https://img.shields.io/badge/Jenkins-D24939?logo=jenkins
[Jenkins-url]: https://www.jenkins.io/
