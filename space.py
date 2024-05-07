import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import matplotlib.colors as mcolors
from PIL import Image

# SET PAGE
st.set_page_config(
    page_title="Space Mission Dashboard",
    page_icon=":🚀:",
    layout="wide", )

with open ("streamlit.css") as f:
    st.markdown(f'<style> {f.read()} </style>', unsafe_allow_html=True)


# READ EXCEL
@st.cache_data
def read_data():
    df = pd.read_csv('Space_Missions.csv')
    return df

df = read_data()
df['Date'] = df['Datum'].str[ :16] 
df['Time'] = df['Datum'].str[17:22]
df[['LocationPart', 'Country']] = df['Location'].apply(lambda x: pd.Series(str(x).rsplit(', ', 1)))
df[['RocketName', 'Mission']] = df['Detail'].apply(lambda x: pd.Series(str(x).split('|', 1)))
df = df.iloc[:, 2:]
df['Year'] = pd.to_datetime(df['Date'], format='%a %b %d, %Y').dt.year
image_sider= Image.open("imgs/pexels-alex-andrews-271121-1983032.jpg")
image= Image.open("imgs/pexels-spacex-23769.jpg")

# SIDEBAR
with st.sidebar:
    st.title("Space Mission by Country")
    st.image(image_sider)
    st.header("Filters:")

country = st.sidebar.multiselect(
    "Select the Country:",
    options=df["Country"].unique(),
    default=df["Country"].unique(),
)

df_selection = df.query(
   "Country == @country"
)

# if the dataframe is empty
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()


# TITLE📡🪐  
st.title("Space Mission Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# METRICS
totalMissions = len(df)
print("Total missions:", totalMissions)
totalSuccessMissions = len(df[df['Status Mission'] == 'Success'])
print("Total missions:", totalSuccessMissions)
totalFailureMission = len(df[df['Status Mission'] == 'Failure'])
print("Total missions:", totalFailureMission )

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Total Missions:", value=totalMissions)
with kpi2:
    st.metric(label="Total Success Missions", value=totalSuccessMissions)
with kpi3:
    st.metric(label = "Total Failure Missions", value = totalFailureMission )
st.markdown("""---""")

st.image(image)
# Custom Colors Style
custom_colors= ['#C46400', '#365BDD', '#11208F' ]
custom_colors2= ['#C46400','#3E529B','#11208F']
custom_colors3=['#C46400', '#11208F',]
custom_cmap = mcolors.ListedColormap(['#C46400'] + 3*['#EEEDF4'] + ['#11208F'])
custom_cmap2 = mcolors.ListedColormap(['#C46400'] + 5*['#EEEDF4'] + ['#11208F'])
color_mission = {
    'Success': '#203FC4',
    'Failure': '#a21b1b',
    'Partial Failure': '#dd5c11',
    'Prelaunch Failure': '#EBC213'
}
color_mission2 = {
    'Success': '#284964',
    'Failure': '#a21b1b',
    'Partial Failure': '#dd5c11',
    'Prelaunch Failure': '#EBC213'
}

#LINECHART Missions by Year
missions_per_year = df_selection.groupby(['Year', 'Status Mission'])['Mission'].count().reset_index()
linechart = px.line(missions_per_year, x='Year', y='Mission', color="Status Mission", color_discrete_map=color_mission, title='Space Missions from 1957 to 2020')
linechart.update_xaxes(range=[df['Year'].min(), df['Year'].max()])
linechart.update_layout(
    plot_bgcolor='#0f0f0f',
    paper_bgcolor='#0f0f0f',
    xaxis=dict(
        tickmode='linear',
        tickangle=45,
        title=dict(text='', font=dict(color='white')),
        title_font={"size": 12}),        
    yaxis=dict(
        title=dict(text='Total Missions', font=dict(color='white')),
        title_font={"size": 12}),
     legend=dict(
        title_font=dict(color='white'),
        font=dict(color='white')),
    title=dict(
        font=dict(color="white", size=22),
        x=0.05,
        y=0.95 ),
    hovermode='closest')
st.plotly_chart(linechart, use_container_width=True)


# Create a choropleth map
MissionByCountry = df_selection.groupby(by=['Country'], as_index=False)['Mission'].count()
custom_colors3= ['#8F3000', '#284964' ,'#11208F' ]
MissionByCountryMap = px.choropleth(MissionByCountry, 
                    locations="Country", 
                    locationmode='country names',
                    color="Mission",
                    hover_name="Country",
                    color_continuous_scale=custom_colors3,
                    title="Number of Missions by Country"
                   )
MissionByCountryMap.update_layout(
    geo=dict(
        showcoastlines=True,
        projection_type='hammer',
        scope="world",
        showland=False,  # Hide land area
        bgcolor='#0f0f0f',
    ),
    plot_bgcolor='#0f0f0f',
    paper_bgcolor='#0f0f0f',
    title=dict(
        font=dict(color="white", size=22),
        x=0.05,
        y=0.95 ),
)
st.plotly_chart(MissionByCountryMap , use_container_width=True)

# Pie charts Missions Status and Rocket Status
col1, col2 = st.columns(2)
MissionStatus = df_selection.groupby(by=["Status Mission"], as_index=False)["Mission"].count()
with col1:
    pieMissionStatus = px.pie(MissionStatus, values="Mission", names="Status Mission",color_discrete_map=color_mission,
                        hole=0.5, title="Mission by Status")
    pieMissionStatus.update_layout(
        font=dict(
            color="rgba(255, 255, 255, 1)",
            size=20),
        legend=dict(
            font=dict(color="white")),
        title=dict(
            font=dict(color="white", size=22, ),
            x=0.05, y=0.95),
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f')
    pieMissionStatus.update_traces(marker=dict(colors=['#a21b1b','#dd5c11','#A7A7AB','#284964'])) 
    st.plotly_chart(pieMissionStatus, use_container_width=True)

RocketStatus = df_selection.groupby(by=["Status Rocket"], as_index=False)["RocketName"].count()
with col2:
    pieRocketStatus = px.pie(RocketStatus, values="RocketName", names="Status Rocket",
                        hole=0.5, title="Rocket by Status")
    pieRocketStatus.update_layout(
        font=dict(
            color="rgba(255, 255, 255, 1)",
            size=20),
        legend=dict(
            font=dict(color="white")),
        title=dict(
            font=dict(color="white", size=22, ),
            x=0.05, y=0.95),
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f')
    pieRocketStatus.update_traces(marker=dict(colors=['#dd5c11','#284964'])) 
    st.plotly_chart(pieRocketStatus, use_container_width=True)

exp1, exp2 = st.columns(2)
MissionDetail = df_selection[["Detail", "Status Mission"]]
with exp1:
    with st.expander("Details about Mission and Status"):
        st.write(MissionDetail.style.background_gradient(cmap=custom_cmap2))
        csv = MissionDetail.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="DetailsOfMission.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

RocketDetail = df_selection[["RocketName", "Status Rocket"]]
with exp2:
    with st.expander("Details about Roket Status"):
        st.write(RocketDetail.style.background_gradient(cmap=custom_cmap2))
        csv = RocketDetail.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="DetailsByRocket.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

# Barcharts Missions by Company and Missions by Rocket
# Group by 'RocketName' and 'Status Mission' and count the number of missions for each combination
MissionsByRocket_sorted = df_selection.groupby(['RocketName', 'Status Mission'])['Mission'].count().reset_index().sort_values(by='Mission', ascending=False)
# Sort DataFrame by MissionCount in descending order and select top 15
top_15_rockets = MissionsByRocket_sorted.groupby('RocketName')['Mission'].sum().nlargest(15).index
df_filtered = MissionsByRocket_sorted[MissionsByRocket_sorted['RocketName'].isin(top_15_rockets)]

barchartRockets = px.bar(df_filtered,
                      x="RocketName",
                      y="Mission",
                      color='Status Mission',
                      color_discrete_map=color_mission2
                      )
barchartRockets.update_layout(
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f',
        legend=dict(
            font=dict(color="white")),
        xaxis=dict(
            tickfont=dict(color='white')),
        yaxis=dict(
            title=dict(text='Missions', font=dict(color='white')),
            title_font={"size": 16}, tickfont=dict(color='white')),
        title=dict(
            text="Top 15 - Missions by Rocket",
            font=dict(color="white", size=22),
            x=0.05, y=0.95),
        hovermode='closest')
st.plotly_chart(barchartRockets, use_container_width=True)

with st.expander("Missions by Rocket with Status"):
        st.write(MissionsByRocket_sorted.style.background_gradient(cmap=custom_cmap2))
        csv = MissionsByRocket_sorted.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="TotalMissionsbyRocket.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')



# Group by 'RocketName' and 'Status Mission'
MissionsByCompany_sorted = df_selection.groupby(['Company Name', 'Status Mission'])['Mission'].count().reset_index().sort_values(by='Mission', ascending=False)
# Sort DataFrame by MissionsCount in descending order and select top 15
top_15_companies = MissionsByCompany_sorted.groupby('Company Name')['Mission'].sum().nlargest(15).index
df_filtered2 = MissionsByCompany_sorted[MissionsByCompany_sorted['Company Name'].isin(top_15_companies)]

barchartCompanies = px.bar(df_filtered2,
                      x="Company Name",
                      y="Mission",
                      color='Status Mission',
                      color_discrete_map=color_mission2
)
barchartCompanies.update_layout(
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f',
        legend=dict(
            font=dict(color="white")),
        xaxis=dict(
            tickfont=dict(color='white')),
        yaxis=dict(
            title=dict(text='Missions', font=dict(color='white')),
            title_font={"size": 16}, tickfont=dict(color='white')),
        title=dict(
            text="Top 15 - Mission by Company",
            font=dict(color="white", size=22),
            x=0.05, y=0.95),
        hovermode='closest')
st.plotly_chart(barchartCompanies, use_container_width=True)


with st.expander("Missions by Company with Status"):
        st.write(MissionsByCompany_sorted.style.background_gradient(cmap=custom_cmap2))
        csv = MissionsByCompany_sorted.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="TotalMissionsbyCompany.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')
        

