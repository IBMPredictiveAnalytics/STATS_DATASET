#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2020
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/


__author__  =  'IBM SPSS, JKP'
__version__ =  '1.0.2'
version = __version__

# history
# 04-jun-2014 Original version
# 05-jun-2014 Adjust for different Datasets table structure before V22

helptext = """
Manage datasets.

STATS DATASET NAME=dsname ACTIVATE=existing dsname
WINDOW=ASIS* or FRONT
CLOSE = list of dsnames or ALL
KEEP = list of dsnames
DISPLAY = NO* or YES.

Examples.
STATS DATASET CLOSE=ALL KEEP=w.
This closes all datasets except the one named w.

STATS DATASET NAME=a ACTIVATE=b CLOSE=c d.
assigns the name a to the active dataset; then
activates dataset b, and finally closes
datasets c and d.
    
All keywords are optional, but if none are given, the command
will do nothing.  * indicates the default choice for keyword
values.

All of the functionality of STATS DATASET maps to built-in 
DATASET commands, but it provides some conveniences and can 
handle the "almost all" case for closing datasets.

Note that closing a dataset does not necessarily remove
it from the session.  The active dataset does not have
to have a name.  However, an unnamed active dataset
would be removed from the session if another (named)
dataset is activated.

NAME specifies a dataset name to assign to the active dataset.

ACTIVATE specifies a dataset to be activated.
WINDOW=ASIS or FRONT specifies the window behavior for ACTIVATE.

CLOSE specifies datasets to be closed.  It can be a list of 
dataset names or ALL.

KEEP specifies datasets not to close whether or not
they are listed or implied in CLOSE.  Specifying KEEP without
CLOSE means that all datasets except the KEEP list will be
closed.

Any names specified that do not exist are silently ignored,
but errors in NAME or ACTIVATE stop the command.

DISPLAY specifies whether or not to run a DATASET DISPLAY
command.

The steps are executed in the order that these keywords are
listed.  That is, first NAME; then ACTIVATE/WINDOW; 
then CLOSE/KEEP; finally DISPLAY.

/HELP displays this help and does nothing else."""


from extension import Template, Syntax, processcmd
import spss
import random


def dodataset(name=None, activate=None, window="asis", close=None, 
    keep="", display=False):
    # debugging
    # makes debug apply only to the current thread
    #try:
        #import wingdbstub
        #if wingdbstub.debugger != None:
            #import time
            #wingdbstub.debugger.StopDebug()
            #time.sleep(1)
            #wingdbstub.debugger.StartDebug()
        #import thread
        #wingdbstub.debugger.SetDebugThreads({thread.get_ident(): 1}, default_policy=0)
        ## for V19 use
        ###    ###SpssClient._heartBeat(False)
    #except:
        #pass

    if name:
        spss.Submit("DATASET NAME %s." % name)
    
    if activate:
        # stops with error if no such dataset
        spss.Submit("DATASET ACTIVATE %s WINDOW=%s" % (activate, window))

    # CLOSE processing
    if keep and not close:
        close = "all"
    if close:
        close = set([ds.lower() for ds in close])
        keep = set([ds.lower() for ds in keep])
        allds = getallds()
        if "all" in close:
            if len(close) > 1:
                raise ValueError(_("""ALL cannot be used with other names in the close list"""))
            close = allds
        close = close.intersection(allds) # remove undefined names
        for d in close - keep:
            spss.Submit("DATASET CLOSE %s" % d)
            
    if display:
        spss.Submit("DATASET DISPLAY") 


def getallds():
    # return set of all datasets with names in lower case
    
    randomname = "D" + str(random.uniform(.1,1))
    spss.Submit("""oms /destination viewer=no xmlworkspace="%(randomname)s" format=oxml
    /tag = "%(randomname)s".
    dataset display.
    omsend tag="%(randomname)s".""" % locals())
    # take care to get only the first-column attributes
    if spss.GetDefaultPlugInVersion() >= "spss220":
        existingdsnames = set([s.lower() for s in spss.EvaluateXPath(randomname, "/outputTree", 
        """//pivotTable[@subType="Datasets"]//dimension/category/dimension/category[1]/cell/@text""")])
    else:
        existingdsnames = set([s.lower() for s in spss.EvaluateXPath(randomname, "/outputTree", 
        """//pivotTable[@subType="Datasets"]/dimension/category/cell/@text""")])
    spss.DeleteXPathHandle(randomname)
    # The unnamed dataset would be listed as (unnamed) or (translation of unnamed)
    for item in existingdsnames:
        if item.startswith("("):
            existingdsnames.discard(item)
            break
    return(existingdsnames)
    
def Run(args):
    """Execute the STATS DATASET extension command"""

    args = args[list(args.keys())[0]]

    oobj = Syntax([
        Template("NAME", subc="", ktype="varname", var="name"),
        Template("ACTIVATE", subc="", ktype="varname", var="activate"),
        Template("WINDOW", subc="", ktype="str", var="window",
            vallist=["asis", "front"]),
        Template("CLOSE", subc="", ktype="varname", var="close", islist=True),
        Template("KEEP", subc="", ktype="varname", var="keep", islist=True),
        Template("DISPLAY", subc="", ktype="bool", var="display"),
        
        Template("HELP", subc="", ktype="bool")])
    
    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
    # A HELP subcommand overrides all else
    if "HELP" in args:
        #print helptext
        helper()
    else:
        processcmd(oobj, args, dodataset)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))
try:    #override
    from extension import helper
except:
    pass

#class NonProcPivotTable(object):
    #"""Accumulate an object that can be turned into a basic pivot table once a procedure state can be established"""
    
    #def __init__(self, omssubtype, outlinetitle="", tabletitle="", caption="", rowdim="", coldim="", columnlabels=[],
                 #procname="Messages"):
        #"""omssubtype is the OMS table subtype.
        #caption is the table caption.
        #tabletitle is the table title.
        #columnlabels is a sequence of column labels.
        #If columnlabels is empty, this is treated as a one-column table, and the rowlabels are used as the values with
        #the label column hidden
        
        #procname is the procedure name.  It must not be translated."""
        
        #attributesFromDict(locals())
        #self.rowlabels = []
        #self.columnvalues = []
        #self.rowcount = 0

    #def addrow(self, rowlabel=None, cvalues=None):
        #"""Append a row labelled rowlabel to the table and set value(s) from cvalues.
        
        #rowlabel is a label for the stub.
        #cvalues is a sequence of values with the same number of values are there are columns in the table."""

        #if cvalues is None:
            #cvalues = []
        #self.rowcount += 1
        #if rowlabel is None:
            #self.rowlabels.append(str(self.rowcount))
        #else:
            #self.rowlabels.append(rowlabel)
        #self.columnvalues.extend(cvalues)
        
    #def generate(self):
        #"""Produce the table assuming that a procedure state is now in effect if it has any rows."""
        
        #privateproc = False
        #if self.rowcount > 0:
            #try:
                #table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            #except:
                #spss.StartProcedure(self.procname)
                #privateproc = True
                #table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            #if self.caption:
                #table.Caption(self.caption)
            #if self.columnlabels != []:
                #table.SimplePivotTable(self.rowdim, self.rowlabels, self.coldim, self.columnlabels, self.columnvalues)
            #else:
                #table.Append(spss.Dimension.Place.row,"rowdim",hideName=True,hideLabels=True)
                #table.Append(spss.Dimension.Place.column,"coldim",hideName=True,hideLabels=True)
                #colcat = spss.CellText.String("Message")
                #for r in self.rowlabels:
                    #cellr = spss.CellText.String(r)
                    #table[(cellr, colcat)] = cellr
            #if privateproc:
                #spss.EndProcedure()
