# MIT License
#
# Copyright (c) 2024 Minniti Julien
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import streamlit as st
import platform
import math

import pandas as pd

# For Master Mix
def adjust_concentration(row):
    return row["Conc. (µg/µL)"] / dilution_factor

def LyB_to_add(row):
    return (((row["Adjusted conc. (µg/µL)"] * sample_volume) / concentration_samples) - sample_volume) - ((row["Adjusted conc. (µg/µL)"] * sample_volume) / concentration_samples) / LoB_concentration

def loading_buffer(row):
    if row["Lysis buffer to add (µL)"] < 0:
        return sample_volume / (LoB_concentration - 1) 
    else:
        return ((row["Adjusted conc. (µg/µL)"] * sample_volume) / concentration_samples) / LoB_concentration

def total_volume(row):
    if row["Lysis buffer to add (µL)"] >= 0:
        return row["Lysis buffer to add (µL)"] + sample_volume + row["Loading buffer (µL)"]
    else: 
        return sample_volume + row["Loading buffer (µL)"]

def nb_sample(row):
    return math.floor((row["Total volume (µL)"]) / volume_per_well)

def vol_to_charge(row):
    if row["Lysis buffer to add (µL)"] < 0:
        return f"All ({row["Total volume (µL)"]})"
    else:
        return volume_per_well
    

# For one sample to load
def sample_vol_OS(row):
    return (proteins_per_well / row["Adjusted conc. (µg/µL)"])

def LyB_to_add_OS(row):
    return volume_per_well - row["Sample volume (µL)"]
   
def loading_buffer_OS(row):
    if row["Lysis buffer to add (µL)"] < 0:
        return row["Sample volume (µL)"] / (LoB_concentration - 1) 
    else:
        return volume_per_well / (LoB_concentration - 1)
    
def total_volume_OS(row):
    if row["Lysis buffer to add (µL)"] >= 0:
        return row["Lysis buffer to add (µL)"] + row["Sample volume (µL)"] + row["Loading buffer (µL)"]
    else: 
        return row["Sample volume (µL)"] + row["Loading buffer (µL)"]

def nb_sample_OS(row):
    if row["Lysis buffer to add (µL)"] <= 0:
        return 1
    else:
        return math.floor((sample_volume) / row["Sample volume (µL)"])   

local_test = platform.processor()

# Settings for Streamlit page
st.set_page_config(page_title="BlotMaster", page_icon="🔬", initial_sidebar_state="expanded", layout="wide")

# Main page
st.sidebar.title('👩🏼‍🔬 BlotMaster')
st.sidebar.write("Created by Minniti Julien")

# Button sidebar
colsb1, colsb2, colsb3 = st.sidebar.columns(3, gap="small")
colsb1.link_button("Help ⁉",
                  '')
colsb2.link_button('GitHub', 'https://github.com/Jumitti/BlotMaster')
if local_test == "":
    colsb3.link_button('Download app 📥', 'https://github.com/Jumitti/BlotMaster/releases')
else:
    colsb3.link_button('Web app 🌐', 'https://blotmaster.streamlit.app/')

# MIT licence
st.sidebar.divider()
st.sidebar.link_button('Under MIT licence', 'https://github.com/Jumitti/BlotMaster/blob/main/LICENSE')

# Main
# Sample table
colm1, colm2, colm3 = st.columns([1, 1, 1], gap="small")
colm1.write("**Samples table**")
samples_table = pd.DataFrame(
    [{"Sample name": "WT_1", "Conc. (µg/µL)": 1.5}, {"Sample name": "KO_1", "Conc. (µg/µL)": 2}]
)
samples_table = colm1.data_editor(samples_table, key="vector", num_rows="dynamic")

dilution_factor = colm2.number_input("**Dilution factor of samples:**",value=1.00, min_value=0.01, step=0.01, help='e.g. if you measured the proteins in 2 µL of your sample with a Bradford or other then the dilution factor of your sample is 2')
sample_volume = colm2.number_input("**Total sample volumes (µL):**",value=30.00, min_value=0.01, step=0.01)

proteins_per_well = colm3.number_input("**Amount of proteins/well (µg):**",value=25.00, min_value=0.01, step=0.01)
volume_per_well = colm3.number_input("**Total volume/well (µL):**",value=30.00, min_value=0.01, step=0.01, help='We take into account the sample, the lysis buffer and the load buffer')

concentration_samples = proteins_per_well/volume_per_well if volume_per_well > 0 else proteins_per_well
colm3.write(f"Concentration of samples: {concentration_samples} µg/µL")

LoB_concentration = colm3.number_input("**Loading buffer conc. (X):**", value=1.00, min_value=0.10, step=0.01, help="e.g. the loading buffer is often in concentration 'X'. If it's 5X then put 5")

st.divider()

# Output Table for Mix
required_columns = ["Sample name", "Conc. (µg/µL)"]
if not set(required_columns).issubset(samples_table.columns):
    st.error("The columns 'Sample name' and 'Conc. (µg/µL)' are required.")
else:
    missing_data = samples_table[samples_table["Sample name"].isnull() | samples_table["Conc. (µg/µL)"].isnull()]
    if not missing_data.empty or (samples_table["Conc. (µg/µL)"] < 0).any():
        st.error("Some lines do not concentrations or are negative.")
    else:
        adjusted_samples_table = samples_table.copy()
        adjusted_samples_table["Adjusted conc. (µg/µL)"] = adjusted_samples_table.apply(adjust_concentration, axis=1)
        adjusted_samples_table["Lysis buffer to add (µL)"] = adjusted_samples_table.apply(LyB_to_add, axis=1)
        adjusted_samples_table["Loading buffer (µL)"] = adjusted_samples_table.apply(loading_buffer, axis=1)
        adjusted_samples_table["Total volume (µL)"] = adjusted_samples_table.apply(total_volume, axis=1)
        adjusted_samples_table["Nb of samples"] = adjusted_samples_table.apply(nb_sample, axis=1)
        adjusted_samples_table["Volume to charge (µL)"] = adjusted_samples_table.apply(vol_to_charge, axis=1)

        styled_table = adjusted_samples_table.style.apply(lambda row: ['background-color: red' if row["Nb of samples"] <= 1 else 'background-color: orange' if row["Nb of samples"] == 2 else '' for _ in row], axis=1)

        st.markdown("**For a Master Mix**", help="Here, the sample is prepared for several samples at the same time, depending on the volume of char in the Western Blot (it's a Master Mix).")
        st.dataframe(styled_table, hide_index=True)

        one_sample = samples_table.copy()
        one_sample["Adjusted conc. (µg/µL)"] = adjusted_samples_table["Adjusted conc. (µg/µL)"]
        one_sample["Sample volume (µL)"] = one_sample.apply(sample_vol_OS, axis=1)
        one_sample["Lysis buffer to add (µL)"] = one_sample.apply(LyB_to_add_OS, axis=1)
        one_sample["Loading buffer (µL)"] = one_sample.apply(loading_buffer_OS, axis=1)
        one_sample["Total volume (µL)"] = one_sample.apply(total_volume_OS, axis=1)
        one_sample["Nb of samples"] = one_sample.apply(nb_sample_OS, axis=1)

        styled_table_OS = one_sample.style.apply(lambda row: ['background-color: red' if row["Nb of samples"] <= 1 else 'background-color: orange' if row["Nb of samples"] == 2 else '' for _ in row], axis=1)

        st.markdown("**For one sample**", help="Here, the sample is prepared for several samples at the same time, depending on the volume of char in the Western Blot (it's a Master Mix).")
        st.dataframe(styled_table_OS, hide_index=True)