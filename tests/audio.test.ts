import {test} from 'node:test';
import assert from 'node:assert/strict';
import {bytesToBase64,pcm16ToFloat32} from '../lib/audio.ts';
test('native PCM audio uses signed little-endian 16-bit samples',()=>{
 const bytes=new ArrayBuffer(8);const view=new DataView(bytes);
 [-32768,0,16384,32767].forEach((sample,i)=>view.setInt16(i*2,sample,true));
 const result=pcm16ToFloat32(bytesToBase64(bytes));
 assert.deepEqual(Array.from(result),[-1,0,.5,32767/32768]);
});
test('truncated PCM frames are rejected',()=>assert.throws(()=>pcm16ToFloat32(btoa('x'))));
