import requests
from datetime import date, timedelta
import tabula
import pandas as pd
import re
import json

#For testing
import os
from fpdf import FPDF
import os.path

#Download PDF locally
def download_pdf(file,filename,URL):
    myfile = requests.get(URL)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 13.0)
    pdf.cell(ln=0, h=5.0, align='L', w=0, border=0)
    pdf.output(file, 'F')
    
    open(filename,'wb').write(myfile.content)

#Read pdf file and
def convert_pdf(filename,yesterdate):
    pdf_df = tabula.read_pdf(filename, pages = "all", multiple_tables = True)
    #pdf_list = pdf_df.values.tolist()
    pdf_list = pdf_df[0].values.tolist()

    #Extract data
    df = pd.DataFrame(columns=["date","city","confirmed_cases","percent_of_total(%)"])
    json_data = {}
    json_data[yesterdate] = []
    
    #Determine where data index begins and ends
    start_index = 0
    end_index = 0

    for i, plist in enumerate(pdf_list):        
        if('incorporated city' in plist[0].lower()):
            start_index = i + 1
        elif('total san diego' in plist[0].lower()):
            end_index = i + 1
            break
    
    #Writing data dataframe and json
    for line in pdf_list[start_index:end_index]:
        if(len(line) == 1):
            tmp_list = re.split('(\d+)',line[0].lower())
            if('incorporated' not in tmp_list[0]):
                df = df.append({"date":yesterdate,\
                                    "city":tmp_list[0],\
                                    "confirmed_cases":tmp_list[1],\
                                    "percent_of_total(%)":"".join(tmp_list[3:-1])},\
                                     ignore_index = True)
                
                json_data[yesterdate].append({"city":tmp_list[0],\
                         "confirmed_cases":tmp_list[1],\
                         "percent_of_total(%)":"".join(tmp_list[3:-1])})
        else:
            tmp_list = line
            if('incorporated' not in tmp_list[0]):
                df = df.append({"date":yesterdate,\
                                    "city":tmp_list[0],\
                                    "confirmed_cases":tmp_list[1].split(" ")[0],\
                                    "percent_of_total(%)":tmp_list[1].split(" ")[1]},\
                                     ignore_index = True)
                
                json_data[yesterdate].append({"city":tmp_list[0],\
                         "confirmed_cases":tmp_list[1],\
                         "percent_of_total(%)":"".join(tmp_list[3:-1])})
            
    
    return df, json_data


if __name__=="__main__":
    
    yesterdate = str(date.today() - timedelta(days=1))
    #yesterdate = '2020-04-09'
    file = "sd_daily_update_city_" + yesterdate + ".pdf"
    filepath = "sd_daily_city_pdfs/"
    filename = file
    URL = "https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/" + \
    "phs/Epidemiology/COVID-19%20Daily%20Update_City%20of%20Residence.pdf"

    #Downloading and converting data
    download_pdf(file,filename,URL)
   
    df, json_data = convert_pdf(filename, yesterdate)
    
    #Writing data
    csv_file = 'sd_daily_city_summary_test.csv'
    json_file = 'sd_daily_city_summary_test.json'
    
    csv_mode = 'a'
    csv_header = False
    if(not os.path.exists(csv_file)):
        csv_mode = 'w'
        csv_header = True
        
    
    df.to_csv(csv_file,mode=csv_mode,header=csv_header,\
              index=False)
    with open(json_file,'a') as file:
        json.dump(json_data,file)
