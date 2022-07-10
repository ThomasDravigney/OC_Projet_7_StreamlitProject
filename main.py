import streamlit as st
import math
import plotly.graph_objects as go
import altair as alt
from api import get_all_id, get_all_data, get_data_from_id, get_metadata_from_id
from functions import match_proba_result

primary_color = '#8375A9'

results = {
    0: {'label': 'défavorable (P < 0.5)', 'color': 'red', 'range': (0, 0.5), 'label_caps': 'DÉFAVORABLE'},
    1: {'label': 'favorable (P > 0.5)', 'color': 'yellow', 'range': (0.5, 0.7), 'label_caps': 'FAVORABLE'},
    2: {'label': 'très favorable (P > 0.7)', 'color': 'green', 'range': (0.7, 1), 'label_caps': 'TRÈS FAVORABLE'},
}

st.title('Outil de scoring crédit')

all_id = get_all_id()
all_data = get_all_data(as_df=True)
all_data['RESULT_ID'] = all_data['TARGET_PROBA'].apply(match_proba_result, results=results)
results_series = all_data['RESULT_ID'].apply(lambda x: results[x]['label_caps'])
id = st.selectbox('ID du crédit :', all_id)
data = get_data_from_id(id, as_df=True)
metadata = get_metadata_from_id(id, as_df=True)
metadata['feature_importance'] = -metadata['feature_importance']  # score reversal for class 0
target_proba = data.loc['TARGET_PROBA']
result = results[match_proba_result(target_proba, results)]


# general info
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


# Target proba chart
st.write(f"""
## Résultat : {result['label']}
""")

chart_proba = go.Figure(go.Indicator(
    mode='gauge+number',
    value=target_proba,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': 'Probabilité de remboursement :'},
    gauge={'axis': {'range': [0, 1]}, 'bar': {'color': result['color']}}))
st.plotly_chart(chart_proba, use_container_width=True)


# Feature importance chart
st.write("""
## Principaux critères de notation
""")

chart_feature_importance = alt.Chart(metadata.head(10)).mark_bar(color=result['color']).encode(
    x='feature_importance:Q',
    y=alt.Y('feature_name:O', sort={'field': 'x'}),
    tooltip=['feature_description']
).properties(height=500)
st.altair_chart(chart_feature_importance, use_container_width=True)


# Exploration chart
st.write("""
## Exploration de variables
""")

idx_0 = all_data[all_data['RESULT_ID'] == 0].index
idx_1 = all_data[all_data['RESULT_ID'] == 1].index
idx_2 = all_data[all_data['RESULT_ID'] == 2].index
filtered_data = all_data.drop(['TARGET', 'TARGET_PROBA', 'RESULT_ID'], axis=1).reindex(metadata['feature_name'], axis=1)
filtered_data['RESULT_TEXT'] = results_series

filter_column = st.selectbox(
    label='Choisir une variable :',
    options=filtered_data.columns
)

st.write(f"""
Crédit sélectionné | **{filter_column}** = **{round(data.loc[filter_column], 2)}**
""")

chart_exploration = go.Figure()
chart_exploration.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1))
chart_exploration.add_trace(go.Violin(x=filtered_data.loc[idx_0]['RESULT_TEXT'], y=filtered_data.loc[idx_0][filter_column],
                                      name=results[0]['label_caps'], fillcolor=results[0]['color'], box_visible=True,
                                      line_color='black', meanline_visible=True, opacity=0.5, x0=filter_column))
chart_exploration.add_trace(go.Violin(x=filtered_data.loc[idx_1]['RESULT_TEXT'], y=filtered_data.loc[idx_1][filter_column],
                                      name=results[1]['label_caps'], fillcolor=results[1]['color'], box_visible=True,
                                      line_color='black', meanline_visible=True, opacity=0.5, x0=filter_column))
chart_exploration.add_trace(go.Violin(x=filtered_data.loc[idx_2]['RESULT_TEXT'], y=filtered_data.loc[idx_2][filter_column],
                                      name=results[2]['label_caps'], fillcolor=results[2]['color'], box_visible=True,
                                      line_color='black', meanline_visible=True, opacity=0.5, x0=filter_column))
st.plotly_chart(chart_exploration, use_container_width=True)
