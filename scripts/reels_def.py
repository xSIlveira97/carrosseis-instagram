"""Definições dos Reels de terça (meses 3 a 12) que já têm material gravado.

Campos:
  saida     nome do arquivo
  trechos   [(origem, início, fim)] — origem "VSL" ou número do corte do podcast; tempos em segundos da origem
  abertura  título de abertura (2,6 s) ou None
  cartoes   lambda m: [(início, fim, texto)] — m(origem, t) converte tempo da origem para o vídeo final;
            tempos negativos contam a partir do fim; \\N quebra linha; {b}...{/b} negrito
  congelar  segundos de imagem parada no fim (para o cartão final)
  fim       texto do cartão final (ou None); fim_dur = duração dele
  capa      (texto branco, texto amarelo); foto = (origem, segundo)
Vocabulário: nunca "captação" (no M12S3 a palavra foi cortada da fala).
"""

REELS = {
    "M3S2": dict(
        saida="M03S2_responsavel_criterio_prazo",
        trechos=[("VSL", 226.2, 231.25), ("VSL", 335.6, 342.75)],
        abertura="TODA ETAPA PRECISA DE 3 COISAS",
        cartoes=lambda m: [
            (m("VSL", 338.6), m("VSL", 342.75), "{b}RESPONSÁVEL · CRITÉRIO · PRAZO{/b}"),
        ],
        congelar=8.0,
        fim="{b}MONTE O SEU QUADRO{/b}\\Netapa · responsável\\npronto quando · prazo".replace("\\n", "\\N")
            + "\\N \\N{b}Exemplo hipotético{/b}\\NPrimeiro contato · Ana\\NPronto: caso registrado\\NPrazo: até 5 minutos",
        fim_dur=8.0,
        capa=("TODA ETAPA PRECISA DE", "3 COISAS"),
        foto=("VSL", 228.5),
        capa_y=1430,
    ),
    "M3S3": dict(
        saida="M03S3_erro_e_processo",
        trechos=[("VSL", 268.2, 273.95), ("07", 7.35, 22.65)],
        abertura=None,  # o próprio VSL abre com o cartão "Se o erro aconteceu…"
        legenda_desde=4.6,  # o cartão do VSL fica na tela de 0,5 s a 4,6 s; legenda só depois
        cartoes=lambda m: [
            (m("07", 15.0), m("07", 22.65), "{b}DEPOIS DE CADA ERRO{/b}\\N1. Em que etapa aconteceu?\\N2. O que permitiu?\\N3. O que impede a repetição?"),
        ],
        congelar=3.0,
        fim="{b}Corrigir o caso resolve hoje.{/b}\\N{b}Corrigir o processo resolve os próximos.{/b}",
        fim_dur=3.0,
        capa=("SE O ERRO ACONTECEU,", "O PROCESSO PERMITIU"),
        foto=("07", 14.0),
    ),
    "M4S2": dict(
        saida="M04S2_estrutura_de_fases",
        trechos=[("08", 22.25, 34.31)],
        abertura="SEU CLIENTE REPETE OS DADOS TODA VEZ?",
        cartoes=lambda m: [
            (m("08", 25.6), m("08", 34.31), "{b}EM CADA FASE{/b}\\Nquem cuida\\Npra onde vai\\Nque etapa está"),
        ],
        congelar=7.0,
        fim="{b}FICHA DO CLIENTE{/b}\\N{b}campos mínimos{/b}\\Nnome, contato e cidade\\Ntipo de caso e resumo\\Norigem do contato\\Nfase atual e responsável\\Ndocumentos recebidos",
        fim_dur=7.0,
        capa=("REGISTRE UMA VEZ.", "NÃO PERGUNTE DE NOVO."),
        foto=("08", 26.0),
    ),
    "M11S2": dict(
        saida="M11S2_pauta_no_whatsapp",
        trechos=[("VSL", 321.7, 329.15)],
        abertura="SUA PAUTA ESTÁ NO SEU WHATSAPP",
        cartoes=lambda m: [],
        congelar=6.0,
        fim="{b}EXERCÍCIO DA SEMANA{/b}\\N1. abra as conversas da semana\\N2. anote as 10 perguntas\\Nque mais se repetem\\N3. cada pergunta vira um conteúdo",
        fim_dur=6.0,
        capa=("SUA PAUTA ESTÁ NO", "SEU WHATSAPP"),
        foto=("VSL", 324.0),
        capa_y=1430,
    ),
    "M12S3": dict(
        saida="M12S3_reuniao_de_15_minutos",
        # corta "sua captação" da fala: "três números simples que mostram onde | está travando…"
        trechos=[("VSL", 358.45, 361.0), ("VSL", 361.78, 366.45)],
        abertura="15 MINUTOS QUE MOSTRAM ONDE O ESCRITÓRIO TRAVA",
        cartoes=lambda m: [],
        congelar=7.0,
        fim="{b}PAUTA DE 15 MINUTOS{/b}\\N1. os 3 números da semana\\N2. o principal gargalo\\N3. uma decisão\\N4. um responsável e um prazo",
        fim_dur=7.0,
        capa=("REUNIÃO DE", "15 MINUTOS"),
        foto=("VSL", 359.5),
        capa_y=1430,
    ),
}
