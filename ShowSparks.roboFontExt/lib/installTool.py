# -*- coding: utf-8 -*-


#install the sparks tool
try:
    from mojo.events import installTool
    from showSparksTool import ShowSparksTool
    p = ShowSparksTool()
    installTool(p)
except:
    print("Could not install ShowSparksTool.")

