export type Stroke = { id: string; points: string; color: string };
// Keep strokes added while the model was replying; clear only the submitted snapshot.
export function clearSubmittedStrokes(current: Stroke[], submitted: Stroke[]): Stroke[] {
 const ids = new Set(submitted.map(s=>s.id));
 return current.filter(s=>!ids.has(s.id));
}
export function restoreClearedStrokes(current: Stroke[], cleared: Stroke[]): Stroke[] {
 const ids = new Set(current.map(s=>s.id));
 return [...cleared.filter(s=>!ids.has(s.id)), ...current];
}
