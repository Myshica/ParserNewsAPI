import requests

resp = requests.get("http://127.0.0.1:8000/parser/get_recent_news", headers={"Secure": "jIw;$[{@pg')e$w19>?rg*f`+R`fS=H}aL[}*gMB[H=gmFUnzBKnR1;:`Ck</ha;ZdXZ&Y`23m+)_;jL%.W$U(.7y%1Xe_T%q/y+7QMvMM@c=6go'Yn%huWvop|4^o6yespYV;Jj_TZNL4s:LjlgWr)awW0L7S9<,(ej(Yn(\hx|0QBl6V!f+j7(aARhXnv[r$C9J+5~Rxf<:.$'w`~ZK41tngwGmcpjsS&'GjS@,QZrSwaw)7-zf23^SKScJ.GC=$Z3phF82r9dz(('l6LMP<v4qKo1o^ny9bP@XZf+NN8}BMGF\^qv0|Kj=&-c_E!e<qXGqH*i2rdeBjtA^-s(5ziT\&zSX85ADVd-__cRSmM\cZuF4S5+(StNkeKV]5+%:g8=9V_CKu`GB6cU,J*ri'wL9rRgq(ww?yoES[bUy_V+7Nn`XT"})
print(resp.json())