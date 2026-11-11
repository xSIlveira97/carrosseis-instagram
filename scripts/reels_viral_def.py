"""Definições dos Reels no padrão viral (reel_viral.py).

Regra do Kenneth: o conteúdo ENTREGA PRONTO. Nada que soe como tarefa ("monte", "faça", "anote", "reveja", "exercício").

  gancho        (texto branco, texto amarelo) — na tela nos 3 primeiros segundos (ou None)
  frases_chave  [(origem, início, fim)] — trechos com zoom de impacto (1.28) e whoosh
  cartoes       lambda m: [(início, fim, texto)] — como em reels_def.py
  musica        arquivo em ~/Movies/_Edicao_Kenneth_TRABALHO/musica (as mesmas trilhas do VSL)
  fim           chamada final (cartão nos últimos fim_dur segundos) ou None
  cauda         segundos finais sem fala, com aproximação lenta e trilha (para cartões com texto longo)
  sem_legenda   [(origem, início, fim)] — onde não mostrar legenda (ex.: cartão de título do VSL)
  evitar_video  [(origem, início, fim)] — tomada de outra pessoa no começo do corte
Vocabulário: nunca "captação".
"""

REELS = {
    "M2S2": dict(
        saida="M02S2_whatsapp_oficial",
        trechos=[("11", 1.7, 58.55)],
        gancho=("SÓ CONSEGUI\\NESCALAR QUANDO", "TIREI O WHATSAPP\\NDO CELULAR"),
        frases_chave=[("11", 10.4, 13.4), ("11", 41.2, 46.6), ("11", 54.2, 58.55)],
        cartoes=lambda m: [
            (m("11", 3.2), m("11", 10.3), "{b}BUSINESS{/b}\\Nnegócio pequeno"),
            (m("11", 10.4), m("11", 14.0), "{b}OFICIAL{/b}\\Nescala"),
            (m("11", 33.0), m("11", 58.55), "{b}3 SINAIS DE QUE É HORA DE TROCAR{/b}\\N"
             "várias pessoas no mesmo número\\Nconversa que se perde\\Nninguém sabe quem respondeu"),
        ],
        musica="pulso_586317.mp3",
        fim="Oficial: a equipe toda no mesmo número",
        capa=("O CELULAR DO SEU ESCRITÓRIO VIROU", "GARGALO?"),
        foto=("11", 13.0),
    ),
    "M2S4": dict(
        saida="M02S4_whatsapp_caiu",
        trechos=[("17", 2.0, 16.7), ("16", 4.9, 29.8)],
        gancho=("MEU WHATSAPP FICOU", "2 MESES TRAVADO"),
        frases_chave=[("17", 12.2, 14.9), ("16", 9.8, 14.3), ("16", 20.4, 24.2)],
        cartoes=lambda m: [
            (m("16", 14.3), m("16", 24.15), "{b}O PLANO B PRONTO{/b}\\N"
             "1. número reserva já ativo\\N2. outros canais divulgados\\N3. aviso pronto para o cliente\\N4. um responsável por acionar"),
        ],
        musica="tensao_313611.mp3",
        evitar_video=[("17", 0.0, 2.6)],  # tomada do Alexandre até 2,5 s
        fim="Com plano B, o escritório não para",
        capa=("E SE O SEU WHATSAPP", "CAIR AMANHÃ?"),
        foto=("16", 22.0),
    ),
    # M3S2 (19/01) retirado: era só VSL; os trechos de podcast que combinam já estão em 08/12 e 16/02 → gravar
    "M3S3": dict(
        saida="M03S3_erro_e_processo",
        # abre com o podcast e fecha com a frase do VSL (que tem cartão de título próprio)
        trechos=[("07", 7.35, 22.65), ("VSL", 268.2, 273.95)],
        gancho=("TODO ERRO DA EQUIPE", "TEM A MESMA ORIGEM"),
        frases_chave=[("07", 15.0, 22.65)],
        cartoes=lambda m: [
            (m("07", 15.0), m("07", 22.65), "{b}O QUE FAZ O ERRO NÃO VOLTAR{/b}\\Nchecklist na etapa onde ele aconteceu\\Nconferência automática no sistema\\Nregra escrita, não só conversa"),
        ],
        sem_legenda=[("VSL", 268.6, 272.85)],  # o cartão do VSL já escreve a frase na tela
        musica="engrenagem_149933.mp3",
        fim=None,
        capa=("SE O ERRO ACONTECEU,", "O PROCESSO PERMITIU"),
        foto=("07", 14.0),
    ),
    "M4S2": dict(
        saida="M04S2_estrutura_de_fases",
        trechos=[("08", 22.25, 34.31)],
        gancho=("PARE DE PERGUNTAR", "A MESMA COISA\\NAO CLIENTE"),
        frases_chave=[("08", 25.6, 28.9)],
        cartoes=lambda m: [
            (m("08", 25.6), m("08", 34.31), "{b}EM CADA FASE{/b}\\Nquem cuida\\Npra onde vai\\Nque etapa está"),
        ],
        musica="pulso_586317.mp3",
        cauda=6.0,
        fim="{b}FICHA DO CLIENTE{/b}\\N{b}campos mínimos{/b}\\Nnome, contato e cidade\\Ntipo de caso e resumo"
            "\\Norigem do contato\\Nfase atual e responsável\\Ndocumentos recebidos",
        fim_dur=6.0,
        capa=("REGISTRE UMA VEZ.", "NÃO PERGUNTE DE NOVO."),
        foto=("08", 26.0),
    ),
    "M11S2": dict(
        saida="M11S2_pauta_no_whatsapp",
        # podcast (corte 19, você falando até 25 s) + frase do VSL
        trechos=[("19", 5.65, 18.2), ("VSL", 321.7, 329.15)],
        gancho=("SUA PRÓXIMA PAUTA", "ESTÁ NO SEU\\NWHATSAPP"),
        frases_chave=[("19", 11.0, 14.0), ("VSL", 323.2, 324.75)],
        legenda_y=1640, card_top=990,  # VSL: tarja CAPTA
        musica="esperanca_112623.mp3",
        cauda=6.0,
        # entrega o resultado: as pautas prontas (perguntas que o cliente trabalhista repete), não uma tarefa
        fim="{b}4 PAUTAS PRONTAS{/b}\\N“Fui demitido, tenho direito a quê?”\\N“Quanto tempo demora o processo?”"
            "\\N“Posso processar se ainda trabalho lá?”\\N“E se eu não tiver testemunha?”",
        fim_dur=6.0,
        capa=("SUA PAUTA ESTÁ NO", "SEU WHATSAPP"),
        foto=("19", 12.0),
    ),
    "M12S3": dict(
        saida="M12S3_reuniao_de_15_minutos",
        # podcast (corte 05) + VSL sem "sua captação": "três números simples que mostram onde | está travando…"
        trechos=[("05", 6.3, 14.9), ("VSL", 358.45, 361.0), ("VSL", 361.78, 366.45)],
        gancho=("3 NÚMEROS MOSTRAM", "ONDE SEU\\NESCRITÓRIO TRAVA"),
        # entrega o resultado: diz quais são os 3 números (os mesmos do Reel de 08/12)
        cartoes=lambda m: [
            (m("VSL", 358.6), m("VSL", 366.45), "{b}OS 3 NÚMEROS{/b}\\N1. custo por contato\\N2. % de contatos qualificados\\N3. % que viraram contrato"),
        ],
        frases_chave=[("05", 9.2, 12.5), ("VSL", 358.5, 360.2)],
        legenda_y=1640, card_top=990,
        musica="confiante_269520.mp3",
        cauda=6.0,
        fim="{b}COMO LER{/b}\\Ncusto alto: público ou anúncio\\Npoucos qualificados: mensagem"
            "\\Nfecha pouco: atendimento",
        fim_dur=6.0,
        capa=("REUNIÃO DE", "15 MINUTOS"),
        foto=("05", 10.0),
    ),
}
