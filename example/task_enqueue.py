import os
import json

from google.cloud.tasks_v2beta3.services.cloud_tasks import CloudTasksClient
from google.cloud.tasks_v2beta3.types import CreateTaskRequest, Task, HttpRequest, OidcToken
from google.cloud.tasks_v2beta3 import HttpMethod

QUEUE_PATH = CloudTasksClient.queue_path(
  os.environ['GCP_PROJECT_ID'],
  os.environ['GCP_REGION'],
  os.environ['DATAFLOW_QUEUE']
)

TASK_URL = 'https://{}-{}.cloudfunctions.net/exampleTask'.format(os.environ['GCP_REGION'], os.environ['GCP_PROJECT_ID'])

client = CloudTasksClient()

def run():
  payload = json.dumps({
    'id': 'id-1'
  }).encode()

  oidc_token = OidcToken(service_account_email=os.environ['FUNCTION_INVOKER_SERVICE_ACCOUNT_EMAIL'])
  headers = { "Content-type": "application/json" }
  http_request = HttpRequest(url=TASK_URL, http_method=HttpMethod.POST, headers=headers, body=payload, oidc_token=oidc_token)

  task = Task(http_request=http_request)

  request = CreateTaskRequest(
    parent=QUEUE_PATH,
    task=task
  )

  client.create_task(request=request)

if __name__ == '__main__':
  run()
