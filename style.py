from fasthtml.common import Style, Script

custom_style = Style("""
    * {
        --text-color: #000000;        
        color: var(--text-color);         
    }
                     
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.7;
        margin: 0 auto;
        padding: 4rem;
        
        /* Background pattern tessellation */
        --primary-color: #266c43;
        --primary-dark: #1e5434;
        
        background-color: var(--primary-color);
        background-image: 
            linear-gradient(30deg, var(--primary-dark) 12%, transparent 12.5%, transparent 87%, var(--primary-dark) 87.5%, var(--primary-dark)),
            linear-gradient(150deg, var(--primary-dark) 12%, transparent 12.5%, transparent 87%, var(--primary-dark) 87.5%, var(--primary-dark)),
            linear-gradient(30deg, var(--primary-dark) 12%, transparent 12.5%, transparent 87%, var(--primary-dark) 87.5%, var(--primary-dark)),
            linear-gradient(150deg, var(--primary-dark) 12%, transparent 12.5%, transparent 87%, var(--primary-dark) 87.5%, var(--primary-dark)),
            linear-gradient(60deg, var(--primary-dark) 25%, transparent 25.5%, transparent 75%, var(--primary-dark) 75%, var(--primary-dark)),
            linear-gradient(60deg, var(--primary-dark) 25%, transparent 25.5%, transparent 75%, var(--primary-dark) 75%, var(--primary-dark));
        background-size: 80px 140px;
        background-position: 0 0, 0 0, 40px 70px, 40px 70px, 0 0, 40px 70px;
        background-repeat: repeat;

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
        margin-bottom: 2rem;
        font-weight: 400;
        letter-spacing: -0.025em;
    }

    a {
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
                     
    .button-container {
        display: flex;
        justify-content: center;
        gap: 4rem;
        margin: 2rem 0;
    }

    .image-button {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        transition: all 0.2s ease;
        text-decoration: none;
        width: 300px;
    }

    .image-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e0;
    }

    .image-button img {
        width: 200px;
        height: auto;
        margin-top: 1rem;
        border-radius: 8px;
    }

    .button-text {
        font-weight: 500;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
""")

def format_plotly_in_fasthtml(div_id, plot_data):
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