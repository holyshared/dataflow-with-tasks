import { GoogleAuth } from "google-auth-library"
import { v4 } from "uuid"

const auth = new GoogleAuth({
  scopes: 'https://www.googleapis.com/auth/cloud-platform',
});

const launchFlexTemplate = async (): Promise<{ job:{ name: string } }> => {
  const client = await auth.getClient();

  const url = `https://dataflow.googleapis.com/v1b3/projects/${process.env.GCP_PROJECT_ID}/locations/${process.env.GCP_REGION}/flexTemplates:launch`
  const res = await client.request<{ job: { name: string } }>({
    url,
    method: "POST",
    body: JSON.stringify({
      launchParameter: {
        jobName: `extract-json-field-${v4()}`,
        containerSpecGcsPath: process.env.GCP_CONTAINER_SPEC_PATH,
        parameters: {
          input: process.env.GCP_INPUT,
          output: process.env.GCP_OUTPUT,
        },
        environment: {
          subnetwork: process.env.GCP_SUBNETWORK,
          serviceAccountEmail: process.env.GCP_SERVICE_ACCOUNT_EMAIL,
        }
      }
    })
  });

  return res.data
}

launchFlexTemplate().then((result) => {
  console.log("job %s created", result.job.name)
}).catch(err=> {
  console.log(err.stack)
})
