from PIL import Image
import os

def cor_valida(pixel_rgb, cor_alvo, tolerancia=10):
    """
    Verifica se o pixel está dentro da tolerância de cor RGB (0-255).
    """
    return all(abs(c_pix - c_alvo) <= tolerancia for c_pix, c_alvo in zip(pixel_rgb[:3], cor_alvo))

def validar_faixa(pixels, x, y_inicio, altura_max, cor_alvo, min_px, max_px):
    """
    Verifica se existe uma sequência vertical contínua da cor especificada.
    Retorna a altura da faixa encontrada ou 0 se for inválida.
    """
    altura = 0
    y = y_inicio
    while y < altura_max and cor_valida(pixels[x, y], cor_alvo):
        altura += 1
        y += 1
        if altura > max_px:
            break
            
    if min_px <= altura <= max_px:
        return altura
    return 0

def encontrar_padrao_vertical(imagem):
    """
    Percorre a coluna x=315 procurando pelo padrão vertical especifico com margem de erro.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    x_alvo = 315
    if x_alvo >= largura:
        print(f"Erro: A imagem possui largura de {largura}px, mas a coluna {x_alvo} foi solicitada.")
        return []

    # Cores RGB 0-255 do padrão
    COR_BRANCO = (255, 255, 255)
    COR_CINZA = (222, 221, 222)

    posicoes_corte = []
    y = 0

    while y < altura - 35:
        # Faixa 1: ~1 px branco (Margem: 1 ± 2 => 0 a 3 px)
        h1 = validar_faixa(pixels, x_alvo, y, altura, COR_BRANCO, min_px=0, max_px=3)
        
        # Se encontrou a faixa 1 (ou se ela tiver 0 px dentro da margem aceita)
        if h1 >= 0:
            y_f2 = y + h1
            # Faixa 2: ~29 px cinza (Margem: 29 ± 2 => 27 a 31 px)
            h2 = validar_faixa(pixels, x_alvo, y_f2, altura, COR_CINZA, min_px=27, max_px=31)
            
            if h2 > 0:
                y_f3 = y_f2 + h2
                # Faixa 3: ~1 px branco (Margem: 1 ± 2 => 0 a 3 px)
                h3 = validar_faixa(pixels, x_alvo, y_f3, altura, COR_BRANCO, min_px=0, max_px=3)
                
                if h3 >= 0:
                    # Padrão confirmado! Corta 6 pixels acima do início da faixa
                    posicao_corte = max(0, y - 6)
                    posicoes_corte.append(posicao_corte)
                    
                    tamanho_total_padrao = h1 + h2 + h3
                    print(f"Padrão encontrado em y={y} (H1:{h1}px, H2:{h2}px, H3:{h3}px). Cortando em y={posicao_corte}")
                    
                    # Avança o ponteiro y para além do padrão atual
                    y += max(1, tamanho_total_padrao)
                    continue

        y += 1

    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem nas posições de corte identificadas.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão correspondente foi encontrado na coluna 315!")
        return
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção até o início do corte atual
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima parte se inicia exatamente no ponto de corte anterior para manter os 6px
        posicao_anterior = posicao_corte

    # Salva a parte restante final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Atualize para o nome da sua imagem
    pasta_saida = "resultado_questoes"                       # Atualize para o nome da pasta de saída

    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")