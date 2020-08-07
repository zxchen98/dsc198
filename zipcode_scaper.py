import requests
from datetime import date, timedelta, datetime
import tabula
import pandas as pd
import re

#For testing
import os
from fpdf import FPDF
import os.path



#Download PDF locally
def download_pdf(file,filename,URL):
    print(file)
    myfile = requests.get(URL)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 13.0)
    pdf.cell(ln=0, h=5.0, align='L', w=0, border=0)
    pdf.output(file, 'F')
    
    open(filename,'wb').write(myfile.content)

   
#Read pdf file and
def convert_pdf(filename, download_date):
    columns = ['zipcode', 'confirmed_cases']
    
    #Loading data from pdf
    pdf_list = tabula.read_pdf(filename, pages = "all", multiple_tables = True)[0]



    #Splitting data into proper format 
    pdf_df = pd.DataFrame(pdf_list)
    pdf_df1 = pd.DataFrame(pdf_df.iloc[:,0:2])
    pdf_df1.columns = columns
    pdf_df2 = pd.DataFrame(pdf_df.iloc[:,2:4])
    pdf_df2.columns = columns
    pdf_df = pd.concat([pdf_df1,pdf_df2])
    pdf_df.reset_index(drop=True, inplace=True)
    
    #Determine date through time. This is the date that the sum goes until found 
    #in the PDF
    text = pdf_df.loc[1,"zipcode"]
    print(text)
    match = re.search(r'\d{1}/\d{1}/\d{4}', text)
    if match == None:    
        match = re.search(r'\d{1}/\d{2}/\d{4}', text)
    elif match == None:
        match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        
 #   date_through = datetime.strptime(match.group(), "%m/%d/%Y")
    date_through = str(date.today() - timedelta(days=1)) 
    pdf_df.drop(0,axis=0,inplace=True)
        
    #Add updated and date through columns
    pdf_df.insert(0,'updated', date.today())
    pdf_df.insert(1,'date through', date_through)
    
    #Find names Zip Code and remove
    zipcode_index = pdf_df[pdf_df["zipcode"] == "Zip Code"].index
    for zi in zipcode_index:
        pdf_df.drop(zi, axis=0, inplace=True)
    
    #Find total and append to bottom of dataframe
    total_line = pdf_df[pdf_df["zipcode"] == "TOTAL"]
    pdf_df.drop(total_line.index,inplace=True)
    pdf_df = pdf_df.append(total_line)
    
    #drop nan values
    pdf_df.dropna(inplace=True)

    return pdf_df


if __name__=="__main__":
    
 #   yesterdate = str(date.today() - timedelta(days=1))
    yesterdate = '2020-04-06'
    file = "sd_daily_update_zipcode_" + yesterdate + ".pdf"
 #   filepath = "sd_daily_zipcode_pdfs/"
    filename = file
    URL = "https://www.sandiegocounty.gov/content/dam/sdc/hhsa/programs/" +\
        "phs/Epidemiology/COVID-19%20Summary%20of%20Cases%20by%20Zip%20Code.pdf"

    #Downloading and converting data
    download_pdf(file, filename,URL)
   
    df = convert_pdf(filename, yesterdate)
    
    #Writing data
    csv_file = 'sd_daily_zipcode_summary_test.csv'
    
    
    csv_mode = 'a'
    csv_header = False
    if(not os.path.exists(csv_file)):
        csv_mode = 'w'
        csv_header = True
        
    
    df.to_csv(csv_file,mode=csv_mode,header=csv_header,\
              index=False)
    


