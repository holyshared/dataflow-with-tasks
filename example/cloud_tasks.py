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

def cloud_functions_url(region, project)
  return 'https://{}-{}.cloudfunctions.net/exampleTask'.format(region, project)

class EnqueueTask(beam.DoFn):
  def __init__(self, queue_path, url, service_account_email)
    super(EnqueueTask, self).__init__()
    self.queue_path = queue_path
    self.url = url
    self.service_account_email = service_account_email

  def process(self, element):
    payload = json.dumps({
      'id': element
    }).encode()

    oidc_token = OidcToken(service_account_email=self.service_account_email)
    headers = { "Content-type": "application/json" }
    http_request = HttpRequest(url=self.url, http_method=HttpMethod.POST, headers=headers, body=payload, oidc_token=oidc_token)

    task = Task(http_request=http_request)

    return [task]

class TaskFormJSON(beam.PTransform)
  def __init__(self, queue_path, url, service_account_email):
    super(TaskFormJSON, self).__init__()
    self.task_creator = EnqueueTask(queue_path, url, service_account_email)

  def expand(self, pcoll):
    return pcoll | beam.Map(extract_json) | beam.PerDo(self.task_creator)



class Enqueue(beam.DoFn):
  def __init__(self, client, queue_path)
    super(Enqueue, self).__init__()
    self.client = client
    self.queue_path = queue_path

  def process(self, task):
    request = CreateTaskRequest(
      parent=self.queue_path,
      task=task
    )
    [self.client.create_task(request)]

class EnqueueToCloudTasks(beam.PTransform):
  def __init__(self, client, project, region, queue):
    super(EnqueueToCloudTasks, self).__init__()
    self.enqueue = Enqueue(client=client, queue_path=client.queue_path(project, region, queue))

  def expand(self, pcoll):
    return pcoll | beam.PerDo(self.enqueue)

def run(argv=None, save_main_session=True):
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      required=True,
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='queue',
      required=True,
      help='Queue name to be enqueued')
  known_args, pipeline_args = parser.parse_known_args(argv)

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

  options = pipeline_options.get_all_options()

  with beam.Pipeline(options=pipeline_options) as p:
    lines = p | ReadFromText(known_args.input)

    output = lines | TaskFormJSON(
      url=cloud_functions_url(options['region'], options['project']),
      service_account_email=options['service_account_email']
    )

    output | EnqueueToCloudTasks(client=CloudTasksClient(), project=options['project'], region=options['region'], queue=known_args.output)

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
