import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Curio · Help him remember', description: 'A few loose screws scrambled Curio’s memories. Help a forgetful little TV rediscover math with your words, voice and drawings.' };
export default function Layout({ children }: { children: React.ReactNode }) { return <html lang="en"><body>{children}</body></html>; }
