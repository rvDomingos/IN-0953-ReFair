# Divisão de Roles para Análise Manual

Dataset: `documents/datasets/essenciais/ustai-stories-para-refair.csv`

- **Total de user stories:** 1260
- **Total de roles únicos:** 179
- **Pessoas:** 4
- **Meta por pessoa:** 315 user stories

## Critério de divisão

Aplicado *greedy bin-packing*: roles são ordenados do maior para o menor número de user stories e cada role é alocado ao grupo com a menor soma acumulada. Resultado: cada pessoa recebe exatamente **315 user stories** (1260 / 4), mas com quantidades distintas de roles, já que poucos roles concentram a maior parte das stories.

## Resumo

| Pessoa | Roles | User stories | Role âncora |
|:------:|------:|-------------:|:------------|
| Pessoa 1 | 43 | 315 | `researcher` (162), `healthcare provider` (21) |
| Pessoa 2 | 44 | 315 | `developer` (139), `advocate` (29) |
| Pessoa 3 | 45 | 315 | `data scientist` (81), `user` (44) |
| Pessoa 4 | 47 | 315 | `analyst` (56), `manager` (45) |

## Pessoa 1

**43 roles · 315 user stories**

| # | Role | User stories |
|--:|:-----|-------------:|
| 1 | researcher | 162 |
| 2 | healthcare provider | 21 |
| 3 | machine learning engineer | 16 |
| 4 | parent | 10 |
| 5 | marketing professional | 9 |
| 6 | player | 9 |
| 7 | librarian | 8 |
| 8 | citizen | 7 |
| 9 | community leader | 7 |
| 10 | music enthusiast | 7 |
| 11 | security professional | 5 |
| 12 | CEO | 4 |
| 13 | safety expert | 3 |
| 14 | commuter | 3 |
| 15 | nurse | 3 |
| 16 | clinical trial coordinator | 3 |
| 17 | biomedical engineer | 3 |
| 18 | music streaming service provider | 3 |
| 19 | car manufacturer | 2 |
| 20 | business owner | 2 |
| 21 | content moderator | 2 |
| 22 | manufacturer | 2 |
| 23 | sleep specialist | 2 |
| 24 | genealogist | 2 |
| 25 | linguist | 2 |
| 26 | diplomat | 1 |
| 27 | trainer | 1 |
| 28 | interoperability coordinator | 1 |
| 29 | Healthcare Administrator | 1 |
| 30 | OEM | 1 |
| 31 | health insurance provider | 1 |
| 32 | pharmaceutical company scientist | 1 |
| 33 | public transportation official | 1 |
| 34 | ethicist | 1 |
| 35 | machine learning model | 1 |
| 36 | modeler | 1 |
| 37 | social scientist studying the impact of technology on dating | 1 |
| 38 | archivist | 1 |
| 39 | News editor | 1 |
| 40 | traffic engineer | 1 |
| 41 | music label | 1 |
| 42 | music producer | 1 |
| 43 | resturant owner | 1 |

## Pessoa 2

**44 roles · 315 user stories**

| # | Role | User stories |
|--:|:-----|-------------:|
| 1 | developer | 139 |
| 2 | advocate | 29 |
| 3 | product manager | 18 |
| 4 | global citizen | 12 |
| 5 | city planner | 10 |
| 6 | driver | 9 |
| 7 | healthcare professional | 9 |
| 8 | cybersecurity expert | 8 |
| 9 | sports fan | 8 |
| 10 | consumer | 7 |
| 11 | company | 5 |
| 12 | mental health professional | 5 |
| 13 | teacher | 4 |
| 14 | decision-maker | 4 |
| 15 | passenger | 3 |
| 16 | lab technician | 3 |
| 17 | neurologist | 3 |
| 18 | neonatologist | 3 |
| 19 | scholar | 3 |
| 20 | candidate | 3 |
| 21 | executive | 2 |
| 22 | technology developer | 2 |
| 23 | bioinformatician | 2 |
| 24 | content creator | 2 |
| 25 | historian | 2 |
| 26 | job seeker | 2 |
| 27 | peacekeeper | 1 |
| 28 | drone operator | 1 |
| 29 | kitchen staff member | 1 |
| 30 | dietary staff member | 1 |
| 31 | tester | 1 |
| 32 | endocrinologist | 1 |
| 33 | computational biologist | 1 |
| 34 | taxi driver | 1 |
| 35 | healthcare policy advisor | 1 |
| 36 | competitor in the search engine market | 1 |
| 37 | research evaluator | 1 |
| 38 | dating coach | 1 |
| 39 | judge or magistrate | 1 |
| 40 | knowledge base specialist | 1 |
| 41 | network security specialist | 1 |
| 42 | playlist creator | 1 |
| 43 | member of the Pokec social network community | 1 |
| 44 | restaurant operator | 1 |

## Pessoa 3

**45 roles · 315 user stories**

| # | Role | User stories |
|--:|:-----|-------------:|
| 1 | data scientist | 81 |
| 2 | user | 44 |
| 3 | policymaker | 39 |
| 4 | patient | 19 |
| 5 | public health official | 14 |
| 6 | IT specialist | 11 |
| 7 | journalist | 9 |
| 8 | freelancer | 9 |
| 9 | software engineer | 8 |
| 10 | engineer | 7 |
| 11 | instructor | 7 |
| 12 | social worker | 7 |
| 13 | caregiver | 5 |
| 14 | system architect | 4 |
| 15 | financial advisor | 4 |
| 16 | moderator | 3 |
| 17 | student | 3 |
| 18 | economist | 3 |
| 19 | psychologist | 3 |
| 20 | news agency | 3 |
| 21 | environmentalist | 2 |
| 22 | child | 2 |
| 23 | logistics coordinator | 2 |
| 24 | taxi dispatcher | 2 |
| 25 | single person | 2 |
| 26 | legal professional | 2 |
| 27 | music industry professional | 2 |
| 28 | non-proliferation expert | 1 |
| 29 | GIS specialist | 1 |
| 30 | resident | 1 |
| 31 | human-factors specialist | 1 |
| 32 | school counselor | 1 |
| 33 | printing press operator | 1 |
| 34 | pharmacist | 1 |
| 35 | non-profit organization leader | 1 |
| 36 | banker | 1 |
| 37 | research funder | 1 |
| 38 | content strategist | 1 |
| 39 | sociologist studying assimilation and discrimination | 1 |
| 40 | law enforcement agency | 1 |
| 41 | shareholder of a wholesale company | 1 |
| 42 | Network engineer | 1 |
| 43 | music streamer | 1 |
| 44 | chef | 1 |
| 45 | innovator | 1 |

## Pessoa 4

**47 roles · 315 user stories**

| # | Role | User stories |
|--:|:-----|-------------:|
| 1 | analyst | 56 |
| 2 | manager | 45 |
| 3 | administrator | 39 |
| 4 | officer | 23 |
| 5 | customer | 20 |
| 6 | quality assurance specialist | 13 |
| 7 | strategist | 11 |
| 8 | HR specialist | 10 |
| 9 | client | 9 |
| 10 | person | 8 |
| 11 | regulator | 7 |
| 12 | UX designer | 7 |
| 13 | online retailer | 7 |
| 14 | radiologist | 5 |
| 15 | specialist | 4 |
| 16 | economic historian | 4 |
| 17 | military commander | 3 |
| 18 | security expert | 3 |
| 19 | non-profit organization | 3 |
| 20 | data engineer | 3 |
| 21 | recruiter | 3 |
| 22 | professional | 2 |
| 23 | system designer | 2 |
| 24 | residential care staff member | 2 |
| 25 | government official | 2 |
| 26 | organizer | 2 |
| 27 | fact-checker | 2 |
| 28 | visually impaired person | 1 |
| 29 | therapist | 1 |
| 30 | defense contractor | 1 |
| 31 | field commander | 1 |
| 32 | system | 1 |
| 33 | participant | 1 |
| 34 | cardiologist | 1 |
| 35 | grant writer | 1 |
| 36 | entrepreneur | 1 |
| 37 | pediatrician | 1 |
| 38 | credit card issuer | 1 |
| 39 | publisher | 1 |
| 40 | software architect | 1 |
| 41 | demographer | 1 |
| 42 | social media moderator | 1 |
| 43 | forecasting expert | 1 |
| 44 | musician | 1 |
| 45 | playlist curator | 1 |
| 46 | person with dietary restricttions | 1 |
| 47 | vaccination site coordinator | 1 |
