import { createVercelBeginHandler } from "netlify-cms-oauth-provider-node"

export default async function handler(req, res) {
    const state = crypto.randomBytes(8).toString('hex');
    const scope = 'repo,user';
    const callback_url = process.env.ORIGIN + '/api/callback';

    // Build the authorization URI
    const authorizationUri = `https://github.com/login/oauth/authorize?client_id=${process.env.OAUTH_CLIENT_ID}&redirect_uri=${callback_url}&scope=${encodeURIComponent(scope)}&response_type=code&state=${state}`;

    // Respond with a redirect to the authorization URI
    res.status(302);
    res.setHeader('Location', authorizationUri);
    res.end();
}