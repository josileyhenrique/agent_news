import feedparser
import os
import requests
from google import genai

# --- CONFIGURAÇÃO DOS FEEDS DE CIBERSEGURANÇA ---
FEEDS = [
    "https://thehackernews.com/feeds/posts/default",
    "https://www.bleepingcomputer.com/feed/"
    "https://www.cybersecbrazil.com.br/blog"
]

ARQUIVO_HISTORICO = "ultimo_link.txt"

def buscar_noticia_inédita():
    """Varre os portais e traz a primeira notícia que ainda não foi postada"""
    # Lemos qual foi o último link postado (se o arquivo existir)
    ultimo_link_gravado = ""
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r") as f:
            ultimo_link_gravado = f.read().strip()

    for url in FEEDS:
        feed = feedparser.parse(url)
        for noticia in feed.entries:
            # Se o link for igual ao último gravado, nós ignoramos e passamos para a próxima
            if noticia.link == ultimo_link_gravado:
                continue
            
            # Se chegou aqui, encontramos uma notícia inédita!
            # Gravamos o link dela para a próxima execução do robô
            with open(ARQUIVO_HISTORICO, "w") as f:
                f.write(noticia.link)
                
            return {"titulo": noticia.title, "link": noticia.link}
            
    return None

def formatar_com_gemini(titulo_noticia):
    """O cérebro da Henry Security processa a notícia usando tags HTML seguras"""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Mudamos as instruções para exigir HTML em vez de Markdown
    prompt = (
        f"Você é o Diretor de Inteligência da Henry Security.\n"
        f"Transforme a seguinte manchete em um alerta de segurança profissional para um canal corporativo do Telegram.\n"
        f"Regras estritas de formatação:\n"
        f"- Use um tom sério, técnico e focado em Blue Team (Defesa).\n"
        f"- Use APENAS as seguintes tags HTML para formatar: <b>para negrito</b> e <i>para itálico</i>.\n"
        f"- NUNCA use colchetes, asteriscos (*) ou underlines (_) para formatar texto.\n"
        f"- Inclua emojis de alerta de forma moderada (ex: 🚨, ⚠️, 🛡️).\n"
        f"- Adicione um parágrafo curtíssimo sobre o impacto ou mitigação geral.\n\n"
        f"Manchete original: {titulo_noticia}"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text

def postar_no_telegram(texto_final, link_original):
    """Envia o alerta formatado em HTML direto para o canal do Telegram"""
    token = os.environ.get("TELEGRAM_BOT_KEY")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    # Montamos o corpo da mensagem com link formatado em HTML nativo
    mensagem_completa = f"{texto_final}\n\n🔗 <b>Fonte original:</b> <a href='{link_original}'>Clique aqui para ler a notícia completa</a>"
    
    url_api = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": mensagem_completa,
        "parse_mode": "HTML"  # Mudamos de Markdown para HTML para blindar contra erros de sintaxe
    }
    
    response = requests.post(url_api, json=payload)
    
    if response.status_code == 200:
        print("🛡️ Alerta Henry Security publicado com sucesso no Telegram!")
    else:
        print(f"Erro ao postar no Telegram: {response.status_code} - {response.text}")

# --- EXECUÇÃO DO FLUXO ---
if __name__ == "__main__":
    noticia_recente = buscar_noticia_inédita()
    
    if noticia_recente:
        print(f"Processando: {noticia_recente['titulo']}")
        alerta_sofisticado = formatar_com_gemini(noticia_recente['titulo'])
        
        # Dispara o envio
        postar_no_telegram(alerta_sofisticado, noticia_recente['link'])
    else:
        print("Nenhuma notícia nova encontrada nos feeds de inteligência.")