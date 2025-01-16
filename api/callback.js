#!/usr/bin/env deno run --version v2.1.5
import { createVercelCompleteHandler } from "netlify-cms-oauth-provider-node"

module.exports = createVercelCompleteHandler({}, { useEnv: true })
