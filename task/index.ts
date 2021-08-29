import type { Request, Response } from "express"

import { logger } from "./logger"

export const exampleTask = (req: Request, res: Response) => {
  logger.info({ message: req.body })
  res.status(200).end()
}