import numpy as np

# Tabela de propriedades de vapor saturado em kcal/kg (convertida de kJ/kg / 4.184)
# Pressão (bar), T (°C), hf (kcal/kg), hfg (kcal/kg), hg (kcal/kg)
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
hgs = data[:, 4]  # hg (kcal/kg)

# Dicionário de PCI típicos em kcal/kg para tipos pré-definidos
pci_predefinidos = {
    'lenha': 3440,  # 20% umidade
    'bagaco': 1800,  # 50% umidade
    'carvao': 6000,  # Carvão típico
    'oleo': 9500  # Óleo combustível
}

# Função para calcular entalpias em kcal/kg
def calcular_entalpias(p_vapor, t_alimentacao):
    if p_vapor < min(pressures) or p_vapor > max(pressures):
        raise ValueError("Pressão fora do intervalo da tabela (0.02 a 30 bar).")
    h_vapor = np.interp(p_vapor, pressures, hgs)
    h_alimentacao = 1.0 * t_alimentacao  # cp ≈ 1 kcal/kg°C
    return h_vapor, h_alimentacao

# Função para calcular PCI a partir de composição (fórmula de Dulong ajustada, em kcal/kg)
def calcular_pci_composicao(c, h, o, s=0, n=0, umidade=0.0):
    c /= 100; h /= 100; o /= 100; s /= 100; n /= 100
    pci_seco = 8080 * c + 34500 * (h - o / 8) + 2250 * s + 2500 * n
    pci_umido = pci_seco * (1 - umidade) - 540 * umidade  # Ajuste para umidade (calor latente approx.)
    return pci_umido

# Função principal
def calcular_ar_combustivel(p_vapor=10.0, t_alimentacao=100.0, umidade=0.20, eficiencia=0.75, pci=3440, excesso=1.25, vazao_vapor=5000, composicao=None):
    h_vapor, h_alimentacao = calcular_entalpias(p_vapor, t_alimentacao)
    delta_h = h_vapor - h_alimentacao
    q_util = vazao_vapor * delta_h
    print(f"Calor útil: {q_util} kcal/h")

    q_entrada = q_util / eficiencia
    print(f"Calor de entrada: {q_entrada} kcal/h")

    m_combustivel = q_entrada / pci
    print(f"Consumo de combustível: {m_combustivel:.2f} kg/h")

    # AFR (usando composição; se pré-definido, assume lenha como base, ajuste se necessário)
    fracao_seca = 1 - umidade
    if composicao:
        c, h, o = composicao['c'], composicao['h'], composicao['o']
    else:
        c = 0.485 * fracao_seca  # Default lenha
        h = 0.062 * fracao_seca
        o = 0.433 * fracao_seca

    mol_c = c / 12
    mol_h_atomos = h / 1
    mol_o_atomos = o / 16

    o2_c = mol_c
    o2_h = mol_h_atomos / 4
    o2_bruto = o2_c + o2_h
    o2_combustivel = mol_o_atomos / 2
    o2_liquido = o2_bruto - o2_combustivel

    mol_ar = o2_liquido / 0.21
    massa_ar = mol_ar * 29 / 1000  # kg ar / kg combustível (ajuste unidades)
    afr_teorica = massa_ar
    print(f"AFR teórica: {afr_teorica:.2f} kg ar / kg combustível")

    afr_real = afr_teorica * excesso
    print(f"AFR real (com excesso): {afr_real:.2f} kg ar / kg combustível")

    m_ar = m_combustivel * afr_real
    print(f"Vazão de ar: {m_ar:.2f} kg/h")

# Entrada do usuário
print("Cálculo para caldeira.")
p_vapor = float(input("Pressão de vapor (bar, ex: 10.0): ") or 10.0)
t_alimentacao = float(input("Temperatura de alimentação (°C, ex: 100.0): ") or 100.0)
vazao_vapor = float(input("Vazão da caldeira (kg/h, ex: 5000): ") or 5000)
umidade = float(input("Umidade (ex: 0.20): ") or 0.20)
eficiencia = float(input("Eficiência (ex: 0.75): ") or 0.75)
excesso = float(input("Coeficiente de excesso (ex: 1.25): ") or 1.25)

opcao = input("Escolha opção para PCI: 1) Tipo pré-definido, 2) Composição personalizada: ")
if opcao == '1':
    tipo = input("Tipo de combustível (lenha, bagaco, carvao, oleo): ").lower()
    pci = pci_predefinidos.get(tipo, 3440)  # Default lenha
    print(f"PCI automático para {tipo}: {pci} kcal/kg")
    composicao = None
elif opcao == '2':
    c = float(input("%C (base seca): "))
    h = float(input("%H (base seca): "))
    o = float(input("%O (base seca): "))
    s = float(input("%S (base seca, opcional): ") or 0)
    n = float(input("%N (base seca, opcional): ") or 0)
    composicao = {'c': c/100, 'h': h/100, 'o': o/100}  # Frações para AFR
    pci = calcular_pci_composicao(c, h, o, s, n, umidade)
    print(f"PCI calculado: {pci:.2f} kcal/kg")
else:
    raise ValueError("Opção inválida.")

# Chamada
calcular_ar_combustivel(p_vapor, t_alimentacao, umidade, eficiencia, pci, excesso, vazao_vapor, composicao=composicao)