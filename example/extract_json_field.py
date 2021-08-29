import argparse
import logging
import json

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

from google.cloud.tasks_v2beta3.services.cloud_tasks import CloudTasksClient
from google.cloud.tasks_v2beta3.types import CreateTaskRequest, Task, HttpRequest, OidcToken
from google.cloud.tasks_v2beta3 import HttpMethod

"""
Extract a specific field from a json string

{ "id": "unique_id_1" } -> unique_id_1
{ "id": "unique_id_2" } -> unique_id_2
"""
def extract_json(element):
  entry = json.loads(element)
  return entry["id"]

def enqueue_task(queue_path, url, service_account_email):
  def _enqueue_task(element):
    payload = json.dumps({
      'id': element
    }).encode()

    oidc_token = OidcToken(service_account_email=service_account_email)
    headers = { "Content-type": "application/json" }
    http_request = HttpRequest(url=url, http_method=HttpMethod.POST, headers=headers, body=payload, oidc_token=oidc_token)

    task = Task(http_request=http_request)

    request = CreateTaskRequest(
      parent=queue_path,
      task=task
    )

    client = CloudTasksClient()
    client.create_task(request=request)

    return element
  return _enqueue_task

def run(argv=None, save_main_session=True):
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      required=True,
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      required=True,
      help='Output file to write results to.')
  parser.add_argument(
      '--queue',
      dest='queue',
      required=True,
      help='Queue name to be enqueued')
  known_args, pipeline_args = parser.parse_known_args(argv)

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

  options = pipeline_options.get_all_options()

  task_creator = enqueue_task(
    queue_path=CloudTasksClient.queue_path(
      options['project'],
      options['region'],
      known_args.queue
    ),
    url='https://{}-{}.cloudfunctions.net/exampleTask'.format(options['region'], options['project']),
    service_account_email=options['service_account_email']
  )

  with beam.Pipeline(options=pipeline_options) as p:
    lines = p | 'Read' >> ReadFromText(known_args.input)

    output = lines | 'Pick' >> beam.Map(extract_json) | 'Enqueue' >> beam.Map(task_creator)

    output | 'Write' >> WriteToText(known_args.output)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
