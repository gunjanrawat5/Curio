export type SketchEvidence = { event_id:string; created_at:string; canvas_revision:number; sketch_revision:string; image_sha256:string; stroke_count:number; analysis:{summary:string;needs_clarification:boolean;reply:string;observations:{description:string;mark:string;element_id:string|null;part_index:number|null;confidence:number}[]} };
export type Message = { id: string; role: 'you' | 'curio'; text: string; kind: string; created_at: string };
export type FractionBar = { id: string; numerator: number; denominator: number; shaded_parts: number[]; source: string; source_event_id: string };
export type MathElement = { id: string; kind: 'line'|'arrow'|'circle'|'polygon'|'text'; x: number; y: number; x2: number; y2: number; radius: number; points: {x:number;y:number}[]; text: string; color: 'purple'|'orange'|'green'|'ink'; filled: boolean };
export type MathDiagram = { id: string; source: string; kind: 'geometry'|'graph'; title: string; elements?: MathElement[]; graph?: { expression: string; x_min:number; x_max:number; y_min:number; y_max:number }; segments?: {x:number;y:number}[][] };
export type BoardCommand = {type:'clear_whiteboard';clear_freehand:boolean} | {type:'move_math_element';element_id:string;dx:number;dy:number} | {type:'edit_math_label';element_id:string;text:string} | { type: 'create_fraction_bar'; numerator: number; denominator: number } | { type: 'shade_fraction_part'; bar_id: string; part_index: number; shaded: boolean };
export type Whiteboard = { revision: number; last_clear_id: string|null; bars: FractionBar[]; diagrams: MathDiagram[]; can_undo: boolean; last_action: { source: string; description: string; operation?: string } | null };
export type Session = { id: string; topic_id: string; phase: 'teaching' | 'challenge'; messages: Message[]; hints: number; whiteboard: Whiteboard; sketches: SketchEvidence[] };
const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export function apiUrl(path:string){return `${base}${path}`;}
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
