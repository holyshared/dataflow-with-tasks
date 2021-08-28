import type { Request, Response } from "express"

export const exampleTask = (req: Request, res: Response) => {
  console.log(req.body)
  res.status(200).end()
}