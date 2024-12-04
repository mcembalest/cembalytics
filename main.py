from datetime import datetime
from fasthtml.common import *

from style import custom_style, format_plotly_in_fasthtml
from download_stats import get_huggingface_data, get_ollama_data, format_downloads_data_for_plotly

app, rt = fast_app(hdrs=(Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),))

@rt("/")
def get():
    return Titled(
        "Cembalytics",
        Script('document.querySelector("meta[name=viewport]").setAttribute("content", "width=device-width, initial-scale=1.0, maximum-scale=1.0");'),
        Script(src="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap", rel="stylesheet"),
        custom_style,
        Div(
            P("My name is ", A("Max Cembalest", href="https://x.com/maxcembalest"), " and I'm interested in what the hell is going on with open-source AI, language models, vision language models, and embedding models."),
            P("This is a ", A("FastHTML", href="https://fastht.ml/"), " web application I built to share some views of the current landscape of AI models. I'm capturing their download counts across a few platforms, their scores on key benchmark tests, and the contents of their weights."),
            Div(
                A(
                    Span("Downloads", cls="button-text"),
                    Img(src="img/downloads.png", alt="Model Downloads"),
                    href="/downloads",
                    cls="image-button",
                ),
                A(
                    Span("Benchmarks", cls="button-text"),
                    Img(src="img/comparison.png", alt="Model Benchmarks"),
                    href="/benchmarks",
                    cls="image-button"
                ),
                A(
                    Span("Weights Analysis", cls="button-text"),
                    Img(src="img/network.png", alt="Model Analysis"),
                    href="/weights-analysis",
                    cls="image-button"
                ),
                cls="button-container"
            ),
            P("The source code for this site is ", A("here", href="https://github.com/mcembalest/cembalytics/"), " on GitHub."),
            P("If you have have feedback or suggestions for improvement, please open an issue in the repo!")
        )
    )

@rt("/downloads")
def get():
    ollama_models = get_ollama_data()
    ollama_embedders = get_ollama_data(model_type='embedding')
    ollama_vlms = get_ollama_data(model_type='vision')

    huggingface_models = get_huggingface_data()
    huggingface_vlms = get_huggingface_data(model_type='image-text-to-text')
    huggingface_embedders = get_huggingface_data(model_type='sentence-similarity')

    ollama_plot_data = format_downloads_data_for_plotly(ollama_models, "Ollama Model Downloads<br>(lifetime)<br>")
    ollama_embedding_plot_data = format_downloads_data_for_plotly(ollama_embedders, "Ollama Embedding Model Downloads<br>(lifetime)<br>")
    ollama_vlm_plot_data = format_downloads_data_for_plotly(ollama_vlms, "Ollama VLM Downloads<br>(lifetime)<br>")
    
    huggingface_plot_data = format_downloads_data_for_plotly(huggingface_models, "HuggingFace Model Downloads<br>(last month)<br>", left_margin=400, right_margin=100)
    huggingface_embedding_plot_data = format_downloads_data_for_plotly(huggingface_embedders, "HuggingFace Embedding Model Downloads<br>(last month)<br>", left_margin=400, right_margin=100)
    huggingface_vlm_plot_data = format_downloads_data_for_plotly(huggingface_vlms, "HuggingFace VLM Downloads<br>(last month)<br>", left_margin=300, right_margin=100)

    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    return Titled(
        "Cembalytics",
        P(A("← Back to home", href="/")),
        H1("Downloads"),
        Script('document.querySelector("meta[name=viewport]").setAttribute("content", "width=device-width, initial-scale=1.0, maximum-scale=1.0");'),
        Script(src="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap", rel="stylesheet"),
        custom_style,
        Div(
            H4("Sources"),
            P(A("HuggingFace", href="https://huggingface.co"), " is the de facto central platform where researchers and companies release their models & training datasets."),
            P(A("Ollama", href="https://ollama.com"), " provides a simple local API server for downloading, managing, and running AI models."),
            H4("Last Updated"),
            P("Thie data was downloaded at ", current_time, " upon loading of this page):"),
            P("Here's are the top models by download count from HuggingFace:"),
            Div(id="huggingfaceModels"),
            format_plotly_in_fasthtml("huggingfaceModels", huggingface_plot_data),
            P("And here are the top models by download count from Ollama:"),
            Div(id="ollamaModels"),
            format_plotly_in_fasthtml("ollamaModels", ollama_plot_data)
        ),
        Div(
            H2("Vision Language Models (VLMs)"),
            P("VLMs are rapidly becoming more capable and usable. Here are the current download counts for VLMs from HuggingFace:"),
            Div(id="huggingfaceVLMs"),
            format_plotly_in_fasthtml("huggingfaceVLMs", huggingface_vlm_plot_data),
            P("And here are the current download counts for VLMs via Ollama:"),
            Div(id="ollamaVLMs"),
            format_plotly_in_fasthtml("ollamaVLMs", ollama_vlm_plot_data)
        ),
        Div(
            H2("Embedding Models"),
            P("I'm particularly interested in embedding models. Here are the current download counts for embedding models from HuggingFace:"),
            Div(id="huggingfaceEmbeddings"),
            format_plotly_in_fasthtml("huggingfaceEmbeddings", huggingface_embedding_plot_data),
            P("And here are the current download counts for embedding models via Ollama:"),
            Div(id="ollamaEmbeddings"),
            format_plotly_in_fasthtml("ollamaEmbeddings", ollama_embedding_plot_data)
        )
    )

@rt("/benchmarks")
def get():
    return Titled(
        "Cembalytics",
        P(A("← Back to home", href="/")),
        H1("Benchmarks"),
        H2("Coming soon!!!!!!!!"),
        custom_style
    )

@rt("/weights-analysis")
def get():
    return Titled(
        "Cembalytics",
        P(A("← Back to home", href="/")),
        H1("Weights Analysis"),
        H2("Coming soon!!!!!!!!"),
        custom_style
    )

serve()