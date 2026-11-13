'use client';
import { useEffect, useRef, useState } from 'react';
import { ArrowUp, Pencil, MousePointer2, Undo2, Lightbulb, ArrowRight, RotateCcw, Volume2, X, BookOpen } from 'lucide-react';
import Curio from '@/components/Curio';
import { api, ApiError, type Session } from '@/lib/api';
type OutgoingMessage = { id: string; text: string; failed: boolean };
type Stroke = { id: string; points: string; color: string };
export default function Home() {
 const [session,setSession]=useState<Session|null>(null), [text,setText]=useState(''), [bars,setBars]=useState(false), [shaded,setShaded]=useState<string[]>([]), [strokes,setStrokes]=useState<Stroke[]>([]), [pen,setPen]=useState(true), [color,setColor]=useState('#8063cf'), [report,setReport]=useState(false), [thinking,setThinking]=useState(false), [loading,setLoading]=useState(true), [error,setError]=useState(''), [outgoing,setOutgoing]=useState<OutgoingMessage|null>(null);
 const svg=useRef<SVGSVGElement>(null), drawing=useRef(false), busy=useRef(false), pending=useRef<{key:string;id:string}|null>(null), conversation=useRef<HTMLDivElement>(null), composer=useRef<HTMLInputElement>(null);
 const started=!!session, messages=session?.messages||[], hints=session?.hints||0, challenge=session?.phase==='challenge';
 const greeting='I know a little about fractions… but I get the pieces mixed up. Can you teach me why ⅓ is bigger than ¼?';
 function applySession(next:Session){setSession(next);localStorage.setItem('curio-session-id',next.id);}
 useEffect(()=>{let active=true;const id=localStorage.getItem('curio-session-id');if(!id){setLoading(false);return;}api<Session>(`/sessions/${id}`).then(next=>{if(active)setSession(next)}).catch(err=>{if(!active)return;if(err instanceof ApiError&&err.status===404)localStorage.removeItem('curio-session-id');else setError(err.message)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false}},[]);
 useEffect(()=>{conversation.current?.scrollTo({top:conversation.current.scrollHeight,behavior:'smooth'})},[messages.length,thinking,outgoing]);
 async function start(){if(busy.current)return;busy.current=true;setThinking(true);setError('');try{applySession(await api<Session>('/sessions',{}))}catch(err){setError((err as Error).message)}finally{busy.current=false;setThinking(false)}}
 async function act(action:'messages'|'hints'|'challenge', retry?:OutgoingMessage){
  if(busy.current||!session|| (action==='messages'&&(!retry&&(!text.trim()||outgoing))))return;
  busy.current=true;setThinking(true);setError('');
  const answer=retry?.text??text.trim();
  const key=`${session.id}:${action}:${action==='messages'?answer:''}`;
  if(retry)pending.current={key,id:retry.id};
  else if(pending.current?.key!==key)pending.current={key,id:crypto.randomUUID()};
  const requestId=pending.current!.id;
  if(action==='messages'){
   setOutgoing({id:requestId,text:answer,failed:false});
   if(!retry)setText('');
   composer.current?.focus();
  }
  try{
   const next=await api<Session>(`/sessions/${session.id}/${action}`,{request_id:requestId,...(action==='messages'?{text:answer}:{})});
   applySession(next);pending.current=null;
   if(action==='messages')setOutgoing(null);
   if(action==='challenge'){setBars(false);setStrokes([]);setShaded([])}
  }catch(err){
   setError((err as Error).message);
   if(action==='messages')setOutgoing({id:requestId,text:answer,failed:true});
  }finally{busy.current=false;setThinking(false)}
 }
 function point(e:React.PointerEvent){const p=svg.current!.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const q=p.matrixTransform(svg.current!.getScreenCTM()!.inverse());return `${q.x.toFixed(1)},${q.y.toFixed(1)}`;}
 return <main><header><a className="brand" href="/">curio<span>✦</span></a><span className="demo">GEMINI · LOCAL</span><button className="text-button" onClick={()=>setReport(true)}><BookOpen size={17}/> My learning journal</button></header>
 <div className="intro"><h1>{started?'Big ideas start with you.':'Meet your newest student.'}<span>✦</span></h1><div className="lesson"><span className="lesson-icon">½</span><strong>Fractions</strong></div></div>
 <div className="workspace"><section className="board-panel"><div className="panel-top"><span><span className="dot"/> Your thinking space</span><button title="Clear whiteboard" onClick={()=>{setStrokes([]);setBars(false);setShaded([])}}><RotateCcw size={17}/></button></div><div className="canvas-wrap"><svg ref={svg} viewBox="0 0 800 540" aria-label="Interactive drawing whiteboard" style={{touchAction:'none',cursor:pen?'crosshair':'default'}} onPointerDown={e=>{if(!pen)return; e.currentTarget.setPointerCapture(e.pointerId);drawing.current=true;setStrokes(s=>[...s,{id:crypto.randomUUID(),points:point(e),color}])}} onPointerMove={e=>{if(!drawing.current)return;const p=point(e);setStrokes(s=>s.map((v,i)=>i===s.length-1?{...v,points:v.points+' '+p}:v))}} onPointerUp={()=>drawing.current=false} onPointerCancel={()=>drawing.current=false}>

 {bars&&[3,4].map((n,row)=><g key={n}><text x="85" y={185+row*155} fontSize="29" fill="#5a4d75">1/{n}</text>{Array.from({length:n},(_,i)=><rect key={i} x={155+i*510/n} y={140+row*155} width={510/n} height="80" fill={shaded.includes(`${n}-${i}`)?row?'#f3b46f':'#ac95e8':'#fffefa'} stroke="#706080" strokeWidth="2" onPointerDown={e=>{if(pen)return;e.stopPropagation();const key=`${n}-${i}`;setShaded(s=>s.includes(key)?s.filter(x=>x!==key):[...s,key])}}/>)}<text x="155" y={244+row*155} fontSize="12" fill="#938798">AI-created example · same-sized whole</text></g>)}
 {strokes.map(s=><polyline key={s.id} points={s.points} stroke={s.color} strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round"/>)}</svg>
 <div className="tools"><button className={pen?'selected':''} title="Draw" onClick={()=>setPen(true)}><Pencil size={19}/></button><button className={!pen?'selected':''} title="Select and shade fraction pieces" onClick={()=>setPen(false)}><MousePointer2 size={19}/></button><span className="divider"/>{['#8063cf','#edaa66','#6baf94'].map(c=><button key={c} aria-label={`Pen color ${c}`} onClick={()=>{setColor(c);setPen(true)}} className={`swatch ${color===c?'active':''}`} style={{background:c}}/>)}<span className="divider"/><button title="Undo last stroke" disabled={!strokes.length} onClick={()=>setStrokes(s=>s.slice(0,-1))}><Undo2 size={19}/></button></div></div>
 <div className="board-footer"><button disabled={challenge} onClick={()=>{setBars(true);setPen(false)}}>Draw fraction bars <ArrowRight size={15}/></button></div></section>
 <aside><div className="student-top"><button title="Read Curio’s latest message aloud" onClick={()=>{if('speechSynthesis' in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(messages.filter(m=>m.role==='curio').at(-1)?.text||greeting));}}}><Volume2 size={17}/></button></div><div className="avatar-stage"><div className="avatar-size"><Curio thinking={thinking}/></div><span className="sr-only" role="status">{thinking?'Curio is thinking':''}</span></div><div className="student-bottom"><div ref={conversation} className="conversation" aria-live="polite">{!session&&<div className="bubble">{greeting}</div>}{messages.map(m=><div key={m.id} className={`bubble ${m.role==='you'?'learner':''}`}><small>{m.role==='you'?'YOU':'CURIO'}</small>{m.text}</div>)}
 {outgoing&&<div className="bubble learner outgoing"><small>YOU</small>{outgoing.text}{outgoing.failed&&<div className="message-retry"><span>Reply not received</span><button disabled={thinking} onClick={()=>act('messages',outgoing)}>Retry</button></div>}</div>}
 {thinking&&session&&<div className="bubble typing" role="status"><span className="typing-dots" aria-hidden="true"><i/><i/><i/></span><span>Curio is typing…</span></div>}
 </div>
 {error&&<div className="connection-error" role="alert">{error}</div>}
 {!started?<button className="primary start" disabled={loading||thinking} onClick={start}>{loading?'Connecting…':thinking?'Starting…':'Let’s teach Curio'} <ArrowRight size={18}/></button>:<form onSubmit={e=>{e.preventDefault();act('messages')}} className="reply"><input ref={composer} maxLength={4000} aria-label="Your explanation" placeholder={thinking?"Write your next thought…":"Teach Curio something…"} value={text} onChange={e=>setText(e.target.value)}/><button aria-label="Send explanation" disabled={!text.trim()||thinking||!!outgoing}><ArrowUp size={19}/></button></form>}
 <div className="student-actions"><button disabled={!session||challenge||thinking||!!outgoing} onClick={()=>act('hints')}><Lightbulb size={16}/> A little hint</button><button disabled={!session||thinking||challenge||!!outgoing} onClick={()=>act('challenge')}>New puzzle <ArrowRight size={14}/></button></div></div></aside></div>

 {report&&<div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="report-title"><button className="close" aria-label="Close report" onClick={()=>setReport(false)}><X/></button><span className="eyebrow">YOUR LEARNING JOURNAL</span><h2 id="report-title">Little steps, real discoveries.</h2><p>Conversations and hints are saved on this computer by the backend. The whiteboard stays in this tab. A mastery evaluator is not connected yet.</p><div className="report-stats"><span><strong>{messages.filter(m=>m.role==='you').length}</strong> explanations</span><span><strong>{hints}</strong> hints used</span><span><strong>{strokes.length}</strong> current strokes</span></div><h3>Your words</h3>{messages.filter(m=>m.role==='you').map((m,i)=><blockquote key={i}>{m.text}</blockquote>)}{!messages.some(m=>m.role==='you')&&<p>Your explanations will appear here as you teach.</p>}<p><b>Independent challenge:</b> {challenge?'Practice opened; evaluation pending.':'Not attempted.'}</p><p><b>Evaluator check:</b> Not run. No mastery result is available.</p><button className="primary" onClick={()=>setReport(false)}>Back to exploring <ArrowRight size={17}/></button></section></div>}
 </main>;
}
