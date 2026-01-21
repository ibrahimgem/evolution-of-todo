import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * PATCH /api/tasks/[userId]/[taskId]/complete - Toggle task completion
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; taskId: string }> }
) {
  try {
    const { userId, taskId } = await params;
    const token = request.headers.get('authorization');

    const response = await fetch(
      `${BACKEND_URL}/api/${userId}/tasks/${taskId}/complete`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: token } : {}),
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error toggling task completion:', error);
    return NextResponse.json(
      { error: 'Failed to toggle task completion' },
      { status: 500 }
    );
  }
}
