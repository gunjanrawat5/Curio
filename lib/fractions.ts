export type Fraction = { numerator: number; denominator: number };
export function compareFractions(a: Fraction, b: Fraction): number {
  for (const f of [a,b]) if (!Number.isInteger(f.denominator) || f.denominator < 1 || f.denominator > 24 || !Number.isInteger(f.numerator) || f.numerator < 0 || f.numerator > f.denominator) throw new Error('Invalid fraction');
  return Math.sign(a.numerator * b.denominator - b.numerator * a.denominator);
}
export function demoReply(text: string): string {
 const s = text.toLowerCase();
 if (/same|equal/.test(s) && /whole/.test(s)) return 'That helps! If the wholes are the same size, what happens to each piece when we make more equal pieces?';
 if (/bigger denominator|fourth.*bigger|1\/4.*bigger/.test(s)) return 'Hmm, does a bigger number of pieces mean each piece is bigger? Try looking at one piece in each bar.';
 if (/smaller|third.*bigger|1\/3.*bigger/.test(s)) return 'Can you explain why? Tell me about the size of the whole and how many equal pieces it has.';
 return 'Tell me a little more! How could we use equal-sized wholes to compare one third and one fourth?';
}
