# Mês 2 · Manter escuta e atendimento quando o volume cresce

Produzido e aprovado em 11/11/2026. Arquivos no GitHub: xSIlveira97/carrosseis-instagram, pasta `mes02_atendimento/`.
O Business Suite só programa até ~29 dias à frente, então cada post tem uma tarefa agendada (no app do Claude) que o programa quando a janela abre, sempre às 12h20.
Horário padrão do pacote: 12h (Brasília), só Instagram @eusoukennethribeiro.

| # | Data | Formato | Tema | Arquivo | Situação |
|---|---|---|---|---|---|
| 01 | ter 15/12 | Reel | Quantos contatos sua equipe aguenta por dia? | — | **Falta gravar** (sua resposta, ~35 s) + autorização do Alexandre |
| 02 | qui 17/12 | Carrossel (9) | Quantos contatos sua equipe aguenta? | `carrosseis/M02C1_capacidade_da_equipe/` | ✅ Aprovado · tarefa programa em 18/11 |
| 03 | ter 22/12 | Reel (55 s, padrão viral) | WhatsApp Business ou oficial: quando trocar | `reels/M02S2_whatsapp_oficial.mp4` | ✅ Aprovado · tarefa programa em 23/11 |
| 04 | qui 24/12 | Carrossel (10) | Saindo do celular: o que preparar | `carrosseis/M02C2_saindo_do_celular/` | ✅ Aprovado · tarefa programa em 25/11 |
| 05 | ter 29/12 | Reel (~20 s) | As perguntas que separam curioso de caso | — | **Falta gravar** o fechamento (~5 s) |
| 06 | qui 31/12 | Carrossel (9) | Roteiro de triagem em 6 perguntas | `carrosseis/M02C3_roteiro_de_triagem/` | **Advogado revisa as perguntas 2 a 5** antes de publicar |
| 07 | ter 05/01 | Reel (39 s, padrão viral) | O dia em que o WhatsApp cai | `reels/M02S4_whatsapp_caiu.mp4` | ✅ Aprovado · tarefa programa em 07/12 |
| 08 | qui 07/01 | Carrossel (9) | Plano B de atendimento | `carrosseis/M02C4_plano_b/` | ✅ Aprovado · tarefa programa em 09/12 |

Reels: envie o .mp4 e use o `_capa.jpg` como capa; o `_capa_feed4x5.jpg` é o recorte do grid.
Carrosséis: envie as lâminas na ordem 01, 02, 03… (1080×1350). A legenda está em `legenda.txt` dentro de cada pasta.

## Legendas dos Reels

### 03 · ter 22/12 · WhatsApp Business ou oficial
```
Enquanto uma pessoa atende pelo celular, o WhatsApp Business resolve. Quando o volume cresce, o celular vira gargalo.

Sinais de que é hora de olhar para o WhatsApp oficial (API):
1. Mais de uma pessoa precisa atender o mesmo número.
2. Conversas se perdem ou ficam sem resposta.
3. Ninguém sabe dizer quem respondeu o cliente e quando.

O oficial é contratado com a Meta, direto ou por um provedor parceiro, fica num sistema e não depende de um aparelho.

Salve para decidir com a equipe.
```

### 07 · ter 05/01 · O dia em que o WhatsApp cai
```
Conta bloqueada não avisa antes. Se todo o atendimento passa por um único número, um bloqueio para o escritório.

Plano B em 4 passos:
1. Um número reserva já ativo e aquecido.
2. Outros canais divulgados ao cliente: telefone, e-mail, Instagram.
3. Uma mensagem de aviso pronta para usar.
4. Uma pessoa responsável por acionar o plano.

Monte o seu esta semana.
```

## O que falta para fechar o mês

1. **Gravar 2 falas curtas** (mesmo cenário do podcast ou selfie com boa luz):
   - 15/12, resposta (~35 s): “Antes de aumentar o anúncio, faça uma conta. Quantas pessoas atendem? Quantas horas por dia cada uma fica no atendimento? Quantos contatos cada uma consegue conduzir bem por hora? Multiplica. Esse é o teto do dia. Se a fila passa disso, o cliente espera, e quem espera vai para outro escritório. Quando a fila chegar perto do teto, você tem duas saídas: reduzir a verba ou colocar mais gente. Limite de anúncio não se decide no susto. Se decide antes, pela capacidade.”
   - 29/12, fechamento (~5 s): “Pergunta fixa, resposta registrada, e o advogado decide com tudo na mão.”
2. **Autorização do Alexandre** para usar a pergunta dele (corte 06) no Reel de 15/12.
3. **Revisão do advogado** nas perguntas 2 a 5 do carrossel de 31/12 (são perguntas da área trabalhista).
4. **Confirmar o número do Reel de 22/12:** agora o vídeo vai até o fim da frase, “…e aguentar receber duas mil mensagens por dia”. Se o número não for exato, corto essa parte.
5. **Conferir outra fala do Reel de 22/12:** você diz que o número oficial “nunca teve WhatsApp”. Hoje a Meta já permite, em alguns casos, usar o número atual (inclusive junto com o app). Se preferir, corto essa frase; a legenda e o carrossel já dizem “confirme com o provedor”.

## Como foi feito
- Reels: `_scripts/reel.py` (cortes do podcast em ~/Downloads/job_…, pausas longas encurtadas, legenda palavra a palavra, cartões amarelos, áudio normalizado).
- Carrosséis: `_scripts/carrosseis_m2.py` + `_scripts/render_carrossel.py` (mesmo modelo do mês 1).
