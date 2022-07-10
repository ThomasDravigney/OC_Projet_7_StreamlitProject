import streamlit as st
import math
import plotly.graph_objects as go
import altair as alt


results = {
    0: {'label': 'défavorable (P < 0.5)', 'color': 'red', 'range': (0, 0.5), 'label_caps': 'DÉFAVORABLE'},
    1: {'label': 'favorable (P > 0.5)', 'color': 'yellow', 'range': (0.5, 0.7), 'label_caps': 'FAVORABLE'},
    2: {'label': 'très favorable (P > 0.7)', 'color': 'green', 'range': (0.7, 1), 'label_caps': 'TRÈS FAVORABLE'},
}


def match_proba_result(x, results):
    for key, value in results.items():
        if value['range'][0] < x < value['range'][1]:
            return key


def get_client_info_table(data):
    client_info = data.loc[['DAYS_BIRTH', 'CNT_FAM_MEMBERS', 'AMT_INCOME_TOTAL', 'FLAG_OWN_REALTY', 'FLAG_OWN_CAR']].copy()
    client_info['DAYS_BIRTH'] = abs(math.floor(client_info['DAYS_BIRTH'] / 365))
    client_info['NAME_FAMILY_STATUS'] = data.loc[[col for col in data.index if col.startswith('NAME_FAMILY_STATUS')]].idxmax().split('_')[-1]

    client_info = client_info.reindex(['DAYS_BIRTH', 'NAME_FAMILY_STATUS', 'CNT_FAM_MEMBERS', 'FLAG_OWN_REALTY', 'FLAG_OWN_CAR'])
    client_info.rename({'DAYS_BIRTH': 'Âge', 'NAME_FAMILY_STATUS': 'Situation familiale', 'CNT_FAM_MEMBERS': 'Taille du foyer',
                        'FLAG_OWN_REALTY': 'Propriétaire d\'un logement', 'FLAG_OWN_CAR': 'Propriétaire d\'un véhicule'}, inplace=True)
    client_info.name = 'Info client'
    return client_info


def get_loan_info_table(data):
    loan_info = data.loc[['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY']].copy()
    loan_info['NAME_INCOME_TYPE'] = data.loc[[col for col in data.index if col.startswith('NAME_INCOME_TYPE')]].idxmax().split('_')[-1]
    loan_info['NAME_CONTRACT_TYPE'] = data.loc[[col for col in data.index if col.startswith('NAME_CONTRACT_TYPE')]].idxmax().split('_')[-1]

    loan_info = loan_info.reindex(['NAME_INCOME_TYPE', 'AMT_INCOME_TOTAL', 'NAME_CONTRACT_TYPE', 'AMT_CREDIT', 'AMT_ANNUITY'])
    loan_info.rename({'NAME_INCOME_TYPE': 'Source des revenus', 'AMT_INCOME_TOTAL': 'Montant des revenus', 'NAME_CONTRACT_TYPE': 'Type du crédit',
                      'AMT_CREDIT': 'Montant du crédit', 'AMT_ANNUITY': 'Montant des annuités'}, inplace=True)
    loan_info.name = 'Info crédit'
    return loan_info


def get_proba_chart(target_proba, result):
    chart_proba = go.Figure(go.Indicator(
        mode='gauge+number',
        value=target_proba,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Probabilité de gain :'},
        gauge={'axis': {'range': [0, 1]}, 'bar': {'color': result['color']}}
    ))
    return chart_proba


def get_feature_importance_chart(metadata, result, size=10):
    metadata['feature_importance'] = -metadata['feature_importance']  # score reversal for class 0
    chart_feature_importance = alt.Chart(metadata.head(size)).mark_bar(color=result['color']).encode(
        x='feature_importance:Q',
        y=alt.Y('feature_name:O', sort={'field': 'x'}),
        tooltip=['feature_description']
    ).properties(height=500)
    return chart_feature_importance


def get_feature_exploration_chart(all_data, reindex, data, results):
    all_data['RESULT_ID'] = all_data['TARGET_PROBA'].apply(match_proba_result, results=results)
    idx_0 = all_data[all_data['RESULT_ID'] == 0].index
    idx_1 = all_data[all_data['RESULT_ID'] == 1].index
    idx_2 = all_data[all_data['RESULT_ID'] == 2].index
    filtered_data = all_data.drop(['TARGET', 'TARGET_PROBA', 'RESULT_ID'], axis=1).reindex(reindex, axis=1)
    filtered_data['RESULT_TEXT'] = all_data['RESULT_ID'].apply(lambda x: results[x]['label_caps'])

    filter = st.selectbox(
        label='Choisir une variable :',
        options=filtered_data.columns
    )

    st.write(f"""
    Crédit sélectionné | **{filter}** = **{round(data.loc[filter], 2)}**
    """)

    chart_exploration = go.Figure()
    chart_exploration.update_layout(showlegend=False)
    chart_exploration.add_trace(
        go.Violin(x=filtered_data.loc[idx_0]['RESULT_TEXT'], y=filtered_data.loc[idx_0][filter],
                  name=results[0]['label_caps'], fillcolor=results[0]['color'], box_visible=True,
                  line_color='black', meanline_visible=True, opacity=0.5, x0=filter))
    chart_exploration.add_trace(
        go.Violin(x=filtered_data.loc[idx_1]['RESULT_TEXT'], y=filtered_data.loc[idx_1][filter],
                  name=results[1]['label_caps'], fillcolor=results[1]['color'], box_visible=True,
                  line_color='black', meanline_visible=True, opacity=0.5, x0=filter))
    chart_exploration.add_trace(
        go.Violin(x=filtered_data.loc[idx_2]['RESULT_TEXT'], y=filtered_data.loc[idx_2][filter],
                  name=results[2]['label_caps'], fillcolor=results[2]['color'], box_visible=True,
                  line_color='black', meanline_visible=True, opacity=0.5, x0=filter))
    return chart_exploration
