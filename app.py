from flask import Flask, request, render_template_string
import numpy as np

app = Flask(__name__)

# Tabela em kcal/kg (mesma do script)
data = np.array([
    [0.02, 17.51, 17.56, 605.55, 623.11],
    [0.03, 24.10, 24.14, 608.41, 632.55],
    [0.04, 28.98, 29.00, 610.42, 639.42],
    [0.05, 32.90, 32.91, 612.04, 644.95],
    [0.06, 36.18, 36.21, 613.42, 649.63],
    [0.07, 39.02, 39.05, 614.62, 653.67],
    [0.08, 41.53, 41.54, 615.70, 657.24],
    [0.09, 43.79, 43.80, 616.69, 660.49],
    [0.1, 45.83, 45.85, 617.60, 663.45],
    [0.2, 60.09, 60.09, 623.68, 683.77],
    [0.3, 69.13, 69.13, 627.65, 696.78],
    [0.4, 75.89, 75.90, 630.49, 706.39],
    [0.5, 81.35, 81.38, 632.69, 714.07],
    [0.6, 85.95, 85.98, 634.47, 720.45],
    [0.7, 89.96, 90.01, 635.95, 725.96],
    [0.8, 93.51, 93.61, 637.22, 730.83],
    [0.9, 96.71, 96.84, 638.33, 735.17],
    [1.0, 99.63, 99.77, 639.31, 739.08],
    [2.0, 120.23, 120.59, 647.00, 767.59],
    [5.0, 151.85, 152.97, 656.45, 809.42],
    [10.0, 179.88, 182.17, 663.43, 845.60],
    [20.0, 212.37, 217.05, 668.40, 885.45],
    [30.0, 233.84, 240.89, 669.70, 910.59]
])

pressures = data[:, 0]
hgs = data[:, 4]

pci_predefinidos = {
    'lenha': 3440,
    'bagaco': 1800,
    'carvao': 6000,
    'oleo': 9500
}

composicoes_predefinidas = {
    'lenha': {'c': 48.5, 'h': 6.2, 'o': 43.3, 's': 0, 'n': 0.2},
    'bagaco': {'c': 48.5, 'h': 7, 'o': 44, 's': 0, 'n': 0.5},
    'carvao': {'c': 90, 'h': 3, 'o': 3, 's': 1, 'n': 1},
    'oleo': {'c': 85, 'h': 12, 'o': 0.5, 's': 2, 'n': 0}
}

def calcular_entalpias(p_vapor, t_alimentacao):
    if p_vapor < min(pressures) or p_vapor > max(pressures):
        return None, None
    h_vapor = np.interp(p_vapor, pressures, hgs)
    h_alimentacao = 1.0 * t_alimentacao
    return h_vapor, h_alimentacao

def calcular_pci_composicao(c, h, o, s=0, n=0, umidade=0.0):
    c /= 100; h /= 100; o /= 100; s /= 100; n /= 100
    pci_seco = 8080 * c + 34500 * (h - o / 8) + 2250 * s + 2500 * n
    pci_umido = pci_seco * (1 - umidade) - 540 * umidade
    return pci_umido

def calcular_ar_combustivel(p_vapor, t_alimentacao, umidade, eficiencia, excesso, opcao, vazao_vapor, tipo=None, c=0, h=0, o=0, s=0, n=0):
    h_vapor_val, h_alimentacao_val = calcular_entalpias(p_vapor, t_alimentacao)
    if h_vapor_val is None:
        return {"error": "Pressão fora do intervalo (0.02 a 30 bar)."}
    delta_h = h_vapor_val - h_alimentacao_val
    q_util = vazao_vapor * delta_h

    q_entrada = q_util / eficiencia

    if opcao == 'predefinido' and tipo in pci_predefinidos:
        pci = pci_predefinidos[tipo]
        comp_pre = composicoes_predefinidas.get(tipo, composicoes_predefinidas['lenha'])
        composicao = {k: v / 100 for k, v in comp_pre.items()}
    elif opcao == 'custom':
        pci = calcular_pci_composicao(c, h, o, s, n, umidade)
        composicao = {'c': c / 100, 'h': h / 100, 'o': o / 100, 's': s / 100, 'n': n / 100}
    else:
        return {"error": "Opção ou tipo inválido."}

    m_combustivel = q_entrada / pci

    fracao_seca = 1 - umidade
    c_frac = composicao['c'] * fracao_seca
    h_frac = composicao['h'] * fracao_seca
    o_frac = composicao['o'] * fracao_seca
    s_frac = composicao['s'] * fracao_seca

    mol_c = (c_frac * 1000) / 12
    mol_h_atomos = (h_frac * 1000) / 1
    mol_o_atomos = (o_frac * 1000) / 16
    mol_s = (s_frac * 1000) / 32

    o2_c = mol_c
    o2_h = mol_h_atomos / 4
    o2_s = mol_s
    o2_bruto = o2_c + o2_h + o2_s
    o2_combustivel = mol_o_atomos / 2
    o2_liquido = o2_bruto - o2_combustivel

    mol_ar = o2_liquido / 0.21
    afr_teorica = mol_ar * 29 / 1000

    afr_real = afr_teorica * excesso
from flask import Flask, request, render_template_string
import numpy as np

app = Flask(__name__)

# Tabela em kcal/kg (mesma do script)
data = np.array([
    [0.02, 17.51, 17.56, 605.55, 623.11],
    [0.03, 24.10, 24.14, 608.41, 632.55],
    [0.04, 28.98, 29.00, 610.42, 639.42],
    [0.05, 32.90, 32.91, 612.04, 644.95],
    [0.06, 36.18, 36.21, 613.42, 649.63],
    [0.07, 39.02, 39.05, 614.62, 653.67],
    [0.08, 41.53, 41.54, 615.70, 657.24],
    [0.09, 43.79, 43.80, 616.69, 660.49],
    [0.1, 45.83, 45.85, 617.60, 663.45],
    [0.2, 60.09, 60.09, 623.68, 683.77],
    [0.3, 69.13, 69.13, 627.65, 696.78],
    [0.4, 75.89, 75.90, 630.49, 706.39],
    [0.5, 81.35, 81.38, 632.69, 714.07],
    [0.6, 85.95, 85.98, 634.47, 720.45],
    [0.7, 89.96, 90.01, 635.95, 725.96],
    [0.8, 93.51, 93.61, 637.22, 730.83],
    [0.9, 96.71, 96.84, 638.33, 735.17],
    [1.0, 99.63, 99.77, 639.31, 739.08],
    [2.0, 120.23, 120.59, 647.00, 767.59],
    [5.0, 151.85, 152.97, 656.45, 809.42],
    [10.0, 179.88, 182.17, 663.43, 845.60],
    [20.0, 212.37, 217.05, 668.40, 885.45],
    [30.0, 233.84, 240.89, 669.70, 910.59]
])

pressures = data[:, 0]
hgs = data[:, 4]

pci_predefinidos = {
    'lenha': 3440,
    'bagaco': 1800,
    'carvao': 6000,
    'oleo': 9500
}

composicoes_predefinidas = {
    'lenha': {'c': 48.5, 'h': 6.2, 'o': 43.3, 's': 0, 'n': 0.2},
    'bagaco': {'c': 48.5, 'h': 7, 'o': 44, 's': 0, 'n': 0.5},
    'carvao': {'c': 90, 'h': 3, 'o': 3, 's': 1, 'n': 1},
    'oleo': {'c': 85, 'h': 12, 'o': 0.5, 's': 2, 'n': 0}
}

def calcular_entalpias(p_vapor, t_alimentacao):
    if p_vapor < min(pressures) or p_vapor > max(pressures):
        return None, None
    h_vapor = np.interp(p_vapor, pressures, hgs)
    h_alimentacao = 1.0 * t_alimentacao
    return h_vapor, h_alimentacao

def calcular_pci_composicao(c, h, o, s=0, n=0, umidade=0.0):
    c /= 100; h /= 100; o /= 100; s /= 100; n /= 100
    pci_seco = 8080 * c + 34500 * (h - o / 8) + 2250 * s + 2500 * n
    pci_umido = pci_seco * (1 - umidade) - 540 * umidade
    return pci_umido

def calcular_ar_combustivel(p_vapor, t_alimentacao, umidade, eficiencia, excesso, opcao, vazao_vapor, tipo=None, c=0, h=0, o=0, s=0, n=0):
    h_vapor_val, h_alimentacao_val = calcular_entalpias(p_vapor, t_alimentacao)
    if h_vapor_val is None:
        return {"error": "Pressão fora do intervalo (0.02 a 30 bar)."}
    delta_h = h_vapor_val - h_alimentacao_val
    q_util = vazao_vapor * delta_h

    q_entrada = q_util / eficiencia

    if opcao == 'predefinido' and tipo in pci_predefinidos:
        pci = pci_predefinidos[tipo]
        comp_pre = composicoes_predefinidas.get(tipo, composicoes_predefinidas['lenha'])
        composicao = {k: v / 100 for k, v in comp_pre.items()}
    elif opcao == 'custom':
        pci = calcular_pci_composicao(c, h, o, s, n, umidade)
        composicao = {'c': c / 100, 'h': h / 100, 'o': o / 100, 's': s / 100, 'n': n / 100}
    else:
        return {"error": "Opção ou tipo inválido."}

    m_combustivel = q_entrada / pci

    fracao_seca = 1 - umidade
    c_frac = composicao['c'] * fracao_seca
    h_frac = composicao['h'] * fracao_seca
    o_frac = composicao['o'] * fracao_seca
    s_frac = composicao['s'] * fracao_seca

    mol_c = (c_frac * 1000) / 12
    mol_h_atomos = (h_frac * 1000) / 1
    mol_o_atomos = (o_frac * 1000) / 16
    mol_s = (s_frac * 1000) / 32

    o2_c = mol_c
    o2_h = mol_h_atomos / 4
    o2_s = mol_s
    o2_bruto = o2_c + o2_h + o2_s
    o2_combustivel = mol_o_atomos / 2
    o2_liquido = o2_bruto - o2_combustivel

    mol_ar = o2_liquido / 0.21
    afr_teorica = mol_ar * 29 / 1000

    afr_real = afr_teorica * excesso

    m_ar = m_combustivel * afr_real

    rho_ar = 1.204  # Densidade do ar a 20°C e 1 atm (kg/m³)
    v_ar = m_ar / rho_ar

    return {
        'q_util': q_util,
        'q_entrada': q_entrada,
        'pci': pci,
        'm_combustivel': m_combustivel,
        'afr_teorica': afr_teorica,
        'afr_real': afr_real,
        'm_ar': m_ar,
        'v_ar': v_ar
    }

HTML = '''
<!doctype html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Combustão Industrial</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --accent-color: #ff5722;
            --secondary-accent: #ff9800;
            --input-bg: #2c2c2c;
            --border-color: #333;
        }
        body {
            font-family: 'Roboto', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background-color: var(--card-bg);
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            width: 100%;
            max-width: 650px;
            border-top: 4px solid var(--accent-color);
            animation: fadeIn 0.5s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            text-align: center;
            color: var(--accent-color);
            margin-bottom: 2rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            font-size: 1.8rem;
        }
        .icon-boiler {
            width: 48px;
            height: 48px;
            fill: var(--accent-color);
            filter: drop-shadow(0 0 5px rgba(255, 87, 34, 0.5));
        }
        .form-group {
            margin-bottom: 1.2rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #bbb;
            font-size: 0.9rem;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: #fff;
            box-sizing: border-box;
            font-size: 1rem;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(255, 87, 34, 0.2);
        }
        .row {
            display: flex;
            gap: 15px;
        }
        .col {
            flex: 1;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--accent-color), var(--secondary-accent));
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 1.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 87, 34, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .results {
            margin-top: 2.5rem;
            padding: 1.5rem;
            background-color: #252525;
            border-radius: 12px;
            border-left: 5px solid var(--secondary-accent);
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
            border-bottom: 1px solid #333;
            padding-bottom: 0.8rem;
        }
        .result-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        .result-label {
            color: #aaa;
            font-size: 0.95rem;
        }
        .result-value {
            font-weight: bold;
            color: #fff;
            font-family: 'Courier New', monospace;
        }
        .highlight {
            color: var(--accent-color);
            font-size: 1.2rem;
        }
        @media (max-width: 600px) {
            .row { flex-direction: column; gap: 0; }
            .container { padding: 1.5rem; }
        }
    </style>
    <script>
        function toggleOpcao() {
            var opcao = document.getElementById('opcao').value;
            var predefinido = document.getElementById('predefinido');
            var custom = document.getElementById('custom');
            
            if (opcao === 'predefinido') {
                predefinido.style.display = 'block';
                custom.style.display = 'none';
                setTimeout(() => predefinido.style.opacity = 1, 10);
            } else {
                predefinido.style.display = 'none';
                custom.style.display = 'block';
                setTimeout(() => custom.style.opacity = 1, 10);
            }
        }
    </script>
</head>
<body onload="toggleOpcao()">
    <div class="container">
        <h1>
            <svg class="icon-boiler" viewBox="0 0 24 24">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,7V13L16.2,16.1L17,14.9L12.5,12.2V7H11Z" />
                <path d="M7,12c0,2.8 2.2,5 5,5s5-2.2 5-5s-2.2-5-5-5S7,9.2 7,12z M12,15c-1.7,0-3-1.3-3-3s1.3-3 3-3s3,1.3 3,3S13.7,15 12,15z" fill="currentColor"/>
            </svg>
            Boiler Calc
        </h1>
        <form method="post">
            <div class="row">
                <div class="col form-group">
                    <label>Pressão de Vapor (bar)</label>
                    <input type="text" name="p_vapor" value="{{ request.form.get('p_vapor', '10.0') }}">
                </div>
                <div class="col form-group">
                    <label>Temp. Alimentação (°C)</label>
                    <input type="text" name="t_alimentacao" value="{{ request.form.get('t_alimentacao', '100.0') }}">
                </div>
            </div>
            
            <div class="row">
                <div class="col form-group">
                    <label>Vazão da Caldeira (kg/h)</label>
                    <input type="text" name="vazao_vapor" value="{{ request.form.get('vazao_vapor', '5000') }}">
                </div>
                <div class="col form-group">
                    <label>Eficiência (0.0 - 1.0)</label>
                    <input type="text" name="eficiencia" value="{{ request.form.get('eficiencia', '0.75') }}">
                </div>
            </div>

            <div class="row">
                <div class="col form-group">
                    <label>Umidade do Combustível</label>
                    <input type="text" name="umidade" value="{{ request.form.get('umidade', '0.20') }}">
                </div>
                <div class="col form-group">
                    <label>Excesso de Ar (Coef.)</label>
                    <input type="text" name="excesso" value="{{ request.form.get('excesso', '1.25') }}">
                </div>
            </div>

            <div class="form-group">
                <label>Configuração do Combustível</label>
                <select id="opcao" name="opcao" onchange="toggleOpcao()">
                    <option value="predefinido" {% if request.form.get('opcao') == 'predefinido' %}selected{% endif %}>Combustível Padrão</option>
                    <option value="custom" {% if request.form.get('opcao') == 'custom' %}selected{% endif %}>Composição Personalizada</option>
                </select>
            </div>

            <div id="predefinido" class="form-group" style="transition: opacity 0.3s; opacity: 0;">
                <label>Tipo de Combustível</label>
                <select name="tipo">
                    <option value="lenha" {% if request.form.get('tipo') == 'lenha' %}selected{% endif %}>Lenha</option>
                    <option value="bagaco" {% if request.form.get('tipo') == 'bagaco' %}selected{% endif %}>Bagaço de Cana</option>
                    <option value="carvao" {% if request.form.get('tipo') == 'carvao' %}selected{% endif %}>Carvão Mineral</option>
                    <option value="oleo" {% if request.form.get('tipo') == 'oleo' %}selected{% endif %}>Óleo Combustível</option>
                </select>
            </div>

            <div id="custom" style="display:none; transition: opacity 0.3s; opacity: 0;">
                <div class="row">
                    <div class="col form-group">
                        <label>% Carbono (C)</label>
                        <input type="text" name="c" value="{{ request.form.get('c', '48.5') }}">
                    </div>
                    <div class="col form-group">
                        <label>% Hidrogênio (H)</label>
                        <input type="text" name="h" value="{{ request.form.get('h', '6.2') }}">
                    </div>
                    <div class="col form-group">
                        <label>% Oxigênio (O)</label>
                        <input type="text" name="o" value="{{ request.form.get('o', '43.3') }}">
                    </div>
                </div>
                <div class="row">
                    <div class="col form-group">
                        <label>% Enxofre (S)</label>
                        <input type="text" name="s" value="{{ request.form.get('s', '0') }}">
                    </div>
                    <div class="col form-group">
                        <label>% Nitrogênio (N)</label>
                        <input type="text" name="n" value="{{ request.form.get('n', '0') }}">
                    </div>
                </div>
            </div>

            <button type="submit" class="btn">Calcular Parâmetros</button>
        </form>

        {% if resultados %}
            {% if resultados.error %}
                <div class="results" style="border-left-color: #f44336;">
                    <h3 style="color: #f44336; margin-top: 0;">Erro no Cálculo</h3>
                    <p>{{ resultados.error }}</p>
                </div>
            {% else %}
                <div class="results">
                    <h3 style="margin-top: 0; color: var(--secondary-accent); border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 15px;">Resultados da Análise</h3>
                    
                    <div class="result-item">
                        <span class="result-label">PCI (Poder Calorífico)</span>
                        <span class="result-value">{{ resultados.pci|round(2) }} kcal/kg</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Calor Útil Gerado</span>
                        <span class="result-value">{{ resultados.q_util|round(2) }} kcal/h</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Energia de Entrada</span>
                        <span class="result-value">{{ resultados.q_entrada|round(2) }} kcal/h</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Consumo de Combustível</span>
                        <span class="result-value highlight">{{ resultados.m_combustivel|round(2) }} kg/h</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Relação Ar/Combustível (Teórica)</span>
                        <span class="result-value">{{ resultados.afr_teorica|round(2) }} kg/kg</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Relação Ar/Combustível (Real)</span>
                        <span class="result-value">{{ resultados.afr_real|round(2) }} kg/kg</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Vazão de Ar (Massa)</span>
                        <span class="result-value">{{ resultados.m_ar|round(2) }} kg/h</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Vazão de Ar (Volume)</span>
                        <span class="result-value">{{ resultados.v_ar|round(2) }} m³/h</span>
                    </div>
                </div>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        p_vapor = float(request.form.get('p_vapor', 10.0))
        t_alimentacao = float(request.form.get('t_alimentacao', 100.0))
        vazao_vapor = float(request.form.get('vazao_vapor', 5000))
        umidade = float(request.form.get('umidade', 0.20))
        eficiencia = float(request.form.get('eficiencia', 0.75))
        excesso = float(request.form.get('excesso', 1.25))
        opcao = request.form.get('opcao', 'predefinido')
        if opcao == 'predefinido':
            tipo = request.form.get('tipo', 'lenha')
            resultados = calcular_ar_combustivel(p_vapor, t_alimentacao, umidade, eficiencia, excesso, opcao, vazao_vapor, tipo=tipo)
        else:
            c = float(request.form.get('c', 48.5))
            h = float(request.form.get('h', 6.2))
            o = float(request.form.get('o', 43.3))
            s = float(request.form.get('s', 0))
            n = float(request.form.get('n', 0))
            resultados = calcular_ar_combustivel(p_vapor, t_alimentacao, umidade, eficiencia, excesso, opcao, vazao_vapor, c=c, h=h, o=o, s=s, n=n)
        return render_template_string(HTML, resultados=resultados)
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)