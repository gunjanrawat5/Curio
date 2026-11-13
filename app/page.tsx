'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { ArrowUp, Pencil, MousePointer2, Undo2, Lightbulb, ArrowRight, RotateCcw, Volume2, X, BookOpen, Eye, Mic, MicOff, Square, PhoneOff } from 'lucide-react';
import Curio from '@/components/Curio';
import { useLiveVoice } from '@/components/useLiveVoice';
import MathDiagram from '@/components/MathDiagram';
import { api, ApiError, type Session, type BoardCommand } from '@/lib/api';
import { captureWhiteboard, sketchRevision, type CanvasSnapshot } from '@/lib/snapshot';
import { clearSubmittedStrokes, restoreClearedStrokes, type Stroke } from '@/lib/strokes';
type OutgoingMessage = { id: string; text: string; failed: boolean; strokeSnapshot: Stroke[]; snapshot?: CanvasSnapshot };
export default function Home() {
 const [session,setSession]=useState<Session|null>(null), [text,setText]=useState(''), [strokes,setStrokes]=useState<Stroke[]>([]), [pen,setPen]=useState(true), [color,setColor]=useState('#8063cf'), [report,setReport]=useState(false), [thinking,setThinking]=useState(false), [loading,setLoading]=useState(true), [error,setError]=useState(''), [outgoing,setOutgoing]=useState<OutgoingMessage|null>(null), [boardBusy,setBoardBusy]=useState(false), [selectedElement,setSelectedElement]=useState<string|null>(null), [labelDraft,setLabelDraft]=useState(''), [analyzing,setAnalyzing]=useState(false);
 const svg=useRef<SVGSVGElement>(null), drawing=useRef(false), busy=useRef(false), pending=useRef<{key:string;id:string}|null>(null), conversation=useRef<HTMLDivElement>(null), composer=useRef<HTMLInputElement>(null);
 const sharedStrokes=useRef<string|null>(null);
 const clearCursor=useRef<string|null>(null), clearedStrokes=useRef(new Map<string,Stroke[]>());
 const bars=session?.whiteboard.bars||[];
 const diagrams=session?.whiteboard.diagrams||[];
 const selected=diagrams.flatMap(d=>d.elements||[]).find(e=>e.id===selectedElement);
 const started=!!session, messages=session?.messages||[], hints=session?.hints||0, challenge=session?.phase==='challenge';
 const serializedStrokes=useMemo(()=>JSON.stringify(strokes),[strokes]);
 const latestSketch=session?.sketches?.at(-1);
 const sketchChanged=!!latestSketch&&(latestSketch.canvas_revision!==session?.whiteboard.revision||serializedStrokes!==sharedStrokes.current);
 const voice=useLiveVoice({session,strokes,onSession:(next,submitted)=>applySession(next,submitted),onError:setError});
 const canEdit=!!session&&!thinking&&!boardBusy&&!outgoing&&!challenge&&!voice.active;
 const greeting='I know a little about fractions… but I get the pieces mixed up. Can you teach me why ⅓ is bigger than ¼?';
 function applySession(next:Session, strokeSnapshot:Stroke[]=[]){
  const nextClear=next.whiteboard.last_clear_id||null;
  if(nextClear!==clearCursor.current){
   const previous=clearCursor.current;
   if(next.whiteboard.last_action?.operation==='undo'&&previous&&clearedStrokes.current.has(previous)){
    const removed=clearedStrokes.current.get(previous)!;
    setStrokes(current=>restoreClearedStrokes(current,removed));
   }else if(nextClear&&!clearedStrokes.current.has(nextClear)){
    clearedStrokes.current.set(nextClear,strokeSnapshot);
    setStrokes(current=>clearSubmittedStrokes(current,strokeSnapshot));
   }
   clearCursor.current=nextClear;setSelectedElement(null);
  }
  if((next.whiteboard.bars.length||next.whiteboard.diagrams?.length)&&next.whiteboard.revision!==session?.whiteboard.revision)setPen(false);
  setSession(next);localStorage.setItem('curio-session-id',next.id);
 }

 useEffect(()=>{let active=true;const id=localStorage.getItem('curio-session-id');if(!id){setLoading(false);return;}api<Session>(`/sessions/${id}`).then(next=>{if(active){clearCursor.current=next.whiteboard.last_clear_id||null;setSession(next)}}).catch(err=>{if(!active)return;if(err instanceof ApiError&&err.status===404)localStorage.removeItem('curio-session-id');else setError(err.message)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false}},[]);
 useEffect(()=>{conversation.current?.scrollTo({top:conversation.current.scrollHeight,behavior:'smooth'})},[messages.length,thinking,outgoing,voice.userText,voice.curioText]);
 async function start(){if(busy.current)return;busy.current=true;setThinking(true);setError('');try{applySession(await api<Session>('/sessions',{}))}catch(err){setError((err as Error).message)}finally{busy.current=false;setThinking(false)}}
 async function act(action:'messages'|'hints'|'challenge'|'explore', retry?:OutgoingMessage){
  if(voice.active||busy.current||!session|| (action==='messages'&&(!retry&&(!text.trim()||outgoing))))return;
  busy.current=true;setThinking(true);setError('');
  const answer=retry?.text??text.trim();
  const strokeSnapshot=retry?.strokeSnapshot??strokes;
  const key=`${session.id}:${action}:${action==='messages'?answer:''}`;
  if(retry)pending.current={key,id:retry.id};
  else if(pending.current?.key!==key)pending.current={key,id:crypto.randomUUID()};
  const requestId=pending.current!.id;
  if(retry?.snapshot){await sendSketch(retry.snapshot,answer,requestId,strokeSnapshot);return;}
  if(action==='messages'){
   setOutgoing({id:requestId,text:answer,failed:false,strokeSnapshot});
   if(!retry)setText('');
   composer.current?.focus();
  }
  try{
   const sketch_revision=action==='messages'?await sketchRevision(strokeSnapshot):undefined;
   const next=await api<Session>(`/sessions/${session.id}/${action}`,{request_id:requestId,...(action==='messages'?{text:answer,canvas_revision:session.whiteboard.revision,sketch_revision}:{})});
   applySession(next,strokeSnapshot);pending.current=null;
   if(action==='messages')setOutgoing(null);
   if(action==='challenge'){setStrokes([]);setPen(true)}
  }catch(err){
   setError((err as Error).message);
   if(action==='messages')setOutgoing({id:requestId,text:answer,failed:true,strokeSnapshot});
  }finally{busy.current=false;setThinking(false)}
 }
 async function sendSketch(snapshot:CanvasSnapshot, question:string, requestId:string, strokeSnapshot:Stroke[]){
  setAnalyzing(true);setOutgoing({id:requestId,text:question,failed:false,strokeSnapshot,snapshot});
  try{
   const next=await api<Session>(`/sessions/${session!.id}/sketch`,{request_id:requestId,snapshot,question});
   applySession(next);sharedStrokes.current=JSON.stringify(strokeSnapshot);setOutgoing(null);pending.current=null;
   }catch(err){
   setError((err as Error).message);
   if(err instanceof ApiError&&err.status===409){
    setOutgoing(null);setText(current=>current||question);pending.current=null;
    try{applySession(await api<Session>(`/sessions/${session!.id}`))}catch{ /* Keep the original stale-snapshot error. */ }
   }else setOutgoing({id:requestId,text:question,failed:true,strokeSnapshot,snapshot});
  }
  finally{busy.current=false;setThinking(false);setAnalyzing(false)}
 }
 async function showSketch(){
  if(voice.active||!session||!svg.current||busy.current||outgoing)return;
  busy.current=true;setThinking(true);setAnalyzing(true);setError('');
  const draft=text;const question=text.trim()||'Can you look at my drawing?';const capturedStrokes=strokes;setText('');
  try{
   const snapshot=await captureWhiteboard(svg.current,session.whiteboard.revision,capturedStrokes);
   await sendSketch(snapshot,question,crypto.randomUUID(),capturedStrokes);
  }catch(err){setText(current=>current||draft);setError((err as Error).message||'Could not capture the whiteboard. Please try again.');busy.current=false;setThinking(false);setAnalyzing(false)}
 }
 async function editBoard(operation:'edit'|'clear'|'undo', commands:BoardCommand[]=[]){
  if(voice.active||!session||busy.current||outgoing)return;
  busy.current=true;setError('');setBoardBusy(true);
  try{
   const next=await api<Session>(`/sessions/${session.id}/whiteboard`,{request_id:crypto.randomUUID(),canvas_revision:session.whiteboard.revision,operation,commands});
   applySession(next,strokes);if(operation==='clear')setSelectedElement(null)
  }catch(err){setError((err as Error).message);if(err instanceof ApiError&&err.status===409){try{applySession(await api<Session>(`/sessions/${session.id}`))}catch{ /* Keep the original error and allow a retry. */ }}}
  finally{busy.current=false;setBoardBusy(false)}
 }
 function point(e:React.PointerEvent){const p=svg.current!.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const q=p.matrixTransform(svg.current!.getScreenCTM()!.inverse());return `${q.x.toFixed(1)},${q.y.toFixed(1)}`;}
 return <main><header><a className="brand" href="/">curio<span>✦</span></a><span className="demo">GEMINI · LOCAL</span><button className="text-button" onClick={()=>setReport(true)}><BookOpen size={17}/> My learning journal</button></header>
 <div className="intro"><h1>{started?'Big ideas start with you.':'Meet your newest student.'}<span>✦</span></h1><div className="lesson"><span className="lesson-icon">½</span><strong>Fractions</strong></div></div>
 <div className="workspace"><section className="board-panel"><div className="panel-top"><span><span className="dot"/> Your thinking space</span><button title="Clear whiteboard" disabled={voice.active||thinking||boardBusy||!!outgoing} onClick={()=>{if(session)editBoard('clear');else setStrokes([])}}><RotateCcw size={17}/></button></div><div className="canvas-wrap"><svg ref={svg} viewBox="0 0 800 540" aria-label="Interactive drawing whiteboard" style={{touchAction:'none',cursor:pen?'crosshair':'default'}} onPointerDown={e=>{if(!pen)return; e.currentTarget.setPointerCapture(e.pointerId);drawing.current=true;setStrokes(s=>[...s,{id:crypto.randomUUID(),points:point(e),color}])}} onPointerMove={e=>{if(!drawing.current)return;const p=point(e);setStrokes(s=>s.map((v,i)=>i===s.length-1?{...v,points:v.points+' '+p}:v))}} onPointerUp={()=>drawing.current=false} onPointerCancel={()=>drawing.current=false}>

 {bars.map((bar,row)=><g key={bar.id}><text x="55" y={108+row*105} fontSize="27" fill="#5a4d75">{bar.shaded_parts.length}/{bar.denominator}</text>{Array.from({length:bar.denominator},(_,i)=><rect key={i} role="button" tabIndex={pen||voice.active||thinking||boardBusy||challenge?-1:0} aria-label={`${bar.shaded_parts.length}/${bar.denominator}, piece ${i+1}: ${bar.shaded_parts.includes(i)?'shaded':'unshaded'}`} aria-pressed={bar.shaded_parts.includes(i)} x={155+i*510/bar.denominator} y={65+row*105} width={510/bar.denominator} height="62" fill={bar.shaded_parts.includes(i)?row%2?'#f3b46f':'#ac95e8':'#fffefa'} stroke="#706080" strokeWidth="2" onKeyDown={e=>{if((e.key==='Enter'||e.key===' ')&&!pen&&!voice.active&&!thinking&&!boardBusy&&!challenge){e.preventDefault();editBoard('edit',[{type:'shade_fraction_part',bar_id:bar.id,part_index:i,shaded:!bar.shaded_parts.includes(i)}])}}} onPointerDown={e=>{if(pen)return;e.stopPropagation();if(voice.active||thinking||boardBusy||challenge)return;editBoard('edit',[{type:'shade_fraction_part',bar_id:bar.id,part_index:i,shaded:!bar.shaded_parts.includes(i)}])}}/>)}<text x="155" y={145+row*105} fontSize="11" fill="#938798">{bar.source==='ai'?'Curio-created example':'Button-created example'} · equal-sized whole · {bar.shaded_parts.length} shaded</text></g>)}
 {diagrams.map(diagram=><MathDiagram key={diagram.id} diagram={diagram} selected={selectedElement} onSelect={id=>{setSelectedElement(id);const item=diagram.elements?.find(e=>e.id===id);setLabelDraft(item?.text||'')}} selectable={!pen&&canEdit}/>)}
 {strokes.map(s=><polyline key={s.id} points={s.points} stroke={s.color} strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round"/>)}</svg>
 {selected&&!pen&&<div className="element-editor"><span>{selected.kind}</span>{selected.kind==='text'&&<><input aria-label="Diagram label" maxLength={120} value={labelDraft} onChange={e=>setLabelDraft(e.target.value)}/><button disabled={!canEdit||!labelDraft.trim()} onClick={()=>editBoard('edit',[{type:'edit_math_label',element_id:selected.id,text:labelDraft}])}>Save</button></>}{[{label:'←',dx:-10,dy:0},{label:'↑',dx:0,dy:-10},{label:'↓',dx:0,dy:10},{label:'→',dx:10,dy:0}].map(move=><button key={move.label} aria-label={`Move element ${move.label}`} disabled={!canEdit} onClick={()=>editBoard('edit',[{type:'move_math_element',element_id:selected.id,dx:move.dx,dy:move.dy}])}>{move.label}</button>)}<button aria-label="Deselect element" onClick={()=>setSelectedElement(null)}><X size={14}/></button></div>}
 <div className="tools"><button className={pen?'selected':''} title="Draw" onClick={()=>setPen(true)}><Pencil size={19}/></button><button className={!pen?'selected':''} title="Select diagrams or shade fraction pieces" onClick={()=>setPen(false)}><MousePointer2 size={19}/></button><span className="divider"/>{['#8063cf','#edaa66','#6baf94'].map(c=><button key={c} aria-label={`Pen color ${c}`} onClick={()=>{setColor(c);setPen(true)}} className={`swatch ${color===c?'active':''}`} style={{background:c}}/>)}<span className="divider"/><button title="Undo last stroke" disabled={!strokes.length} onClick={()=>setStrokes(s=>s.slice(0,-1))}><Undo2 size={19}/></button></div></div>
 <div className="board-footer"><button className="show-sketch" disabled={!session||voice.active||thinking||boardBusy||!!outgoing} onClick={showSketch}><Eye size={15}/>{analyzing?'Looking…':'Show Curio'}</button><span className="board-status" role="status">{analyzing?'Curio is looking at your sketch…':boardBusy?'Updating board…':session?.whiteboard.last_action?.description||''}</span><button disabled={!session||voice.active||thinking||boardBusy||!!outgoing||challenge||!session.whiteboard.can_undo} onClick={()=>editBoard('undo')}><Undo2 size={14}/> Undo diagram</button><button disabled={!session||voice.active||thinking||boardBusy||!!outgoing||challenge||bars.length>2||diagrams.length>0} onClick={()=>editBoard('edit',[{type:'create_fraction_bar',numerator:1,denominator:3},{type:'create_fraction_bar',numerator:1,denominator:4}])}>Draw fraction bars <ArrowRight size={15}/></button></div></section>
 <aside><div className="student-top"><button title="Read Curio’s latest message aloud" disabled={voice.active} onClick={()=>{if('speechSynthesis' in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(messages.filter(m=>m.role==='curio').at(-1)?.text||greeting));}}}><Volume2 size={17}/></button></div><div className="avatar-stage"><div className="avatar-size"><Curio thinking={thinking||voice.status==='connecting'} speaking={voice.status==='speaking'} listening={voice.status==='listening'}/></div><span className="sr-only" role="status">{thinking?'Curio is thinking':''}</span></div><div className="student-bottom">{challenge&&<div className="practice-notice" role="status"><span>Independent practice · Curio’s drawing is paused</span><button disabled={voice.active||thinking||boardBusy||!!outgoing} onClick={()=>act('explore')}>Back to exploring <ArrowRight size={14}/></button></div>}<div ref={conversation} className="conversation" aria-live="polite">{!session&&<div className="bubble">{greeting}</div>}{messages.map(m=><div key={m.id} className={`bubble ${m.role==='you'?'learner':''}`}><small>{m.role==='you'?'YOU':'CURIO'}{m.kind==='sketch'?' · SHARED DRAWING':m.kind.startsWith('voice')?' · VOICE':''}</small>{m.text}</div>)}
 {voice.userText&&<div className="bubble learner"><small>YOU · LIVE</small>{voice.userText}</div>}
 {voice.curioText&&<div className="bubble"><small>CURIO · LIVE</small>{voice.curioText}</div>}
 {outgoing&&<div className="bubble learner outgoing"><small>YOU</small>{outgoing.text}{outgoing.failed&&<div className="message-retry"><span>Reply not received</span><button disabled={thinking} onClick={()=>act('messages',outgoing)}>Retry</button></div>}</div>}
 {thinking&&session&&<div className="bubble typing" role="status"><span className="typing-dots" aria-hidden="true"><i/><i/><i/></span><span>{analyzing?'Curio is looking at your sketch…':'Curio is typing…'}</span></div>}
 </div>
 {session&&<div className="voice-controls">{!voice.active?<button className="voice-start" disabled={thinking||boardBusy||!!outgoing} onClick={()=>{setError('');if('speechSynthesis' in window)speechSynthesis.cancel();voice.start()}}><Mic size={16}/> Talk to Curio</button>:<><span className="voice-status" role="status"><i/>{voice.status==='connecting'?'Connecting…':voice.status==='speaking'?'Curio is speaking':voice.muted?'Microphone muted':'Listening…'}</span><button disabled={voice.status==='connecting'} aria-label={voice.muted?'Unmute microphone':'Mute microphone'} aria-pressed={voice.muted} onClick={voice.toggleMute}>{voice.muted?<MicOff size={16}/>:<Mic size={16}/>}</button><button disabled={voice.status!=='speaking'} aria-label="Stop Curio speaking" onClick={voice.interrupt}><Square size={14}/></button><button aria-label="End voice conversation" onClick={voice.stop}><PhoneOff size={16}/></button></> }</div>}
 {voice.active&&<div className="sketch-status">End voice to send typed messages or share a new sketch.</div>}
 {latestSketch&&<div className="sketch-status" role="status">{sketchChanged?'Drawing changed · Show Curio again':latestSketch.analysis.needs_clarification?'Curio needs a little clarification':'Curio has seen this snapshot'}</div>}
 {error&&<div className="connection-error" role="alert">{error}</div>}
 {!started?<button className="primary start" disabled={loading||thinking} onClick={start}>{loading?'Connecting…':thinking?'Starting…':'Let’s teach Curio'} <ArrowRight size={18}/></button>:<form onSubmit={e=>{e.preventDefault();act('messages')}} className="reply"><input ref={composer} maxLength={4000} aria-label="Your explanation" placeholder={thinking?"Write your next thought…":"Teach Curio something…"} value={text} onChange={e=>setText(e.target.value)}/><button aria-label="Send explanation" disabled={voice.active||!text.trim()||thinking||boardBusy||!!outgoing}><ArrowUp size={19}/></button></form>}
 <div className="student-actions"><button disabled={!session||voice.active||challenge||thinking||boardBusy||!!outgoing} onClick={()=>act('hints')}><Lightbulb size={16}/> A little hint</button><button disabled={!session||voice.active||thinking||challenge||boardBusy||!!outgoing} onClick={()=>act('challenge')}>New puzzle <ArrowRight size={14}/></button></div></div></aside></div>

 {report&&<div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="report-title"><button className="close" aria-label="Close report" onClick={()=>setReport(false)}><X/></button><span className="eyebrow">YOUR LEARNING JOURNAL</span><h2 id="report-title">Little steps, real discoveries.</h2><p>Conversations and hints are saved on this computer by the backend. Diagrams are saved too; freehand strokes stay in this tab. A mastery evaluator is not connected yet.</p><div className="report-stats"><span><strong>{messages.filter(m=>m.role==='you').length}</strong> explanations</span><span><strong>{hints}</strong> hints used</span><span><strong>{strokes.length}</strong> current strokes</span></div>{latestSketch&&<><h3>Last shared sketch</h3><p>{latestSketch.analysis.summary}</p><p>{latestSketch.analysis.needs_clarification?'Clarification requested; interpretation is uncertain.':'Snapshot observations recorded; not a mastery assessment.'}</p></>}<h3>Your words</h3>{messages.filter(m=>m.role==='you').map((m,i)=><blockquote key={i}>{m.text}</blockquote>)}{!messages.some(m=>m.role==='you')&&<p>Your explanations will appear here as you teach.</p>}<p><b>Independent challenge:</b> {challenge?'Practice opened; evaluation pending.':messages.some(m=>m.kind==='challenge')?'Left practice to explore; not graded.':'Not attempted.'}</p><p><b>Evaluator check:</b> Not run. No mastery result is available.</p><button className="primary" onClick={()=>setReport(false)}>Back to workspace <ArrowRight size={17}/></button></section></div>}
 </main>;
}
