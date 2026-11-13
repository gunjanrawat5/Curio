import ReportShell from '@/components/ReportShell';
import ReportDetail from '@/components/ReportDetail';
export const metadata={title:'Conversation report · Curio'};
export default async function ReportPage({params}:{params:Promise<{id:string}>}){const {id}=await params;return <ReportShell><ReportDetail key={id} id={id}/></ReportShell>;}
