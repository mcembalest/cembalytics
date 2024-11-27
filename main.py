from bs4 import BeautifulSoup
from fasthtml.common import fast_app, serve, Titled, Div, Script
import json
import requests

app, rt = fast_app(hdrs=(Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),))

def parse_number(number_str):
    number_str = number_str.replace(",", "")
    if 'M' in number_str:
        return float(number_str.replace('M', '')) * 1_000_000
    elif 'K' in number_str:
        return float(number_str.replace('K', '')) * 1_000
    return float(number_str)

def get_ollama_data():
    response = requests.get('https://ollama.com/search')
    soup = BeautifulSoup(response.text, 'html.parser')
    models_data = []
    for model in soup.find_all('li', attrs={'x-test-model': True}):
        name = model.find('span', attrs={'x-test-search-response-title': True}).text
        pulls = parse_number(model.find('span', attrs={'x-test-pull-count': True}).text)
        models_data.append({'name': name, 'pulls': pulls})
    return sorted(models_data, key=lambda x: x['pulls'], reverse=True)[:20]

@rt("/")
def get():
    models = get_ollama_data()
    
    plot_data = json.dumps({
        "data": [{
            "x": [model['pulls'] for model in models][::-1],
            "y": [model['name'] for model in models][::-1],
            "type": "bar",
            "orientation": "h"
        }],
        "layout": {
            "title": "Ollama",
            "titlefont": {"size": 20},
            "height": 700,
            "margin": {"l": 150, "r": 20, "t": 40, "b": 50},
            "showlegend": False,
            "plot_bgcolor": "white",
            "xaxis": {"title": "Downloads", "titlefont": {"size": 18}},
            "yaxis": {"title": "Model", "titlefont": {"size": 18}}
        }
    })

    return Titled("Cembalytics", 
                 Div(id="plotDiv"),
                 Script(f"Plotly.newPlot('plotDiv', {plot_data}.data, {plot_data}.layout);"))

serve()