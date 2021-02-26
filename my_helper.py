import pandas as pd
import numpy as np
import streamlit as st
import base64
from io import BytesIO


def split_data(merge, col):
    final = pd.DataFrame([])
    for ind in merge.index:
        new = pd.DataFrame([])
        new[col + " analysis"] = list(set([i for i in [i.strip() for i in str(merge[col].iloc[ind]).split(",")] if (len(i.strip()) > 0) & (i != "nan")]))
        for mcol in merge.columns:
            new[mcol] = merge[mcol].iloc[ind]
        final = pd.concat([final, new], axis=0, ignore_index=True)
    return final


def pivot_split(final, val, banners):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = final.pivot_table(columns = banner, values = "SbjNum", index = val+" analysis", aggfunc = "count", fill_value=0, margins = True, margins_name = "TOTAL")
        piv_table = piv_table.astype(int)
        init_df = pd.concat([init_df, piv_table], axis=1)
    return init_df.fillna("")


def pivot_by_index(final, val, banners):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(final, columns = banner, index=val, values = "SbjNum", aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()
        
        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.fillna("")




def pivot_by_value(final, val, banners):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(final, columns = banner, values = val, aggfunc = "count")
        piv_table = piv_table.astype(int)
        init_df = pd.concat([init_df, piv_table], axis=1)
    return init_df.fillna("")



def clean_never(final, val):
    if type(val) == list:
        for v in val:
            final[v] = final[v].apply(lambda x: "Never" if x == "0" else x)
    else:
        final[val] = final[val].apply(lambda x: "Never" if x == "0" else x)
    return final

def use_filter(final, val, Filters):
    if type(val) == list:
        for v in val:
            final[v] = final[v].apply(lambda x: x if x in Filters else np.nan)
    else:
        final[val] = final[val].apply(lambda x: x if x in Filters else np.nan)
    return final

def use_filter_split(final, val, Filters):
    if type(val) == list:
        for v in val:
            final[v+" analysis"] = final[v+" analysis"].apply(lambda x: x if x in Filters else np.nan)
    else:
        final[val+" analysis"] = final[val+" analysis"].apply(lambda x: x if x in Filters else np.nan)
    return final


def print_func(final):
    final_html = final.to_html()
    return st.markdown(final_html, unsafe_allow_html=True)

def print_perc(final):
#     final_html = final.render()
    return st.dataframe(final)


def download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def download_link_perc(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_excel("data.xlsx",index=True)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Sheet1")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64, {b64.decode()}" download="extract.xlsx">Download csv file</a>'


def percentage_row_by_value(data, banners, val):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, values = val, aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()

        total = piv_table[f"{banner.upper()} TOTAL"]
        for col in piv_table.columns:
            piv_table[col] = np.round((piv_table[col]/total), 4)

        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.style.format("{:.2%}")


def percentage_column_by_value(data, banners, val):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, values = val, aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()

        total = piv_table.loc["TOTAL"]
        for col in piv_table.index:
            piv_table.loc[col] = np.round((piv_table.loc[col]/total), 4)

        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.style.format("{:.2%}")





def percentage_row_by_index(data, banners, val):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, index=val, values = "SbjNum", aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()

        total = piv_table[f"{banner.upper()} TOTAL"]
        for col in piv_table.columns:
            piv_table[col] = np.round((piv_table[col]/total), 4)

        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.style.format("{:.2%}")


def percentage_column_by_index(data, banners, val):
    init_df = pd.DataFrame({})
    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, index=val, values = "SbjNum", aggfunc="count")
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
        piv_table.loc["TOTAL"] = piv_table.sum()

        total = piv_table.loc["TOTAL"]
        for col in piv_table.index:
            piv_table.loc[col] = np.round((piv_table.loc[col]/total), 4)

        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)
    return init_df.style.format("{:.2%}")


def NatColImpression(data, banners, val):
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
#         piv_table.loc["TOTAL"] = piv_table.sum()

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


def nat_col2(data, banners, val):
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
#         piv_table.loc["TOTAL"] = piv_table.sum()

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



def nat_row(data, banners, val):
    w_fac1 = {"Central":0.44424900233496, "Copperbelt":1.2576976109871, "Eastern":2.9462472373327, 	 
          "Luapula":0.507423440067554, "Lusaka":3.82420441843976, "Muchinga":0.48537151734463,
          "North-Western":2.29475372284397, "Northern":0.754703566250043, "Southern":3.64905954547725, 	 
          "Western":0.385637752542655, "Female":0.762891093110099, "Male":1.48672821544687, "Rural":0.934287817881662, 	 
          "Urban":1.08615459967583, "15 – 18":1.49047210759739, "19 – 24":0.805458833379023, 	 
          "25 – 34":0.844592620188083, 	 "35 – 44":1.03956504521652, 	 "45+":1.47583147876734,
          "Kafue":3.82420441843976, "Lusaka_d":3.82420441843976, "Nakonde":0.48537151734463,"Chibombo":0.44424900233496,
          "Solwezi":2.29475372284397,"Kapiri Mposhi":0.44424900233496,"Mkushi":0.44424900233496,"Mazabuka":3.64905954547725,
          "Kabwe":0.44424900233496,"Kitwe":0.48537151734463,"Petauke":2.9462472373327,"Chilililabombwe":0.48537151734463,
          "Kalulushi":0.48537151734463,"Mufulira":0.48537151734463,"Ndola":0.48537151734463,"Luanshya":0.48537151734463,
          "Chipata":2.9462472373327,"Chingola":0.48537151734463,"Kasama":0.754703566250043,"Livingstone":3.64905954547725,
          "Mpika":0.48537151734463,"Kaoma":0.385637752542655,"Kalabo":0.385637752542655,"Lukulu":0.385637752542655,
          "Mongu":0.385637752542655,"Senanga":0.385637752542655,"Mungwi":0.754703566250043,"Chinsali":0.48537151734463,
          "Isoka":0.48537151734463,"Mansa":0.507423440067554,"Nchelenge":0.507423440067554,
          "Samfya":0.507423440067554,"Kawambwa":0.507423440067554,"Serenje":0.44424900233496}
    init_df = pd.DataFrame({})
    total_table = pd.pivot_table(data, columns = "Province", index=val+" analysis", values = "SbjNum", aggfunc="count")
    for col in total_table.columns:
        total_table[col] = total_table[col] * w_fac1[col]
    pro_total = total_table.sum(axis=1)

    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, index=val+" analysis", values = "SbjNum", aggfunc="count")

        #APPLYING WEIGHTING FACTOR
        for col in piv_table.columns[:]:
            piv_table[col] = piv_table[col] * w_fac1[col]

        #CREATING TOTAL COLUMN AND ROW
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
#         piv_table.loc["TOTAL"] = piv_table.sum()

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
        total = piv_table[f"{banner.upper()} TOTAL"]
        for col in piv_table.columns:
            piv_table[col] = np.round((piv_table[col]/total), 4)


        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)

    return init_df.style.format("{:.2%}")


def nat_count(data, banners, val):
    w_fac1 = {"Central":0.44424900233496, "Copperbelt":1.2576976109871, "Eastern":2.9462472373327, 	 
          "Luapula":0.507423440067554, "Lusaka":3.82420441843976, "Muchinga":0.48537151734463,
          "North-Western":2.29475372284397, "Northern":0.754703566250043, "Southern":3.64905954547725, 	 
          "Western":0.385637752542655, "Female":0.762891093110099, "Male":1.48672821544687, "Rural":0.934287817881662, 	 
          "Urban":1.08615459967583, "15 – 18":1.49047210759739, "19 – 24":0.805458833379023, 	 
          "25 – 34":0.844592620188083, 	 "35 – 44":1.03956504521652, 	 "45+":1.47583147876734,
          "Kafue":3.82420441843976, "Lusaka_d":3.82420441843976, "Nakonde":0.48537151734463,"Chibombo":0.44424900233496,
          "Solwezi":2.29475372284397,"Kapiri Mposhi":0.44424900233496,"Mkushi":0.44424900233496,"Mazabuka":3.64905954547725,
          "Kabwe":0.44424900233496,"Kitwe":0.48537151734463,"Petauke":2.9462472373327,"Chilililabombwe":0.48537151734463,
          "Kalulushi":0.48537151734463,"Mufulira":0.48537151734463,"Ndola":0.48537151734463,"Luanshya":0.48537151734463,
          "Chipata":2.9462472373327,"Chingola":0.48537151734463,"Kasama":0.754703566250043,"Livingstone":3.64905954547725,
          "Mpika":0.48537151734463,"Kaoma":0.385637752542655,"Kalabo":0.385637752542655,"Lukulu":0.385637752542655,
          "Mongu":0.385637752542655,"Senanga":0.385637752542655,"Mungwi":0.754703566250043,"Chinsali":0.48537151734463,
         "Isoka":0.48537151734463,"Mansa":0.507423440067554,"Nchelenge":0.507423440067554,
          "Samfya":0.507423440067554,"Kawambwa":0.507423440067554,"Serenje":0.44424900233496}
    init_df = pd.DataFrame({})
    total_table = pd.pivot_table(data, columns = "Province", index=val+" analysis", values = "SbjNum", aggfunc="count")
    for col in total_table.columns:
        total_table[col] = total_table[col] * w_fac1[col]
    pro_total = total_table.sum(axis=1)

    for banner in banners:
        piv_table = pd.pivot_table(data, columns = banner, index=val+" analysis", values = "SbjNum", aggfunc="count")

        #APPLYING WEIGHTING FACTOR
        for col in piv_table.columns[:]:
            piv_table[col] = piv_table[col] * w_fac1[col]

        #CREATING TOTAL COLUMN AND ROW
        piv_table[f"{banner.upper()} TOTAL"] = piv_table.sum(axis=1)
#         piv_table.loc["TOTAL"] = piv_table.sum()

        total = piv_table[f"{banner.upper()} TOTAL"]

        #Using Province total as the key total
        if banner == "Province":
            pass
        else:
            for col in piv_table.columns:
                piv_table[col] = (piv_table[col]/total)
                piv_table[col] = (piv_table[col]*pro_total)

        piv_table.loc["TOTAL"] = piv_table.sum()

        init_df = pd.concat([init_df, piv_table], axis=1)
        init_df.fillna(0, inplace=True)

    return init_df



def final_output2(analysis, banners):
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
    #Dictionary for national population for each of the banner (Province, Age, Area Type and Gender)
    p7d_weighted_total = {
 'Central': 842402.936401135,
 'Copperbelt': 1412680.67888379,
 'Eastern': 983703.307715038,
 'Luapula': 617831.669166188,
 'Lusaka': 1783410.59611979,
 'Muchinga': 534613.718580612,
 'North-Western': 466370.666020739,
 'Northern': 731298.663344461,
 'Southern': 1039579.53884837,
 'Western': 512233.224919868,
 'Female': 4577979.67062382,
 'Male': 4346145.32937618,
 'Rural': 4730009.46542932,
 'Urban': 4194115.53457068,
 '15 – 18': 1552433.0,
 '19 – 24': 2046202,
 '25 – 34': 2496580,
 '35 – 44': 1650581,
 '45+': 1178329,
"Chibombo":233773.516064138,
"Kabwe":142108.230707858,
"Kapiri Mposhi":202601.19872173,
"Mkushi":135592.663638037,
"Serenje":128327.327269373,
"Chilililabombwe":82571.0164455953,
"Chingola":180771.072325807,
"Kalulushi":87958.0078068874,
"Kitwe":469178.659714363,
"Luanshya":109421.109689515,
"Mufulira":122434.137565805,
"Ndola":360346.67533582,
"Chipata":575106.76282511,
"Petauke":408596.544889928,
"Kawambwa":118764.226544613,
"Mansa":194480.024332114,
"Nchelenge":141321.966917501,
"Samfya":163265.451371959,
"Kafue":195118.304555167,
"Lusaka district":1588292.29156462,
"Muchinga":534613.718580612,
"Chinsali":106919.652394588,
"Mafinda":58597.7170804201,
"Isoka":58597.7170804201,
"Mpika":181647.770746745,
"Nakonde":121403.066248971,
"Kasama":445192.303838331,
"Mungwi":286106.35950613,
"Solwezi":466370.666020739,
"Livingstone":433940.173457016,
"Mazabuka":605639.365391357,
"Kalabo":90542.6465339181,
"Kaoma":137877.428856362,
"Lukulu":67491.3754426626,
"Mongu":124587.858621757,
"Senanga":91733.9154651684
}

    #This line helps to get the non-total columns in the analysis
    tot_drop = []
    for item in banners:
        tot_drop.append(item.upper()+" TOTAL")
    valid_col = analysis.drop(tot_drop, axis=1).columns

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


    for ban in banner_tot.keys():
        che = []
        for item in analysis.columns:
            if item in banner_tot[ban]:
                che.append(item)
            else:
                pass
        analysis[ban] = analysis[che].sum(1)


    pro_total = analysis["PROVINCE TOTAL"]

    for banners in banner_tot.keys():
        total = analysis[banners]
        for banner in banner_tot[banners]:
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


def NationalImpression(analysis, banners):
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
    #Dictionary for national population for each of the banner (Province, Age, Area Type and Gender)
    p7d_weighted_total = {
 'Central': 842402.936401135,
 'Copperbelt': 1412680.67888379,
 'Eastern': 983703.307715038,
 'Luapula': 617831.669166188,
 'Lusaka': 1783410.59611979,
 'Muchinga': 534613.718580612,
 'North-Western': 466370.666020739,
 'Northern': 731298.663344461,
 'Southern': 1039579.53884837,
 'Western': 512233.224919868,
 'Female': 4577979.67062382,
 'Male': 4346145.32937618,
 'Rural': 4730009.46542932,
 'Urban': 4194115.53457068,
 '15 – 18': 1552433.0,
 '19 – 24': 2046202,
 '25 – 34': 2496580,
 '35 – 44': 1650581,
 '45+': 1178329,
"Chibombo":233773.516064138,
"Kabwe":142108.230707858,
"Kapiri Mposhi":202601.19872173,
"Mkushi":135592.663638037,
"Serenje":128327.327269373,
"Chilililabombwe":82571.0164455953,
"Chingola":180771.072325807,
"Kalulushi":87958.0078068874,
"Kitwe":469178.659714363,
"Luanshya":109421.109689515,
"Mufulira":122434.137565805,
"Ndola":360346.67533582,
"Chipata":575106.76282511,
"Petauke":408596.544889928,
"Kawambwa":118764.226544613,
"Mansa":194480.024332114,
"Nchelenge":141321.966917501,
"Samfya":163265.451371959,
"Kafue":195118.304555167,
"Lusaka district":1588292.29156462,
"Mafinga":534613.718580612,
"Chinsali":106919.652394588,
"Isoka":58597.7170804201,
"Mpika":181647.770746745,
"Nakonde":121403.066248971,
"Kasama":445192.303838331,
"Mungwi":286106.35950613,
"Solwezi":466370.666020739,
"Livingstone":433940.173457016,
"Mazabuka":605639.365391357,
"Kalabo":90542.6465339181,
"Kaoma":137877.428856362,
"Lukulu":67491.3754426626,
"Mongu":124587.858621757,
"Senanga":91733.9154651684,
"AB":515342,"C1":1535138,"C2":1206698,"DE":5666946}
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



def final_output3(analysis, banners):
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
    #Dictionary for national population for each of the banner (Province, Age, Area Type and Gender)
    p7d_weighted_total = {
 'Central': 842402.936401135,
 'Copperbelt': 1412680.67888379,
 'Eastern': 983703.307715038,
 'Luapula': 617831.669166188,
 'Lusaka': 1783410.59611979,
 'Muchinga': 534613.718580612,
 'North-Western': 466370.666020739,
 'Northern': 731298.663344461,
 'Southern': 1039579.53884837,
 'Western': 512233.224919868,
 'Female': 4577979.67062382,
 'Male': 4346145.32937618,
 'Rural': 4730009.46542932,
 'Urban': 4194115.53457068,
 '15 – 18': 1552433.0,
 '19 – 24': 2046202,
 '25 – 34': 2496580,
 '35 – 44': 1650581,
 '45+': 1178329,
"Chibombo":233773.516064138,
"Kabwe":142108.230707858,
"Kapiri Mposhi":202601.19872173,
"Mkushi":135592.663638037,
"Serenje":128327.327269373,
"Chilililabombwe":82571.0164455953,
"Chingola":180771.072325807,
"Kalulushi":87958.0078068874,
"Kitwe":469178.659714363,
"Luanshya":109421.109689515,
"Mufulira":122434.137565805,
"Ndola":360346.67533582,
"Chipata":575106.76282511,
"Petauke":408596.544889928,
"Kawambwa":118764.226544613,
"Mansa":194480.024332114,
"Nchelenge":141321.966917501,
"Samfya":163265.451371959,
"Kafue":195118.304555167,
"Lusaka district":1588292.29156462,
"Mafinga":534613.718580612,
"Chinsali":106919.652394588,
"Isoka":58597.7170804201,
"Mpika":181647.770746745,
"Nakonde":121403.066248971,
"Kasama":445192.303838331,
"Mungwi":286106.35950613,
"Solwezi":466370.666020739,
"Livingstone":433940.173457016,
"Mazabuka":605639.365391357,
"Kalabo":90542.6465339181,
"Kaoma":137877.428856362,
"Lukulu":67491.3754426626,
"Mongu":124587.858621757,
"Senanga":91733.9154651684,
"AB":515342,"C1":1535138,"C2":1206698,"DE":5666946}
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

def final_output4(analysis, banners, p7d_weighted_total):
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



def link_mmr(data, banner):
    import my_helper as hp
    demo = pd.read_csv("DATA/demo new.csv", low_memory=False)
#     mediaRadio = pd.read_csv("DATA/radio_media_diary_clean.csv", low_memory=False)

    impression = []
    new_df = pd.DataFrame()
    
    stations = list(data["Station"].unique())
    days = list(data["Day"].unique())
    for station in stations:
        for day in days:
            split_merge = pd.read_csv(f"OFFLINE DATA/{station} {day}.csv")
            pivot = hp.nat_col(split_merge, banner, f"{station}  {day}")
            pivot = hp.final_output3(pivot, banner).astype(int)#.round()

            run_data = data[(data["Day"] == day) & (data["Station"] == station)]
            
            for ind in run_data.index:
                time = run_data.loc[ind]["New Time"]            
                try:
                    impression.append(pivot.loc[time]["PROVINCE TOTAL"])
                except:
                    impression.append("0")
            new_df = pd.concat([new_df, run_data], axis=0, ignore_index=True)

        imp = pd.DataFrame(impression, columns = ["IMPRESSION"])
        finish = pd.concat([new_df, imp], axis=1)
    return finish


def weekly_impression_data(radio_data, week):
    final = pd.DataFrame()
    weekly_data = radio_data[radio_data["Week"] == week].copy()
    stations = weekly_data["Station"].unique()
    for station in stations:
#         print(station)
        new_df = pd.DataFrame()
        station_weekly = weekly_data[weekly_data["Station"] == station].copy()
        days = station_weekly["Day"].unique()
        unique_id = []
        for day in days:
            radio_offline = pd.read_csv(f"OFFLINE DATA/{station} {day}.csv")
            daily_data = station_weekly[station_weekly["Day"] == day]
            for ind in daily_data.index:
                time_stamp = daily_data.loc[ind]["Time stamp"]
                unique_id = unique_id + list(radio_offline[radio_offline[f"{station}  {day} analysis"] == time_stamp]["SbjNum"])
        new_df["SbjNum"] = list(set(unique_id))
        new_df["SbjNum"] = new_df["SbjNum"].astype(int)
        new_df["Station"] = station
        merge = demo.merge(new_df, on="SbjNum")

        final = pd.concat([final, merge], ignore_index=True)   
    return final