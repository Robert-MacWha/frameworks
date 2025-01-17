// import { createVercelBeginHandler } from "netlify-cms-oauth-provider-node"
import crypto from 'crypto';

export default async function handler(req, res) {
    // Generate a random state for CSRF protection
    const state = crypto.randomBytes(8).toString('hex');
    const scope = 'public_repo'; // Scopes required for the app
    const redirectUri = "https://" + process.env.ORIGIN + "/api/callback";

    // Build the authorization URI
    const authorizationUri = `https://github.com/login/oauth/authorize?client_id=${process.env.OAUTH_CLIENT_ID}&redirect_uri=${redirectUri}&scope=${encodeURIComponent(scope)}&response_type=code&state=${state}`;

    // Respond with a redirect to the authorization URI
    res.status(302); // HTTP 302 Found
    res.setHeader('Location', authorizationUri);
    res.end();
}