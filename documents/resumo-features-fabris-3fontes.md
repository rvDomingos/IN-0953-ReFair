# Resumo — Proveniência das features (Fabris) e comparação de 3 fontes (Estágio 3)

**Data:** 2026-06-11
**O que este doc é:** o resumo das duas tabelas geradas ao investigar de onde vêm as *sensitive features* do ReFAIR e como a recomendação do Estágio 3 se compara à ontologia do Fabris.

> Pergunta que originou isto: *"o PDF do Fabris (`s10618-022-00854-z`), que cruza tarefas de ML com domínios, não serviria como ground truth?"*

---

## Conclusão em uma frase

As *sensitive features* **vêm mesmo do Fabris** — mas a tabela `domains-features-mapping.csv` do ReFAIR **já é** essa ontologia re-engenheirada pelos autores. Re-derivar do `.ttl` cru **não dá um ground truth melhor** (só mais ruidoso); o ground truth independente do Estágio 3 ainda exige **anotação humana** (ver [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md)).

---

## Tabela 1 — Proveniência: Fabris (`.ttl`) × tabela do ReFAIR

**Arquivo:** [datasets/analises/fabris-ttl-vs-refair-csv-dominios.csv](datasets/analises/fabris-ttl-vs-refair-csv-dominios.csv) (`.xlsx` ao lado)

Compara, por domínio, as features sensíveis extraídas da ontologia do Fabris (`fairness_databriefs_alpha_v01.ttl`) contra as da tabela que o ReFAIR usa em runtime.

| Coluna | O que é |
|---|---|
| `dominio` | domínio (vocabulário ReFAIR) |
| `features_fabris_ttl_norm` | features extraídas do `.ttl` e normalizadas ao vocabulário canônico |
| `features_refair_csv` | features na `domains-features-mapping.csv` do ReFAIR |
| `so_no_fabris` / `so_no_refair` | diferenças entre as duas |

**Leitura honesta:** a tabela do ReFAIR **mantém texto livre cru** do Fabris ("news provider", "user age", "jersey color (athletes)", "textual references…"). Isso prova que ela **é** a curadoria oficial do `.ttl`. As diferenças que aparecem são, em boa parte, **artefato da minha normalização/mapeamento** (ex.: colapsei "applied psychology"→psychology, "skin color/type/tone"→skin tone), **não** "implementação divergindo da ontologia". Use esta tabela para **documentar a proveniência** no relatório — não como gabarito alternativo.

---

## Tabela 2 — Comparação de 3 fontes de features, por user story

**Arquivo:** [datasets/analises/ustai-features-3fontes.csv](datasets/analises/ustai-features-3fontes.csv) (`.xlsx` ao lado) — 1258 US

| Coluna | O que é |
|---|---|
| `features_refair` | o que o ReFAIR **de fato** recomendou (domínio∩tarefa previstos) |
| `features_proxy_intersecao` | proxy: domínio∩tarefa **do gabarito** (lógica do `feature_extraction`) |
| `features_dominio_ontologia` | todas as features do **domínio do gabarito** na ontologia curada = **teto/upper bound** |
| `refair_dentro_do_dominio` | `Sim`/`Não`/`—`: as features do ReFAIR cabem no domínio correto? |
| `refair_falsos_positivos` | features que o ReFAIR sugeriu **fora** do domínio correto |

### Números

| Métrica | Valor |
|---|---|
| Stories com features do ReFAIR **⊆ domínio correto** | **140 / 1258** |
| Stories com **falsos positivos** (feature de outro domínio) | **361 / 1258** |

**Interpretação:** o baixo "dentro do domínio" e o alto número de falsos positivos **não são um problema novo do Estágio 3** — são **reflexo do erro de domínio** (acerto de 9,4% no Estágio 1). Como o ReFAIR erra o domínio, ele recomenda features do domínio **errado**. É a mesma **propagação de erro** (domínio → tarefa → features), agora medida no estágio final.

---

## O que isso fecha e o que continua aberto

- ✅ **Proveniência documentada:** dá para afirmar, com tabela, que as features são do Fabris e que a tabela do ReFAIR é a curadoria dele.
- ✅ **Comparação de 3 fontes pronta** para o relatório (ReFAIR × proxy × ontologia).
- 🔴 **Continua aberto (item D):** o ground truth **independente** do Estágio 3 — anotação humana das US. Nem o código (`feature_extraction`) nem o `.ttl` cru substituem isso. Passo a passo em [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md).

---

## Arquivos relacionados
- [o-que-falta.md](o-que-falta.md) · [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md)
