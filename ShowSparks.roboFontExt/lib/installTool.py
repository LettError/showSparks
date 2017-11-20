# -*- coding: utf-8 -*-


#install the sparks tool
try:
    from mojo.events import installTool
    from showSparksTool import ShowSparksTool
    from ratioTool import RatioTool

    p = ShowSparksTool()
    installTool(p)
    p = RatioTool()
    installTool(p)

except:
    print("Could not install ShowSparksTool.")

