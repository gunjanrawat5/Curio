import { test } from 'node:test';
import assert from 'node:assert/strict';
import { compareFractions } from '../lib/fractions.ts';
test('compares the teaching example exactly',()=>assert.equal(compareFractions({numerator:1,denominator:3},{numerator:1,denominator:4}),1));
test('compares transfer and retry examples',()=>{assert.equal(compareFractions({numerator:1,denominator:6},{numerator:1,denominator:8}),1);assert.equal(compareFractions({numerator:2,denominator:3},{numerator:2,denominator:5}),1)});
test('handles equivalence and reversed order',()=>{assert.equal(compareFractions({numerator:1,denominator:2},{numerator:2,denominator:4}),0);assert.equal(compareFractions({numerator:1,denominator:4},{numerator:1,denominator:3}),-1)});
test('rejects invalid diagram fractions',()=>{for(const denominator of [0,-1,1.5,25])assert.throws(()=>compareFractions({numerator:1,denominator},{numerator:1,denominator:3}));assert.throws(()=>compareFractions({numerator:5,denominator:3},{numerator:1,denominator:3}))});
