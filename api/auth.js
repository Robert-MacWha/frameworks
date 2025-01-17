// import { createVercelBeginHandler } from "netlify-cms-oauth-provider-node"
import crypto from 'crypto';

export default async function handler(req, res) {
    // Generate a random state for CSRF protection
    const state = crypto.randomBytes(8).toString('hex');
    const scope = 'repo'; // Scopes required for the app

    // Build the authorization URI
    const authorizationUri = `https://github.com/login/oauth/authorize?client_id=${process.env.GITHUB_CLIENT_ID}&redirect_uri=${process.env.CALLBACK_REDIRECT_URI}&scope=${encodeURIComponent(scope)}&response_type=code&state=${state}`;

    // Respond with a redirect to the authorization URI
    res.status(302); // HTTP 302 Found
    res.setHeader('Location', authorizationUri);
    res.end();
}