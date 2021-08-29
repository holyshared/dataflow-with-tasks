import { createLogger } from 'bunyan'
import { LoggingBunyan } from '@google-cloud/logging-bunyan'

const loggingBunyan = new LoggingBunyan({
  projectId: process.env.GCP_PROJECT_ID,
  logName: 'dataflow',
})

export const logger = createLogger({
  name: 'dataflow',
  streams: [
    loggingBunyan.stream('info'),
  ],
})
