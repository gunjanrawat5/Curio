"""Gemini Live audio relay. The API key and diagram validation stay on the server."""
import asyncio
import base64
import json
import os
import time
import logging
from uuid import uuid4
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from google import genai
from google.genai import types
from backend.gemini import SYSTEM_PROMPT
from backend.store import event
from backend.whiteboard import CurioReply, apply_commands, BoardError, provider_reply_schema


VOICE_CONNECTION_SECONDS=14*60
logger=logging.getLogger(__name__)

def live_config(session: dict, sketch_revision: str | None):
    board = {k:v for k,v in session['whiteboard'].items() if k != 'history'}
    board['diagrams'] = [{k:v for k,v in d.items() if k != 'segments'} for d in board.get('diagrams', [])]
    latest = session.get('sketches', [])[-1:]
    if latest and latest[0]['canvas_revision'] == board['revision'] and latest[0]['sketch_revision'] == sketch_revision:
        board['vision_context'] = {**latest[0], 'current': False, 'historical_snapshot': True}
    drawing_rules = SYSTEM_PROMPT[SYSTEM_PROMPT.index('Use create_fraction_bar'):SYSTEM_PROMPT.index('Return commands=[]')]
    prompt = SYSTEM_PROMPT[:SYSTEM_PROMPT.index('Return text and commands')] + drawing_rules + """
You are now in LIVE VOICE mode. Speak naturally, never return JSON or read internal
IDs aloud. Use at most 2–3 short sentences and one question. Listen patiently.
For any whiteboard operation call edit_whiteboard with commands using the provided
schema, wait for success, then describe what actually happened. Never claim an edit
before the tool confirms it. On failure, explain briefly and ask for clarification.
Do not speak the schema or tool details. Do not mistake background noise for a request.
You can be interrupted. When the child interrupts, stop and listen.
You cannot see live pen strokes. Any snapshot in this voice connection is historical,
not live: do not describe it as the current drawing, even if it matched on connection.
You may discuss it explicitly as the previously shared snapshot. Ask the learner to
end voice and use Show Curio to inspect a new or current drawing.
Never grade or certify mastery. In challenge phase, do not give hints, solutions,
corrections or diagram actions; ask the child to explain independently.
The current phase overrides historical challenge messages.
"""
    prompt += '\nCurrent phase: ' + session['phase'] + '\nCurrent board: ' + json.dumps(board)
    prompt += '\nPrior conversation (context only; wait for new speech): ' + json.dumps([{'role':m['role'],'text':m['text']} for m in session['messages'][-30:]])
    schema = provider_reply_schema()
    tool_schema = {'type':'object','properties':{'commands':schema['properties']['commands']},'required':['commands'],'$defs':schema.get('$defs',{})}
    return types.LiveConnectConfig(
        response_modalities=['AUDIO'], input_audio_transcription={}, output_audio_transcription={},
        system_instruction=prompt, temperature=0.5,
        speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=os.getenv('GEMINI_LIVE_VOICE','Aoede')))),
        tools=[types.Tool(function_declarations=[types.FunctionDeclaration(name='edit_whiteboard',description='Apply a validated batch of math drawing commands to the shared board. Only on explicit learner requests.',parameters_json_schema=tool_schema)])],
    )


def voice_error_details(exc):
    """Classify close frames without exposing provider payloads or credentials."""
    frame=getattr(exc,'rcvd',None) or getattr(exc,'sent',None)
    code=getattr(frame,'code',None) or getattr(exc,'code',None)
    # Read reasons for classification only; never log or return the raw payload.
    reason=' '.join(str(value) for value in [getattr(frame,'reason',''),getattr(exc,'reason',''),getattr(exc,'message',''),str(exc)]).lower()
    if code==429 or any(word in reason for word in ('resource_exhausted','resource exhausted','quota','rate limit','too many requests')):
        category='quota';message='Gemini voice reached a usage or rate limit. Wait a little, then reconnect, or keep typing.'
    elif code in (401,403,404) or any(word in reason for word in ('api key not valid','permission_denied','permission denied','model not found','unsupported model')):
        category='configuration';message='Gemini denied voice access. Check the backend key, live model and account permissions, then reconnect.'
    elif any(word in reason for word in ('session expired','session duration','maximum session','time limit','connection lifetime')):
        category='expired';message='This voice connection reached Gemini’s time limit. Tap Talk to Curio to continue with your saved conversation.'
    elif isinstance(exc,TimeoutError) or 'deadline exceeded' in reason:
        category='timeout';message='The voice connection timed out. Tap Talk to Curio to reconnect, or keep typing.'
    elif code in (1000,1001):
        category='provider_closed';message='Gemini ended this voice connection. Tap Talk to Curio to continue with your saved conversation.'
    elif code in (1011,1012,1013) or 'internal error' in reason or 'unavailable' in reason:
        category='provider_unavailable';message='Gemini’s voice service interrupted the connection. Reconnect in a moment, or keep typing.'
    elif code==1008 or code==400:
        category='request_rejected';message='Gemini rejected a voice request. Reconnect; if it repeats, check the backend live-model configuration.'
    elif code==1006 or isinstance(exc,(ConnectionError,OSError)):
        category='network';message='The voice connection was lost. Check your connection, then reconnect or keep typing.'
    else:
        category='unexpected';message='Voice stopped unexpectedly. Reconnect or keep typing; your saved conversation is still available.'
    return {'category':category,'close_code':int(code) if isinstance(code,int) else None,'message':message}


def provider_error(exc):
    return voice_error_details(exc)['message']


async def handle_voice(ws: WebSocket, app, session_id):
    from backend.main import public
    allowed=[x.strip() for x in os.getenv('FRONTEND_ORIGINS','http://localhost:3000,http://127.0.0.1:3000').split(',')]
    if ws.headers.get('origin') not in allowed:
        await ws.close(code=1008);return
    await ws.accept()
    session_id=str(session_id)
    session_lock=app.state.locks.setdefault(session_id,asyncio.Lock())
    reserved=False
    started_at=time.monotonic();ending_reason='stopped'
    user_text='';curio_text='';turn_id=str(uuid4());call_results={}
    async def send(payload):
        await ws.send_json(payload)
    async def flush(interrupted=False, deliver=True):
        nonlocal user_text,curio_text,turn_id
        if not user_text.strip() and not curio_text.strip():return
        async with session_lock:
            current=app.state.store.get(session_id)
            if current is None:return
            if user_text.strip():
                learner=event('you',user_text.strip(),'voice');learner['id']=turn_id
                current['messages'].append(learner)
            if curio_text.strip():
                current['messages'].append(event('curio',curio_text.strip(),'voice_interrupted' if interrupted else 'voice'))
            app.state.store.save(current)
            user_text='';curio_text='';turn_id=str(uuid4())
            result=public(current)
        if deliver:await send({'type':'session','session':result,'committed':True})
    try:
        async with session_lock:
            current=app.state.store.get(session_id)
            if current is None:
                await send({'type':'error','message':'Session not found. Start a teaching session first.'});return
            if len(current['messages'])>=120:
                await send({'type':'error','message':'This session is full. Start a new teaching session.'});return
            if session_id in app.state.voice_sessions:
                await send({'type':'error','message':'Voice is already connected in another tab.'});return
            app.state.voice_sessions.add(session_id);reserved=True
        key=os.getenv('GEMINI_API_KEY','').strip()
        if not key or key=='your_gemini_api_key_here':
            await send({'type':'error','message':'Add GEMINI_API_KEY to the backend .env and restart it.'});return
        initial=await asyncio.wait_for(ws.receive_json(),timeout=15)
        if initial.get('type')!='start':
            await send({'type':'error','message':'Start the voice connection again.'});return
        config=live_config(current,initial.get('sketch_revision'))
        async with genai.Client(api_key=key,http_options=types.HttpOptions(api_version='v1beta')).aio as client:
            async with client.live.connect(model=os.getenv('GEMINI_LIVE_MODEL','gemini-3.8-live'),config=config) as live:
                await send({'type':'ready'})
                async def receive_browser():
                    while True:
                        message=await ws.receive_json()
                        kind=message.get('type')
                        if kind=='stop':return
                        if kind=='audio':
                            encoded=message.get('data','')
                            if not isinstance(encoded,str) or len(encoded)>48000:raise ValueError('Invalid audio chunk')
                            audio=base64.b64decode(encoded,validate=True)
                            if not audio or len(audio)%2:raise ValueError('Invalid PCM audio')
                            await live.send_realtime_input(audio=types.Blob(data=audio,mime_type='audio/pcm;rate=16000'))
                        elif kind=='mute':
                            await live.send_realtime_input(audio_stream_end=True)
                        elif kind=='interrupt':
                            await send({'type':'interrupted'})
                        else:raise ValueError('Unsupported voice message')
                async def receive_gemini():
                    nonlocal user_text,curio_text,ending_reason
                    awaiting_tool_output=False
                    while True:
                        async for response in live.receive():
                            if response.go_away:
                                ending_reason='provider_rotation';return
                            if response.tool_call:
                                awaiting_tool_output=True
                            content=response.server_content
                            if content:
                                if not response.tool_call and (content.output_transcription or content.model_turn):
                                    awaiting_tool_output=False
                                if content.interrupted:
                                    awaiting_tool_output=False
                                    await send({'type':'interrupted'})
                                    await flush(interrupted=True)
                                if content.input_transcription and content.input_transcription.text:
                                    user_text+=content.input_transcription.text
                                    await send({'type':'transcript','role':'you','text':user_text})
                                if content.output_transcription and content.output_transcription.text:
                                    curio_text+=content.output_transcription.text
                                    await send({'type':'transcript','role':'curio','text':curio_text})
                                if content.model_turn:
                                    for part in content.model_turn.parts or []:
                                        if part.inline_data and part.inline_data.data:
                                            await send({'type':'audio','data':base64.b64encode(part.inline_data.data).decode(),'sample_rate':24000})
                                if content.turn_complete and not awaiting_tool_output:
                                    await flush()
                                    await send({'type':'turn_complete'})
                                    if len(app.state.store.get(session_id)['messages'])>=120:
                                        await send({'type':'error','message':'This session is full. End voice and start a new session.'});return
                            if response.tool_call:
                                results=[]
                                for call in response.tool_call.function_calls or []:
                                    cache_id=call.id or str(uuid4())
                                    if cache_id in call_results:
                                        result=call_results[cache_id]
                                    else:
                                        try:
                                            if call.name!='edit_whiteboard' or not user_text.strip():raise BoardError('Please ask for the drawing again clearly.')
                                            commands=CurioReply.model_validate({'text':'Drawing action','commands':(call.args or {}).get('commands',[])}).commands
                                            async with session_lock:
                                                latest=app.state.store.get(session_id)
                                                latest['whiteboard']=apply_commands(latest['whiteboard'],commands,'ai',turn_id,latest['phase'],user_text)
                                                app.state.store.save(latest)
                                                board=public(latest)['whiteboard']
                                            provider_board=dict(board)
                                            provider_board['diagrams']=[{k:v for k,v in d.items() if k!='segments'} for d in board.get('diagrams',[])]
                                            result={'ok':True,'whiteboard':provider_board}
                                            await send({'type':'session','session':public(latest),'committed':False})
                                        except (ValidationError,BoardError):
                                            result={'ok':False,'message':'The drawing request could not be applied. Ask the learner to clarify; no edits were made.'}
                                        call_results[cache_id]=result
                                    results.append(types.FunctionResponse(id=call.id,name=call.name,response=result))
                                await live.send_tool_response(function_responses=results)
                tasks=[asyncio.create_task(receive_browser()),asyncio.create_task(receive_gemini())]
                try:
                    done,_=await asyncio.wait(tasks,timeout=VOICE_CONNECTION_SECONDS,return_when=asyncio.FIRST_COMPLETED)
                    if not done:ending_reason='time_limit'
                    for task in done:task.result()
                finally:
                    for task in tasks:task.cancel()
                    await asyncio.gather(*tasks,return_exceptions=True)
                await flush(interrupted=True)
                ending={'type':'ended','reason':ending_reason}
                if ending_reason in ('time_limit','provider_rotation'):
                    ending['message']='This voice connection reached its time limit. Tap Talk to Curio to continue with your saved conversation.' if ending_reason=='time_limit' else 'Gemini is refreshing its voice connection. Tap Talk to Curio to continue with your saved conversation.'
                await send(ending)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        details=voice_error_details(exc)
        elapsed=round(time.monotonic()-started_at,1)
        logger.warning('Voice ended: category=%s close_code=%s elapsed_seconds=%s exception_type=%s',details['category'],details['close_code'],elapsed,type(exc).__name__)
        if reserved:
            async with session_lock:
                current=app.state.store.get(session_id)
                if current is not None:
                    diagnostic={'category':details['category'],'close_code':details['close_code'],'elapsed_seconds':elapsed,'created_at':event('curio','')['created_at']}
                    current.setdefault('voice_disconnects',[]).append(diagnostic)
                    current['voice_disconnects']=current['voice_disconnects'][-20:]
                    app.state.store.save(current)
        try:await send({'type':'error','message':details['message'],'category':details['category'],'elapsed_seconds':elapsed})
        except (WebSocketDisconnect,RuntimeError):pass
    finally:
        if reserved:
            try:await flush(interrupted=True,deliver=False)
            finally:app.state.voice_sessions.discard(session_id)
        try:await ws.close()
        except (WebSocketDisconnect,RuntimeError):pass
