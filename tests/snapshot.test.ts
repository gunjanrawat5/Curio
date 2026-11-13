import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sketchRevision} from '../lib/snapshot.ts';
test('snapshot identity changes on drawing edits and survives restoring identical strokes',async()=>{
 const a={id:'a',points:'1,1 2,2',color:'purple'};
 const revision=await sketchRevision([a]);
 assert.equal(revision.length,64);
 assert.equal(await sketchRevision([{...a}]),revision);
 assert.notEqual(await sketchRevision([{...a,points:'1,1 3,3'}]),revision);
 assert.notEqual(await sketchRevision([]),revision);
});
