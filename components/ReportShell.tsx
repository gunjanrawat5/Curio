import Link from 'next/link';
import Brand from './Brand';
import {ArrowLeft,BookOpen} from 'lucide-react';
export default function ReportShell({children}:{children:React.ReactNode}){
 return <main className="reports-shell"><header><Brand/><Link href="/reports" className="report-nav"><BookOpen size={17}/> Reports</Link><Link href="/" className="report-back"><ArrowLeft size={16}/> Back to Curio</Link></header><div className="reports-scroll">{children}</div></main>;
}
