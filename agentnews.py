import feedparser
import os
import requests
from google import genai

# --- CONFIGURAÇÃO DOS FEEDS DE CIBERSEGURANÇA ---
FEEDS = [
    "https://thehackernews.com/feeds/posts/default",
    "https://www.bleepingcomputer.com/feed/"
]

def buscar_ultima_noticia():
    """Varre os portais e traz a manchete mais recente"""
    for url in FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            noticia = feed.entries[0]
            return {"titulo": noticia.title, "link": noticia.link}
    return None

def formatar_com_gemini(titulo_noticia):
    """O cérebro da Henry Security processa a notícia"""
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Prompt focado no formato de relatório/alerta do Telegram
    prompt = (
        f"Você é o Diretor de Inteligência da Henry Security.\n"
        f"Transforme a seguinte manchete em um alerta de segurança profissional para um canal corporativo do Telegram.\n"
        f"Regras:\n"
        f"- Use um tom sério, técnico e focado em Blue Team (Defesa).\n"
        f"- Use formatação Markdown (como **negrito** para destacar pontos críticos).\n"
        f"- Inclua emojis de alerta de forma moderada (ex: 🚨, ⚠️, 🛡️).\n"
        f"- Adicione um parágrafo curtíssimo sobre o impacto ou mitigação geral.\n\n"
        f"Manchete original: {titulo_noticia}"
    )
    
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    return response.text

def postar_no_telegram(texto_final, link_original):
    """Envia o alerta formatado direto para o canal do Telegram de forma 100% gratuita"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    # Montamos o corpo da mensagem com formatação rica
    mensagem_completa = f"{texto_final}\n\n🔗 **Fonte original:** {link_original}"
    
    # URL oficial da API do Telegram
    url_api = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": mensagem_completa,
        "parse_mode": "Markdown"  # Permite que o Telegram renderize negritos e links amigáveis
    }
    
    response = requests.post(url_api, json=payload)
    
    if response.status_code == 200:
        print("🛡️ Alerta Henry Security publicado com sucesso no Telegram!")
    else:
        print(f"Erro ao postar no Telegram: {response.status_code} - {response.text}")

# --- EXECUÇÃO DO FLUXO ---
if __name__ == "__main__":
    noticia_recente = buscar_ultima_noticia()
    
    if noticia_recente:
        print(f"Processando: {noticia_recente['titulo']}")
        alerta_sofisticado = formatar_com_gemini(noticia_recente['titulo'])
        
        # Dispara o envio
        postar_no_telegram(alerta_sofisticado, noticia_recente['link'])
    else:
        print("Nenhuma notícia nova encontrada nos feeds de inteligência.")