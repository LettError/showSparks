# -*- coding: utf-8 -*-

from AppKit import NSColor, NSFont, NSFontAttributeName, NSForegroundColorAttributeName, NSCursor
from mojo.events import installTool, EditingTool, BaseEventTool, setActiveEventTool
from mojo.drawingTools import *
from mojo.UI import UpdateCurrentGlyphView
from defconAppKit.windows.baseWindow import BaseWindowController
import math

#
#
#     a visualisation for RoboFont
#     Show the ratio between incoming and outgoing sections of bcps and tangents.

def getAngle(a, b):
    r = atan2(a[1],a[0])-atan2(b[1],b[0])
    if r < 0:
        r += 2*pi
    return r

class RatioTool(EditingTool):
    balloonDistance = 40
    textAttributes = {
        NSFontAttributeName : NSFont.systemFontOfSize_(10),
        NSForegroundColorAttributeName : NSColor.whiteColor(),
    }
    incomingColor = (1,0,.5, .7)
    outgoingColor = (.5,0,1, .7)
    lineColor =  (.5,0,1, .125)
    _offcurveNames = ['offcurve', 'offCurve']     # RF1.8: offcurve, RF2.0 offCurve

    def setup(self):
        self._rin = None
        self._rout = None
        self._multiple = False    # if we're selecting more than 1
        
    def draw(self, viewScale):
        g =  self.getGlyph()
        if g is not None:
            save()
            self.getRatio(g, viewScale)
            restore()
    
    def getRatio(self, g, viewScale):
        # get the in/out ratio of selected smooth points
        self._multiple = 0
        for c in g.contours:
            if c is None: continue
            l = len(c.points)
            for i, p in enumerate(c.points):
                # we're dragging a bcp so we need the previous and the one before that
                # or, the next and the one after that.
                if not p.selected: continue
                if c is None:
                    continue

                pppt = c.points[i-2]
                ppt = c.points[i-1]
                npt = c.points[(i+1)%l]
                nnpt = c.points[(i+2)%l]
                
                if False:
                    print '\npppt', pppt, "\t", pppt.type, "\t", pppt.smooth
                    print 'ppt', ppt, "\t", ppt.type, "\t", ppt.smooth
                    print 'p', p, "\t", p.type, "\t", p.smooth
                    print 'npt', npt, "\t", npt.type, "\t", npt.smooth
                    print 'nnpt', nnpt, "\t", nnpt.type, "\t", nnpt.smooth
                
                    print '-'*40
                    print "ppt.type in self._offcurveNames", ppt.type in self._offcurveNames, ppt.type
                    print "ppt.type==curve", ppt.type=="curve"
                    print "p.smooth==True", p.smooth==True
                    print "p.type==line", p.type=="line"
                    print "npt.type in self._offcurveNames", npt.type in self._offcurveNames
                    print '-'*40

                # incoming
                # x pppt <RPoint curve (218.0, 130.0) smooth=True at 4782415312>
                # x ppt <RPoint offcurve (218.0, 223.0) at 4782413008>
                # p <RPoint offcurve (200, 271) at 4706168208>
                # npt <RPoint curve (152, 387) smooth=True at 4782415632>
                # nnpt <RPoint offcurve (107, 496) at 4782412944>
                
                # outgoing
                # pppt <RPoint offcurve (200, 271) at 4535639696>
                # ppt <RPoint curve (152, 387) smooth=True at 4535639760>
                # p <RPoint offcurve (106, 498) at 4535607120>
                # x npt <RPoint offcurve (90, 559) at 4535637712>
                # x nnpt <RPoint curve (90.0, 620.0) smooth=True at 4535637904>

                # dragging the center on curve
                # pppt <RPoint offcurve (71.0, 355.0) at 4716508304>
                # ppt <RPoint offcurve (156, 251) at 4716508496>
                # p <RPoint curve (568, 256) name=u'this is master 2' smooth=True at 4716489680>
                # npt <RPoint offcurve (798, 259) at 4716508752>
                # nnpt <RPoint offcurve (822.0, 241.0) at 4716508944>

                
                
                # is this an in?
                apt = None
                bpt = None
                cpt = None
                r = None
                rin = None
                rout = None
                
                if p.type in self._offcurveNames and npt.type=="curve" and npt.smooth==True and nnpt.type in self._offcurveNames:
                    apt = p
                    bpt = npt
                    cpt = nnpt
                elif ppt.type == "curve" and p.type in self._offcurveNames and npt.type in self._offcurveNames and ppt.smooth==True:
                    apt = pppt
                    bpt = ppt
                    cpt = p
                elif ppt.type in self._offcurveNames and p.smooth==True and p.type=="curve" and npt.type in self._offcurveNames:
                    apt = ppt
                    bpt = p
                    cpt = npt

                # incoming tangent, clicked on the tangent
                # pppt <RPoint offcurve (1218, 447) at 4818181584> 	offcurve 	False
                # ppt <RPoint offcurve (1082, 495) at 4818181840> 	offcurve 	False
                # p <RPoint curve (856, 495) smooth=True at 4750235536> 	curve 	True
                # npt <RPoint line (494, 495) smooth=True at 4818181968> 	line 	True
                # nnpt <RPoint offcurve (424, 495) at 4818178832> 	offcurve 	False
                elif ppt.type in self._offcurveNames and p.smooth==True and p.type=="curve" and npt.type == "line":
                    apt = ppt
                    bpt = p
                    cpt = npt
                # incoming tangent, clicked on the bcp
                # pppt <RPoint curve (347, 157) smooth=True at 4737364880> 	curve 	True
                # ppt <RPoint offcurve (346, 235) at 4737366800> 	offcurve 	False
                # p <RPoint offcurve (324, 271) at 4737344848> 	offcurve 	False
                # npt <RPoint curve (238, 343) smooth=True at 4737367120> 	curve 	True
                # nnpt <RPoint line (180, 391) smooth=True at 4737364176> 	line 	True
                elif pppt.type=="curve" and ppt.type in self._offcurveNames and p.type in self._offcurveNames and npt.type=='curve' and nnpt.type=='line':
                    apt = p
                    bpt = npt
                    cpt = nnpt
                # outgoing tangent, clicked on the tangent
                # pppt <RPoint offcurve (206, 305) at 4868902544> 	offcurve 	False
                # ppt <RPoint curve (472, 305) smooth=True at 4868899920> 	curve 	True
                # p <RPoint line (794, 305) smooth=True at 4868899152> 	line 	True
                # npt <RPoint offcurve (864, 305) at 4868899984> 	offcurve 	False
                # nnpt <RPoint offcurve (873, 298) at 4868900176> 	offcurve 	False
                elif pppt.type in self._offcurveNames and ppt.type=="curve" and p.smooth==True and p.type=="line" and npt.type in self._offcurveNames:
                    apt = ppt
                    bpt = p
                    cpt = npt
                # outgoing tangent, clicked on the bcp
                # pppt <RPoint curve (238, 343) smooth=True at 4737453520> 	curve 	True
                # ppt <RPoint line (180, 391) smooth=True at 4737453776> 	line 	True
                # p <RPoint offcurve (123, 438) at 4737451024> 	offcurve 	False
                # npt <RPoint offcurve (90, 474) at 4737451472> 	offcurve 	False
                # nnpt <RPoint curve (90, 544) smooth=True at 4737478800> 	curve 	True
                elif p.type in self._offcurveNames and ppt.type == "line" and ppt.smooth==True and pppt.type=="curve":
                    apt = pppt
                    bpt = ppt
                    cpt = p

                if apt is not None and bpt is not None and cpt is not None:
                    rin = math.hypot(apt.x-bpt.x,apt.y-bpt.y)
                    rout = math.hypot(cpt.x-bpt.x,cpt.y-bpt.y)
                    r = rin / rout
                if r is not None:
                    self._multiple += 1
                    # text bubble for the ratio
                    angle = math.atan2(apt.y-cpt.y,apt.x-cpt.x)- math.pi*.5
                    sbd = self.balloonDistance * viewScale * .25
                    tp = bpt.x + math.cos(angle)*sbd*2, bpt.y -20 + math.sin(angle)*sbd*2
                    self.getNSView()._drawTextAtPoint(
                        "%3.4f"%(r ),
                        self.textAttributes,
                        tp,
                        yOffset=0,
                        drawBackground=True,
                        backgroundColor=NSColor.blueColor())
                    
                    ap = apt.x + math.sin(angle)*sbd*2, apt.y -20 + math.cos(angle)*sbd*2
                    self.getNSView()._drawTextAtPoint(
                        "%3.4f"%(math.degrees(angle)%180 ),
                        self.textAttributes,
                        ap,
                        yOffset=0,
                        drawBackground=True,
                        backgroundColor=NSColor.blackColor())
                    
                    # text bubble for the angles
                        
                    # if False:
                    #     stroke(self.incomingColor[0], self.incomingColor[1], self.incomingColor[2])
                    #     strokeWidth(1*viewScale)
                    #     line((apt.x+math.cos(angle)*sbd,apt.y+math.sin(angle)*sbd), 
                    #     (bpt.x+math.cos(angle)*sbd,bpt.y+math.sin(angle)*sbd))

                    #     line((apt.x,apt.y), 
                    #     (apt.x+math.cos(angle)*sbd,apt.y+math.sin(angle)*sbd))

                    #     stroke(self.outgoingColor[0], self.outgoingColor[1], self.outgoingColor[2])
                    #     line((cpt.x+math.cos(angle)*sbd,cpt.y+math.sin(angle)*sbd), 
                    #     (bpt.x+math.cos(angle)*sbd,bpt.y+math.sin(angle)*sbd))

                    #     line((cpt.x,cpt.y), 
                    #     (cpt.x+math.cos(angle)*sbd,cpt.y+math.sin(angle)*sbd))

                    #     line((bpt.x,bpt.y), 
                    #     (bpt.x+math.cos(angle)*sbd,bpt.y+math.sin(angle)*sbd))

                    
                    fill(None)
                    self._rin = rin
                    self._rout = rout

                    #lineDash(4*viewScale,4*viewScale)
                    strokeWidth(1*viewScale)
                    stroke(self.incomingColor[0], self.incomingColor[1], self.incomingColor[2], self.incomingColor[3])
                    oval(bpt.x-self._rin, bpt.y-self._rin, 2*self._rin, 2*self._rin)


                    stroke(self.outgoingColor[0], self.outgoingColor[1], self.outgoingColor[2], self.outgoingColor[3])
                    oval(bpt.x-self._rout, bpt.y-self._rout, 2*self._rout, 2*self._rout)
                    
                    strokeWidth(10*viewScale)
                    stroke(self.incomingColor[0], self.incomingColor[1], self.incomingColor[2], 0.25)
                    line((apt.x,apt.y),(bpt.x,bpt.y))
                    stroke(self.outgoingColor[0], self.outgoingColor[1], self.outgoingColor[2], 0.25)
                    line((cpt.x,cpt.y),(bpt.x,bpt.y))

    
    def mouseDown(self, point, event):
        pass

    def mouseUp(self, xx):
        self._rin = None
        self._rout = None
    
    def keyDown(self, event):
        letter = event.characters()
        mods = self.getModifiers()
        cmd = mods['commandDown'] > 0
        option = mods['optionDown'] > 0
            

if __name__ == "__main__":
    from mojo.events import installTool
    p = RatioTool()
    installTool(p)
