from bs4 import BeautifulSoup
from fasthtml.common import fast_app, serve, Titled, Div, Script, H2, P, A
import json
import requests

def get_ollama_data(model_type=None):
    url = 'https://ollama.com/search'
    if model_type:
        url += f'?c={model_type}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    models_data = []

    def parse_number_of_ollama_downloads(number_str):
        number_str = number_str.replace(",", "")
        if 'M' in number_str:
            return float(number_str.replace('M', '')) * 1_000_000
        elif 'K' in number_str:
            return float(number_str.replace('K', '')) * 1_000
        return float(number_str)

    for model in soup.find_all('li', attrs={'x-test-model': True}):
        name = model.find('span', attrs={'x-test-search-response-title': True}).text
        pulls = parse_number_of_ollama_downloads(model.find('span', attrs={'x-test-pull-count': True}).text)
        models_data.append({'name': name, 'pulls': pulls})
    return sorted(models_data, key=lambda x: x['pulls'])[-20:]

def plotly_format_data(data, title):
    plot_layout = {
        "title": title,
        "titlefont": {"size": 15},
        "height": 700,
        "margin": {"l": 250, "r": 20, "t": 60, "b": 70},
        "plot_bgcolor": "white",
        "xaxis": {
            "standoff": 10,
            "title": "Downloads", 
            "titlefont": {"size": 22}
        },
        "yaxis": {
            "standoff": 10,
            "title": "Model", 
            "titlefont": {"size": 22},
            "tickfont": {"size": 16}
        },
        "dragmode": False,
        "autosize": True,
        "responsive": True
    }
    return json.dumps({
        "data": [{
            "x": [model['pulls'] for model in data],
            "y": [model['name'] for model in data],
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

def plotly_in_fasthtml(div_id, plot_data):
    return Script(
        f"""
        var d = {plot_data};
        var config = {{
            displayModeBar: false,
            responsive: true,
            useResizeHandler: true
        }};
        Plotly.newPlot('{div_id}', d.data, d.layout, config);
        
        // Add resize handler
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('{div_id}');
        }});
        """
    )

app, rt = fast_app(hdrs=(Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),))

@rt("/")
def get():
    ollama_models = get_ollama_data()
    ollama_embedding_models = get_ollama_data(model_type='embedding')
    
    plot_data = plotly_format_data(ollama_models, "Ollama Model Downloads")
    embedding_plot_data = plotly_format_data(ollama_embedding_models, "Ollama Embedding Model Downloads")

    return Titled(
        "Cembalytics",
        Script('document.querySelector("meta[name=viewport]").setAttribute("content", "width=device-width, initial-scale=1.0, maximum-scale=1.0");'),
        Div(
            P("My name is ", A("Max Cembalest", href="https://x.com/maxcembalest"), " and I'm interested in what's going on with open source AI & LLMs."),
            P("This is a ", A("FastHTML", href="https://fastht.ml/"), " web application I built to visualize real-time stats of downloads from various model providers."),
            P(
                "This chart shows current model download counts from ", A("ollama", href="https://ollama.com"), ":",
                cls="description"
            ),
            Div(id="plotDiv"),
        ),
        plotly_in_fasthtml("plotDiv", plot_data),
        Div(
            H2("Embedding models"),
            P(
                "I'm particularly interested in embeddings. This chart shows download counts for embedding models on ollama"
            ),
            Div(id="plotDivEmbeddings"),
        ),
        plotly_in_fasthtml("plotDivEmbeddings", embedding_plot_data)
    )

serve()