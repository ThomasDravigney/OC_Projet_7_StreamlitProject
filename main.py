import streamlit as st
from api import get_all_id, get_all_data, get_data_from_id, get_metadata_from_id
from functions import results, match_proba_result, get_client_info_table, get_loan_info_table, get_proba_chart,\
    get_feature_importance_chart, get_feature_exploration_chart


st.set_page_config(page_title='Dashboard - Scoring crédit')

st.title('Outil de scoring crédit')


# LOAD GLOBAL DATA
all_id = get_all_id()
all_data = get_all_data(as_df=True)


# LOAD SPECIFIC DATA
id = st.selectbox('ID du crédit :', all_id)
data = get_data_from_id(id, as_df=True)
metadata = get_metadata_from_id(id, as_df=True)
target_proba = data.loc['TARGET_PROBA']
result = results[match_proba_result(target_proba, results)]


# GENERAL INFO
st.write("""
## Informations générales
""")

col_client_info, col_loan_info = st.columns(2)

with col_client_info:
    st.table(get_client_info_table(data).astype('str'))

with col_loan_info:
    st.table(get_loan_info_table(data).astype('str'))


# CHART TARGET PROBA
st.write(f"""
## Résultat : {result['label']}
""")

st.plotly_chart(get_proba_chart(target_proba, result), use_container_width=True)


# CHART FEATURE IMPORTANCE
st.write("""
## Principaux critères de notation
""")

st.altair_chart(get_feature_importance_chart(metadata, result, size=10), use_container_width=True)


# CHART FEATURE EXPLORATION
st.write("""
## Exploration de variables
""")

st.plotly_chart(get_feature_exploration_chart(all_data, metadata['feature_name'], data, results), use_container_width=True)
