export type Fraction = { numerator: number; denominator: number };
export function compareFractions(a: Fraction, b: Fraction): number {
  for (const f of [a,b]) if (!Number.isInteger(f.denominator) || f.denominator < 1 || f.denominator > 24 || !Number.isInteger(f.numerator) || f.numerator < 0 || f.numerator > f.denominator) throw new Error('Invalid fraction');
  return Math.sign(a.numerator * b.denominator - b.numerator * a.denominator);
}
