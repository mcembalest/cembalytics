from bs4 import BeautifulSoup
import json
import requests

def parse_number_of_downloads(number_str):
    number_str = number_str.replace(",", "")
    if 'M' in number_str:
        return float(number_str.replace('M', '')) * 1_000_000
    elif 'K' in number_str:
        return float(number_str.replace('K', '')) * 1_000
    return float(number_str)

def get_ollama_data(model_type=None, n_top_models=30):
    url = 'https://ollama.com/search'
    if model_type:
        url += f'?c={model_type}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    models_data = []

    for model in soup.find_all('li', attrs={'x-test-model': True}):
        name = model.find('span', attrs={'x-test-search-response-title': True}).text
        pulls = parse_number_of_downloads(model.find('span', attrs={'x-test-pull-count': True}).text)
        models_data.append({'name': name, 'pulls': pulls})
    return sorted(models_data, key=lambda x: x['pulls'])[-n_top_models:]

def get_huggingface_data(model_type=None, n_top_models=30):
    url = "https://huggingface.co/api/models"
    params = {
        "sort": "downloads",
        "limit": n_top_models,
        "full": "true"
    }
    if model_type:
        params["filter"] = model_type
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    models = response.json()
    models_data = [{'name': model['id'], 'downloads': model['downloads']} for model in models]
    return sorted(models_data, key=lambda x: x['downloads'])

def format_downloads_data_for_plotly(data, title, left_margin=200, right_margin=20):
    plot_layout = {
        "title": title,
        "titlefont": {"size": 22},
        "height": 700,
        "margin": {"l": left_margin, "r": right_margin, "t": 100, "b": 70},
        "plot_bgcolor": "white",
        "xaxis": {
            "standoff": 20,
            "title": "Downloads", 
            "titlefont": {"size": 18}
        },
        "yaxis": {
            "standoff": 20,
            "titlefont": {"size": 18},
            "tickfont": {"size": 12}
        },
        "dragmode": False,
        "autosize": True,
        "responsive": True
    }
    x_values = [model.get('pulls', model.get('downloads', 0)) for model in data]
    y_values = [model['name'] for model in data]
    
    return json.dumps({
        "data": [{
            "x": x_values,
            "y": y_values,
            "type": "bar",
            "orientation": "h"
        }],
        "layout": plot_layout,
        "config": {
            "responsive": True,
            "displayModeBar": False,
            "width": None,
            "height": None
        }
    })