import requests
import pandas as pd


def get_response(route):
    response = requests.get('https://tdr-oc-projet-7-fastapi.herokuapp.com/' + route)
    return response.json()


def get_all_id():
    return get_response('id')


def get_all_data(as_df=False):
    data = get_response('data')
    if as_df:
        return pd.read_json(data)
    return data


def get_client_data(id, as_df=False):
    data = get_response(f'data/{id}')
    if as_df:
        return pd.read_json(data, typ='series')
    return data


def get_client_metadata(id, as_df=False):
    data = get_response(f'metadata/{id}')
    if as_df:
        return pd.read_json(data)
    return data


if __name__ == '__main__':
    print(get_client_metadata(141410, as_df=True))
