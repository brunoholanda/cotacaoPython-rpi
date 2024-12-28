import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import Toplevel, Label, Frame, Canvas, Text, Scrollbar
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
from html.parser import HTMLParser


# Função para criar um card com borda arredondada e sombra
def create_card(parent, x, y, width, height, bg="#FFFFFF", shadow_color="#d3d3d3", radius=10):
    canvas = Canvas(parent, width=width, height=height, bg="#f0f0f0", highlightthickness=0)
    canvas.place(x=x, y=y)

    # Sombra
    canvas.create_rectangle(
        radius, radius, width, height, fill=shadow_color, outline="", tags="shadow"
    )
    canvas.tag_lower("shadow")

    # Retângulo arredondado
    canvas.create_oval(0, 0, radius * 2, radius * 2, fill=bg, outline="")
    canvas.create_oval(width - radius * 2, 0, width, radius * 2, fill=bg, outline="")
    canvas.create_oval(0, height - radius * 2, radius * 2, height, fill=bg, outline="")
    canvas.create_oval(
        width - radius * 2, height - radius * 2, width, height, fill=bg, outline=""
    )
    canvas.create_rectangle(radius, 0, width - radius, height, fill=bg, outline="")
    canvas.create_rectangle(0, radius, width, height - radius, fill=bg, outline="")

    return canvas

    # Função para buscar as notícias
NEWS_API_KEY = "14715ced631043f590e23014e80f7fe5"  # Substitua pela sua chave da API NewsAPI

class HTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        self.result.append(data)

    def clean(self, html):
        self.result = []
        self.feed(html)
        return ''.join(self.result)

# Instância do limpador de HTML
html_cleaner = HTMLCleaner()

# Função para buscar notícias do feed XML
def get_news_from_feed():
    try:
        url = "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Erro ao acessar o feed XML: {response.status_code}")
            return []

        # Parse do XML
        root = ET.fromstring(response.content)

        # Extrair títulos e descrições das notícias
        news = [
            {
                "title": item.find("title").text,
                "description": html_cleaner.clean(item.find("description").text) if item.find("description") is not None else "Sem descrição disponível."
            }
            for item in root.findall(".//item")
        ]

        return news[:5]  # Retornar até 5 notícias
    except Exception as e:
        print(f"Erro ao buscar notícias do feed XML: {e}")
        return []
    
    
def get_temperature():
    try:
        api_key = "f110c29a80dc5fc42e64deebcbb3e4c4"  # Substitua pela sua chave de API
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Joao%20Pessoa,BR&units=metric&appid={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]  # Temperatura atual
            return temp
        else:
            print(f"Erro ao buscar dados da API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao buscar temperatura: {e}")
        return None

# Função para atualizar o valor da temperatura
def update_temperature():
    temp = get_temperature()
    if temp is not None:
        temperature_value_label.config(text=f"{temp:.1f}°C")
    else:
        temperature_value_label.config(text="Erro")

    # Atualizar a temperatura a cada 10 minutos
    root.after(600000, update_temperature)
def show_full_news(event):
    global news_headlines, current_news_index

    if news_headlines:
        news = news_headlines[current_news_index]
        # Criar uma nova janela
        news_window = Toplevel(root)
        news_window.title("Detalhes da Notícia")
        news_window.geometry("400x300")
        news_window.configure(bg="#ffffff")

        # Scrollbar
        scrollbar = Scrollbar(news_window)
        scrollbar.pack(side="right", fill="y")

        # Text widget para exibir o título e a descrição com scroll
        text_widget = Text(news_window, wrap="word", font=("Arial", 10), bg="#ffffff", yscrollcommand=scrollbar.set)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Inserir título e descrição no Text widget
        text_widget.insert("1.0", f"{news['title']}\n\n")
        text_widget.insert("2.0", news["description"])

        # Configurar scrollbar para o Text widget
        scrollbar.config(command=text_widget.yview)

        # Desabilitar edição no Text widget
        text_widget.config(state="disabled")
        
# Função para atualizar o feed de notícias
def update_news_feed():
    global news_headlines, current_news_index

    # Busca as notícias se não estiverem carregadas
    if not news_headlines:
        news_headlines = get_news_from_feed()

    if news_headlines:
        # Atualiza o texto da notícia exibida
        current_news = news_headlines[current_news_index]
        news_feed_label.config(text=current_news["title"])
        # Alterna para a próxima notícia
        current_news_index = (current_news_index + 1) % len(news_headlines)
    else:
        news_feed_label.config(text="Erro ao carregar notícias.")

    # Atualiza novamente em 30 segundos
    root.after(30000, update_news_feed)
    
# Função para buscar a cotação do dólar no Investing.com
def get_investing_data():
    try:
        url = "https://br.investing.com/currencies/usd-brl"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Erro ao acessar o Investing.com: {response.status_code}")
            return None, None, None

        soup = BeautifulSoup(response.text, "html.parser")
        rate_element = soup.find("div", {"data-test": "instrument-price-last"})
        rate = float(rate_element.text.replace(",", ".")) if rate_element else None

        change_element = soup.find("span", {"data-test": "instrument-price-change"})
        change = change_element.text if change_element else None

        change_percent_element = soup.find("span", {"data-test": "instrument-price-change-percent"})
        change_percent = change_percent_element.text if change_percent_element else None

        return rate, change, change_percent
    except Exception as e:
        print(f"Erro ao buscar dados do Investing: {e}")
        return None, None, None

# Função para buscar a cotação do dólar no Banco Central
def get_bacen_data():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"Erro ao acessar o Banco Central: {response.status_code}")
            return None

        data = response.json()
        if len(data) > 0 and "valor" in data[0]:
            return float(data[0]["valor"])
        else:
            print("Dados do Banco Central não disponíveis ou no formato esperado.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao Banco Central: {e}")
        return None
    except ValueError as e:
        print(f"Erro ao interpretar os dados do Banco Central: {e}")
        return None

# Função para atualizar os dados do Investing
def update_investing_data():
    rate, change, change_percent = get_investing_data()

    if rate is not None:
        investing_value_label.config(text=f"R$ {rate:.4f}")

        # Determinar a cor e o ícone da variação
        if change and "+" in change:
            variation_color = "green"
            arrow = "▲"
        elif change and "-" in change:
            variation_color = "red"
            arrow = "▼"
        else:
            variation_color = "#333"
            arrow = ""

        investing_variation_label.config(
            text=f"Variação: {change} {change_percent} {arrow}",
            fg=variation_color
        )
        update_last_updated_time()
    else:
        investing_value_label.config(text="Erro ao buscar cotação.")
        investing_variation_label.config(text="", fg="#333")

    # Atualiza novamente em 60 segundos
    root.after(60000, update_investing_data)

# Função para atualizar os dados do Banco Central
def update_bacen_data():
    bacen_rate = get_bacen_data()

    if bacen_rate is not None:
        bacen_value_label.config(text=f"R$ {bacen_rate:.4f}")
        update_last_updated_time()
    else:
        bacen_value_label.config(text="Erro ao buscar cotação.", fg="red")

    # Atualiza novamente em 1 hora
    root.after(3600000, update_bacen_data)

# Função para atualizar o horário da última atualização
def update_last_updated_time():
    current_time = datetime.now(timezone).strftime("%H:%M:%S")
    last_updated_label.config(text=f"Última atualização: {current_time}")

# Configurando a interface gráfica
root = tk.Tk()
root.title("Cotação do Dólar")
root.attributes("-fullscreen", True)  # Iniciar em tela cheia
root.configure(bg="#f0f0f0")

news_headlines = []  # Lista de notícias
current_news_index = 0  # Índice da notícia atual

# Cabeçalho
header_frame = Frame(root, bg="#1e88e5", height=40)
header_frame.pack(fill="x")
timezone = pytz.timezone("America/Sao_Paulo")

date_label = Label(
    header_frame,
    text=datetime.now(timezone).strftime("%d/%m/%Y"),  # Exibe a data no fuso correto
    font=("Arial", 10, "bold"),
    bg="#1e88e5",
    fg="white"
)
date_label.pack(side="left", padx=10, pady=5)  # Posiciona no canto esquerdo

header_label = Label(
    header_frame,
    text="Cotação do Dólar Brasil",
    font=("Arial", 14, "bold"),
    bg="#1e88e5",
    fg="white"
)
header_label.pack(side="left", expand=True, pady=5)  # Centraliza o texto

time_label = Label(
    header_frame,
    text=datetime.now().strftime("%H:%M:%S"),  # Exibe a hora atual
    font=("Arial", 10, "bold"),
    bg="#1e88e5",
    fg="white"
)
time_label.pack(side="right", padx=10, pady=5)  # Posiciona no canto direito

footer_frame = Frame(root, bg="#1e88e5", height=20)
footer_frame.pack(side="bottom", fill="x")

footer_label = Label(
    footer_frame,
    text="Bruno Holanda All rights reserved",
    font=("Arial", 8, "italic"),
    bg="#1e88e5",
    fg="white"
)
footer_label.pack(pady=5)

# Função para atualizar dinamicamente a hora no canto superior direito
def update_time():
    current_time = datetime.now(timezone).strftime("%H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)  # Atualiza a cada 1 segundo

# Atualizar a hora dinamicamente
update_time()
header_label.pack(pady=5)

# Cards
# Card para o Dólar
investing_card = create_card(root, 30, 50, 220, 80, bg="white", shadow_color="#d3d3d3")
investing_title_label = Label(investing_card, text="Dólar (Real Time Investing)", font=("Arial", 12, "bold"), bg="white", fg="#333")
investing_title_label.place(x=10, y=5)
investing_value_label = Label(investing_card, text="Carregando...", font=("Arial", 16, "bold"), bg="white", fg="#333")
investing_value_label.place(x=10, y=30)
investing_variation_label = Label(investing_card, text="", font=("Arial", 10), bg="white", fg="#333")
investing_variation_label.place(x=10, y=55)

# Card para a Temperatura de João Pessoa
temperature_card = create_card(root, 260, 50, 210, 80, bg="white", shadow_color="#d3d3d3")  # Posição x ajustada
temperature_title_label = Label(temperature_card, text="João Pessoa", font=("Arial", 12, "bold"), bg="white", fg="#333")
temperature_title_label.place(x=10, y=5)
temperature_value_label = Label(temperature_card, text="Carregando...", font=("Arial", 16, "bold"), bg="white", fg="#333")
temperature_value_label.place(x=10, y=30)


bacen_card = create_card(root, 30, 140, 440, 60, bg="white", shadow_color="#d3d3d3")
bacen_title_label = Label(bacen_card, text="Dólar (Banco Central)", font=("Arial", 12, "bold"), bg="white", fg="#333")
bacen_title_label.place(x=0, y=5)
bacen_value_label = Label(bacen_card, text="Carregando...", font=("Arial", 16, "bold"), bg="white", fg="#333")
bacen_value_label.place(x=10, y=30)

news_card = create_card(root, 30, 210, 440, 50)
news_title_label = Label(news_card, text="News", font=("Arial", 10, "bold"), bg="white")
news_title_label.place(x=5, y=5)
news_feed_label = Label(news_card, text="Carregando notícias...", font=("Arial", 10), bg="white", wraplength=420, justify="left", anchor="w")
news_feed_label.place(x=5, y=30)

news_card.bind("<Button-1>", show_full_news)

# Última atualização
last_updated_label = Label(root, text="Última atualização: --:--:--", font=("Arial", 8), bg="#f0f0f0", fg="#555")
last_updated_label.pack(side="bottom", pady=10)

# Inicializar as atualizações
update_news_feed()
update_investing_data()  # Atualiza o Investing a cada 60 segundos
update_bacen_data()  # Atualiza o Banco Central a cada 1 hora
update_temperature()

# Iniciar o loop principal da interface gráfica
root.mainloop()
