import { test } from 'node:test';
import assert from 'node:assert/strict';
import { clearSubmittedStrokes, restoreClearedStrokes, type Stroke } from '../lib/strokes.ts';
const a:Stroke={id:'a',points:'1,1',color:'purple'},b:Stroke={id:'b',points:'2,2',color:'green'};
test('clearing a submitted snapshot preserves strokes made while waiting',()=>{
 assert.deepEqual(clearSubmittedStrokes([a,b],[a]),[b]);
 assert.deepEqual(clearSubmittedStrokes([b],[a]),[b]);
});
test('undo restores cleared strokes without losing or duplicating newer strokes',()=>{
 assert.deepEqual(restoreClearedStrokes([b],[a]),[a,b]);
 assert.deepEqual(restoreClearedStrokes([a,b],[a]),[a,b]);
});
