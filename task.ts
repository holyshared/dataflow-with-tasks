import type { Request, Response } from "express"

export const exampleTask = (req: Request, res: Response) => {
  res.status(200).end()
}