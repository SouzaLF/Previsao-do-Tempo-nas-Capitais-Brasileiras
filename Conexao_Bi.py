import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🔐 Sua chave da API do OpenWeatherMap (substitua pela sua)
API_KEY = 'SUA_CHAVE_API'

# 📍 Capitais brasileiras com respectivos estados
capitais_estados = {
    "Rio Branco": "AC", "Maceió": "AL", "Manaus": "AM", "Macapá": "AP", "Salvador": "BA",
    "Fortaleza": "CE", "Brasília": "DF", "Vitória": "ES", "Goiânia": "GO", "São Luís": "MA",
    "Belo Horizonte": "MG", "Campo Grande": "MS", "Cuiabá": "MT", "Belém": "PA", "João Pessoa": "PB",
    "Recife": "PE", "Teresina": "PI", "Curitiba": "PR", "Rio de Janeiro": "RJ", "Natal": "RN",
    "Porto Velho": "RO", "Boa Vista": "RR", "Porto Alegre": "RS", "Florianópolis": "SC",
    "Aracaju": "SE", "São Paulo": "SP", "Palmas": "TO"
}

# 🔄 Função para buscar previsão de uma capital
def buscar_previsao(cidade):
    estado = capitais_estados[cidade]
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br'
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        previsoes = r.json()['list']
        return [
            {
                'Cidade': cidade,
                'Estado': estado,
                'Data': datetime.fromtimestamp(item['dt']).date(),
                'Hora': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                'Temperatura (°C)': float(item['main']['temp']),
                'Sensação Térmica (°C)': float(item['main']['feels_like']),
                'Umidade (%)': int(item['main']['humidity']),
                'Condição': item['weather'][0]['description'],
                'Probabilidade de Precipitação': float(item.get('pop', 0)),
                'Chuva (mm/3h)': float(item.get('rain', {}).get('3h', 0.0))
            }
            for item in previsoes
        ]
    except Exception as e:
        print(f"[Erro] {cidade}: {e}")
        return []

# 🚀 Executa as requisições em paralelo
linhas = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futuros = [executor.submit(buscar_previsao, cidade) for cidade in capitais_estados]
    for futuro in as_completed(futuros):
        resultado = futuro.result()
        if resultado:
            linhas.extend(resultado)

# 📊 Cria o DataFrame
Dados = pd.DataFrame(linhas)

# 🧼 Ajuste de tipos
Dados['Data'] = pd.to_datetime(Dados['Data'])
Dados['Hora'] = pd.to_datetime(Dados['Hora'], format='%H:%M').dt.time
Dados['Temperatura (°C)'] = Dados['Temperatura (°C)'].astype(float)
Dados['Sensação Térmica (°C)'] = Dados['Sensação Térmica (°C)'].astype(float)
Dados['Umidade (%)'] = Dados['Umidade (%)'].astype(int)
Dados['Probabilidade de Precipitação'] = Dados['Probabilidade de Precipitação'].astype(float)
Dados['Chuva (mm/3h)'] = Dados['Chuva (mm/3h)'].astype(float)

# 💾 Visualizar
Dados