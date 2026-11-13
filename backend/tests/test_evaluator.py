import json
from copy import deepcopy
from backend.evaluator import ROOT, validate_report


def fixtures():
    return json.loads((ROOT/'sample_report.json').read_text()), json.loads((ROOT/'sample_transcript.json').read_text())


def test_demo_report_counts_and_outcome():
    raw, log = fixtures()
    r = validate_report(raw, log)
    assert [o['after'] for o in r['objectives']] == ['not_observed','demonstrated_independent','demonstrated_independent']
    assert r['outcome'] == 'developing'
    assert r['misconceptions'][0]['resolved']
    assert r['sample'] is False
    assert r['transfer']['attempted'] is False


def test_missing_or_curio_correction_cannot_raise_demonstration():
    for remove in (True, False):
        raw, log = fixtures()
        if remove: log['events'] = [e for e in log['events'] if e['id'] != 'e10']
        else:
            for e in log['events']:
                if e['id']=='e10': e['actor']='pip'
        r = validate_report(raw, log)
        assert not any(o['after'].startswith('demonstrated') for o in r['objectives'])
        assert not r['misconceptions'][0]['resolved']
        assert r['misconceptions'][0]['resolution_quote'] is None


def test_fixed_rubric_unknown_ids_invalid_quotes_and_transfer():
    raw, log = fixtures()
    raw['objectives'] = [{'id':'invented','after':'demonstrated_independent'}]
    raw['misconceptions'][0]['quote']='fabricated'
    raw['outcome']='mastery_demonstrated'
    raw['transfer']={'attempted':True,'passed':True}
    r=validate_report(raw,log)
    assert len(r['objectives'])==3 and all(o['after']=='not_observed' for o in r['objectives'])
    assert r['outcome']=='more_evidence_needed' and not r['misconceptions']
    assert not r['transfer']['attempted']

from backend.tests.test_sessions import client, session
from backend import main
from backend.store import event


def test_evaluation_endpoint_persists_caches_and_invalidates(client, monkeypatch):
    calls=[]
    async def evaluate(s):
        calls.append(s['id'])
        raw,log=fixtures()
        return validate_report(raw,log)
    monkeypatch.setattr('backend.evaluator.evaluate',evaluate)
    data=session(client)
    path='/reports/'+data['id']
    assert client.post(path+'/evaluate').status_code==422
    stored=main.app.state.store.get(data['id'])
    stored['messages'].append(event('you','One third is larger because the same whole has fewer equal pieces.'))
    main.app.state.store.save(stored)
    result=client.post(path+'/evaluate')
    assert result.status_code==200 and result.json()['evaluation']['outcome']=='developing'
    assert client.get(path).json()['evaluation'] is not None
    client.post(path+'/evaluate')
    assert len(calls)==1
    stored=main.app.state.store.get(data['id'])
    stored['messages'].append(event('you','What about fifths?'))
    main.app.state.store.save(stored)
    assert client.get(path).json()['evaluation'] is None
    assert client.get(path).json()['messages']==stored['messages']
    client.post(path+'/evaluate')
    assert len(calls)==2
