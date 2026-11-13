import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Curio · Little teacher, big ideas', description: 'Teach a curious little TV with your words and drawings. A playful learning-by-teaching workspace.' };
export default function Layout({ children }: { children: React.ReactNode }) { return <html lang="en"><body>{children}</body></html>; }
