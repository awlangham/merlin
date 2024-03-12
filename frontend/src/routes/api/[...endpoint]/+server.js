export function GET({ params, url }) {
    const { endpoint } = params;
    return fetch('http://localhost:8051/api/' + endpoint + '?' + url.searchParams.toString());
}

export async function POST({ params, request }) {
    const { endpoint } = params;
    const request_json = await request.json();
    return fetch('http://localhost:8051/api/' + endpoint, { method: 'POST', headers: { "Content-Type": "application/json" }, body: JSON.stringify(request_json) });
}

export async function PUT({ params, request }) {
    const { endpoint } = params;
    const request_json = await request.json();
    return fetch('http://localhost:8051/api/' + endpoint, { method: 'PUT', headers: { "Content-Type": "application/json" }, body: JSON.stringify(request_json) });
}