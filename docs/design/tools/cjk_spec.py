import sys, pathlib, re
from fontTools.ttLib import TTFont
from fontTools import subset
repo=pathlib.Path(sys.argv[1]); dl=pathlib.Path(sys.argv[2])
post=(repo/"content/post/books-summer-2021/index.md").read_text().split("---",2)[2].split("<!--more-->")[0]
text="".join(sorted(set(post)))+"陳威達片次也北公花突化名心"
def go(src,dst,fam):
    f=TTFont(src)
    o=subset.Options(); o.flavor="woff2"; o.layout_features=["*"]; o.name_IDs=["*"]; o.notdef_outline=True
    s=subset.Subsetter(o); s.populate(text=text); s.subset(f)
    for r in f["name"].names:
        if r.nameID in (1,4,16,18,21): r.string=fam
        elif r.nameID==6: r.string=fam.replace(" ","")
        elif r.nameID==3: r.string=fam+" subset"
    f.flavor="woff2"; f.save(repo/"static/fonts"/dst); print(dst,(repo/"static/fonts"/dst).stat().st_size//1024,"KB")
go(dl/"notoserif/NotoSerifTC.ttf","spec-notoserif-tc.woff2","UDC Spec Noto Serif TC")
go(dl/"iansui/Iansui-Regular.ttf","spec-iansui.woff2","UDC Spec Iansui")
