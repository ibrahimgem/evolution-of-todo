import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
    });

    return NextResponse.json(
      { status: response.ok ? 'healthy' : 'unhealthy' },
      { status: response.ok ? 200 : 503 }
    );
  } catch (error) {
    console.error('Health check proxy error:', error);
    return NextResponse.json(
      { status: 'unhealthy', error: 'Backend unreachable' },
      { status: 503 }
    );
  }
}