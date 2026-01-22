/**
 * Frontend health check endpoint for Kubernetes liveness/readiness probes
 * [Task]: T019
 * [From]: specs/004-local-k8s-deployment/spec.md §US1, plan.md §DD-006
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'todo-chatbot-frontend',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    },
    { status: 200 }
  );
}
