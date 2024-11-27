from datetime import datetime
from bs4 import BeautifulSoup
from fasthtml.common import fast_app, serve, Titled, Div, Script, H2, H3, P, A, Style
import json
import requests

custom_style = Style("""
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.7;
        margin: 0 auto;
        padding: 3rem;
        background: #4a9c7d;
        color: #1a202c;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    }

    h1, h2 {
        color: #1a365d;
        margin-bottom: 2rem;
        font-weight: 400;
        letter-spacing: -0.025em;
    }

    a {
        color: #3182ce;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 500;
        border-bottom: 1px solid transparent;
    }

    a:hover {
        color: #2c5282;
        border-bottom: 1px solid currentColor;
    }

    .chart-container {
        margin: 3rem 0;
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    @media (max-width: 768px) {
        body {
            padding: 1.5rem;
        }
        
        .container {
            padding: 1.5rem;
            border-radius: 12px;
        }
    }
""")

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

def plotly_format_data(data, title, left_margin=200, right_margin=20):
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
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('{div_id}');
        }});
        """
    )

app, rt = fast_app(hdrs=(Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),))

@rt("/")
def get():
    ollama_models = get_ollama_data()
    ollama_embedders = get_ollama_data(model_type='embedding')
    ollama_vlms = get_ollama_data(model_type='vision')

    huggingface_models = get_huggingface_data()
    huggingface_vlms = get_huggingface_data(model_type='image-text-to-text')
    huggingface_embedders = get_huggingface_data(model_type='sentence-similarity')
    
    ollama_plot_data = plotly_format_data(ollama_models, "Ollama Model Downloads<br>(lifetime)<br>")
    ollama_embedding_plot_data = plotly_format_data(ollama_embedders, "Ollama Embedding Model Downloads<br>(lifetime)<br>")
    ollama_vlm_plot_data = plotly_format_data(ollama_vlms, "Ollama VLM Downloads<br>(lifetime)<br>")
    
    huggingface_plot_data = plotly_format_data(huggingface_models, "HuggingFace Model Downloads<br>(last month)<br>", left_margin=400, right_margin=100)
    huggingface_embedding_plot_data = plotly_format_data(huggingface_embedders, "HuggingFace Embedding Model Downloads<br>(last month)<br>", left_margin=400, right_margin=100)
    huggingface_vlm_plot_data = plotly_format_data(huggingface_vlms, "HuggingFace VLM Downloads<br>(last month)<br>", left_margin=300, right_margin=100)

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    return Titled(
        "Cembalytics",
        Script('document.querySelector("meta[name=viewport]").setAttribute("content", "width=device-width, initial-scale=1.0, maximum-scale=1.0");'),
        Script(src="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap", rel="stylesheet"),
        custom_style,
        Div(
            P("My name is ", A("Max Cembalest", href="https://x.com/maxcembalest"), " and I'm interested in what the hell is going on with open-source AI, language models, vision language models, and embeddings."),
            P("This is a ", A("FastHTML", href="https://fastht.ml/"), " web application I built to visualize some statistics about model usage and performance (", A("source code on GitHub", href="https://github.com/mcembalest/cembalytics/"), ")."),
            H3("Sources (last downloaded ", current_time, "):"),
            P(A("HuggingFace", href="https://huggingface.co"), " is the de facto central platform where researchers and companies release their models & training datasets."),
            P(A("Ollama", href="https://ollama.com"), " provides a simple local API server for downloading, managing, and running AI models."),
            P(),
            P("Here's are the top models by download count from HuggingFace:"),
            Div(id="huggingfaceModels"),
            plotly_in_fasthtml("huggingfaceModels", huggingface_plot_data),
            P("And here are the top models by download count from Ollama:"),
            Div(id="ollamaModels"),
            plotly_in_fasthtml("ollamaModels", ollama_plot_data),
        ),
        Div(
            H2("Vision Language Models (VLMs)"),
            P("VLMs are rapidly becoming more capable and usable. Here are the current download counts for VLMs from HuggingFace:"),
            Div(id="huggingfaceVLMs"),
            plotly_in_fasthtml("huggingfaceVLMs", huggingface_vlm_plot_data),
            P("And here are the current download counts for VLMs via Ollama:"),
            Div(id="ollamaVLMs"),
            plotly_in_fasthtml("ollamaVLMs", ollama_vlm_plot_data),
        ),
        Div(
            H2("Embedding Models"),
            P("I'm particularly interested in embeddings. Here are the current download counts for embedding models from HuggingFace:"),
            Div(id="huggingfaceEmbeddings"),
            plotly_in_fasthtml("huggingfaceEmbeddings", huggingface_embedding_plot_data),
            P("And here are the current download counts for embedding models via Ollama:"),
            Div(id="ollamaEmbeddings"),
            plotly_in_fasthtml("ollamaEmbeddings", ollama_embedding_plot_data),
        )
    )

serve()