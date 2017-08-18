###pricker-v.0.1.36 author A.SOLBIATI 07/07/17###
import os
import pandas
import datetime
from pandas_datareader import data as web
from bs4 import BeautifulSoup
import logging
logging.basicConfig(filename='pricker-errors.log', level=logging.ERROR)

def read_file(FNAME, FIXED_LINES):
    'read input file skipping the first FIXED_LINES lines'
    with open(FNAME) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines] 
    lines = lines[FIXED_LINES:]
    
    return lines

CONFIG = os.path.abspath("config.txt")
config_lines = read_file((CONFIG),10)

#FNAME: path for input file (bloomberg-request-software format)
READFROMCONFIG = int(config_lines[0])
if (READFROMCONFIG==1):
    #FNAME = config_lines[1][config_lines[0].index(' ')+1:]
    FNAME = config_lines[1]
    FIXED_LINES = config_lines[2]
    FILENAME_INPUT= config_lines[3]
    FILENAME_OUTPUT= config_lines[4]
    MARKET = config_lines[5]
    
else:
    FNAME = os.path.abspath("Prezzi"+datetime.datetime.today().strftime('%d%m%y')+".out"+datetime.datetime.today().strftime('%Y%m%d'))
    #FIXED_LINES:  number of fixed lines to be skipped in input file
    FIXED_LINES = 30
    #MARKET: market to run the pricker on {'EQUITITES US', 'EQUITIES IM'}
    MARKET = "EQUITIES US"
    FILENAME_INPUT= os.path.abspath("www/template.html")
    FILENAME_OUTPUT= os.path.abspath("www/report.html")

print(CONFIG, READFROMCONFIG, FNAME, FIXED_LINES, FILENAME_INPUT, FILENAME_OUTPUT, MARKET)

def checkfor(line, strs):
    #return 1 if there are all strs[i] in line
    _bool = True
    for _str in strs:
        if(line.find(_str)==-1):
            _bool = False
    return _bool

def equity_market(line):
    return line[line.index(' ')+1:line.index(' ')+3]

def equity_name(line):
    return line[:line.index(' ')]

def equity_vals(line):
    vec = []
    for i in range(4,12):
        vec.append(line.split('|')[i])
    return vec

class Equity():
    
    def __init__(self, line):
        self.market=equity_market(line)
        self.name=equity_name(line)
        self.vals=equity_vals(line)
        if(self.vals[5]!='N.A.' and self.vals[5]!=""):
            self.close=float(self.vals[5])
        else:
            self.close=0
        self.curr=equity_vals(line)[7]
    
    def summary(self):
        print '\nEquity summary'
        print '- Name: ',self.name,' Market: ',self.market,' Close: ',self.close,' Curr: ',self.curr
        
    

def parse_equities(FNAME, FIXED_LINES):
	#parse equities from the input file populating the Equity object arrays
    
    lines = read_file(FNAME, FIXED_LINES)
    
    equities_US = []
    equities_IM = []
    
    for line in lines:
        if(checkfor(line,'Equity') and len(line.split(" "))<4):
            try:
                equity = Equity(line)
                if(equity.market=='US'):
                    equities_US.append(equity)
                if(equity.market=='IM'):
                    equities_IM.append(equity)
            except:
                logging.exception(datetime.datetime.now())
                
    
    return equities_US, equities_IM

def pricker_equities(equities, market="US", source="google"):
    #cross-validate the input prices with source prices using the Equity object arrays
    
    anomalies= []
    comparisons=0
    dataset=len(equities)
    
    #loop in the equities objects
    for equity in equities:
        
        try:
            #compare1: dowload data from source not monday
            if(datetime.datetime.today().weekday()!=0): 
                compare1 = float(web.DataReader(equity.name, source, datetime.datetime.today() - datetime.timedelta(days=1),datetime.datetime.today()).Close)
            else:
                compare1 = float(web.DataReader(equity.name, source, datetime.datetime.today() - datetime.timedelta(days=3),datetime.datetime.today()).Close)
             
            
            #compare2: from the input file
            compare2 = equity.close
            
            if(compare1!=compare2):
                anomaly = equity.name,equity.close,compare1
                anomalies.append(anomaly)
                print len(anomalies),'FOUND ANOMALY (name,bloomberg,source)',anomaly
                
            else:
                print " | dowloaded [",compare1,"] from ",source,", regular [",compare2,"] on: ",equity.name
           
            comparisons=comparisons+1
            
        except Exception as e: print(e)
            
    print '\nANOMALIES:\n'
    for anomaly in anomalies:
        print anomaly
    print 'COMPARISONS:', comparisons,' (', dataset-comparisons, ' not found from source )'
    
    return anomalies, comparisons, dataset

def update_html(anomalies, comparisons, dataset, FILENAME_INPUT=os.path.abspath("www/template.html"), FILENAME_OUTPUT=os.path.abspath("www/report.html")):
    
    with open(FILENAME_INPUT) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    
    for anomaly in anomalies:
        new_tag = soup.new_tag('li')
        
        new_tag = soup.new_tag('li')

        a = soup.new_tag('a')
        a_content = anomaly[0]+' '
        a.string=unicode(a_content)
        a['class']="small_a"

        p = soup.new_tag('p')
        p_content = 'Bloomberg:'+str(anomaly[1])+' Google: '+str(anomaly[2])
        p['style']="font-size:9px"
        p.string=unicode(p_content)
        a.insert(1,p)

        new_tag.append(a)
        
        soup.body.find('ul').append(new_tag)
    
    soup.find_all('a')[0].string = str(datetime.datetime.today())[:16]+" CHECK completed"
    
    soup.find_all('span')[0].string = "Regular: "+str(comparisons)
    soup.find_all('span')[1].string = "Anomalies: "+str(len(anomalies))
    soup.find_all('a')[1].string = "Instruments found from the source "+str(comparisons)+"/"+str(dataset)
    
    with open(FILENAME_OUTPUT, "wb") as f_output:
        f_output.write(soup.prettify("utf-8"))   

try:
    equities_US, equities_IM = parse_equities(FNAME,int(FIXED_LINES))
    
    if(MARKET=='EQUITIES US'):        
        anomalies, comparisons, dataset = pricker_equities(equities_US)
    if(MARKET=='EQUITIES IM'):
        print '..not implemented yet'

    update_html(anomalies,comparisons,dataset,FILENAME_INPUT,FILENAME_OUTPUT)
    
except:
    logging.exception(datetime.datetime.now())