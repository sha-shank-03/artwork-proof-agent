import http.cookiejar
import io
import json
import time
import urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def call(path,data=None,mime="application/json"):
    payload=json.dumps(data).encode() if mime=="application/json" and data is not None else data
    req=urllib.request.Request("http://127.0.0.1:8081"+path,data=payload,headers={"Content-Type":mime,"Origin":"http://localhost:5174"})
    with opener.open(req,timeout=20) as r:return json.load(r)
call("/session",{"token":Path(".local/invite.txt").read_text().strip()})
im=Image.new("RGB",(900,900),"#eee8dc");d=ImageDraw.Draw(im);d.rounded_rectangle((90,90,810,810),radius=80,fill="#204d3f");d.ellipse((275,200,625,550),fill="#d8ef7c");d.text((320,610),"FIELD NOTES",fill="white",font_size=38);b=io.BytesIO();im.save(b,"PNG")
upload=call("/uploads?name=field-notes.png",b.getvalue(),"image/png")
run=call("/runs",{"uploadId":upload["id"],"width":3,"height":3})
print("Created",run["id"],flush=True)
for _ in range(120):
    time.sleep(1);run=call("/runs/"+run["id"])
    if run["state"]!="running":break
Path(".local/smoke.json").write_text(json.dumps(run,indent=2))
print(json.dumps({k:v for k,v in run.items() if k not in ("previews","measurements")},indent=2))
