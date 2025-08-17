/** Error message helpers. */

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "object" && error !== null && "message" in error) {
    return String((error as { message: unknown }).message);
  }

  return "An unexpected error occurred. Please try again.";
}

export function getErrorMessageWithFallback(
  error: unknown,
  fallback: string
): string {
  const message = getErrorMessage(error);
  return message === "An unexpected error occurred. Please try again."
    ? fallback
    : message;
}
