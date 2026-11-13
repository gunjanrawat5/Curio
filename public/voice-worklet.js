/* Microphone PCM16 capture. This worklet runs on the browser audio thread. */
class CurioMicrophone extends AudioWorkletProcessor {
  constructor(){super();this.samples=new Float32Array(2048);this.offset=0;}
  process(inputs){
    const channel=inputs[0]&&inputs[0][0];
    if(channel)for(let i=0;i<channel.length;i++){
      this.samples[this.offset++]=channel[i];
      if(this.offset===this.samples.length){
        const bytes=new ArrayBuffer(this.samples.length*2),view=new DataView(bytes);
        for(let j=0;j<this.samples.length;j++){const v=Math.max(-1,Math.min(1,this.samples[j]));view.setInt16(j*2,v<0?v*32768:v*32767,true);}
        this.port.postMessage(bytes,[bytes]);this.offset=0;
      }
    }
    return true;
  }
}
registerProcessor('curio-microphone',CurioMicrophone);
