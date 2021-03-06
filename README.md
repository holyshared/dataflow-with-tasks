# dataflow-with-tasks

## Setup

```
brew update
brew install pyenv
pyenv install 3.8.11
pyenv virtualenv 3.8.11 dataflow
pyenv local dataflow
```

## Setup for project

### apache-beam

```shell
pip install --upgrade virtualenv
python -m virtualenv env
source env/bin/activate
pip install --quiet apache-beam[gcp]
```

### GCP

```
terraform init
terraform apply
```

## Run dataflow enqueue task

```
GOOGLE_APPLICATION_CREDENTIALS=[CREDENTIALS_FILE] \
python -m \
  example.cloud_tasks \
  --project \
  [PROJECT_ID] \
  --runner DataflowRunner \
  --temp_location \
  gs://[BUCKET_NAME]/temp \
  --output \
  [QUEUE_NAME] \
  --job_name dataflow-intro \
  --region asia-northeast1 \
  --service_account_email [SERVICE_ACCOUNT_EMAIL] \
  --subnetwork=https://www.googleapis.com/compute/v1/projects/[PROJECT_ID]/regions/asia-northeast1/subnetworks/[NETWORK_NAME]
  --requirements_file ./requirements.txt
```

## Code format

```shell
pip install autopep8
autopep8 --in-place --aggressive --aggressive --ignore=E111,E114 --indent-size=2 --recursive example
```
