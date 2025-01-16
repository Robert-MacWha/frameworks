#!/usr/bin/env deno run --version v2.1.5
import { createVercelBeginHandler } from "netlify-cms-oauth-provider-node"

module.exports = createVercelBeginHandler({}, { useEnv: true })
