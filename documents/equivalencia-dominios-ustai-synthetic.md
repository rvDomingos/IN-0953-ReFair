# Equivalência de Domínios — UStAI ↔ Synthetic User Stories (ReFAIR)

> Documento gerado para o projeto **IN-0953-ReFair**. Estabelece a correspondência entre o eixo de "domínio" do dataset **UStAI-annotated_V2** e os eixos de **domínio de aplicação** e **ML task** do dataset **Synthetic User Stories** do ReFAIR.

## 1. Objetivo

Mapear cada *user story* do dataset **UStAI** para o vocabulário do dataset **Synthetic User Stories** (ReFAIR), produzindo um dataset de equivalência que permita usar as user stories do UStAI como entrada/validação externa da pipeline do ReFAIR (ver `documents/analise-replicacao-novo-dataset.md`).

## 2. Os dois datasets e a coluna de "domínio"

| Dataset | Arquivo | Coluna usada como "domínio" | Cardinalidade |
|---|---|---|---|
| UStAI | `UStAI-annotated_V2.pdf` | `role_shorten` (papel declarado na user story) | 1260 user stories · 179 papéis distintos · 42 *abstracts* |
| Synthetic User Stories | `Synthetic User Stories.xlsx` | `Domain` (domínio de aplicação) | 34 domínios |
| Synthetic User Stories | `Synthetic User Stories.xlsx` | `Machine Learning Task` | 367 ML tasks |

> ⚠️ **Ressalva importante.** O PDF `Synthetic-User-Stories.pdf` entregue contém, na verdade, a lista das **367 ML Tasks** (coluna `Machine Learning Task` / aba *ML Dictionary*) — **não** a coluna de domínio. A coluna `Domain` real do dataset Synthetic está na aba *Dataset* do `.xlsx` e tem **34 domínios de aplicação**. Por isso a equivalência foi feita para **os dois eixos** (domínio de aplicação **e** ML task), conforme combinado.

Os **34 domínios** do Synthetic (ontologia de Fabris et al., reusada pelo ReFAIR):

`Biology, Cardiology, Computer Networks, Computer Vision, Demography, Dermatology, Economics, Education, Endocrinology, Finance & Marketing, Health, Information Systems, Law, Library, Linguistics, Literature, Medicine, Movies, Music, Nephrology, News, Pediatrics, Pharmacology, Plant Science, Political Science, Psychology, Radiology, Social Media, Social Networks, Social Work, Sociology, Sport, Transportation, Urban Studies`

## 3. Metodologia da equivalência

1. **Extração do UStAI.** As 1260 user stories foram extraídas do PDF (42 *abstracts* × 3 LLMs × 10 US). Cada linha tem `id`, `abstract`, `us_num`, `llm`, `role_shorten` e o texto da `user_story`.
2. **Âncora = `role_shorten`.** O `role_shorten` é o campo-chave do lado UStAI, como solicitado.
3. **Desambiguação pelo *abstract*.** Cada *abstract* (A1–A42) descreve **um único sistema de IA** — logo, todas as 30 user stories de um *abstract* compartilham o mesmo domínio de aplicação e a mesma ML task. Papéis genéricos (`researcher`, `developer`, `data scientist`, `manager`, `user`…) aparecem em dezenas de *abstracts*; sozinhos não determinam um domínio. Por isso o domínio é fixado **por *abstract*** (o contexto do sistema), exatamente a desambiguação escolhida. Papéis específicos de domínio (`radiologist`, `cardiologist`, `taxi driver`…) são coerentes com o *abstract* em que ocorrem.
4. **Domínio de aplicação.** Cada *abstract* foi classificado em 1 dos 34 domínios por análise temática das suas user stories.
5. **ML task.** Cada *abstract* foi associado a 1 das 367 ML tasks: a técnica nomeada quando o estudo gira em torno dela (ex.: *Fuzzy SVM* → `support vector machine`, *GANs* → `generative adversarial network`), ou o conceito da tarefa quando não há técnica única (ex.: `anomaly detection`, `recommendation system`).
6. **Confiança.** Cada *abstract* recebe `High`/`Medium`/`Low` para o mapeamento de domínio. `Low` = não há domínio perfeito entre os 34 (ex.: A4 militar, A38 recrutamento).

## 4. Tabela de equivalência por *abstract* (núcleo da equivalência)

Cada *abstract* = 30 user stories (10 Gemini_1.5_flash + 10 Llama 3.1 70b + 10 O1_mini).

| Abstract | Tema do sistema de IA | Domínio equivalente (Synthetic) | ML Task equivalente (Synthetic) | Confiança |
|---|---|---|---|---|
| A1 | Autonomous vehicles (AI + real-time data for perception & collision avoidance) | Transportation | machine perception | High |
| A2 | Wearable-based detection of physical aggression in children | Psychology | time-series classification | Medium |
| A3 | Real-time aggression detection on Twitter | Social Media | text classification | High |
| A4 | AI-powered military drones & international security | Political Science | reinforcement learning | Low |
| A5 | GoCart autonomous delivery robot in healthcare/residential facilities | Health | robot learning | High |
| A6 | ADAS driver-intention recognition with Gaussian Mixture Models | Transportation | mixture model | High |
| A7 | ML-based mental health / mental illness prediction | Psychology | classification method | Medium |
| A8 | Anomaly detection in smart-health wearable data | Health | anomaly detection | High |
| A9 | Heart disease diagnosis with Fuzzy SVM & incremental learning | Cardiology | support vector machine | High |
| A10 | Blood-glucose / hypoglycemia prediction with Support Vector Regression | Endocrinology | support vector regression | High |
| A11 | Anti-counterfeiting copy-detection patterns (digital twin, image-to-image GANs) | Computer Vision | generative adversarial network | Medium |
| A12 | Firearm Violence Vulnerability Index (XGBoost community-risk forecasting) | Social Work | gradient boosting | Low |
| A13 | AI-DrugNet drug repurposing for Alzheimer’s disease | Pharmacology | deep learning | High |
| A14 | NYC taxi / Uber ridership prediction | Transportation | forecasting algorithms | High |
| A15 | Income / poverty prediction from demographic & lifestyle data | Economics | classification method | High |
| A16 | Newborn cry diagnostic system (cry-audio classification) | Pediatrics | classification method | High |
| A17 | Sleep apnea / hypopnea prediction with LAMSTAR neural networks | Medicine | artificial neural network | High |
| A18 | Tuberculosis detection from chest X-rays with CNNs | Radiology | convolutional neural network | High |
| A19 | Credit-card default prediction | Finance & Marketing | classification method | High |
| A20 | Drug-abuse prediction from Big Five personality traits | Psychology | classification method | Medium |
| A21 | Racial & gender bias in online freelancing marketplaces | Economics | data mining | Low |
| A22 | Multidimensional freelancer assessment framework for online labor | Economics | learning ranking | Low |
| A23 | Search-engine bias analysis (PAWS platform) | Information Systems | information retrieval | Medium |
| A24 | ArnetMiner academic search / academic social network | Library | information retrieval | High |
| A25 | E-commerce recommendation (item-to-item collaborative filtering) | Information Systems | recommendation system | Medium |
| A26 | Explainable recommendation justifications (Seq2Seq, aspect-planning) | Information Systems | natural language generation | Medium |
| A27 | Session-based recommendation with RNNs | Information Systems | recommendation system | Medium |
| A28 | Reciprocal dating recommender from speed-dating data | Social Networks | recommendation system | Medium |
| A29 | Historical census record linkage | Demography | classification method | High |
| A30 | Recidivism prediction with Decision Trees (criminal justice) | Law | decision tree | High |
| A31 | Advertisement identification on web pages | Finance & Marketing | classification method | Low |
| A32 | Stance detection with multi-task learning (NLP) | Linguistics | multi-task learning | Medium |
| A33 | Semantic news search with Wikidata annotation | News | information retrieval | High |
| A34 | DNN-based network intrusion detection system | Computer Networks | deep neural network | High |
| A35 | Wholesale sales prediction with ARIMA | Finance & Marketing | time series forecasting | High |
| A36 | Moving-vehicle classification via wireless sensor networks | Transportation | time-series classification | High |
| A37 | Fantasy sports analytics & player selection | Sport | data mining | High |
| A38 | AI recruitment & personality assessment | Psychology | classification method | Low |
| A39 | Playlist success prediction | Music | classification method | High |
| A40 | Compromised social-network account detection | Social Networks | anomaly detection | High |
| A41 | Food image recognition with stacked global-local attention network | Computer Vision | attention mechanism | Medium |
| A42 | Mobile vaccination-site placement optimization | Health | recommendation system | High |

**Notas dos mapeamentos de menor confiança:**

- **A2** (Psychology): Alternativa: Pediatrics (populacao infantil).
- **A4** (Political Science): Nao ha dominio Militar/Defesa nos 34; Political Science e o mais proximo (seguranca internacional).
- **A7** (Psychology): Alternativa: Health.
- **A11** (Computer Vision): Dominio de aplicacao = seguranca de marca; Computer Vision e o mais proximo dos 34.
- **A12** (Social Work): Alternativas: Sociology / Political Science / Health (saude publica).
- **A20** (Psychology): Alternativas: Pharmacology / Social Work.
- **A21** (Economics): Mercado de trabalho online; alternativas: Social Networks / Sociology.
- **A22** (Economics): Alternativas: Social Networks / Information Systems.
- **A23** (Information Systems): Alternativa: Social Media.
- **A25** (Information Systems): Alternativa: Finance & Marketing.
- **A26** (Information Systems): Contexto = sistemas de recomendacao explicaveis.
- **A27** (Information Systems): Alternativa: Finance & Marketing.
- **A28** (Social Networks): Alternativa: Sociology.
- **A31** (Finance & Marketing): Publicidade; alternativa: Information Systems.
- **A32** (Linguistics): Alternativa: Social Media.
- **A38** (Psychology): Recrutamento/RH; nao ha dominio de RH nos 34. Alternativa: Economics.
- **A41** (Computer Vision): Alternativa de task: convolutional neural network.

### Distribuição das 1260 user stories por domínio equivalente

| Domínio | Nº user stories | Nº abstracts |
|---|---|---|
| Information Systems | 120 | 4 |
| Psychology | 120 | 4 |
| Transportation | 120 | 4 |
| Economics | 90 | 3 |
| Finance & Marketing | 90 | 3 |
| Health | 90 | 3 |
| Computer Vision | 60 | 2 |
| Social Networks | 60 | 2 |
| Cardiology | 30 | 1 |
| Computer Networks | 30 | 1 |
| Demography | 30 | 1 |
| Endocrinology | 30 | 1 |
| Law | 30 | 1 |
| Library | 30 | 1 |
| Linguistics | 30 | 1 |
| Medicine | 30 | 1 |
| Music | 30 | 1 |
| News | 30 | 1 |
| Pediatrics | 30 | 1 |
| Pharmacology | 30 | 1 |
| Political Science | 30 | 1 |
| Radiology | 30 | 1 |
| Social Media | 30 | 1 |
| Social Work | 30 | 1 |
| Sport | 30 | 1 |

## 5. Equivalência `role_shorten` → domínio

Dos **179** papéis distintos, **110** mapeiam para um **único** domínio (papéis específicos) e **69** aparecem em **vários** domínios (papéis genéricos) — confirmando que o papel isolado não determina o domínio e que a desambiguação pelo *abstract* é necessária.

### 5.1. Papéis com domínio único

| role_shorten | Nº US | Domínio equivalente |
|---|---|---|
| archivist | 1 | Demography |
| banker | 1 | Finance & Marketing |
| bioinformatician | 2 | Pharmacology |
| candidate | 3 | Psychology |
| car manufacturer | 2 | Transportation |
| cardiologist | 1 | Cardiology |
| chef | 1 | Computer Vision |
| child | 2 | Psychology |
| client | 9 | Economics |
| commuter | 3 | Transportation |
| competitor in the search engine market | 1 | Information Systems |
| computational biologist | 1 | Pharmacology |
| content creator | 2 | Information Systems |
| content strategist | 1 | Information Systems |
| credit card issuer | 1 | Finance & Marketing |
| dating coach | 1 | Social Networks |
| defense contractor | 1 | Political Science |
| demographer | 1 | Demography |
| dietary staff member | 1 | Health |
| diplomat | 1 | Political Science |
| driver | 9 | Transportation |
| drone operator | 1 | Political Science |
| economic historian | 4 | Demography |
| endocrinologist | 1 | Endocrinology |
| entrepreneur | 1 | Pharmacology |
| environmentalist | 2 | Transportation |
| ethicist | 1 | Pediatrics |
| field commander | 1 | Political Science |
| forecasting expert | 1 | Finance & Marketing |
| freelancer | 9 | Economics |
| genealogist | 2 | Demography |
| GIS specialist | 1 | Political Science |
| grant writer | 1 | Social Work |
| health insurance provider | 1 | Endocrinology |
| Healthcare Administrator | 1 | Health |
| healthcare policy advisor | 1 | Medicine |
| historian | 2 | Demography |
| human-factors specialist | 1 | Transportation |
| innovator | 1 | Computer Vision |
| interoperability coordinator | 1 | Political Science |
| job seeker | 2 | Psychology |
| judge or magistrate | 1 | Law |
| kitchen staff member | 1 | Health |
| knowledge base specialist | 1 | News |
| lab technician | 3 | Health |
| law enforcement agency | 1 | Law |
| linguist | 2 | Linguistics |
| machine learning model | 1 | Psychology |
| member of the Pokec social network community | 1 | Social Networks |
| military commander | 3 | Political Science |
| modeler | 1 | Library |
| moderator | 3 | Social Media |
| music enthusiast | 7 | Music |
| music industry professional | 2 | Music |
| music label | 1 | Music |
| music producer | 1 | Music |
| music streamer | 1 | Music |
| musician | 1 | Music |
| neonatologist | 3 | Pediatrics |
| Network engineer | 1 | Transportation |
| network security specialist | 1 | Transportation |
| neurologist | 3 | Pharmacology |
| news agency | 3 | News |
| News editor | 1 | News |
| non-profit organization leader | 1 | Economics |
| non-proliferation expert | 1 | Political Science |
| OEM | 1 | Transportation |
| online retailer | 7 | Information Systems |
| organizer | 2 | Social Networks |
| participant | 1 | Transportation |
| passenger | 3 | Transportation |
| peacekeeper | 1 | Political Science |
| pediatrician | 1 | Pediatrics |
| person with dietary restricttions | 1 | Computer Vision |
| pharmaceutical company scientist | 1 | Pharmacology |
| pharmacist | 1 | Pharmacology |
| player | 9 | Sport |
| playlist creator | 1 | Music |
| playlist curator | 1 | Music |
| printing press operator | 1 | Computer Vision |
| public transportation official | 1 | Transportation |
| publisher | 1 | Library |
| radiologist | 5 | Radiology |
| recruiter | 3 | Psychology |
| research evaluator | 1 | Library |
| research funder | 1 | Library |
| resident | 1 | Health |
| residential care staff member | 2 | Health |
| restaurant operator | 1 | Computer Vision |
| resturant owner | 1 | Computer Vision |
| safety expert | 3 | Transportation |
| school counselor | 1 | Psychology |
| security expert | 3 | Computer Vision |
| shareholder of a wholesale company | 1 | Finance & Marketing |
| single person | 2 | Social Networks |
| sleep specialist | 2 | Medicine |
| social media moderator | 1 | Linguistics |
| social scientist studying the impact of technology on dating | 1 | Social Networks |
| sociologist studying assimilation and discrimination | 1 | Demography |
| software architect | 1 | Information Systems |
| sports fan | 8 | Sport |
| system | 1 | Health |
| taxi dispatcher | 2 | Transportation |
| taxi driver | 1 | Transportation |
| tester | 1 | Transportation |
| therapist | 1 | Psychology |
| traffic engineer | 1 | Transportation |
| trainer | 1 | Political Science |
| vaccination site coordinator | 1 | Health |
| visually impaired person | 1 | Transportation |

### 5.2. Papéis multi-domínio (genéricos)

Formato: `Domínio (nº user stories)`.

| role_shorten | Nº US | Domínios equivalentes |
|---|---|---|
| researcher | 162 | Information Systems (15), Psychology (14), Economics (14), Transportation (13), Computer Vision (11), Health (9), Social Work (7), Pharmacology (6), Medicine (6), Library (6), Social Networks (6), Linguistics (6), Computer Networks (6), Cardiology (5), Pediatrics (5), Finance & Marketing (5), Demography (5), Social Media (4), Endocrinology (4), Radiology (4), News (4), Law (3), Political Science (2), Sport (1), Music (1) |
| developer | 139 | Information Systems (30), Computer Vision (11), Finance & Marketing (11), Transportation (10), Psychology (10), Health (9), Social Networks (6), Pediatrics (5), Medicine (5), Social Media (4), Cardiology (4), Endocrinology (4), Library (4), News (4), Computer Networks (4), Law (3), Linguistics (3), Radiology (2), Economics (2), Demography (2), Sport (2), Political Science (1), Social Work (1), Pharmacology (1), Music (1) |
| data scientist | 81 | Information Systems (9), Psychology (7), Transportation (7), Economics (7), Health (6), Finance & Marketing (5), Social Networks (4), Cardiology (3), Computer Vision (3), Pharmacology (3), Library (3), Demography (3), Law (3), Computer Networks (3), Social Media (2), Social Work (2), Pediatrics (2), Medicine (2), Linguistics (2), Music (2), Endocrinology (1), Radiology (1), News (1) |
| analyst | 56 | Finance & Marketing (9), Transportation (6), Social Networks (6), Psychology (4), Economics (4), Information Systems (4), Linguistics (4), Health (2), Computer Vision (2), Social Work (2), Demography (2), Computer Networks (2), Sport (2), Music (2), Political Science (1), Cardiology (1), Endocrinology (1), Law (1), News (1) |
| manager | 45 | Finance & Marketing (13), Transportation (8), Health (8), Psychology (4), Economics (4), Sport (2), Social Media (1), Computer Vision (1), Library (1), Information Systems (1), Linguistics (1), Computer Networks (1) |
| user | 44 | Social Networks (12), Computer Vision (8), Psychology (4), Information Systems (4), Finance & Marketing (4), Social Media (3), Health (2), Sport (2), Music (2), Cardiology (1), Economics (1), Computer Networks (1) |
| administrator | 39 | Psychology (7), Social Networks (5), Social Media (4), Cardiology (4), Library (4), Economics (3), Health (2), Endocrinology (2), Radiology (2), Law (2), Computer Networks (2), Transportation (1), Medicine (1) |
| policymaker | 39 | Economics (8), Psychology (6), Information Systems (4), Social Work (3), Pharmacology (3), Finance & Marketing (3), Law (2), Health (2), Political Science (1), Computer Vision (1), Transportation (1), Radiology (1), Library (1), Demography (1), Computer Networks (1), Sport (1) |
| advocate | 29 | Transportation (4), Finance & Marketing (4), Economics (4), Psychology (3), Pediatrics (2), Radiology (2), Law (2), Linguistics (2), Political Science (1), Health (1), Endocrinology (1), Social Work (1), Pharmacology (1), Information Systems (1) |
| officer | 23 | Law (5), Health (3), Social Media (2), Transportation (2), Finance & Marketing (2), Social Networks (2), Psychology (1), Political Science (1), Endocrinology (1), Computer Vision (1), Social Work (1), Economics (1), Computer Networks (1) |
| healthcare provider | 21 | Psychology (5), Cardiology (4), Medicine (4), Health (3), Radiology (2), Endocrinology (1), Pharmacology (1), Pediatrics (1) |
| customer | 20 | Information Systems (14), Finance & Marketing (5), Economics (1) |
| patient | 19 | Health (7), Radiology (4), Cardiology (3), Endocrinology (3), Medicine (2) |
| product manager | 18 | Information Systems (3), Social Networks (3), Finance & Marketing (3), Linguistics (3), Music (2), Pediatrics (1), Radiology (1), News (1), Computer Networks (1) |
| machine learning engineer | 16 | Computer Vision (3), Information Systems (2), Social Networks (2), Social Work (1), Pharmacology (1), Economics (1), Pediatrics (1), Radiology (1), Psychology (1), Demography (1), Linguistics (1), Computer Networks (1) |
| public health official | 14 | Psychology (4), Social Work (4), Health (3), Radiology (2), Pediatrics (1) |
| quality assurance specialist | 13 | Computer Vision (3), Health (1), Cardiology (1), Pediatrics (1), Medicine (1), Radiology (1), Economics (1), Information Systems (1), Social Networks (1), Computer Networks (1), Transportation (1) |
| global citizen | 12 | Information Systems (4), Economics (2), News (1), Transportation (1), Sport (1), Psychology (1), Music (1), Health (1) |
| IT specialist | 11 | Health (4), Finance & Marketing (2), Cardiology (1), Computer Vision (1), Medicine (1), Law (1), Social Networks (1) |
| strategist | 11 | Political Science (4), Information Systems (2), Transportation (1), Social Work (1), Social Networks (1), Sport (1), Music (1) |
| city planner | 10 | Transportation (8), Social Work (1), Health (1) |
| HR specialist | 10 | Psychology (7), Economics (3) |
| parent | 10 | Psychology (6), Pediatrics (2), Finance & Marketing (2) |
| healthcare professional | 9 | Psychology (3), Health (2), Pediatrics (2), Radiology (2) |
| journalist | 9 | News (5), Social Media (1), Information Systems (1), Linguistics (1), Health (1) |
| marketing professional | 9 | Information Systems (3), Finance & Marketing (2), Social Media (1), Economics (1), Medicine (1), Music (1) |
| cybersecurity expert | 8 | Political Science (3), Transportation (1), Social Media (1), Health (1), Computer Networks (1), Social Networks (1) |
| librarian | 8 | Library (3), Demography (2), News (2), Information Systems (1) |
| person | 8 | Endocrinology (6), Social Media (1), Psychology (1) |
| software engineer | 8 | Transportation (2), Linguistics (2), Endocrinology (1), Information Systems (1), Social Networks (1), Music (1) |
| citizen | 7 | Health (2), Political Science (1), Economics (1), Law (1), News (1), Transportation (1) |
| community leader | 7 | Social Work (5), Health (2) |
| consumer | 7 | Information Systems (2), News (2), Transportation (1), Economics (1), Finance & Marketing (1) |
| engineer | 7 | Transportation (5), Health (1), Computer Networks (1) |
| instructor | 7 | Finance & Marketing (2), Transportation (1), Cardiology (1), Linguistics (1), Sport (1), Computer Vision (1) |
| regulator | 7 | Transportation (3), Finance & Marketing (2), Endocrinology (1), Pharmacology (1) |
| social worker | 7 | Economics (3), Psychology (3), Law (1) |
| UX designer | 7 | Information Systems (3), Transportation (1), Economics (1), Library (1), Social Networks (1) |
| caregiver | 5 | Health (3), Endocrinology (2) |
| company | 5 | Pharmacology (2), Transportation (1), Finance & Marketing (1), Psychology (1) |
| mental health professional | 5 | Psychology (4), Social Media (1) |
| security professional | 5 | Computer Networks (3), Finance & Marketing (2) |
| CEO | 4 | Finance & Marketing (3), Pharmacology (1) |
| decision-maker | 4 | Transportation (2), Law (1), Computer Networks (1) |
| financial advisor | 4 | Economics (2), Finance & Marketing (2) |
| specialist | 4 | Computer Vision (2), Cardiology (1), Law (1) |
| system architect | 4 | Political Science (1), Computer Vision (1), Library (1), Information Systems (1) |
| teacher | 4 | Psychology (3), News (1) |
| biomedical engineer | 3 | Medicine (2), Pediatrics (1) |
| clinical trial coordinator | 3 | Medicine (2), Pharmacology (1) |
| data engineer | 3 | Economics (1), Finance & Marketing (1), Computer Vision (1) |
| economist | 3 | Economics (2), Transportation (1) |
| music streaming service provider | 3 | Information Systems (2), Music (1) |
| non-profit organization | 3 | Economics (2), Psychology (1) |
| nurse | 3 | Health (2), Pediatrics (1) |
| psychologist | 3 | Psychology (2), Social Networks (1) |
| scholar | 3 | Demography (2), Library (1) |
| student | 3 | Psychology (1), Library (1), Demography (1) |
| business owner | 2 | Transportation (1), Psychology (1) |
| content moderator | 2 | Social Media (1), News (1) |
| executive | 2 | Transportation (1), Finance & Marketing (1) |
| fact-checker | 2 | Linguistics (1), News (1) |
| government official | 2 | Economics (1), Law (1) |
| legal professional | 2 | Law (1), Psychology (1) |
| logistics coordinator | 2 | Political Science (1), Finance & Marketing (1) |
| manufacturer | 2 | Transportation (1), Computer Vision (1) |
| professional | 2 | Transportation (1), Psychology (1) |
| system designer | 2 | Psychology (1), Social Media (1) |
| technology developer | 2 | Political Science (1), Health (1) |

## 6. O dataset de equivalência gerado

Arquivo: **`documents/datasets/equivalencia-ustai-synthetic.csv`** — 1260 linhas (1 por user story).

| Coluna | Descrição |
|---|---|
| `id` | Identificador da user story no UStAI (ex.: A1US1Ge) |
| `abstract` | Abstract de origem (A1–A42) |
| `abstract_theme` | Tema/sistema de IA descrito pelo abstract |
| `us_num` | Número da user story dentro do abstract (US1–US10) |
| `llm` | LLM que gerou a user story (Gemini_1.5_flash, Llama 3.1 70b, O1_mini) |
| `role_shorten` | Papel declarado — eixo de "domínio" do UStAI (âncora) |
| `user_story` | Texto completo da user story |
| `equivalent_domain` | Domínio de aplicação equivalente (1 dos 34 do Synthetic) |
| `equivalent_ml_task` | ML task equivalente (1 das 367 do Synthetic) |
| `domain_confidence` | Confiança do mapeamento de domínio (High/Medium/Low) |
| `mapping_notes` | Observações para mapeamentos de menor confiança |

A partir desse CSV é possível gerar o **PDF** e o **Excel** solicitados (mesmo conteúdo, formatos de apresentação).

## 7. Limitações

- **Domínio fixado por *abstract*.** Como cada *abstract* descreve um só sistema, o domínio é constante entre suas 30 user stories. Eventuais user stories "fora do tema" geradas pelos LLMs (ex.: um *cybersecurity expert* falando de rede em um abstract de saúde) mantêm o domínio do *abstract*.
- **6 abstracts de baixa confiança** (A4, A12, A21, A22, A31, A38): não há domínio perfeito entre os 34 — ver notas na Seção 4.
- **ML task por *abstract*.** Representa a técnica/tarefa central do estudo de origem; user stories individuais podem mencionar tarefas auxiliares.
- Vocabulário-alvo: 34 domínios e 367 ML tasks extraídos de `Synthetic User Stories.xlsx` (abas *Dataset*, *Domains*, *ML Dictionary*).
