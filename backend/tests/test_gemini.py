import asyncio
from types import SimpleNamespace
import pytest
from backend import gemini

@pytest.mark.parametrize('mode', ['success', 'empty', 'quota', 'rejected', 'network'])
def test_adapter_uses_sdk_and_sanitizes_errors(monkeypatch, mode):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-secret-never-returned')
    monkeypatch.setenv('GEMINI_MODEL', 'test-model')
    calls = []
    class FakeAsyncClient:
        models = None
        def __init__(self):
            self.models = self
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def generate_content(self, **kwargs):
            calls.append(kwargs)
            if mode in ('quota', 'rejected', 'network'):
                exc = RuntimeError('test-secret-never-returned')
                exc.code = {'quota': 429, 'rejected': 403, 'network': 500}[mode]
                raise exc
            return SimpleNamespace(text='{"text":"Why?","commands":[]}' if mode == 'success' else '')
    monkeypatch.setattr(gemini.genai, 'Client', lambda **kwargs: SimpleNamespace(aio=FakeAsyncClient()))
    run = lambda: asyncio.run(gemini.generate_reply([{'role': 'curio', 'text': 'Teach me.'}, {'role': 'you', 'text': 'Equal wholes.'}], 'teaching'))
    if mode == 'success':
        assert run().text == 'Why?'
    else:
        with pytest.raises(gemini.ProviderError) as result:
            run()
        assert 'test-secret-never-returned' not in result.value.message
        assert result.value.status == {'empty':502, 'quota':429, 'rejected':503, 'network':502}[mode]
    assert calls[0]['model'] == 'test-model'
    assert calls[0]['config'].response_mime_type == 'application/json'
    assert calls[0]['config'].response_json_schema is not None
    assert [m.role for m in calls[0]['contents']] == ['model', 'user']
    assert 'Current phase: teaching' in calls[0]['config'].system_instruction

