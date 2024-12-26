# Cotação do Dólar e Notícias em Tempo Real

Este projeto exibe informações sobre a cotação do dólar (Real Time Investing e Banco Central) e as últimas notícias, com uma interface gráfica desenvolvida em Python usando o `tkinter`. Ele foi projetado para ser executado automaticamente em uma Raspberry Pi.

---

## 📦 Bibliotecas Necessárias

Certifique-se de ter as seguintes bibliotecas instaladas:

### Python Built-in
- `tkinter` (incluso na instalação padrão do Python)
- `datetime`
- `xml.etree.ElementTree`
- `html.parser`

### Terceiros
- `requests`
- `bs4` (BeautifulSoup)

Instale as bibliotecas de terceiros usando:

```bash
pip install requests beautifulsoup4


## 🛠️ O que o código faz?

1. **Cotação do Dólar**:
   - Obtém a cotação em tempo real do site [Investing.com](https://br.investing.com) e do Banco Central.
   - Exibe as variações da cotação com indicação visual (setas e cores).

2. **Notícias**:
   - Obtém as últimas notícias de um feed RSS (`https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml`).
   - Exibe as manchetes alternadamente, permitindo clicar para visualizar os detalhes em uma janela com rolagem.

3. **Interface Gráfica**:
   - Tela cheia (fullscreen).
   - Informações formatadas em "cards".
   - Data no canto superior esquerdo e hora no canto superior direito.
   - Rodapé com o texto: `Bruno Holanda All rights reserved`.

---

## 🚀 Como executar automaticamente na Raspberry Pi

### 1. Configurar o script para rodar no boot

Crie um arquivo `.sh` para iniciar o programa. Por exemplo:

#### Arquivo `start_dolar.sh`:
```bash
#!/bin/bash
cd /caminho/para/o/script
python3 cotacao_dolar.py

##Torne o script executável:

chmod +x start_dolar.sh


##Configurar o autostart no Raspbian

icione o script ao arquivo de inicialização:

Abra o arquivo de configuração do autostart:
nano ~/.config/lxsession/LXDE-pi/autostart
@/caminho/para/o/script/start_dolar.sh


 Reiniciar a Raspberry Pi
 sudo reboot
