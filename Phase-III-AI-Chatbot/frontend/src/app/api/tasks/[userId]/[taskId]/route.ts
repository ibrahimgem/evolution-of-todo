import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * PUT /api/tasks/[userId]/[taskId] - Update a task
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; taskId: string }> }
) {
  try {
    const { userId, taskId } = await params;
    const token = request.headers.get('authorization');
    const body = await request.json();

    const response = await fetch(
      `${BACKEND_URL}/api/${userId}/tasks/${taskId}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: token } : {}),
        },
        body: JSON.stringify(body),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating task:', error);
    return NextResponse.json(
      { error: 'Failed to update task' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/tasks/[userId]/[taskId] - Delete a task
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string; taskId: string }> }
) {
  try {
    const { userId, taskId } = await params;
    const token = request.headers.get('authorization');

    const response = await fetch(
      `${BACKEND_URL}/api/${userId}/tasks/${taskId}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: token } : {}),
        },
      }
    );

    if (response.status === 204) {
      return NextResponse.json({ message: 'Task deleted successfully' });
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting task:', error);
    return NextResponse.json(
      { error: 'Failed to delete task' },
      { status: 500 }
    );
  }
}
