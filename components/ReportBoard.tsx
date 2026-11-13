'use client';
import MathDiagram from './MathDiagram';
import type {BoardArtifact} from '@/lib/reports';
export default function ReportBoard({board}:{board:BoardArtifact['whiteboard']}){
 if(!board.bars.length&&!board.diagrams.length)return <div className="cleared-board">A fresh thinking space · board cleared</div>;
 return <svg className="report-board" viewBox="0 0 800 540" role="img" aria-label="Saved mathematical drawing"><rect width="800" height="540" fill="#fffdfa"/>{board.bars.map((bar,row)=><g key={bar.id}><text x="55" y={108+row*105} fontSize="27" fill="#34463a">{bar.shaded_parts.length}/{bar.denominator}</text>{Array.from({length:bar.denominator},(_,i)=><rect key={i} x={155+i*510/bar.denominator} y={65+row*105} width={510/bar.denominator} height="62" fill={bar.shaded_parts.includes(i)?row%2?'#f3b46f':'#ac95e8':'#fffefa'} stroke="#706080" strokeWidth="2"/>)}<text x="155" y={145+row*105} fontSize="11" fill="#6e786b">{bar.source==='ai'?'Curio-created':'Button-created'} example · equal-sized whole</text></g>)}{board.diagrams.map(d=><MathDiagram key={d.id} diagram={d} selected={null} onSelect={()=>{}} selectable={false}/>)}</svg>;
}
