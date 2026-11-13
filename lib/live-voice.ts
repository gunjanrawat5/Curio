import {bytesToBase64,pcm16ToFloat32} from './audio';
import type {Session} from './api';
export type VoiceStatus='idle'|'connecting'|'listening'|'speaking'|'muted';
export type VoiceCallbacks={status:(status:VoiceStatus)=>void;transcript:(role:'you'|'curio',text:string)=>void;session:(session:Session,committed:boolean)=>void;error:(message:string)=>void;closed:()=>void;};
export class LiveVoice {
 private socket:WebSocket|null=null;
 private input:AudioContext|null=null;private output:AudioContext|null=null;
 private stream:MediaStream|null=null;private source:MediaStreamAudioSourceNode|null=null;private worklet:AudioWorkletNode|null=null;private silent:GainNode|null=null;
 private sources=new Set<AudioBufferSourceNode>();private playbackAt=0;private muted=false;private disposed=false;private stopping=false;private ignoreAudio=false;private connected=false;
 constructor(private callbacks:VoiceCallbacks){}
 async start(sessionId:string,sketchRevision:string|Promise<string>){
  this.callbacks.status('connecting');
  try{
   if(!navigator.mediaDevices?.getUserMedia||!window.AudioContext)throw new Error('Voice needs microphone access in a current browser on localhost or HTTPS. You can keep typing.');
   this.input=new AudioContext({sampleRate:16000});this.output=new AudioContext();
   await Promise.all([this.input.resume(),this.output.resume()]);
   this.stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
   if(this.disposed){this.stream.getTracks().forEach(t=>t.stop());return;}
   if(this.input.sampleRate!==16000)throw new Error('This browser cannot capture the required audio rate. Try Chrome, or keep typing.');
   await this.input.audioWorklet.addModule('/voice-worklet.js');
   if(this.disposed)return;
   const revision=await sketchRevision;if(this.disposed)return;
   const base=process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000';
   const url=new URL(base);url.protocol=url.protocol==='https:'?'wss:':'ws:';url.pathname=`${url.pathname.replace(/\/$/,'')}/sessions/${sessionId}/voice`;
   const socket=new WebSocket(url);this.socket=socket;
   const timeout=setTimeout(()=>{if(!this.connected){this.callbacks.error('Curio’s voice connection took too long. Reconnect or keep typing.');this.dispose();}},20000);
   socket.onopen=()=>socket.send(JSON.stringify({type:'start',sketch_revision:revision}));
   socket.onmessage=event=>{
    try{
     const message=JSON.parse(event.data);
     if(message.type==='ready'){
      clearTimeout(timeout);if(this.disposed)return;this.connected=true;
      this.source=this.input!.createMediaStreamSource(this.stream!);this.worklet=new AudioWorkletNode(this.input!,'curio-microphone');
      this.silent=this.input!.createGain();this.silent.gain.value=0;this.source.connect(this.worklet);this.worklet.connect(this.silent);this.silent.connect(this.input!.destination);
      this.worklet.port.onmessage=({data}:{data:ArrayBuffer})=>{if(!this.muted&&!this.stopping&&socket.readyState===WebSocket.OPEN){if(socket.bufferedAmount>256000){this.callbacks.error('The voice connection is falling behind. Reconnect or keep typing.');this.dispose();return;}socket.send(JSON.stringify({type:'audio',data:bytesToBase64(data)}));}};
      this.callbacks.status('listening');
     }else if(message.type==='audio'){
      if(!this.ignoreAudio&&!this.stopping)this.play(message.data,message.sample_rate||24000);
     }else if(message.type==='transcript')this.callbacks.transcript(message.role,message.text);
     else if(message.type==='session')this.callbacks.session(message.session,message.committed===true);
     else if(message.type==='interrupted'){this.ignoreAudio=false;this.stopPlayback();}
     else if(message.type==='turn_complete'){this.ignoreAudio=false;if(!this.sources.size)this.callbacks.status(this.muted?'muted':'listening');}
     else if(message.type==='error'){this.callbacks.error(message.message);this.dispose();}
     else if(message.type==='ended'){if(message.message)this.callbacks.error(message.message);this.dispose();}
    }catch{this.callbacks.error('Curio’s voice message could not be played. Reconnect or keep typing.');this.dispose();}
   };
   socket.onerror=()=>this.callbacks.error('Could not connect to Curio’s voice. Check the backend connection, or keep typing.');
   socket.onclose=()=>{clearTimeout(timeout);const unexpected=!this.stopping&&!this.disposed;if(unexpected)this.callbacks.error('Voice disconnected. Your saved conversation is still available; reconnect or keep typing.');this.dispose();};
  }catch(error){
   if(this.disposed)return;
   const denied=error instanceof DOMException&&['NotAllowedError','PermissionDeniedError'].includes(error.name);
   this.callbacks.error(denied?'Microphone access was denied. Allow the microphone in your browser to use voice, or keep typing.':error instanceof Error?error.message:'Could not start voice. You can keep typing.');
   this.dispose();
  }
 }
 private play(data:string,sampleRate:number){
  if(!this.output||!this.connected)return;
  const samples=pcm16ToFloat32(data);if(!samples.length)return;
  const buffer=this.output.createBuffer(1,samples.length,sampleRate);buffer.getChannelData(0).set(samples);
  const source=this.output.createBufferSource();source.buffer=buffer;source.connect(this.output.destination);this.sources.add(source);
  this.playbackAt=Math.max(this.playbackAt,this.output.currentTime+.025);source.start(this.playbackAt);this.playbackAt+=buffer.duration;
  this.callbacks.status('speaking');source.onended=()=>{source.disconnect();this.sources.delete(source);if(!this.sources.size&&!this.disposed)this.callbacks.status(this.muted?'muted':'listening');};
 }
 private stopPlayback(){for(const source of this.sources){source.onended=null;try{source.stop()}catch{}source.disconnect();}this.sources.clear();this.playbackAt=this.output?.currentTime||0;if(!this.disposed)this.callbacks.status(this.muted?'muted':'listening');}
 toggleMute(){this.muted=!this.muted;this.stream?.getAudioTracks().forEach(track=>track.enabled=!this.muted);if(this.muted&&this.socket?.readyState===WebSocket.OPEN)this.socket.send(JSON.stringify({type:'mute'}));this.callbacks.status(this.muted?'muted':'listening');return this.muted;}
 interrupt(){this.ignoreAudio=true;this.stopPlayback();}
 stop(){
  this.stopping=true;this.stream?.getTracks().forEach(t=>t.stop());this.stopPlayback();
  if(this.socket?.readyState===WebSocket.OPEN){this.socket.send(JSON.stringify({type:'stop'}));setTimeout(()=>this.dispose(),2000);}else this.dispose();
 }
 dispose(){
  if(this.disposed)return;this.disposed=true;this.connected=false;this.stopPlayback();
  this.stream?.getTracks().forEach(t=>t.stop());this.source?.disconnect();this.worklet?.disconnect();this.silent?.disconnect();
  if(this.worklet)this.worklet.port.onmessage=null;
  void this.input?.close().catch(()=>{});void this.output?.close().catch(()=>{});
  if(this.socket&&this.socket.readyState<WebSocket.CLOSING)this.socket.close();
  this.callbacks.status('idle');this.callbacks.closed();
 }
}
