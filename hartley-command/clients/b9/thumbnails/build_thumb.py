from PIL import Image, ImageDraw, ImageFont
import math

S=720
NAVY=(11,21,51)          # #0B1533
GOLD=(201,161,79)        # #C9A14F
WHITE=(245,247,252)
BLUE=(107,132,255)       # #5B7FFF-ish light periwinkle
POP_B="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
MONO_B="/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"

def F(path,sz): return ImageFont.truetype(path,sz)
f_kick=F(MONO_B,17); f_eye=F(POP_B,19); f_head=F(POP_B,62)

def tracked_width(draw,text,font,tr):
    w=0
    for ch in text: w+=draw.textlength(ch,font=font)+tr
    return w-tr if text else 0

def draw_tracked(base,xy,text,font,fill,tr,anchor="la",alpha=255):
    # render on temp layer for alpha
    layer=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    total=tracked_width(d,text,font,tr)
    x,y=xy
    if anchor=="ma": x=x-total/2
    if anchor=="ra": x=x-total
    cx=x
    for ch in text:
        d.text((cx,y),ch,font=font,fill=fill+(alpha,))
        cx+=d.textlength(ch,font=font)+tr
    base.alpha_composite(layer)

def draw_center(base,cx,y,text,font,fill,alpha=255,dy=0):
    layer=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    w=d.textlength(text,font=font)
    d.text((cx-w/2,y+dy),text,font=font,fill=fill+(alpha,))
    base.alpha_composite(layer)

def asterisk(base,cx,cy,r,color,alpha=255,rot=0,scale=1.0):
    layer=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    r=r*scale
    for i in range(6):
        a=math.radians(rot+i*60)
        x2=cx+math.cos(a)*r; y2=cy+math.sin(a)*r
        d.line([(cx,cy),(x2,y2)],fill=color+(alpha,),width=max(2,int(6*scale)))
    rr=max(3,int(7*scale))
    d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=color+(alpha,))
    base.alpha_composite(layer)

def ease(t): 
    t=max(0,min(1,t)); return 1-(1-t)**3

def seg(t,a,b): return ease((t-a)/(b-a)) if b>a else 1.0

# headline lines: (text, color)
HEAD=[("They judge",WHITE),("your building —",WHITE),("before they read",BLUE),("a word.",BLUE)]

def frame(t):  # t in seconds
    img=Image.new("RGBA",(S,S),NAVY+(255,))
    d=ImageDraw.Draw(img)
    # subtle top+bottom hairline gold rules (static, appear w/ kickers)
    ka=int(255*seg(t,0.0,0.45))
    # corner kickers
    draw_tracked(img,(46,40),"BRAND 9 · EST. 1986",f_kick,GOLD,3,"la",ka)
    draw_tracked(img,(S-46,40),"SIGNAGE",f_kick,GOLD,3,"ra",ka)
    # thin gold rule under kickers
    if ka>0:
        ov=Image.new("RGBA",img.size,(0,0,0,0)); dd=ImageDraw.Draw(ov)
        dd.line([(46,74),(S-46,74)],fill=GOLD+(int(ka*0.5),),width=1); img.alpha_composite(ov)
    # asterisk emblem (fade+scale in, then gentle twinkle)
    aa=seg(t,0.3,0.8); 
    tw=1.0
    if t>1.7: tw=1.0+0.12*math.sin((t-1.7)*3.2)
    if aa>0:
        asterisk(img,S/2,150+ (1-aa)*-8,26,GOLD,int(255*aa),rot=(1-aa)*40,scale=(0.6+0.4*aa)*tw)
    # eyebrow
    ea=int(255*seg(t,0.55,1.0))
    draw_center(img,S/2,205,"EVERY PROPERTY MAKES A FIRST IMPRESSION",f_eye,GOLD,ea)
    # eyebrow tracking (redraw tracked centered for spacing)
    # (using center plain draw above for reliability)
    # headline lines staggered
    y0=270
    for i,(txt,col) in enumerate(HEAD):
        start=0.85+i*0.13; a=seg(t,start,start+0.55)
        dy=int((1-a)*26)
        draw_center(img,S/2,y0+i*78 - dy, txt, f_head, col, int(255*a))
    # bottom CTA-ish url
    ua=int(255*seg(t,1.5,2.0))
    draw_tracked(img,(S/2,S-58),"BRAND9SIGNS.COM",f_kick,GOLD,3,"ma",ua)
    return img.convert("RGB")

# timeline
fps=20; dur=2.4; hold=1.0
frames=[]; 
n=int(dur*fps)
for k in range(n): frames.append(frame(k/fps))
last=frame(dur)
for _ in range(int(hold*fps)): frames.append(last)

# save GIF (optimized palette)
frames[0].save("monument-thumb.gif",save_all=True,append_images=frames[1:],
               duration=int(1000/fps),loop=0,optimize=True,disposal=2)
last.save("monument-thumb-final.png")
print("frames:",len(frames),"| GIF + final PNG saved at",S,"px")
