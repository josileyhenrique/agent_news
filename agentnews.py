import feedparser
import tweepy
import os
from google import genai

# --- CONFIGURAÇÃO DOS FEEDS DE CIBERSEGURANÇA ---
# Buscaremos do The Hacker News e BleepingComputer
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
    # Buscando a chave da IA de forma segura do sistema
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Prompt blindado para evitar vazamento de dados sensíveis e manter o tom sênior
    prompt = (
        f"Você é o Diretor de Inteligência da Henry Security. "
        f"Transforme a seguinte manchete em um tweet de alerta profissional para o Twitter/X. "
        f"Regras estritas: Use um tom sério, técnico e focado em mitigação/defesa. "
        f"NUNCA exponha credenciais, links de bancos de dados vazados ou informações sensíveis de vítimas. "
        f"Mantenha o texto curto (máximo 220 caracteres) para caber no limite do Twitter. "
        f"Adicione 2 hashtags relevantes como #BlueTeam ou #CyberSecurity.\n\n"
        f"Manchete: {titulo_noticia}"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text

def postar_no_twitter(texto_final, link_original):
    """Conecta com a API v2 garantindo o mapeamento completo de chaves para o plano Free"""
    
    # Passamos as 4 chaves juntas para não dar divergência de escopo
    client_x = tweepy.Client(
        consumer_key=os.environ.get("X_CONSUMER_KEY"),
        consumer_secret=os.environ.get("X_CONSUMER_SECRET"),
        access_token=os.environ.get("X_ACCESS_TOKEN"),
        access_token_secret=os.environ.get("X_ACCESS_TOKEN_SECRET")
    )
    
    conteudo_tweet = f"{texto_final}\n\nFonte: {link_original}"
    
    # O método v2 puro, usando autenticação explícita de usuário
    client_x.create_tweet(text=conteudo_tweet, user_auth=False)
    print("🛡️ Henry Security News publicado com sucesso!")
# --- EXECUÇÃO DO FLUXO ---
if __name__ == "__main__":
    noticia_recente = buscar_ultima_noticia()
    
    if noticia_recente:
        print(f"Processando: {noticia_recente['titulo']}")
        tweet_sofisticado = formatar_com_gemini(noticia_recente['titulo'])
        
        # Executa a postagem
        postar_no_twitter(tweet_sofisticado, noticia_recente['link'])
    else:
        print("Nenhuma notícia encontrada nos servidores parceiros.")