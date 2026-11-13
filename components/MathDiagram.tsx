'use client';
import { useId } from 'react';
import type { MathDiagram as Diagram, MathElement } from '@/lib/api';
const colors={purple:'#8063cf',orange:'#dd9b51',green:'#519f85',ink:'#50445e'};
export default function MathDiagram({diagram,selected,onSelect,selectable}:{diagram:Diagram;selected:string|null;onSelect:(id:string)=>void;selectable:boolean}){
 const arrowId=useId().replaceAll(':','');
 const g=diagram.graph;
 const elements=diagram.elements||[];
 function shape(e:MathElement){
  switch(e.kind){
   case 'line':case 'arrow':return <line x1={e.x} y1={e.y} x2={e.x2} y2={e.y2} markerEnd={e.kind==='arrow'?`url(#${arrowId})`:undefined}/>;
   case 'circle':return <circle cx={e.x} cy={e.y} r={e.radius}/>;
   case 'polygon':return <polygon points={e.points.map(p=>`${p.x},${p.y}`).join(' ')}/>;
   case 'text':return <text x={e.x} y={e.y} stroke="none" fill={colors[e.color]} fontSize="20">{e.text}</text>;
  }
 }
 const mapX=(x:number)=>50+(x-g!.x_min)/(g!.x_max-g!.x_min)*600;
 const mapY=(y:number)=>350-(y-g!.y_min)/(g!.y_max-g!.y_min)*300;
 return <g transform="translate(50 35)"><defs><marker id={arrowId} markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 Z" fill="#8063cf"/></marker></defs>
 <text x="350" y="0" textAnchor="middle" fill="#756086" fontSize="18">{diagram.title}</text>
 {g&&<g><rect x="50" y="50" width="600" height="300" fill="#fffdfa" stroke="#e1d6e9"/>{Array.from({length:11},(_,i)=>{const x=g.x_min+(g.x_max-g.x_min)*i/10;return <g key={i}><line x1={mapX(x)} y1="50" x2={mapX(x)} y2="350" stroke="#eee6f3"/><text x={mapX(x)} y="373" textAnchor="middle" fill="#9a88a6" fontSize="11">{Number(x.toFixed(2))}</text></g>})}{Array.from({length:7},(_,i)=>{const y=g.y_min+(g.y_max-g.y_min)*i/6;return <g key={i}><line x1="50" y1={mapY(y)} x2="650" y2={mapY(y)} stroke="#eee6f3"/><text x="40" y={mapY(y)+4} textAnchor="end" fill="#9a88a6" fontSize="11">{Number(y.toFixed(2))}</text></g>})}
 {g.x_min<=0&&g.x_max>=0&&<line x1={mapX(0)} y1="50" x2={mapX(0)} y2="350" stroke="#9d8ca9"/>}{g.y_min<=0&&g.y_max>=0&&<line x1="50" y1={mapY(0)} x2="650" y2={mapY(0)} stroke="#9d8ca9"/>}<text x="666" y="360" fontSize="14" fill="#756086">x</text><text x="35" y="38" fontSize="14" fill="#756086">y</text>
 {diagram.segments?.map((segment,i)=><polyline key={i} points={segment.map(p=>`${p.x},${p.y}`).join(' ')} fill="none" stroke="#8063cf" strokeWidth="3" strokeLinejoin="round"/>)}</g>}
 {elements.map(e=><g key={e.id} role="button" tabIndex={selectable?0:-1} aria-label={`Select ${e.kind}${e.text?': '+e.text:''}`} aria-pressed={selected===e.id} onPointerDown={event=>{if(!selectable)return;event.stopPropagation();onSelect(e.id)}} onKeyDown={event=>{if(selectable&&(event.key==='Enter'||event.key===' ')){event.preventDefault();onSelect(e.id)}}} style={{cursor:selectable?'pointer':'inherit'}} stroke={selected===e.id?'#dd9b51':colors[e.color]} strokeWidth={selected===e.id?4:2.5} fill={e.filled?colors[e.color]+'33':'none'} strokeLinecap="round" strokeLinejoin="round">{shape(e)}</g>)}
 <text x="350" y="410" textAnchor="middle" fill="#a493ae" fontSize="11">Curio-created diagram{g?' · computed from the expression':' · select elements to move or edit labels'}</text>
 </g>;
}
