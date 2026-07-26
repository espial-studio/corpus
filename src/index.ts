interface Env {
	ASSETS: Fetcher;
}

const API_PREFIX = '/api/v1/';
const IMMUTABLE_PREFIX = '/releases/';

function cacheControl(pathname: string): string {
	if (pathname.startsWith(IMMUTABLE_PREFIX)) return 'public, max-age=31536000, immutable';
	if (pathname === '/api/v1/manifest.json') return 'public, max-age=60, must-revalidate';
	if (pathname.startsWith(API_PREFIX)) return 'public, max-age=300, must-revalidate';
	return 'public, max-age=3600';
}

export default {
	async fetch(request: Request, env: Env): Promise<Response> {
		if (request.method !== 'GET' && request.method !== 'HEAD') {
			return new Response('Method not allowed', {
				status: 405,
				headers: { Allow: 'GET, HEAD' }
			});
		}

		const response = await env.ASSETS.fetch(request);
		const headers = new Headers(response.headers);
		const pathname = new URL(request.url).pathname;
		headers.set('Cache-Control', cacheControl(pathname));
		if (pathname.startsWith(API_PREFIX) || pathname.startsWith(IMMUTABLE_PREFIX)) {
			headers.set('Access-Control-Allow-Origin', '*');
			headers.set('X-Content-Type-Options', 'nosniff');
		}
		return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
	}
};
