import winston from 'winston'
import { LoggingWinston } from '@google-cloud/logging-winston'

const loggingWinston = new LoggingWinston({
  projectId: process.env.GCP_PROJECT_ID,
  logName: "dataflow",
  level: 'info',
})

export const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    loggingWinston,
  ],
})
