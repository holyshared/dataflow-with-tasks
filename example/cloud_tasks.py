import argparse
import logging
import json

import apache_beam as beam
from apache_beam.io import ReadFromText

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

from google.cloud.tasks_v2.services.cloud_tasks import CloudTasksClient
from google.cloud.tasks_v2.types import CreateTaskRequest, Task, HttpRequest, OidcToken
from google.cloud.tasks_v2.types import CreateTaskRequest
from google.cloud.tasks_v2 import HttpMethod

"""
Extract a specific field from a json string

{ "id": "unique_id_1" } -> unique_id_1
{ "id": "unique_id_2" } -> unique_id_2
"""


def extract_json(element):
  entry = json.loads(element)
  return entry["id"]


def cloud_functions_url(region, project):
  return 'https://{}-{}.cloudfunctions.net/exampleTask'.format(region, project)


class TaskRequestFactory:
  def __init__(self, url: str, service_account_email: str, payload: str):
    self._url = url
    self._service_account_email = service_account_email
    self._payload = payload

  def create_request_for(self, queue_path: str):
    oidc_token = OidcToken(service_account_email=self._service_account_email)
    headers = {"Content-type": "application/json"}
    http_request = HttpRequest(
        url=self._url,
        http_method=HttpMethod.POST,
        headers=headers,
        body=self.payload,
        oidc_token=oidc_token)

    return CreateTaskRequest(
        parent=queue_path,
        task=Task(http_request=http_request)
    )


class CreateTask(beam.DoFn):
  def __init__(self, url: str, service_account_email: str):
    self._url = url
    self._service_account_email = service_account_email

  def process(self, element):
    payload = json.dumps({
        'id': element
    }).encode()

    return [
        TaskRequestFactory(
            url=self._url,
            service_account_email=self._service_account_email,
            payload=payload)]


class TaskFormJSON(beam.PTransform):
  def __init__(self, url: str, service_account_email: str):
    # TODO(BEAM-6158): Revert the workaround once we can pickle super() on py3.
    # super(TaskFormJSON, self).__init__()
    beam.PTransform.__init__(self)
    self._url = url
    self._service_account_email = service_account_email

  def expand(self, pcoll):
    return pcoll | beam.Map(extract_json) | beam.ParDo(CreateTask(
        url=self._url, service_account_email=self._service_account_email))


class Enqueue(beam.DoFn):
  def __init__(self, project, region, queue):
    self._project = project
    self._region = region
    self._queue = queue

  def setup(self):
    self._client = CloudTasksClient()
    self._queue_path = self._client.queue_path(
        self._project, self._region, self._queue)

  def process(self, factory):
    request = factory.create_request_for(self._queue_path)
    created_task = self._client.create_task(request)
    return [created_task.name]


class EnqueueToCloudTasks(beam.PTransform):
  def __init__(self, project, region, queue):
    # TODO(BEAM-6158): Revert the workaround once we can pickle super() on py3.
    # super(EnqueueToCloudTasks, self).__init__()
    beam.PTransform.__init__(self)
    self._project = project
    self._region = region
    self._queue = queue

  def expand(self, pcoll):
    return pcoll | beam.ParDo(
        Enqueue(
            project=self._project,
            region=self._region,
            queue=self._queue))


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

    output | EnqueueToCloudTasks(
        project=options['project'],
        region=options['region'],
        queue=known_args.queue)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
