import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator
from datetime import timedelta
import numpy as np
from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import sys
import os
from PyPDF2 import PdfWriter

def extract_properties(filename):
    properties = {}
    string = ""
    with open(filename, 'r') as file:
        for row in file:
            string+=row
            row = row.strip()  # Rimuove spazi bianchi e a capo dalla riga
            if '=' in row:
                property, value = row.split('=', 1)
                properties[property] = value
    return properties, string

def divide_line(line, dim): # divide a string in in more lines of max 'dim' characters each
    lines = [line[i:i + dim] for i in range(0, len(line), dim)]
    return lines

def phrases_splitter(line, dim):    # Used to divide info string without cut the words
    words = line.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > dim:
            lines.append(current_line.strip())
            current_line = ""
        current_line += word + " "
    lines.append(current_line.strip())
    return lines


def divide_string(string, num_lines, line_dim): # divide a string in more strings of max 'num_lines' lines each. Each line has max 'line_dim' characters
    blocks = []
    lines = string.splitlines()
    new_lines_list=[]
    for line in lines:
        if len(line)>line_dim:
            line_split=divide_line(line,line_dim)
            new_lines_list.extend(line_split)
        else:
            new_lines_list.append(line)
    for i in range(0, len(new_lines_list), num_lines):
        block = '\n'.join(new_lines_list[i:i + num_lines])
        blocks.append(block)
    return blocks

def retreive_time_series_from_prometheus(prometheus_connect, metric_name, start_time, end_time, container):
    start_time = start_time
    end_time = end_time
    chunk_size = timedelta(seconds=30)
    metric_data = prometheus_connect.get_metric_range_data(
        metric_name=metric_name,
        label_config={'name': container},
        start_time=start_time,
        end_time=end_time,
        chunk_size=chunk_size,
    )
    metric_df = MetricRangeDataFrame(metric_data)
    time_series = metric_df["value"]
    return time_series

def promql_query(prometheus_connect, query, start_time, end_time):
    metric_data = prometheus_connect.custom_query_range(query=query,start_time=start_time,end_time=end_time,step=1.0)
    metric_df = MetricRangeDataFrame(metric_data)
    time_series = metric_df["value"]
    return time_series

def metric_plot(title, xlabel, ylabel, *args):
    plot_beautify_params = (("-", "gray"), ("-", "red"), ("-", "blue"),
                            ("-", "orange"), ("-", "lightblue"), ("-", "green"), ("-", "yellow"), ("-", "black"), ("-", "magenta"), ("-", "cyan"))
    plt.figure()
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xticks(rotation=45, ha='right')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    plt.title(testName+": "+title)
    plt.grid(True)
    plt.tight_layout()
    i = 0
    for time_series_args in args:
        plt.plot(time_series_args[0], plot_beautify_params[i][0],
                 color=plot_beautify_params[i][1], label=time_series_args[1])
        i += 1
        i %= 10
    # La tupla plot_beautify_params contiene 5 stili per il plotting della serie. Quindi, una eventuale sesta serie nel plot avrebbe lo stesso stile della prima e così via.
    legend=plt.legend(loc='upper left', bbox_to_anchor=(0,-0.4))
    plt.savefig(testpath+"/"+title+"_"+testName+".png",bbox_extra_artists=(legend,), bbox_inches='tight')
    pdf_file.savefig(bbox_extra_artists=(legend,), bbox_inches='tight')

testpath=sys.argv[1] # folder in which results_<testName>.csv and properties_<testName>.txt are stored, example: path/to/test1, test1 is the folder with our files and it is the <testName>
pdfpath=sys.argv[2] # path+filename of the .pdf that we want to save, example: path/to/myPdf --> it will create the file myPdf.pdf in folder path/to/
append=sys.argv[3]
info=sys.argv[4] # general informations to add in pdf (like container resources)
testName=os.path.basename(testpath)
containers_list=[]

with open("containers_list.txt") as file:
    for line in file:
        if line.strip()!="":
            containers_list.append(line.strip())

df = pd.read_csv(testpath+"/results_"+testName+".csv")
df = df.reset_index()
df = df.rename(columns={'index': 'sample'})
df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='ms')
df['endTimeStamp'] = pd.to_datetime(df['timeStamp'], unit='ms') + pd.to_timedelta(df['elapsed'],unit='ms')
max_endTimeStamp = df.loc[df['endTimeStamp'].idxmax()]['endTimeStamp']
min_startTimeStamp = df.loc[df['timeStamp'].idxmin()]['timeStamp']
elapsedTotal=max_endTimeStamp - df.loc[0]['timeStamp']

properties,text_properties=extract_properties(testpath+"/properties_"+testName+".txt")

newPdf=False
if not os.path.exists(pdfpath):
    if os.path.dirname(pdfpath)!="" and not os.path.exists(os.path.dirname(pdfpath)):
        os.makedirs(os.path.dirname(pdfpath))
    pdf_file = PdfPages(pdfpath)
    newPdf=True
elif append=="true":
    pdf_folder = os.path.dirname(pdfpath)
    if pdf_folder!="":
        pdf_folder+="/"
    pdf_file = PdfPages(pdf_folder+"temp_pdf.pdf")
else:
    pdf_file=PdfPages(pdfpath)


text_properties_divided=divide_string(text_properties,20,60)
firstPage=True
for block in text_properties_divided:
    page = plt.figure(figsize=(10,7))
    plt.clf()
    if firstPage:
        if info != "":
            infoList = phrases_splitter(str(info), 80)
            page.text(0.1,0.96, "General Informations: "+infoList[0], size=12, ha="left", va="top")
            if len(infoList) > 1:
                page.text(0.12,0.93, infoList[1], size=12, ha="left", va="top") # only the second line is considered (to respect the format page)
        page.text(0.1,0.87, "Elapsed time: "+str(elapsedTotal), size=20, ha="left")
        page.text(0.1,0.8, "Properties_"+testName+":", size=20, ha="left")
        page.text(0.1,0.75, block, size=16, ha="left", va="top")
    else:
        page.text(0.1,0.9, block, size=16, ha="left", va="top")
    pdf_file.savefig()
    plt.close()
    firstPage=False

plt.figure()
plt.scatter(df['timeStamp'], df['Latency'], c=df['responseMessage'].map(lambda x: 'blue' if x == 'OK' else 'red'), alpha=0.7, s=15)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
plt.title(testName+': Latency vs Timestamp')
plt.xlabel('Timestamp (hh:mm:ss)')
plt.ylabel('Latency (ms)')
plt.xticks(rotation=45, ha='right')
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
plt.tight_layout()
plt.grid(True)
plt.savefig(testpath+"/latency_timestamp_"+testName+".png")

pdf_file.savefig()
plt.clf()


plt.figure()
plt.scatter(df['sample'], df['Latency'], c=df['responseMessage'].map(lambda x: 'blue' if x == 'OK' else 'red'), alpha=0.7, s=15)
plt.title(testName+': Latency vs Sample')
plt.xlabel('Sample')
plt.ylabel('Latency (ms)')
plt.xticks(rotation=45, ha='right')
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
plt.tight_layout()
plt.grid(True)
plt.savefig(testpath+"/latency_sample_"+testName+".png")

pdf_file.savefig()
plt.clf()

start_time=min_startTimeStamp-pd.to_timedelta(300000,unit='ms')
end_time=max_endTimeStamp+pd.to_timedelta(300000,unit='ms') if parse_datetime("now")>(max_endTimeStamp+pd.to_timedelta(300000,unit='ms')) else parse_datetime("now")
prom = PrometheusConnect(url="http://"+os.getenv("PROMETHEUS_HOST") +
                             ":"+os.getenv("PROMETHEUS_PORT"), disable_ssl=True)
time_series_list=[(retreive_time_series_from_prometheus(prom,"container_memory_usage_bytes",start_time,end_time,container), container) for container in containers_list]
if len(time_series_list)>0:
    metric_plot("container_memory_usage_bytes","time","bytes", *time_series_list)
    plt.clf()

#"100 * avg(irate(container_cpu_usage_seconds_total{name=\""+container+"\"}[1m])) / count(count without(cpu)(container_cpu_usage_seconds_total{name=\""+container+"\"}))"
#"avg(100*(rate(container_cpu_usage_seconds_total{name=\""+container+"\"}[5m]) / on(node) group_left() machine_cpu_cores))"
#"100*avg(rate(container_cpu_usage_seconds_total{name="scm-hasura-db"}[20s]))"
time_series_list1=[(promql_query(prom,"100*avg(rate(container_cpu_usage_seconds_total{name=\""+container+"\"}[20s]))",start_time,end_time), container) for container in containers_list]
if len(time_series_list1)>0:
    metric_plot("container_cpu_core_avg_usage_increase[20s]","time","%", *time_series_list1)
    plt.clf()
plt.close()
pdf_file.close()

if newPdf==False and append=="true":
    merger = PdfWriter()
    merger.append(pdfpath)
    pdf_folder = os.path.dirname(pdfpath)
    if pdf_folder!="":
        pdf_folder+="/"
    merger.append(pdf_folder+"temp_pdf.pdf")
    merger.write(pdfpath)
    merger.close()
    os.remove(pdf_folder+"temp_pdf.pdf")

