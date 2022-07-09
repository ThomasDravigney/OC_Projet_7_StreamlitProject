import streamlit as st
import math
import plotly.graph_objects as go
from functions import get_all_id, get_all_data, get_data_from_id, get_metadata_from_id


st.title('Outil de scoring crédit')

id_list = get_all_id()
id = st.selectbox('ID du crédit :', id_list)
data = get_data_from_id(id, as_df=True)
target_proba = data.loc['TARGET_PROBA']


st.write("""
## Informations générales
""")

col_client_info, col_loan_info = st.columns(2)

with col_client_info:
    client_info = data.loc[['DAYS_BIRTH', 'CNT_FAM_MEMBERS', 'AMT_INCOME_TOTAL', 'FLAG_OWN_REALTY', 'FLAG_OWN_CAR']].copy()
    client_info['DAYS_BIRTH'] = abs(math.floor(client_info['DAYS_BIRTH'] / 365))
    client_info['NAME_FAMILY_STATUS'] = data.loc[[col for col in data.index if col.startswith('NAME_FAMILY_STATUS')]].idxmax().split('_')[-1]

    client_info = client_info.reindex(['DAYS_BIRTH', 'NAME_FAMILY_STATUS', 'CNT_FAM_MEMBERS', 'FLAG_OWN_REALTY', 'FLAG_OWN_CAR'])
    client_info.rename({'DAYS_BIRTH': 'Âge', 'NAME_FAMILY_STATUS': 'Situation familiale', 'CNT_FAM_MEMBERS': 'Taille du foyer',
                        'FLAG_OWN_REALTY': 'Propriétaire d\'un logement', 'FLAG_OWN_CAR': 'Propriétaire d\'un véhicule'}, inplace=True)
    client_info.name = 'Info client'
    st.table(client_info.astype('str'))

with col_loan_info:
    loan_info = data.loc[['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY']].copy()
    loan_info['NAME_INCOME_TYPE'] = data.loc[[col for col in data.index if col.startswith('NAME_INCOME_TYPE')]].idxmax().split('_')[-1]
    loan_info['NAME_CONTRACT_TYPE'] = data.loc[[col for col in data.index if col.startswith('NAME_CONTRACT_TYPE')]].idxmax().split('_')[-1]

    loan_info = loan_info.reindex(['NAME_INCOME_TYPE', 'AMT_INCOME_TOTAL', 'NAME_CONTRACT_TYPE', 'AMT_CREDIT', 'AMT_ANNUITY'])
    loan_info.rename({'NAME_INCOME_TYPE': 'Source des revenus', 'AMT_INCOME_TOTAL': 'Montant des revenus', 'NAME_CONTRACT_TYPE': 'Type du crédit',
                      'AMT_CREDIT': 'Montant du crédit', 'AMT_ANNUITY': 'Montant des annuités'}, inplace=True)
    loan_info.name = 'Info crédit'
    st.table(loan_info.astype('str'))


st.write("""
## Résultat : Crédit {}.
""".format('accordé' if target_proba > 0.5 else 'refusé'))

color_code = 'red'
if target_proba > 0.5: color_code = 'yellow'
if target_proba > 0.7: color_code = 'green'

fig = go.Figure(go.Indicator(
    mode='gauge+number',
    value=target_proba,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': 'Probabilité de remboursement'},
    gauge={'axis': {'range': [0, 1]}, 'bar': {'color': color_code}}))

st.plotly_chart(fig, use_container_width=True)
