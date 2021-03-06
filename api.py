import streamlit as st
import requests
import pandas as pd


def get_response(route):
    response = requests.get('https://tdr-oc-projet-7-fastapi.herokuapp.com/' + route)
    return response.json()


@st.cache(persist=True, allow_output_mutation=True)
def get_all_id():
    data = list(map(int, get_response('id')[1:-1].split(', ')))
    return data


@st.cache(persist=True, allow_output_mutation=True)
def get_all_data(as_df=False):
    data = get_response('data')
    if as_df:
        data = pd.read_json(data)
    return data


@st.cache(persist=True, allow_output_mutation=True)
def get_data_from_id(id, as_df=False):
    data = get_response(f'data/{id}')
    if as_df:
        data = pd.read_json(data, typ='series')
    return data


@st.cache(persist=True, allow_output_mutation=True)
def get_metadata_from_id(id, as_df=False):
    data = get_response(f'metadata/{id}')
    if as_df:
        data = pd.read_json(data)
    return data


if __name__ == '__main__':
    print(get_all_id())
