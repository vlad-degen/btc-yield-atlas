"""Export an identical static research chart to SVG and high-resolution PNG."""
import datetime as dt,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.shapes import Drawing,Line,PolyLine,String,Rect
from reportlab.graphics import renderSVG
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[2]
def run():
 src=json.loads((ROOT/'data/eth/comparable_ETH_wealth.json').read_text());series=src['series'];dest=ROOT/'research/eth/figures';dest.mkdir(exist_ok=True)
 W,H=1100,680;L,R,B,U=88,50,145,112;pw=W-L-R;ph=H-B-U
 vals=[p['normalized_ETH_book_wealth'] for ps in series.values() for p in ps];lo=math.floor(min(vals))-1;hi=math.ceil(max(vals))+1
 x=lambda t:L+(t-src['start_timestamp'])/(src['end_timestamp']-src['start_timestamp'])*pw
 y=lambda v:B+(v-lo)/(hi-lo)*ph
 scale=2;im=Image.new('RGB',(W*scale,H*scale),'#ffffff');pd=ImageDraw.Draw(im);svg=Drawing(W,H)
 fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
 def text(txt,xx,yy,size=13,color='#46536b'):
  svg.add(String(xx,yy,txt,fontName='Helvetica',fontSize=size,fillColor=HexColor(color)))
  f=ImageFont.truetype(fontpath,size*scale);pd.text((int(xx*scale),int((H-yy-size)*scale)),txt,font=f,fill=color)
 def line(xx,yy,xx2,yy2,color='#e2e7ef',width=1):
  svg.add(Line(xx,yy,xx2,yy2,strokeColor=HexColor(color),strokeWidth=width));pd.line([(int(xx*scale),int((H-yy)*scale)),(int(xx2*scale),int((H-yy2)*scale))],fill=color,width=max(1,int(width*scale)))
 text('ETH book wealth over the same 730-day window',L,H-45,25,'#14223b')
 text('2 Oct 2024 to 2 Oct 2026 | start = 100 | published PPS and issuer conversion rates',L,H-74,14)
 for val in range(lo,hi+1,2):
  line(L,y(val),W-R,y(val));text(str(val),L-42,y(val)-5,12)
 for yy,mm,dd in [(2024,10,2),(2025,4,2),(2025,10,2),(2026,4,2),(2026,10,2)]:
  t=int(dt.datetime(yy,mm,dd,23,59,59,tzinfo=dt.timezone.utc).timestamp());xx=x(t)
  line(xx,B,xx,H-U,'#edf0f5');text(dt.date(yy,mm,dd).strftime('%b %Y'),xx-28,B-25,12)
 palette=['#1555bb','#8793a6','#8759c0','#00857b','#d59024','#bd4456']
 for i,(name,ps) in enumerate(series.items()):
  color=palette[i];coords=[(x(p['timestamp']),y(p['normalized_ETH_book_wealth'])) for p in ps]
  svg.add(PolyLine([z for xy in coords for z in xy],strokeColor=HexColor(color),strokeWidth=2.5,fillColor=None))
  pd.line([(int(xx*scale),int((H-yy)*scale)) for xx,yy in coords],fill=color,width=5)
  col=i%3;row=i//3;xx=L+col*325;yy=78-row*29
  line(xx,yy+3,xx+22,yy+3,color,3)
  text(f'{name}: {ps[-1]["normalized_ETH_book_wealth"]-100:+.2f}%',xx+31,yy-2,13,'#14223b')
 text('Observed points joined for display. No external rewards, market depeg, execution or withdrawal costs.',L,20,11)
 renderSVG.drawToFile(svg,str(dest/'eth-wealth.svg'))
 svgfile=dest/'eth-wealth.svg';svgfile.write_text(svgfile.read_text().replace('fill: None','fill: none'))
 im.save(dest/'eth-wealth.png')
 print('Figure',dest/'eth-wealth.png','range',lo,hi)

if __name__=='__main__':run()
