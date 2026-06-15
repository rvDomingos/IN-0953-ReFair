# Índice da documentação — IN-0953-ReFAIR

Mapa de todos os documentos do projeto, por finalidade. **Comece pelo relatório final.**
Dados em [datasets/](datasets/) (ver [datasets/README.md](datasets/README.md)); scripts em [scripts/](scripts/).

---

## 🎯 Entrega (leia estes primeiro)
| Doc | O que é |
|---|---|
| **[RELATORIO-GERAL-experimento.md](RELATORIO-GERAL-experimento.md)** | **Relatório final** consolidado — método, resultados (RQ1), extensão (RQ2), causa-raiz, ameaças. |
| [ameacas-a-validade.md](ameacas-a-validade.md) | Ameaças à validade (4 categorias + status). |
| [o-que-falta.md](o-que-falta.md) | Estado atual e o que falta para entregar. |
| [mapa-do-projeto-e-divisao-4-pessoas.md](mapa-do-projeto-e-divisao-4-pessoas.md) | Tudo que foi feito (bullets) + divisão de trabalho para 4 pessoas. |
| [apresentacao-3-pessoas.md](apresentacao-3-pessoas.md) | Roteiro de apresentação (3 pessoas, baseado no artigo). |

## 🔬 Experimento (RQ1 — o ReFAIR não generaliza)
| Doc | O que é |
|---|---|
| [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) | Resultados estágio a estágio (domínio/ML task/features). |
| [metricas-formais-item-a.md](metricas-formais-item-a.md) | Métricas formais (F1, Hamming, subset, por LLM, causa de erro). |
| [analise-raiz-xgboost.md](analise-raiz-xgboost.md) | **Causa-raiz**: parser/posição-3, dump da árvore, prova por permutação. |
| [refair-vetorizacao-e-defeito-do-parser.md](refair-vetorizacao-e-defeito-do-parser.md) | Técnico: tokenização × embeddings, o defeito do parser, validação no TTL. |
| [explicacao-simples-porque-o-refair-erra.md](explicacao-simples-porque-o-refair-erra.md) | Versão ELI5 da causa-raiz. |

## 🛠️ Extensão (RQ2 — como consertar)
| Doc | O que é |
|---|---|
| [passo-a-passo-extensao-37.md](passo-a-passo-extensao-37.md) | **A extensão**: domínio por embeddings (37%) + ML task config D (0,283) + ablação. Como (re)treinar e rodar. |
| [roadmap-80-porcento.md](roadmap-80-porcento.md) | Caminho rumo a ≥80% (sentence-transformers, augmentation, LLM). |

## 📚 Apoio / como rodar
| Doc | O que é |
|---|---|
| [SETUP.md](SETUP.md) | Setup cross-platform (Docker / venv / app web). |
| [como-rodar-no-windows.md](como-rodar-no-windows.md) | Passo a passo no Windows. |
| [estagio3-passo-a-passo.md](estagio3-passo-a-passo.md) | Fluxo da anotação humana do estágio 3 (κ + painel). |
| [resumo-features-fabris-3fontes.md](resumo-features-fabris-3fontes.md) | Por que o `.ttl` do Fabris não vira ground truth melhor. |

## 🏗️ Construção do gabarito / equivalência
| Doc | O que é |
|---|---|
| [equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md) | Equivalência UStAI ↔ Synthetic (fonte do gabarito). |
| [pessoa4-mapeamento-dominios.md](pessoa4-mapeamento-dominios.md) | Fatia de mapeamento da Pessoa 4 (artefato de divisão de trabalho). |
| [divisao-roles-analise-manual.md](divisao-roles-analise-manual.md) | Divisão dos roles entre as 4 pessoas para anotação. |

## 🗂️ Histórico / planejamento (início do projeto — contexto, não resultado)
| Doc | O que é |
|---|---|
| [analise-replicacao-novo-dataset.md](analise-replicacao-novo-dataset.md) | (18/mai) Viabilidade: por que não é replicação fiel; propõe validade externa. |
| [plano-de-acao-refair.md](plano-de-acao-refair.md) | (19/mai) Plano operacional para colocar o ReFAIR para rodar. |
| [validade-externa-refair-ustai.md](validade-externa-refair-ustai.md) | (21/mai) Plano da Rota A (validade externa) que virou o experimento. |
| [roteiro-apresentacao.md](roteiro-apresentacao.md) | Roteiro de apresentação para **4** pessoas (versão anterior; a atual é a de 3). |

> **Nota:** os docs de "histórico/planejamento" registram o raciocínio inicial e as decisões; os resultados finais estão nos blocos 🎯/🔬/🛠️. Em caso de divergência de números, vale o **relatório final**.
