import Link from 'next/link';
import {ArrowLeft,BookOpen} from 'lucide-react';
import ReportShell from '@/components/ReportShell';
import Curio from '@/components/Curio';
export default function NotFound(){return <ReportShell><div className="report-empty missing-page"><Curio/><h1>This page isn’t here.</h1><p>The link may have changed. Your saved conversations are in Reports.</p><div><Link className="primary" href="/"><ArrowLeft size={16}/> Back to Curio</Link><Link className="secondary-button" href="/reports"><BookOpen size={16}/> Reports</Link></div></div></ReportShell>;}
