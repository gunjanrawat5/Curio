import type { Stroke } from './strokes';
export type CanvasSnapshot = { png_base64: string; canvas_revision: number; sketch_revision: string; stroke_count: number };
export async function sketchRevision(strokes: Stroke[]): Promise<string> {
 const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(strokes)));
 return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
}
export async function captureWhiteboard(svg: SVGSVGElement, canvasRevision:number, strokes:Stroke[]): Promise<CanvasSnapshot> {
 // Clone synchronously, before awaiting, to freeze exactly what was submitted.
 const clone=svg.cloneNode(true) as SVGSVGElement;
 clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
 clone.setAttribute('width','800');clone.setAttribute('height','540');
 clone.setAttribute('viewBox','0 0 800 540');clone.removeAttribute('style');
 clone.setAttribute('font-family','Arial, sans-serif');
 const background=document.createElementNS('http://www.w3.org/2000/svg','rect');
 background.setAttribute('width','800');background.setAttribute('height','540');background.setAttribute('fill','#fffdfa');
 clone.insertBefore(background,clone.firstChild);
 const source=new XMLSerializer().serializeToString(clone);
 const url=URL.createObjectURL(new Blob([source],{type:'image/svg+xml;charset=utf-8'}));
 try{
  const image=new Image();image.src=url;await image.decode();
  const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=810;
  const context=canvas.getContext('2d');if(!context)throw new Error('Your browser could not capture the whiteboard.');
  context.drawImage(image,0,0,1200,810);
  const data=canvas.toDataURL('image/png').split(',')[1];
  if(!data||data.length>2800000)throw new Error('This sketch is too large to share. Try a simpler drawing.');
  return {png_base64:data,canvas_revision:canvasRevision,sketch_revision:await sketchRevision(strokes),stroke_count:strokes.length};
 }finally{URL.revokeObjectURL(url)}
}
