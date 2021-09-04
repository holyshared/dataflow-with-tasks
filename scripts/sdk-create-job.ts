import { FlexTemplatesServiceClient } from "@google-cloud/dataflow"
import { v4 } from "uuid"

const client = new FlexTemplatesServiceClient({
  projectId: process.env.GCP_PROJECT_ID,
})

// https://dataflow.googleapis.com/v1b3/projects/{projectId}/locations/{location}/flexTemplates:launch?
client.launchFlexTemplate({
  projectId: process.env.GCP_PROJECT_ID,
  location: process.env.GCP_REGION,
  launchParameter: {
    jobName: `dataflow-cloud-tasks-${v4()}`,
    containerSpecGcsPath: process.env.GCP_CONTAINER_SPEC_PATH,
    parameters: {
      input: process.env.GCP_INPUT,
      output: process.env.GCP_OUTPUT,
      queue: process.env.DATAFLOW_QUEUE,
    },
    environment: {
      subnetwork: process.env.GCP_SUBNETWORK,
      serviceAccountEmail: process.env.GCP_SERVICE_ACCOUNT_EMAIL,
    }
  }
}).then(([res, req]) => {
  console.log("job %s created", res.job.name)
}).catch(err => {
  console.log(err.stack)
})
