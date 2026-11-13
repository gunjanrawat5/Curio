export type Message = { id: string; role: 'you' | 'curio'; text: string; kind: string; created_at: string };
export type Session = { id: string; topic_id: string; phase: 'teaching' | 'challenge'; messages: Message[]; hints: number };
const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export class ApiError extends Error {
 constructor(message: string, public status: number) { super(message); }
}
export async function api<T>(path: string, body?: unknown): Promise<T> {
 const controller = new AbortController();
 const timeout = setTimeout(() => controller.abort(), 45000);
 try {
  const response = await fetch(`${base}${path}`, { method: body === undefined ? 'GET' : 'POST', headers: { 'Content-Type': 'application/json' }, body: body === undefined ? undefined : JSON.stringify(body), signal: controller.signal });
  const data = await response.json();
  if (!response.ok) throw new ApiError(typeof data.detail === 'string' ? data.detail : 'Curio couldn’t process that request. Please retry.', response.status);
  return data as T;
 } catch (error) {
  if (error instanceof ApiError) throw error;
  throw new ApiError('Curio couldn’t reach the backend. Check that it is running on port 8000, then retry.', 0);
 } finally { clearTimeout(timeout); }
}
