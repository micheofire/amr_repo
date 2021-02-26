import base64
import re
import pandas as pd
import numpy as np
from calendar import Calendar
import streamlit as st
import MyHelper as mh
import my_helper as hp
import datetime as dt
import warnings
warnings.filterwarnings("ignore")

#Application welcome address
# st.title("WELCOME TO THE DEMO VERSION OF OUR MMR REPORT GENERATOR")

#Import dataset from your PC
uploaded_files = st.sidebar.file_uploader("Upload file", type=["csv","xls","xlsx"], accept_multiple_files=False)
if uploaded_files:
    data = pd.read_excel(uploaded_files)

    #Import a sample mmr data
    # data = pd.read_excel("Daily_report_between_2020-11-09_and_2020-12-09_1608541610.xls")

    #Preprocess the mmr data
    data = mh.PreprocessData(data)

    comb_data = pd.DataFrame(columns = data.columns)
    # for media in data["Media Type"].unique():

    #---------->GENERATING LISTENERSHIP AND IMPRESSION FOR RADIO<-----------
    #SELECTING MEDIA TYPE
    data = data.copy()[data["Media Type"] == "Radio"]

    #GENERATING WEEKLY LISTENERS
    #ORIGINAL CODE
    for brand in data["Brand"].unique():
        brand_clean = re.sub(r'[^\w]', ' ', brand)
        writer = pd.ExcelWriter(f'NEW EXPORT/{brand_clean}.xlsx', engine='xlsxwriter')
        df = data.copy()[data["Brand"] == brand]
        for week in df["Week"].unique():
            week_df = mh.WeeklyListenersData(df, week)
            try:
                listeners = mh.GenerateListeners(week_df, ["Province", "Districts", "AREA TYPE", "Gender", "LSM GROUP", "Age Range"])
                listeners_final = mh.RestructureListeners(["Province", "Districts", "AREA TYPE", "Gender", "LSM GROUP", "Age Range"], df, listeners.copy())
                listeners_final.to_excel(writer, sheet_name=f"{week}")
            except:
                listeners_final = pd.DataFrame()
                for item in ["Province", "Districts", "AREA TYPE", "Gender", "LSM GROUP", "Age Range"]:
                    listeners = pd.DataFrame(index=week_df["Station"].unique(), columns=week_df[item].unique()).fillna(0)
                    listeners[f"{item.upper()} TOTAL"] = 0
                    listeners_final = pd.concat([listeners_final, listeners], axis=1)
                listeners_final.to_excel(writer, sheet_name=f"{week}")
        writer.save()

    #IMPRESSION
    impression = mh.Impression(data, ["Province"])

    #FINAL LISTENERSHIP
    final_listeners = pd.DataFrame()
    for brand in impression["Brand"].unique():
        brand_data = impression[impression["Brand"] == brand]
        for week in sorted(brand_data["Week"].unique()):
            try:
                listeners_df = pd.read_excel(f"NEW EXPORT/{brand_clean}.xlsx", sheet_name = week, index_col=0)
                brand_week = brand_data[brand_data["Week"] == week]
                for station in sorted(brand_week["Station"].unique()):
                    brand_station = brand_week[brand_week["Station"] == station]
                    try:
                        brand_station["Listeners"] = int(listeners_df.loc[station]["PROVINCE TOTAL"]/brand_station.shape[0])
                    except:
                        brand_station["Listeners"] = 0
                    final_listeners = pd.concat([final_listeners, brand_station])
            except:
                brand_station = pd.DataFrame(columns=["Listeners"])
                brand_station["Listeners"] = 0
                final_listeners = pd.concat([final_listeners, brand_station])
    final_listeners["Listeners"] = final_listeners[["IMPRESSION", "Listeners"]].apply(lambda x: 0 if x["IMPRESSION"] == 0 else x["Listeners"], axis=1)
    final_listeners["Listeners"] = final_listeners[["IMPRESSION", "Listeners"]].apply(lambda x: int(x["Listeners"]-x["IMPRESSION"])/(x["IMPRESSION"]-x["Listeners"]) if x["IMPRESSION"] < x["Listeners"] else x["Listeners"],axis=1)
    final_listeners["Listeners"] = final_listeners["Listeners"].apply(lambda x: x*(-1) if x<0 else x)
    final_listeners= final_listeners.reset_index(0, True)





    data = final_listeners.copy()
    data["Count"] = np.ones(data.shape[0])
    for col in  ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]:
        data[col] = data[col].astype(int)
    # comb_data = pd.concat([data, comb_data], 1)
        
    # data = comb_data.copy()

    #Get columns an thir data types
    column_dtype = dict(data.dtypes)

    #For integers and float
    int_columns = []
    for item in column_dtype.keys():
        if (column_dtype[item] == int) | (column_dtype[item] == float):
            int_columns.append(item)
    # int_columns = int_columns.sort()

    #For objects
    obj_columns = []
    for item in column_dtype.keys():
        if column_dtype[item] == object:
            obj_columns.append(item)
    # obj_columns = obj_columns.sort()



    sub_menu = ["Share of Voice Analysis", "Advertising Expenditure Analysis", 
                "Media Type Analysis", "Company, Player & Brand Analysis", 
                "Campaign Analysis", "Spot ID Analysis", 
                "Sub Brand Analysis", "Advert Type Analysis", 
                "Industry Analysis", "Media Exposure Analysis"]
    defaults = {
        "Share of Voice Analysis" : [["Brand", "Media Type"], ["Week"], ["Duration", "Gross", "Count"]],
        "Advertising Expenditure Analysis" : [["Brand", "Media Type"], [], ["Gross", "Count"]],
        "Media Type Analysis" : [["Media Type", "Station"], [], ["Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Company, Player & Brand Analysis" : [["Brand"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Campaign Analysis" : [["Media Type"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Spot ID Analysis" : [["Spot ID"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Sub Brand Analysis" : [["SubBrand"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Advert Type Analysis" : [["Media Type"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Industry Analysis" : [["Brand"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]],
        "Media Exposure Analysis" : [["Media Type"], [], ["Count","Gross", "Duration", "IMPRESSION", "Listeners"]]
    }

    analysis = st.sidebar.selectbox("Select analysis", sub_menu)


    #ANALYSIS

    #Get the default values for each analysis
    my_default = defaults[analysis]
    value_default = my_default[2]
    row_default = my_default[0]
    column_default = my_default[1]


    #Print out analysis type
    st.title(analysis.upper())


    ###Pivot table input   


    #Values, Rows and Columns
    iValues = st.sidebar.multiselect("SELECT VALUE", sorted(int_columns), default = value_default)
    iRows = st.sidebar.multiselect("SELECT SEARCH CRITERIA", sorted(obj_columns), default=row_default)
    iColumns = st.sidebar.selectbox("SELECT COLUMN VARIABLES", sorted(obj_columns, reverse=True))


    #Get the aggretion function for each value
    aggf = {}
    for item in iValues:
        if item == "Count":
            aggf.update({"Count":"count"})
        else:
            aggf.update({str(item):"sum"})
            
            
    #USERS SHOULD SELECT OTHER OPTIONS
    iFilter = st.selectbox("FILTER BY WHAT VARIABLE", sorted(obj_columns))
    filterV = st.multiselect("BY WHAT?", sorted(data[iFilter].unique()))


    #Apply the filter to generate new dataframe
    filtered_data = pd.DataFrame([])
    for value in filterV:
        filtered_data = pd.concat([filtered_data, data[data[iFilter] == value]])

        
    #Pivot table
    try:
        if len(filterV) == 0:
            st.title("FULL DATA")
            piv_table = pd.pivot_table(data, values=iValues, index=iRows, margins=True, margins_name = "GRAND TOTAL",
                                        columns=iColumns, fill_value=0, dropna=True, aggfunc = aggf)
            piv_table = piv_table.astype(int)

            #Print table to screen
            piv_html = piv_table.to_html()
            st.markdown(piv_html, unsafe_allow_html=True)
            st.markdown(hp.get_table_download_link(piv_table), unsafe_allow_html=True)
            
            if st.sidebar.button("Row Percentage", key="k1"):
                piv = hp.mmr_row(data, iValues, iColumns, iRows)
                st.table(piv)
                st.markdown(hp.get_table_download_link(piv), unsafe_allow_html=True)

            if st.sidebar.button("Column Percentage", key="k2"):
                piv = hp.mmr_col(data, iValues, iColumns,iRows)
                st.table(piv)
                st.markdown(hp.get_table_download_link(piv), unsafe_allow_html=True)

        else: 
            st.title("Filter by {}".format(iFilter))
            piv_table = pd.pivot_table(filtered_data, 
                                        values=iValues, index=iRows, margins=True, margins_name = "GRAND TOTAL",
                                        columns=iColumns, fill_value=0, dropna=True, aggfunc = aggf)
            piv_table = piv_table.astype(int)

            #Print table to screen
            piv_html = piv_table.to_html()
            st.markdown(piv_html, unsafe_allow_html=True)
            st.markdown(hp.get_table_download_link(piv_table), unsafe_allow_html=True)
            
            if st.sidebar.button("Row Percentage", key="k1"):
                piv = hp.mmr_row(filtered_data, 
                                    iValues, iColumns, iRows)
                st.table(piv)
                st.markdown(hp.get_table_download_link(piv), unsafe_allow_html=True)

            if st.sidebar.button("Column Percentage", key="k2"):
                piv = hp.mmr_col(filtered_data, 
                                    iValues, iColumns,iRows)
                st.table(piv)
                st.markdown(hp.get_table_download_link(piv), unsafe_allow_html=True)


    except:
        st.write("Please make a valid selection")
else:
    st.header("Please import your data in the sidebar")