import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. KONFIGURATION AV SIDAN ---
# Ställer in titel, ikon och layout för webbappen
st.set_page_config(
    page_title="Analys av Detaljhandelsförsäljning",
    page_icon="🛍️",
    layout="wide"
)

# --- 2. LADDA OCH FÖRBEREDA DATA ---
# Vi använder cache för att slippa ladda om filen varje gång användaren ändrar ett filter
@st.cache_data
def load_and_clean_data():
    # Läs in datasetet
    df = pd.read_csv("data/retail_sales_dataset.csv")
    
    # Konvertera datumkolumnen till datetime-format för tidsserieanalys
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Skapa nya kolumner för att kunna analysera trender per månad och veckodag
    df['Month'] = df['Date'].dt.month_name()
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Year_Month'] = df['Date'].dt.to_period('M').astype(str)
    
    # Dela upp kunderna i åldersgrupper för en tydligare demografisk bild
    bins = [0, 25, 35, 45, 55, 100]
    labels = ['18-24', '25-34', '35-44', '45-54', '55+']
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    return df

# Försök ladda data och visa felmeddelande om filen saknas
try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("Fel: Hittade inte 'retail_sales_dataset.csv'. Kontrollera att filen ligger i rätt mapp.")
    st.stop()

# --- 3. SIDOPANEL (FILTER) ---
st.sidebar.header("Filter för Dashboard")

# Datumfilter: Låter användaren välja en specifik tidsperiod
min_date = df['Date'].min().to_pydatetime()
max_date = df['Date'].max().to_pydatetime()
date_range = st.sidebar.date_input("Välj tidsperiod:", [min_date, max_date])

# Kategorifilter: Möjliggör jämförelse mellan olika produkttyper
categories = st.sidebar.multiselect(
    "Välj produktkategorier:",
    options=df["Product Category"].unique(),
    default=df["Product Category"].unique()
)

# Könsfilter: Analysera köpmönster baserat på kön
genders = st.sidebar.multiselect(
    "Välj kön:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Logik för att applicera valda filter på dataramen (dataframe)
mask = (
    (df['Date'].dt.date >= date_range[0]) & 
    (df['Date'].dt.date <= date_range[1]) &
    (df['Product Category'].isin(categories)) &
    (df['Gender'].isin(genders))
)
df_filtered = df.loc[mask]

# --- 4. HUVUDLAYOUT & NYCKELTAL ---
st.title("📊 Analys av Detaljhandel")
st.markdown("""
Denna dashboard ger en djupdykning i transaktionsdata för att identifiera kundbeteenden, 
produktprestanda och säsongstrender. Använd filtren till vänster för att anpassa vyn.
""")

# Visa viktiga nyckeltal i kolumner för en snabb överblick
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Intäkt", f"${df_filtered['Total Amount'].sum():,.0f}")
col2.metric("Antal Transaktioner", f"{len(df_filtered):,}")
col3.metric("Snittvärde per köp", f"${df_filtered['Total Amount'].mean():.2f}")
col4.metric("Snittålder (Kund)", f"{df_filtered['Age'].mean():.1f} år")

st.divider()

# --- 5. VISUALISERINGAR ---

# Rad 1: Tidstrender
st.subheader("📈 Måntlig Försäljningstrend")
trend_data = df_filtered.groupby('Year_Month')['Total Amount'].sum()
st.line_chart(trend_data)
st.caption("Diagrammet visar den totala försäljningsutvecklingen över den valda tidsperioden.")

# Rad 2: Demografi & Kategorier
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Intäkter per Åldersgrupp")
    fig1, ax1 = plt.subplots()
    # Barplot för att se vilken åldersgrupp som spenderar mest totalt sett
    sns.barplot(data=df_filtered, x='Age Group', y='Total Amount', estimator=sum, palette='viridis', ax=ax1)
    ax1.set_ylabel("Total Försäljning ($)")
    st.pyplot(fig1)
    st.info("Insikt: Detta visar vilket ålderssegment som genererar mest värde för verksamheten.")

with col_right:
    st.subheader("Fördelning av köp per Kön")
    fig2, ax2 = plt.subplots()
    # Cirkeldiagram för att se den procentuella fördelningen mellan könen
    gender_counts = df_filtered['Gender'].value_counts()
    ax2.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140, colors=['#87CEEB','#FFB6C1'])
    st.pyplot(fig2)

# Rad 3: Veckodagar & Prisspridning
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Populäraste Shoppingdagarna")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig3, ax3 = plt.subplots()
    # Countplot för att se frekvensen av transaktioner per veckodag
    sns.countplot(data=df_filtered, x='Day_of_Week', order=day_order, palette='magma', ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

with col_b:
    st.subheader("Fördelning av Transaktionsvärde")
    fig4, ax4 = plt.subplots()
    # Violinplot visar både spridning och täthet (var de flesta köpen landar prismässigt)
    sns.violinplot(data=df_filtered, x='Product Category', y='Total Amount', ax=ax4)
    plt.xticks(rotation=45)
    st.pyplot(fig4)
    st.info("Analys: Här ser vi hur köpbeloppen fördelar sig inom varje kategori.")

# --- 6. DATAUTFORSKARE ---
st.divider()
with st.expander("Visa Filtrerad Rådata"):
    # Gör det möjligt för läraren att se datan bakom graferna
    st.write(df_filtered)
