'use client';
import {useId} from 'react';
export default function Curio({thinking=false,speaking=false,listening=false}:{thinking?:boolean;speaking?:boolean;listening?:boolean}){
 const id=useId().replace(/[^a-zA-Z0-9_-]/g,'');
 return <div className={`curio ${thinking?'thinking':''} ${speaking?'speaking':''} ${listening?'listening':''}`} role="img" aria-label="Curio, a blue, slightly worn TV facing left, with round gold glasses, yellow eyes, red antenna tips and a loose screw">
 <svg className="curio-art" viewBox="0 0 300 360" fill="none" aria-hidden="true">
 <defs><clipPath id={`${id}-case`}><path d="M43 91 211 98Q231 99 231 121L235 295Q234 317 213 320L45 315Q25 313 24 292L20 116Q20 93 43 91Z"/></clipPath></defs>
 <ellipse cx="150" cy="340" rx="113" ry="10" fill="#24362b" opacity=".12"/>
 <g className="curio-body" stroke="#15160f" strokeLinecap="round" strokeLinejoin="round">
 {/* The cabinet recedes to the right, keeping Curio's face toward the whiteboard. */}
 <path d="M191 95Q215 77 248 86Q270 89 272 113L278 273Q280 302 231 315L208 308Z" fill="#08619f" strokeWidth="7"/>
 <path d="M236 93Q256 90 260 113L267 272Q267 288 247 295" stroke="#1494db" strokeWidth="5"/>
 <path d="m239 111 5 168m8-154 4 144m-10-42 4 40" stroke="#073b61" strokeWidth="4"/>
 <path d="m263 278-1 12-8 7 2-13m-11 15-5 5" stroke="#d7b36e" strokeWidth="3"/>
 <path d="m51 308-15 18q-8 9 12 11l44 1 17-23m74 0 28-1 35 24q6 8-10 8l-51-7-13-20" fill="#15160f" strokeWidth="5"/>
 <path d="M90 92Q89 59 116 52q31-6 48 41" fill="#f5d32d" strokeWidth="7"/>
 <path d="m99 80 4-10m4 12 3-8" stroke="#997a1b" strokeWidth="1.7"/>
 <path d="m137 65 13 8-8-1 9 6" stroke="#ed6440" strokeWidth="6"/>
 <g className="curio-aerials"><path d="m109 71-25-46m65 42 24-45" strokeWidth="6"/>
 <ellipse cx="81" cy="22" rx="10" ry="12" fill="#f04335" strokeWidth="5"/>
 <ellipse cx="176" cy="20" rx="10" ry="12" fill="#f04335" strokeWidth="5"/>
 <path d="m78 17 2-3m93 1 2-3" stroke="#fff5cb" strokeWidth="3"/>
 </g>
 <path d="M43 91 211 98Q231 99 231 121L235 295Q234 317 213 320L45 315Q25 313 24 292L20 116Q20 93 43 91Z" fill="#1065a6" strokeWidth="7"/>
 <g clipPath={`url(#${id}-case)`} stroke="none">
 <path d="m26 111 5-14 19-5 21 2-3 4-11 1-5-3-7 6-9 2-3 13-5-1Zm182-12 13 4 9 15-6 1-2-11-10-1-3-4-10 1Zm-182 177 7 5-1 13 5 8 4-1 5 8 14 2 7 6-24-1-13-8-7-17Zm171 39 6-5 6 2 6-7 7-1 4-12 5 2-2 21-18 8-18-3Z" fill="#e7c389"/>
 <path d="m32 136 3 47-3 38-4-15m201-65-2 46 5 45m-183 74 65 4" fill="none" stroke="#1c8ccc" strokeWidth="2" opacity=".8"/>
 <path d="m40 108 9-6m-7 13 14-12m-20 173 8 11m-6 1 10 11m153 6 7-9m-1 13 11-14m-159-20 11 12m-14-8 7 9" stroke="#d3b57e" strokeWidth=".9"/>
 </g>
 <path d="M53 116 186 122Q207 123 211 146L215 245Q215 271 191 276L58 272Q43 271 40 254L35 149Q33 119 53 116Z" fill="#d5d8dd" strokeWidth="6"/>
 <path d="m46 249q3 14 17 16l116 3q21 1 26-13" stroke="#087fc2" strokeWidth="2.8"/>
 <path d="M45 144q1-13 14-18l-10 15" fill="#fff1ba" stroke="none" opacity=".75"/>
 <g className="curio-brow curio-brow-left"><path d="M65 150q12-13 26-10" stroke="#604b24" strokeWidth="10"/></g>
 <g className="curio-brow curio-brow-right"><path d="M142 145q18 0 31 13" stroke="#604b24" strokeWidth="10"/></g>
 <g className="curio-eye"><ellipse cx="82" cy="193" rx="13" ry="24" fill="#fffdf5" stroke="none"/><ellipse cx="77" cy="195" rx="5.5" ry="11" fill="#10140f" stroke="none"/><ellipse cx="74" cy="188" rx="3" ry="4" fill="#fffdf5" stroke="none"/></g>
 <g className="curio-eye"><ellipse cx="157" cy="196" rx="14" ry="25" fill="#fffdf5" stroke="none"/><ellipse cx="151" cy="198" rx="6" ry="11" fill="#10140f" stroke="none"/><ellipse cx="148" cy="190" rx="3" ry="4" fill="#fffdf5" stroke="none"/></g>
 <g className="curio-glasses" stroke="#b18225" strokeWidth="4.5">
 <ellipse cx="78" cy="192" rx="29" ry="35"/><ellipse cx="156" cy="196" rx="31" ry="36"/>
 <path d="M108 194q8-7 17 2" stroke="#e6ba52" strokeWidth="5"/>
 <path d="m41 189 8 1m139 7 7 1" stroke="#e6ba52" strokeWidth="5"/>
 <circle cx="42" cy="190" r="4" fill="#f4cf68" stroke="#bf8d2c" strokeWidth="1.5"/><circle cx="195" cy="198" r="4" fill="#f4cf68" stroke="#bf8d2c" strokeWidth="1.5"/>
 <path d="m59 177 6-7m72 12 7-7" stroke="#fff6d6" strokeWidth="3"/>
 </g>
 <path className="curio-mouth-rest" d="M101 240q15 16 30 1" stroke="#604b24" strokeWidth="5"/>
 <g className="curio-mouth-open" stroke="none"><ellipse cx="116" cy="244" rx="12" ry="9" fill="#604b24"/><ellipse cx="116" cy="241" rx="8" ry="5" fill="#10140f"/></g>
 <path d="m71 284 87 2q9 0 9 9v9l-96-2q-7 0-7-8v-3q0-7 7-7Z" fill="#078cd2" strokeWidth="5"/>
 <path d="m73 288 1 10m81-8 1 10" stroke="#06416b" strokeWidth="3"/>
 <ellipse cx="201" cy="294" rx="13" ry="15" fill="#f2cf2b" strokeWidth="5"/>
 <path d="m198 284-2 4" stroke="#fff4c4" strokeWidth="3"/>
 <g className="curio-loose-screw"><circle cx="216" cy="115" r="4" fill="#dfbd76" stroke="#8c713c" strokeWidth="1.3"/><path d="m214 114 4 2" stroke="#8c713c" strokeWidth="1.1"/></g>
 </g></svg></div>;
}
