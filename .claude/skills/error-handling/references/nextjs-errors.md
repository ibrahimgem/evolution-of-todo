# Next.js Error Handling Patterns

## Client-Side Error Fetching Wrapper

Use a standard wrapper for API calls to catch HTTP errors and transform them into readable messages.

```typescript
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.message || 'Something went wrong';
    const code = errorData.code || 'UNKNOWN_ERROR';

    throw new Error(`${message} (${code})`);
  }
  return response.json();
}
```

## Error Boundaries

Use Next.js `error.tsx` files to catch runtime errors in specific segments.

```tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button
        onClick={() => reset()}
        className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg"
      >
        Try again
      </button>
    </div>
  );
}
```

## Form Error Handling

Always clear previous errors and show specific field-level validation errors when using `useActionState` or standard forms.
