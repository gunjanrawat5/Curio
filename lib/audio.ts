export function pcm16ToFloat32(base64:string):Float32Array {
 const raw=atob(base64);
 if(raw.length%2)throw new Error('Invalid audio data');
 const data=new DataView(Uint8Array.from(raw,c=>c.charCodeAt(0)).buffer);
 const result=new Float32Array(raw.length/2);
 for(let i=0;i<result.length;i++)result[i]=data.getInt16(i*2,true)/32768;
 return result;
}
export function bytesToBase64(buffer:ArrayBuffer):string {
 const bytes=new Uint8Array(buffer);let binary='';
 for(let i=0;i<bytes.length;i++)binary+=String.fromCharCode(bytes[i]);
 return btoa(binary);
}
