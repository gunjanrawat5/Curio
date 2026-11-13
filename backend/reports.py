"""Conversation archives with optional validated rubric evaluation."""
from copy import deepcopy


def report_summary(session: dict, active_voice=False) -> dict:
    messages=session.get('messages',[])
    learner=[m for m in messages if m['role']=='you']
    first=next((m for m in learner if m.get('kind')!='sketch'),learner[0] if learner else None)
    title=' '.join(first['text'].split()) if first else 'A new memory adventure'
    if len(title)>76:title=title[:73].rstrip()+'…'
    return {'id':session['id'],'title':title,'subject':'Mathematics',
        'created_at':session.get('created_at') or (messages[0]['created_at'] if messages else None),
        'updated_at':session.get('updated_at') or (messages[-1]['created_at'] if messages else None),
        'preview':learner[-1]['text'] if learner else 'No learner contributions yet.',
        'status':'in_progress' if active_voice else 'saved' if learner else 'not_started',
        'result':'Review pending' if learner else 'Not started',
        'channels':[channel for channel in ('text','voice','sketch') if any(('voice' if m.get('kind','').startswith('voice') else 'sketch' if m.get('kind')=='sketch' else 'text')==channel for m in learner)],
        'has_contributions':bool(learner)}


def collect_artifacts(session: dict) -> list[dict]:
    board=session['whiteboard'];archived=deepcopy(session.get('artifacts',[]))
    # Older sessions retained undo states, but not a complete drawing archive.
    if not archived:
        for index,state in enumerate(board.get('history',[])):
            if state['bars'] or state.get('diagrams'):
                archived.append({'id':f'legacy-{index}','revision':None,'created_at':None,'source':'unknown',
                    'source_event_id':None,'description':'Earlier saved board','legacy':True,
                    'whiteboard':{'bars':state['bars'],'diagrams':state.get('diagrams',[])}})
    current={'bars':board['bars'],'diagrams':board.get('diagrams',[])}
    if not archived or archived[-1].get('revision')!=board['revision']:
        if current['bars'] or current['diagrams']:
            archived.append({'id':'current','revision':board['revision'],'created_at':None,'source':'unknown',
                'source_event_id':None,'description':'Latest saved board','legacy':not bool(session.get('artifacts')),'whiteboard':current})
    return archived


def build_report(session: dict, available_images: set[str], active_voice=False) -> dict:
    summary=report_summary(session,active_voice)
    contributions=[];hints=[];in_practice=False;practice_started=False
    for index,message in enumerate(session['messages']):
        kind=message.get('kind','message')
        if kind=='hint':hints.append(message)
        if kind=='challenge':in_practice=True;practice_started=True
        if kind=='explore':in_practice=False
        if message['role']!='you':continue
        following=[]
        for next_message in session['messages'][index+1:]:
            if next_message['role']=='you':break
            following.append(next_message)
        contributions.append({'message':message,'follow_ups':following,'prior_hint_ids':[hint['id'] for hint in hints],
            'phase':'independent_practice' if in_practice else 'exploration'})
    sketches=[{**sketch,'image_available':sketch['image_sha256'] in available_images} for sketch in session.get('sketches',[])]
    return {**summary,'evaluation':session.get('evaluation') if session.get('evaluation_message_id') == session['messages'][-1]['id'] else None,'messages':session['messages'],'contributions':contributions,'hints':hints,'sketches':sketches,
        'artifacts':collect_artifacts(session),
        'result_summary':{'status':'not_assessed',
            'description':'The child’s explanations and Curio’s follow-up questions are recorded below. Understanding has not been scored yet.' if contributions else 'Start a conversation to record the child’s explanations and Curio’s replies.',
            'first_contribution_id':contributions[0]['message']['id'] if contributions else None,
            'latest_contribution_id':contributions[-1]['message']['id'] if contributions else None,
            'practice_status':'open' if in_practice else 'left_practice' if practice_started else 'not_attempted',
            'metrics_available':False},
        'archive_note':any(a.get('legacy') for a in collect_artifacts(session)) or any(not s['image_available'] for s in sketches)}
