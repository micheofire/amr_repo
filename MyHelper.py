import pandas as pd
import numpy as np
import streamlit as st
import base64
from io import BytesIO
from calendar import Calendar
import datetime as dt


def SplitData(merge, col):
    final = pd.DataFrame([])
    for ind in merge.index:
        new = pd.DataFrame([])
        new[col + " analysis"] = list(set([i for i in [i.strip() for i in str(merge[col].iloc[ind]).split(",")] if (len(i.strip()) > 0) & (i != "nan")]))
        for mcol in merge.columns:
            new[mcol] = merge[mcol].iloc[ind]
        final = pd.concat([final, new], axis=0, ignore_index=True)
    return final


def PivotSplitData(final, val, banners):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = final.pivot_table(columns = banner, values = "SbjNum", index = val+" analysis", aggfunc = "count", fill_value=0, margins = True, margins_name = "TOTAL")
        piv_table = piv_table.astype(int)
        init_df = pd.concat([init_df, piv_table], axis=1)
    return init_df.fillna("")


def PivotData(final, val, banners):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(final, columns = banner, index=val, values = "SbjNum", aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()
        
        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.fillna("")


def FilterData(final, val, Filters):
    if type(val) == list:
        for v in val:
            final[v] = final[v].apply(lambda x: x if x in Filters else np.nan)
    else:
        final[val] = final[val].apply(lambda x: x if x in Filters else np.nan)
    return final

def FilterSplitData(final, val, Filters):
    if type(val) == list:
        for v in val:
            final[v+" analysis"] = final[v+" analysis"].apply(lambda x: x if x in Filters else np.nan)
    else:
        final[val+" analysis"] = final[val+" analysis"].apply(lambda x: x if x in Filters else np.nan)
    return final


def PrintOut(final):
    final_html = final.to_html()
    return st.markdown(final_html, unsafe_allow_html=True)

def PrintPercentage(final):
#     final_html = final.render()
    return st.dataframe(final)


def DownloadTable(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def DownloadPercentage(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_excel("data.xlsx",index=True)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def ToExcel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def GetTableDownload(df):
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64, {b64.decode()}" download="extract.xlsx">Download csv file</a>'

def NationalColumn(data, banners, val):
    data["Districts"] = data["Districts"].apply(lambda x: "Lusaka district" if x == "Lusaka" else x)
    w_fac1 = {"Central":0.44424900233496, "Copperbelt":1.2576976109871, "Eastern":2.9462472373327, 	 
          "Luapula":0.507423440067554, "Lusaka":3.82420441843976, "Muchinga":0.48537151734463,
          "North-Western":2.29475372284397, "Northern":0.754703566250043, "Southern":3.64905954547725, 	 
          "Western":0.385637752542655, "Female":0.762891093110099, "Male":1.48672821544687, "Rural":0.934287817881662, 	 
          "Urban":1.08615459967583, "15 – 18":1.49047210759739, "19 – 24":0.805458833379023, 	 
          "25 – 34":0.844592620188083, 	 "35 – 44":1.03956504521652, 	 "45+":1.47583147876734,
          "Kafue":3.82420441843976, "Lusaka district":3.82420441843976, "Nakonde":0.48537151734463,"Chibombo":0.44424900233496,
          "Solwezi":2.29475372284397,"Kapiri Mposhi":0.44424900233496,"Mkushi":0.44424900233496,"Mazabuka":3.64905954547725,
          "Kabwe":0.44424900233496,"Kitwe":0.48537151734463,"Petauke":2.9462472373327,"Chilililabombwe":0.48537151734463,
          "Kalulushi":0.48537151734463,"Mufulira":0.48537151734463,"Ndola":0.48537151734463,"Luanshya":0.48537151734463,
          "Chipata":2.9462472373327,"Chingola":0.48537151734463,"Kasama":0.754703566250043,"Livingstone":3.64905954547725,
          "Mpika":0.48537151734463,"Kaoma":0.385637752542655,"Kalabo":0.385637752542655,"Lukulu":0.385637752542655,
          "Mongu":0.385637752542655,"Senanga":0.385637752542655,"Mungwi":0.754703566250043,"Chinsali":0.48537151734463,
          "Mafinga":0.48537151734463 , "Isoka":0.48537151734463,"Mansa":0.507423440067554,"Nchelenge":0.507423440067554,
          "Samfya":0.507423440067554,"Kawambwa":0.507423440067554,"Serenje":0.44424900233496,
          "AB":1.75345221068103, "C1":1.54536190159596, "C2":1.24381025854949, "DE":0.578751114158285 }
    init_df = pd.DataFrame({})
    total_table = pd.pivot_table(data, columns = "Province", index=val, values = "SbjNum", aggfunc="count")
    for col in total_table.columns:
        total_table[col] = total_table[col] * w_fac1[col]
    pro_total = total_table.sum(axis=1)

    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, index=val, values = "SbjNum", aggfunc="count")

        #APPLYING WEIGHTING FACTOR
        for col in piv_table.columns[:]:
            piv_table[col] = piv_table[col] * w_fac1[col]

        #CREATING TOTAL COLUMN AND ROW
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)

        total = piv_table[f"{banner.upper()} TOTAL"]

        #Using Province total as the key total
        if banner == "Province":
            pass
        else:
            for col in piv_table.columns:
                piv_table[col] = (piv_table[col]/total)
                piv_table[col] = (piv_table[col]*pro_total)

        piv_table.loc["TOTAL"] = piv_table.sum()

        #CALCULATING COLUMN PERCENTAGE
        total = piv_table.loc["TOTAL"]
        for col in piv_table.index:
            piv_table.loc[col] = np.round((piv_table.loc[col]/total), 4)


        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)

    return init_df #.style.format("{:.2%}")

def NationalCount(analysis, banners):
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
    #Dictionary for national population for each of the banner (Province, Age, Area Type and Gender)
    p7d_weighted_total = {
        'Central': 842402.936401135, 'Copperbelt': 1412680.67888379, 'Eastern': 983703.307715038, 'Luapula': 617831.669166188, 'Lusaka': 1783410.59611979, 
        'Muchinga': 534613.718580612, 'North-Western': 466370.666020739, 'Northern': 731298.663344461, 'Southern': 1039579.53884837, 
        'Western': 512233.224919868, 'Female': 4577979.67062382, 'Male': 4346145.32937618, 'Rural': 4730009.46542932, 'Urban': 4194115.53457068, 
        '15 – 18': 1552433.0, '19 – 24': 2046202, '25 – 34': 2496580, '35 – 44': 1650581, '45+': 1178329,"Chibombo":233773.516064138,
        "Kabwe":142108.230707858,"Kapiri Mposhi":202601.19872173,"Mkushi":135592.663638037,"Serenje":128327.327269373,"Chilililabombwe":82571.0164455953,
        "Chingola":180771.072325807,"Kalulushi":87958.0078068874,"Kitwe":469178.659714363,"Luanshya":109421.109689515,"Mufulira":122434.137565805,
        "Ndola":360346.67533582,"Chipata":575106.76282511,"Petauke":408596.544889928,"Kawambwa":118764.226544613,"Mansa":194480.024332114,
        "Nchelenge":141321.966917501,"Samfya":163265.451371959,"Kafue":195118.304555167,"Lusaka district":1588292.29156462,
        "Mafinga":534613.718580612,"Chinsali":106919.652394588,"Isoka":58597.7170804201,"Mpika":181647.770746745,"Nakonde":121403.066248971,
        "Kasama":445192.303838331,"Mungwi":286106.35950613,"Solwezi":466370.666020739,"Livingstone":433940.173457016,"Mazabuka":605639.365391357,
        "Kalabo":90542.6465339181,"Kaoma":137877.428856362,"Lukulu":67491.3754426626,"Mongu":124587.858621757,"Senanga":91733.9154651684,"AB":515342,
        "C1":1535138,"C2":1206698,"DE":5666946
    }
    
    #This line helps to get the non-total columns in the analysis
    tot_drop = []
    for item in banners:
        tot_drop.append(item.upper()+" TOTAL")
    valid_col = analysis.drop(tot_drop, axis=1)
    valid_col = valid_col.columns

    #This line multiplies the valid columns with the national population data
    for item in valid_col:
        analysis[item] = analysis[item] * p7d_weighted_total[item]


    analysis.drop("TOTAL", inplace = True)
    analysis.loc["TOTAL"] = analysis.sum()


    #This line creates a dictionary where the keys are the banner total 
    #and the values are the unique banners
    banner_tot = {}
    for item in banners:
        banner_tot[item.upper()+" TOTAL"] = demo[item].unique().tolist()

    new_banner = {}
    for ban in banner_tot.keys():
        che = []
        for item in analysis.columns:
            if item in banner_tot[ban]:
                che.append(item)
            else:
                pass
        analysis[ban] = analysis[che].sum(1)
        new_banner[ban] = che


    pro_total = analysis["PROVINCE TOTAL"]

    for banners in new_banner.keys():
        total = analysis[banners]
        for banner in new_banner[banners]:
            analysis[banner] = analysis[banner]/total
            analysis[banner] = analysis[banner]*pro_total



    for ban in banner_tot.keys():
        che = []
        for item in analysis.columns:
            if item in banner_tot[ban]:
                che.append(item)
            else:
                pass
        analysis[ban] = analysis[che].sum(1)
    return analysis     

def NationalCountBase(analysis, banners, p7d_weighted_total):
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
    #This line helps to get the non-total columns in the analysis
    tot_drop = []
    for item in banners:
        tot_drop.append(item.upper()+" TOTAL")
    valid_col = analysis.drop(tot_drop, axis=1)
    valid_col = valid_col.columns

    #This line multiplies the valid columns with the national population data
    for item in valid_col:
        analysis[item] = analysis[item] * p7d_weighted_total[item]


    analysis.drop("TOTAL", inplace = True)
    analysis.loc["TOTAL"] = analysis.sum()


    #This line creates a dictionary where the keys are the banner total 
    #and the values are the unique banners
    banner_tot = {}
    for item in banners:
        banner_tot[item.upper()+" TOTAL"] = demo[item].unique().tolist()

    new_banner = {}
    for ban in banner_tot.keys():
        che = []
        for item in analysis.columns:
            if item in banner_tot[ban]:
                che.append(item)
            else:
                pass
        analysis[ban] = analysis[che].sum(1)
        new_banner[ban] = che


    pro_total = analysis["PROVINCE TOTAL"]

    for banners in new_banner.keys():
        total = analysis[banners]
        for banner in new_banner[banners]:
            analysis[banner] = analysis[banner]/total
            analysis[banner] = analysis[banner]*pro_total



    for ban in banner_tot.keys():
        che = []
        for item in analysis.columns:
            if item in banner_tot[ban]:
                che.append(item)
            else:
                pass
        analysis[ban] = analysis[che].sum(1)
    return analysis     


def Impression(radio_data, banner):
    impression = []
    new_df = pd.DataFrame()
    stations = list(radio_data["Station"].unique())
    days = list(radio_data["Day"].unique())
#     mediaRadio = pd.read_csv("NEW EXPORT/merged past seven days.csv")
#     if "LSM GROUP" in banner:
#         mediaRadio["LSM GROUP"] = mediaRadio["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
#     else:
#         pass
#     pivotR = NationalColumn(mediaRadio, banner, "Past 7 days analysis")
#     pivotRN = NationalCount(pivotR, banner).fillna(0).astype(int)
    
    for station in stations:
#         p7d = dict(pivotRN.copy().loc[station])
        for day in days:
            split_merge = pd.read_csv(f"OFFLINE DATA/{station} {day}.csv")
            if "LSM GROUP" in banner:
                split_merge["LSM GROUP"] = split_merge["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
            else:
                pass
            pivot = NationalColumn(split_merge, banner, f"{station}  {day} analysis")
#             nat_pivot = NationalCountBase(pivot.copy(), banner, p7d)
            nat_pivot = NationalCount(pivot.copy(), banner)

            run_data = radio_data[(radio_data["Day"]==day) & (radio_data["Station"] == station)]
            for ind in run_data.index:
                time = run_data.loc[ind]["New Time"]
                try:
                    impression.append(nat_pivot.loc[time]["PROVINCE TOTAL"])
                except:
                    impression.append(0)
            new_df = pd.concat([new_df, run_data], axis=0, ignore_index=True)

        imp = pd.DataFrame(impression, columns =["IMPRESSION"])
        imp["IMPRESSION"] = round(imp["IMPRESSION"]).astype(int)
        finish = pd.concat([new_df, imp], axis=1)
    return finish


def ImpressionBase(radio_data, banner):
    impression = []
    new_df = pd.DataFrame()
    stations = list(radio_data["Station"].unique())
    days = list(radio_data["Day"].unique())
    mediaRadio = pd.read_csv("NEW EXPORT/merged past seven days.csv")
    if "LSM GROUP" in banner:
        mediaRadio["LSM GROUP"] = mediaRadio["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
    else:
        pass
    pivotR = NationalColumn(mediaRadio, banner, "Past 7 days analysis")
    pivotRN = NationalCount(pivotR, banner).fillna(0).astype(int)
    
    for station in stations:
        p7d = dict(pivotRN.copy().loc[station])
        for day in days:
            split_merge = pd.read_csv(f"OFFLINE DATA/{station} {day}.csv")
            if "LSM GROUP" in banner:
                split_merge["LSM GROUP"] = split_merge["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
            else:
                pass
            pivot = NationalColumn(split_merge, banner, f"{station}  {day} analysis")
            nat_pivot = NationalCountBase(pivot.copy(), banner, p7d)

            run_data = radio_data[(radio_data["Day"]==day) & (radio_data["Station"] == station)]
            for ind in run_data.index:
                time = run_data.loc[ind]["New Time"]
                try:
                    impression.append(nat_pivot.loc[time]["PROVINCE TOTAL"])
                except:
                    impression.append(0)
            new_df = pd.concat([new_df, run_data], axis=0, ignore_index=True)

        imp = pd.DataFrame(impression, columns =["IMPRESSION"])
        imp["IMPRESSION"] = round(imp["IMPRESSION"]).astype(int)
        finish = pd.concat([new_df, imp], axis=1)
    return finish


def ImpressionTV(radio_data, banner):
    impression = []
    new_df = pd.DataFrame()
    stations = list(radio_data["Station"].unique())
    days = list(radio_data["Day"].unique())
#     mediaRadio = pd.read_csv("NEW EXPORT/merged past seven days.csv")
#     if "LSM GROUP" in banner:
#         mediaRadio["LSM GROUP"] = mediaRadio["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
#     else:
#         pass
#     pivotR = NationalColumn(mediaRadio, banner, "Past 7 days analysis")
#     pivotRN = NationalCount(pivotR, banner).fillna(0).astype(int)
    
    for station in stations:
#         p7d = dict(pivotRN.copy().loc[station])
        for day in days:
            split_merge = pd.read_csv(f"TV OFFLINE NEW/{station} {day}.csv")
            if "LSM GROUP" in banner:
                split_merge["LSM GROUP"] = split_merge["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
            else:
                pass
            pivot = NationalColumn(split_merge, banner, f"{station}  {day} analysis")
#             nat_pivot = NationalCountBase(pivot.copy(), banner, p7d)
            nat_pivot = NationalCount(pivot.copy(), banner)

            run_data = radio_data[(radio_data["Day"]==day) & (radio_data["Station"] == station)]
            for ind in run_data.index:
                time = run_data.loc[ind]["New Time"]
                try:
                    impression.append(nat_pivot.loc[time]["PROVINCE TOTAL"])
                except:
                    impression.append(0)
            new_df = pd.concat([new_df, run_data], axis=0, ignore_index=True)

        imp = pd.DataFrame(impression, columns =["IMPRESSION"])
        imp["IMPRESSION"] = round(imp["IMPRESSION"]).astype(int)
        finish = pd.concat([new_df, imp], axis=1)
    return finish



def WeeklyListenersData(radio_data, week):
    demo = pd.read_csv("DATA/demo new.csv")
    final = pd.DataFrame()
    weekly_data = radio_data[radio_data["Week"] == week].copy()
    stations = weekly_data["Station"].unique()
    for station in stations:
        new_df = pd.DataFrame()
        station_weekly = weekly_data[weekly_data["Station"] == station].copy()
        days = station_weekly["Day"].unique()
        unique_id = []
        for day in days:
            radio_offline = pd.read_csv(f"OFFLINE DATA/{station} {day}.csv")
            daily_data = station_weekly[station_weekly["Day"] == day]
            for ind in daily_data.index:
                time_stamp = daily_data.loc[ind]["New Time"]
                unique_id = unique_id + list(radio_offline[radio_offline[f"{station}  {day} analysis"] == time_stamp]["SbjNum"])
        new_df["SbjNum"] = list(set(unique_id))
        new_df["SbjNum"] = new_df["SbjNum"].astype(int)
        new_df["Station"] = station
        merge = demo.merge(new_df, on="SbjNum")
        
        final = pd.concat([final, merge], ignore_index=True)   
    return final


def GenerateListeners(week, banners):
    merge = pd.read_csv("NEW EXPORT/merged past seven days.csv")
    merge["LSM GROUP"] = merge["LSM GROUP"].apply(lambda x: "AB" if x=="A" else ("DE" if x=="D" else x))
    
    w_fac1 = {"Central":0.44424900233496, "Copperbelt":1.2576976109871, "Eastern":2.9462472373327, 	 
              "Luapula":0.507423440067554, "Lusaka":3.82420441843976, "Muchinga":0.48537151734463,
              "North-Western":2.29475372284397, "Northern":0.754703566250043, "Southern":3.64905954547725, 	 
              "Western":0.385637752542655, "Female":0.762891093110099, "Male":1.48672821544687, "Rural":0.934287817881662, 	 
              "Urban":1.08615459967583, "15 – 18":1.49047210759739, "19 – 24":0.805458833379023, 	 
              "25 – 34":0.844592620188083, 	 "35 – 44":1.03956504521652, 	 "45+":1.47583147876734,
              "Kafue":3.82420441843976, "Lusaka district":3.82420441843976, "Nakonde":0.48537151734463,"Chibombo":0.44424900233496,
              "Solwezi":2.29475372284397,"Kapiri Mposhi":0.44424900233496,"Mkushi":0.44424900233496,"Mazabuka":3.64905954547725,
              "Kabwe":0.44424900233496,"Kitwe":0.48537151734463,"Petauke":2.9462472373327,"Chilililabombwe":0.48537151734463,
              "Kalulushi":0.48537151734463,"Mufulira":0.48537151734463,"Ndola":0.48537151734463,"Luanshya":0.48537151734463,
              "Chipata":2.9462472373327,"Chingola":0.48537151734463,"Kasama":0.754703566250043,"Livingstone":3.64905954547725,
              "Mpika":0.48537151734463,"Kaoma":0.385637752542655,"Kalabo":0.385637752542655,"Lukulu":0.385637752542655,
              "Mongu":0.385637752542655,"Senanga":0.385637752542655,"Mungwi":0.754703566250043,"Chinsali":0.48537151734463,
              "Mafinga":0.48537151734463 , "Isoka":0.48537151734463,"Mansa":0.507423440067554,"Nchelenge":0.507423440067554,
              "Samfya":0.507423440067554,"Kawambwa":0.507423440067554,"Serenje":0.44424900233496,
              "AB":515342,"C1":1535138,"C2":1206698,"DE":5666946}
    init_df = pd.DataFrame({})
    
    #STEP ONE
    total_table = pd.pivot_table(week, columns = "Province", index="Station", values = "SbjNum", aggfunc="count", fill_value=0)
    for col in total_table.columns:
        total_table[col] = total_table[col] * w_fac1[col]
    
    #STEP TWO
    radio_listen_count = PivotSplitData(merge, "Past 7 days", ["Province"])
    my_radio_listeners = radio_listen_count.loc[total_table.index].drop("TOTAL", axis=1)
    for col in my_radio_listeners.columns:
        my_radio_listeners[col] = my_radio_listeners[col]*w_fac1[col]
    
    #STEP THREE -- CALCULATE PERCENTAGE
    for col in total_table.columns:
        total_table[col] = total_table[col]/my_radio_listeners[col]
    
    #STEP FOUR -- AMR NATIONAL COUNT
    amr_nat = NationalColumn(merge, banners, "Past 7 days analysis")
    amr_nat = NationalCount(amr_nat, banners)
    amr_nat_province = amr_nat.copy()[merge["Province"].unique()]
    amr_nat_province = amr_nat_province.loc[total_table.index]
    
    #STEP FIVE
    for col in total_table.columns:
        total_table[col] = total_table[col]*amr_nat_province[col]
    
    total_table = total_table.fillna(0).astype(int)
    #-_-_-_-_-_------------------_-_-_-_-_-_-_-_
    
    pro_total = total_table.sum(axis=1)
    
    for banner in banners:
        #STEP ONE
        piv_table = pd.pivot_table(week.copy(), columns = banner, index="Station", values = "SbjNum", aggfunc="count", fill_value=0)
        for col in piv_table.columns:
            piv_table[col] = piv_table[col] * w_fac1[col]
        
        #STEP TWO
        radio_listen_count = merge.pivot_table(index="Past 7 days analysis",values="SbjNum",
                                              columns=banner, aggfunc="count")
        my_radio_listeners = radio_listen_count.loc[piv_table.copy().index]
        for col in my_radio_listeners.columns:
            my_radio_listeners[col] = my_radio_listeners[col]*w_fac1[col]
        
        #STEP THREE -- CALCULATING PERCENTAGE
        for col in piv_table.columns:
            piv_table[col] = piv_table[col]/my_radio_listeners[col]
            
        #STEP FOUR --- AMR NATIONAL COUNT
        amr_nat_now = amr_nat.copy()[merge[banner].unique()]
        amr_nat_now = amr_nat_now.loc[piv_table.index]
        
        #STEP FIVE
        for col in piv_table.columns:
            piv_table[col] = piv_table[col]*amr_nat_now[col]
        
        
        #CREATING TOTAL COLUMN AND ROW
        piv_table[banner.upper()+" TOTAL"] = piv_table.sum(axis=1)

        total = piv_table[f"{banner.upper()} TOTAL"]

        #Using Province total as the key total
        if banner == "Province":
            pass
        else:
            for col in piv_table.columns:
                piv_table[col] = piv_table[col]/total
                piv_table[col] = piv_table[col]*pro_total

        piv_table.loc["TOTAL"] = piv_table.sum()
        
        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.astype(int).fillna(0)


def RestructureListeners(banner, mmr_data, week):
    demo = pd.read_csv("DATA/demo new.csv")
    all_banner = []
    for ban in banner:
        all_banner.append(list(demo[ban].unique()))
        all_banner.append(f"{ban.upper()} TOTAL")

    flatlist = []
    for sublist in all_banner:
        if type(sublist) == list:
            for item in sublist:
                flatlist.append(item)
        else:
            flatlist.append(sublist)

    ind = sorted(mmr_data["Station"].unique())
    week1_a = pd.DataFrame(columns=flatlist, index=ind)
    for col in week:
        for ind in week.index:
            week1_a.at[ind, col] = week.at[ind, col]
    return week1_a.fillna(0).astype(int)



def PreprocessData(data):
    data['Date']= pd.to_datetime(data['Date']) 
    def week_number(date):
        cal = Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(date.year, date.month)
        for x in range(len(weeks)):
            if date.day in weeks[x]:
                return "Week {}".format(x+1)
    data['Week'] = data['Date'].apply(week_number)
    data['Day Number'] = data['Date'].apply(lambda x: x.day)
    if "Monday" in data["Day"].unique():
        pass
    else:
        data["Day"] = data["Day"].map({"Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday",
                                       "Sat": "Saturday", "Sun": "Sunday", "Mon": "Monday", "Tue": "Tuesday"})
    stamp_list = [
        "0:00  -  0:14","0:15  -  0:29", "0:30  -  0:44","0:45  -  0:59",
        "1:00  -  1:14","1:15  -  1:29", "1:30  -  1:44","1:45  -  1:59",
        "2:00  -  2:14","2:15  -  2:29", "2:30  -  2:44","2:45  -  2:59",
        "3:00  -  3:14","3:15  -  3:29", "3:30  -  3:44","3:45  -  3:59",
        "4:00  -  4:14","4:15  -  4:29", "4:30  -  4:44","4:45  -  4:59",
        "5:00  -  5:14","5:15  -  5:29", "5:30  -  5:44","5:45  -  5:59",
        "6:00  -  6:14","6:15  -  6:29", "6:30  -  6:44","6:45  -  6:59",
        "7:00  -  7:14","7:15  -  7:29", "7:30  -  7:44","7:45  -  7:59",
        "8:00  -  8:14","8:15  -  8:29", "8:30  -  8:44","8:45  -  8:59",
        "9:00  -  9:14","9:15  -  9:29", "9:30  -  9:44","9:45  -  9:59",
        "10:00  -  10:14","10:15  -  10:29", "10:30  -  10:44","10:45  -  10:59",
        "11:00  -  11:14","11:15  -  11:29", "11:30  -  11:44","11:45  -  11:59",
        "12:00  -  12:14","12:15  -  12:29", "12:30  -  12:44","12:45  -  12:59",
        "13:00  -  13:14","13:15  -  13:29", "13:30  -  13:44","13:45  -  13:59",
        "14:00  -  14:14","14:15  -  14:29", "14:30  -  14:44","14:45  -  14:59",
        "15:00  -  15:14","15:15  -  15:29", "15:30  -  15:44","15:45  -  15:59",
        "16:00  -  16:14","16:15  -  16:29", "16:30  -  16:44","16:45  -  16:59",
        "17:00  -  17:14","17:15  -  17:29", "17:30  -  17:44","17:45  -  17:59",
        "18:00  -  18:14","18:15  -  18:29", "18:30  -  18:44","18:45  -  18:59",
        "19:00  -  19:14","19:15  -  19:29", "19:30  -  19:44","19:45  -  19:59",
        "20:00  -  20:14","20:15  -  20:29", "20:30  -  20:44","20:45  -  20:59",
        "21:00  -  21:14","21:15  -  21:29", "21:30  -  21:44","21:45  -  21:59",
        "22:00  -  22:14","22:15  -  22:29", "22:30  -  22:44","22:45  -  22:59",
        "23:00  -  23:14","23:15  -  23:29", "23:30  -  23:44","23:45  -  23:59"    
    ]

    def restamp(x):
        a = x.split(":")[0]
        b = x.split(":")[1]
        if int(a) <=23:

            x = dt.time(int(a), int(b))
            for item in stamp_list:
                one = item.split("-")[0].strip().split(":")
                two = item.split("-")[1].strip().split(":")
                if (x >= dt.time(int(one[0]), int(one[1]))) and (x <= dt.time(int(two[0]), int(two[1]))):
                    return item
        else:
            return x

    data["New Time"] = data["Time"].apply(restamp)
    return data
