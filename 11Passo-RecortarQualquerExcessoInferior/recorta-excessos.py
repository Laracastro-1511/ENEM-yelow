import os
import shutil
from PIL import Image


def encontrar_linha_pontilhada(
    imagem, cor_alvo=(0, 0, 0), tolerancia=50, min_pontos=3
):
    """Percorre a imagem de baixo para cima procurando por uma linha pontilhada.

    Identifica sequências de pixels escuros com largura entre 3 e 8px
    separados por lacunas de aproximadamente 8px.
    """
    largura, altura = imagem.size
    pixels = imagem.load()

    # Define a margem de inspeção horizontal (evita bordas laterais da imagem)
    x_inicio = int(largura * 0.1)
    x_fim = int(largura * 0.9)

    def pixel_corresponde(p):
        r, g, b = p[:3]
        return (
            abs(r - cor_alvo[0]) <= tolerancia
            and abs(g - cor_alvo[1]) <= tolerancia
            and abs(b - cor_alvo[2]) <= tolerancia
        )

    # Percorre de baixo para cima
    for y in range(altura - 1, 10, -1):
        pontos_encontrados = 0
        largura_ponto_atual = 0
        tamanho_lacuna_atual = 0
        em_ponto = False

        for x in range(x_inicio, x_fim):
            p = pixels[x, y]

            if pixel_corresponde(p):
                if not em_ponto:
                    # Transição de espaço para ponto
                    em_ponto = True
                    # Valida se a lacuna anterior tinha aproximadamente ~8px (tolerância: 5 a 12px)
                    if pontos_encontrados > 0 and not (
                        5 <= tamanho_lacuna_atual <= 12
                    ):
                        # Se a lacuna não bateu com o padrão pontilhado, reseta a contagem
                        pontos_encontrados = 0
                    tamanho_lacuna_atual = 0

                largura_ponto_atual += 1

            else:
                if em_ponto:
                    # Transição de ponto para espaço
                    em_ponto = False
                    # Valida se a largura do ponto está no intervalo observado (3 a 8px)
                    if 3 <= largura_ponto_atual <= 8:
                        pontos_encontrados += 1
                    else:
                        pontos_encontrados = 0
                    largura_ponto_atual = 0

                tamanho_lacuna_atual += 1

        # Se encontrou ao menos 'min_pontos' alinhados com o padrão na mesma linha
        if pontos_encontrados >= min_pontos:
            print(
                f"Linha pontilhada de rascunho encontrada na posição y={y}!"
            )
            return y

    return None


def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    os.makedirs(pasta_destino, exist_ok=True)

    arquivos = [
        f
        for f in os.listdir(pasta_origem)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
    ]

    print(f"Encontrados {len(arquivos)} arquivos para processar")

    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)

        try:
            with Image.open(caminho_origem) as imagem:
                print(
                    f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})"
                )

                # Busca pela linha pontilhada de baixo para cima
                posicao_corte = encontrar_linha_pontilhada(imagem, cor_alvo)

                if posicao_corte is not None and posicao_corte > 0:
                    # Recorta exatamente acima da linha pontilhada
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(
                        f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}"
                    )
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print("✓ Imagem mantida original (sem rascunho detectado)")

        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print("✓ Arquivo copiado mesmo com erro")
            except Exception:
                print("✗ Não foi possível copiar o arquivo")


if __name__ == "__main__":
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"

    # Defina a cor dos pontinhos (ex: preto/cinza escuro da linha)
    cor_alvo = (0, 0, 0)

    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")

    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)

    processar_imagens(pasta_origem, pasta_destino, cor_alvo)

    print("\n" + "=" * 50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")