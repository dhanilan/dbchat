# Description: This script is used to download the Spider dataset
# if env variable ATTACH_SPIDER_DATASET is set, then download the dataset
if [ -z "$ATTACH_SPIDER_DATASET" ]
then
    echo "ATTACH_SPIDER_DATASET is not set"
else
    echo "ATTACH_SPIDER_DATASET is set"
    echo "Downloading Spider dataset"

    # python3 -m venv .venv
    # source .venv/bin/activate
    pip install gdown
    gdown 1iRDVHLr4mX2wQKSgA9J8Pire73Jahh0m
    unzip spider.zip