import os
import platform

import streamlit as st

local_test = platform.processor()


# Page config and sidebar
def page_config(logo=None, tool_expanded=None, hide_licence=None):
    if st.get_option("client.showSidebarNavigation") is True:
        st.set_option("client.showSidebarNavigation", False)
        st.rerun()
    st.set_page_config(page_title="LabMaster", page_icon="🔬", initial_sidebar_state="expanded", layout="wide")

    # Main page
    img_path = os.path.join(os.path.dirname(__file__), '../img', 'labmaster_logo.png')

    st.logo(img_path)
    if logo is True:
        st.sidebar.image(img_path)
    st.sidebar.title('👩🏼‍🔬 LabMaster')
    st.sidebar.write("Created by Minniti Julien")

    # Button sidebar
    colsb1, colsb2, colsb3 = st.sidebar.columns(3, gap="small")
    colsb1.link_button("Help ⁉", '')
    colsb2.link_button('GitHub', 'https://github.com/Jumitti/BlotMaster')
    if local_test == "":
        colsb3.link_button('Download app 📥', 'https://github.com/Jumitti/BlotMaster/releases')
    else:
        colsb3.link_button('Web app 🌐', 'https://blotmaster.streamlit.app/')

    # Table
    st.sidebar.divider()
    st.sidebar.page_link("labmaster.py", label="**Home**", icon="🏠")
    with st.sidebar.expander("Tools", expanded=True if tool_expanded is not False else False):
        st.page_link("pages/RT-qPCR.py", label="RT-qPCR")
        st.page_link("pages/transfection.py", label="Transfection")
        st.page_link("pages/venn_diagram.py", label="Venn diagram")
        st.page_link("pages/westernblot.py", label="Western Blot")

    # Licence <-- I preferred to add it like this to allow you to always use the sidebar and add the license afterwards (like in pages/transfection.py)
    if hide_licence is not True:
        licence()


# MIT licence
def licence():
    st.sidebar.divider()
    st.sidebar.link_button('Under MIT licence', 'https://github.com/Jumitti/BlotMaster/blob/main/LICENSE')