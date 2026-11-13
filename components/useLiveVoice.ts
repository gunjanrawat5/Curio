'use client';
import {useEffect,useRef,useState} from 'react';
import {LiveVoice,type VoiceStatus} from '@/lib/live-voice';
import {api,type Session} from '@/lib/api';
import {sketchRevision} from '@/lib/snapshot';
import type {Stroke} from '@/lib/strokes';
export function useLiveVoice(options:{session:Session|null;strokes:Stroke[];onSession:(session:Session,strokes:Stroke[])=>void;onError:(message:string)=>void}){
 const mounted=useRef(true);
 const current=useRef(options);current.current=options;
 const client=useRef<LiveVoice|null>(null),turnStrokes=useRef<Stroke[]>([]),hasUser=useRef(false);
 const [status,setStatus]=useState<VoiceStatus>('idle'),[muted,setMuted]=useState(false),[userText,setUserText]=useState(''),[curioText,setCurioText]=useState('');
 const active=status!=='idle';
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;client.current?.dispose()}},[]);
 async function start(){
  if(client.current||!current.current.session)return;
  setUserText('');setCurioText('');setMuted(false);hasUser.current=false;turnStrokes.current=current.current.strokes;
  const voice=new LiveVoice({status:setStatus,error:message=>current.current.onError(message),closed:()=>{
    client.current=null;if(!mounted.current)return;setMuted(false);
    const session=current.current.session;
    if(session)void api<Session>(`/sessions/${session.id}`).then(next=>{if(mounted.current){current.current.onSession(next,turnStrokes.current);setUserText('');setCurioText('');hasUser.current=false;}}).catch(()=>{});
   },
   transcript:(role,text)=>{if(role==='you'){if(!hasUser.current){turnStrokes.current=current.current.strokes;hasUser.current=true;}setUserText(text);}else setCurioText(text);},
   session:(session,committed)=>{current.current.onSession(session,turnStrokes.current);if(committed){setUserText('');setCurioText('');hasUser.current=false;}}
  });
  client.current=voice;
  // Audio contexts are created on the click gesture, before the asynchronous hash resolves.
  setStatus('connecting');
  await voice.start(current.current.session!.id,sketchRevision(current.current.strokes));
 }
 function stop(){client.current?.stop();}
 function toggleMute(){setMuted(client.current?.toggleMute()||false);}
 function interrupt(){client.current?.interrupt();}
 return {status,active,muted,userText,curioText,start,stop,toggleMute,interrupt};
}
