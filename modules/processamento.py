import pandas as pd
import datetime
import locale


def transformar_dados_evolucao(df_geral_raw, df_detalhes_raw, data_alvo):
    """
    Processa os dados da consulta unificada para montar a Tabela 1 final.
    O df_detalhes_raw não é mais necessário, mas é mantido na assinatura por compatibilidade.
    """
    if df_geral_raw.empty:
        print("Aviso: DataFrame geral de evolução está vazio.")
        return pd.DataFrame()
        
    ano = data_alvo.year
    ano_anterior = ano - 1

    # --- 1. Processa os dados GERAIS ---
    df_geral = df_geral_raw.set_index('situacao').drop(columns=['ordem', 'total_geral'], errors='ignore')
    df_geral_saldo = df_geral.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- LÓGICA DE CÁLCULO DA VARIAÇÃO MENSAL ---
    # A query retorna o saldo acumulado em cada coluna 'mes_XX'.
    # Precisamos calcular a diferença (delta) entre um mês e o anterior.
    df_geral_variacao = df_geral_saldo.copy()
    mes_cols = sorted([col for col in df_geral_variacao.columns if col.startswith('mes_')])
    
    if mes_cols:
        # A variação do primeiro mês é a diferença em relação ao saldo anterior.
        df_geral_variacao[mes_cols[0]] = df_geral_variacao[mes_cols[0]] - df_geral_variacao[f'saldo_{ano_anterior}']
        
        # Para os meses subsequentes, a variação é a diferença para o saldo acumulado do mês anterior.
        for i in range(len(mes_cols) - 1, 0, -1):
            col_atual = mes_cols[i]
            col_anterior = mes_cols[i-1]
            df_geral_variacao[col_atual] = df_geral_saldo[col_atual] - df_geral_saldo[col_anterior]

    df_final = df_geral_variacao.T # Transpõe o DataFrame para o formato de processamento
    
    novos_nomes_geral = {}
    for idx in df_final.index:
        if idx.startswith('saldo_'): novos_nomes_geral[idx] = f"Saldo {ano_anterior}"
        elif idx.startswith('acumulado_'): novos_nomes_geral[idx] = f"Acumulado/{ano}" # Mantido por segurança
        elif idx == 'acumulado_ano_corrente': novos_nomes_geral[idx] = f"Acumulado/{ano}"
        elif idx.startswith('mes_'):
            try:
                num_mes = int(idx.split('_')[1])
                nome_mes_ano = datetime.date(ano, num_mes, 1).strftime('%b/%Y').lower()
                novos_nomes_geral[idx] = nome_mes_ano
            except (ValueError, IndexError):
                novos_nomes_geral[idx] = idx # Mantém o nome original se falhar
        else:
            novos_nomes_geral[idx] = idx
    df_final = df_final.rename(index=novos_nomes_geral)
    
    # --- 2. Monta a tabela final com a estrutura correta ---
    colunas_finais = pd.MultiIndex.from_tuples([
        ('Mês/Ano', ''), ('Patrocinado', ''), ('Vinculado', ''), ('BPD', 'Patrocinado'), ('BPD', 'Vinculado'),
        ('Autopatrocinado', 'Patrocinado'), ('Autopatrocinado', 'Vinculado'),
        ('No prazo opção dos institutos', ''), ('Assistido', '')
    ])
    
    df_tabela_final = pd.DataFrame(index=df_final.index, columns=colunas_finais)
    df_tabela_final[('Mês/Ano', '')] = df_final.index # Preenche a primeira coluna com os nomes dos meses
    df_tabela_final[('Patrocinado', '')] = df_final.get('PATROCINADO', 0)
    df_tabela_final[('Vinculado', '')] = df_final.get('VINCULADO', 0)
    df_tabela_final[('BPD', 'Patrocinado')] = df_final.get('BPD (Patrocinado)', 0)
    df_tabela_final[('BPD', 'Vinculado')] = df_final.get('BPD (Vinculado)', 0)
    df_tabela_final[('Autopatrocinado', 'Patrocinado')] = df_final.get('Autopatrocinado (Patrocinado)', 0)
    df_tabela_final[('Autopatrocinado', 'Vinculado')] = df_final.get('Autopatrocinado (Vinculado)', 0)
    df_tabela_final[('No prazo opção dos institutos', '')] = df_final.get('NO PRAZO OPÇÃO INSTITUTOS', 0)
    df_tabela_final[('Assistido', '')] = df_final.get('ASSISTIDO', 0)
    
    # Preenche valores nulos com 0
    df_tabela_final = df_tabela_final.fillna(0)

    # Converte para inteiro apenas as colunas numéricas, ignorando a coluna 'Mês/Ano'
    colunas_numericas = [col for col in df_tabela_final.columns if col != ('Mês/Ano', '')]
    for col in colunas_numericas:
        df_tabela_final[col] = df_tabela_final[col].astype(int)
    
    # Adiciona a coluna Total
    df_tabela_final[('Total', '')] = df_tabela_final.sum(axis=1, numeric_only=True)

    # Adiciona a linha de Acumulado Total
    # Soma apenas as colunas numéricas para evitar erro de concatenação de string
    colunas_numericas_com_total = [col for col in df_tabela_final.columns if col != ('Mês/Ano', '')]
    saldo_anterior = df_tabela_final.loc[f"Saldo {ano_anterior}", colunas_numericas_com_total]
    acumulado_ano = df_tabela_final.loc[f"Acumulado/{ano}", colunas_numericas_com_total]
    acumulado_total_row = saldo_anterior + acumulado_ano
    df_tabela_final.loc['Acumulado Total'] = acumulado_total_row
    df_tabela_final.loc['Acumulado Total', ('Mês/Ano', '')] = 'Acumulado Total'

    # Garante que todas as colunas numéricas sejam inteiras após adicionar a linha de total
    colunas_numericas_final = [col for col in df_tabela_final.columns if col != ('Mês/Ano', '')]
    for col in colunas_numericas_final:
        df_tabela_final[col] = pd.to_numeric(df_tabela_final[col], errors='coerce').fillna(0).astype(int)
    
    # Prepara o DataFrame para ser usado pela função que gera a imagem
    df_tabela_final.reset_index(inplace=True)
    df_tabela_final.columns = [' '.join(col).strip() for col in df_tabela_final.columns.values]
    
    return df_tabela_final.rename(columns={'Mês/Ano ': 'Mês/Ano'})


def formatar_tabela_arrecadacao(df, data_alvo):
    """Formata o DataFrame da Tabela 5 para exibição."""
    if df.empty:
        return df
    
    # Pega os nomes dos meses
    mes_atual_nome = data_alvo.strftime('%B/%Y').capitalize()
    mes_passado_nome = (data_alvo - pd.DateOffset(months=1)).strftime('%B/%Y').capitalize()

    # Renomeia as colunas
    df = df.rename(columns={'mes_passado': mes_passado_nome, 'mes_atual': mes_atual_nome})

    # Função auxiliar para formatar moeda sem depender do locale global
    def formatar_moeda(valor):
        return f"R$ {valor:_.2f}".replace('.', 'X').replace(',', '.').replace('_', ',').replace('X', ',')

    # Formata as colunas de moeda
    df[mes_passado_nome] = df[mes_passado_nome].apply(formatar_moeda)
    df[mes_atual_nome] = df[mes_atual_nome].apply(formatar_moeda)
    
    # Formata a coluna de variação
    df['Variacao'] = df['Variacao'].apply(lambda x: f'{x:.2f}%'.replace('.',','))
    
    df.rename(columns={
        'Contribuicao': 'Contribuição', 
        'Variacao': 'Variação'
    }, inplace=True)

    return df


def formatar_tabela_cargo(df):
    """Formata o DataFrame da Tabela 6 para exibição, usando nomes de colunas simples."""
    if df.empty:
        return df
    
    # Adiciona a linha de Total Geral ANTES de formatar, usando os dados brutos
    total_contribuicao_geral = df['TotalContribuicao'].sum()
    total_participantes_geral = df['QuantidadeParticipantes'].sum()
    
    total_row = pd.DataFrame([{
        'CARGO': 'TOTAL',
        'RepresentatividadeContribuicao': '',
        'ContribuicaoMedia': '',
        'QuantidadeParticipantes': '',
        'RepresentatividadeParticipantes': '',
        'TotalContribuicao': total_contribuicao_geral
    }])
    
    df_com_total = pd.concat([df, total_row], ignore_index=True)

    # Função auxiliar para formatar moeda sem depender do locale global
    def formatar_moeda(valor):
        if isinstance(valor, (int, float)):
            return f"R$ {valor:_.2f}".replace('.', 'X').replace(',', '.').replace('_', ',').replace('X', ',')
        return valor

    # Formata as colunas
    df_com_total['RepresentatividadeContribuicao'] = df_com_total['RepresentatividadeContribuicao'].apply(lambda x: f'{x:.1f}%'.replace('.',',') if isinstance(x, (int, float)) else x)
    df_com_total['ContribuicaoMedia'] = df_com_total['ContribuicaoMedia'].apply(formatar_moeda)
    df_com_total['QuantidadeParticipantes'] = df_com_total['QuantidadeParticipantes'].apply(lambda x: f'{x:,.0f}'.replace(',','.') if isinstance(x, (int, float)) else x)
    df_com_total['RepresentatividadeParticipantes'] = df_com_total['RepresentatividadeParticipantes'].apply(lambda x: f'{x:.1f}%'.replace('.',',') if isinstance(x, (int, float)) else x)
    df_com_total['TotalContribuicao'] = df_com_total['TotalContribuicao'].apply(formatar_moeda)

    # Renomeia as colunas para a versão final, com acentos
    df_com_total.rename(columns={
        'CARGO': 'CARGO',
        'RepresentatividadeContribuicao': 'REPRESENTATIVIDADE DA CONTRIBUIÇÃO',
        'ContribuicaoMedia': 'CONTRIBUIÇÃO MÉDIA',
        'QuantidadeParticipantes': 'QUANTIDADE DE PARTICIPANTES',
        'RepresentatividadeParticipantes': 'REPRESENTATIVIDADE DOS PARTICIPANTES',
        'TotalContribuicao': 'TOTAL CONTRIBUIÇÃO'
    }, inplace=True)
    
    return df_com_total.fillna('')

def formatar_tabela_patrocinador(df):
    """Formata o DataFrame da Tabela 7 para exibição (versão defensiva).

    Esta versão normaliza nomes de colunas, detecta colunas equivalentes de forma
    tolerante (case-insensitive) e converte valores numéricos com `pd.to_numeric`
    usando errors='coerce' antes de formatar. Isso evita erros quando o input
    contém strings malformadas ou junções indevidas.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # Normaliza nomes: tira espaços e converte para string
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # Mapeia colunas por nome lower para achar correspondentes tolerantes
    cols_lower = {c.lower(): c for c in df.columns if isinstance(c, str)}

    def find_col(substring):
        substring = substring.lower()
        for k, orig in cols_lower.items():
            if substring in k:
                return orig
        return None

    # aceita tanto 'patrocinador' quanto 'empresa' (a query usa EMPRESA)
    patrocinador_col = find_col('patrocinador') or find_col('empresa') or find_col('emp')
    contrib_mes_col = find_col('mes') or find_col('contribuicao') or find_col('contrib')
    # Detecta coluna de contribuições acumuladas: procura por colunas que contenham
    # 'contrib' e também uma marca de total/acumulado; só como último recurso aceita
    # colunas que contenham apenas 'contrib' ou 'acumul' para evitar capturar
    # colunas genéricas como 'representatividade_total'. Isso evita mapear a coluna
    # de total para uma coluna de representatividade.
    contrib_total_col = None
    for k, orig in cols_lower.items():
        if 'contrib' in k and ('total' in k or 'acumul' in k or 'acumulad' in k):
            contrib_total_col = orig
            break
    if contrib_total_col is None:
        contrib_total_col = find_col('contrib') or find_col('acumul') or find_col('total')
    # Detecta colunas de representatividade de forma robusta
    def find_col_contains(*parts):
        parts = [p.lower() for p in parts]
        for k, orig in cols_lower.items():
            if all(p in k for p in parts):
                return orig
        return None

    # Detecta representatividades com heurísticas mais específicas. Evita o
    # fallback genérico 'represent' para não capturar a mesma coluna para ambas
    # as representatividades (caso comum quando a origem usa algo como
    # 'representatividade_total'). Primeiro procura por termos que indiquem
    # representatividade da contribuição; só usa correspondências mais gerais
    # como último recurso.
    # Prioriza colunas explícitas usadas por algumas queries
    # Aceita várias grafias/variações que aparecem nas queries: "prec", "perc" ou sem sufixo
    explicit_repr_mes = (
        cols_lower.get('representatividade_mes_prec')
        or cols_lower.get('representatividade_mes_perc')
        or cols_lower.get('representatividade_mes')
    )
    explicit_repr_total = (
        cols_lower.get('representatividade_total_prec')
        or cols_lower.get('representatividade_total_perc')
        or cols_lower.get('representatividade_total')
    )

    repr_contrib_col = explicit_repr_mes or find_col_contains('represent', 'contrib') or find_col_contains('represent', 'contribuicao')
    repr_patr_col = explicit_repr_total or find_col_contains('represent', 'patr') or find_col_contains('represent', 'patrimonio')

    # Se encontrar apenas uma das representatividades, prioriza manter apenas
    # a que foi identificada; não faz fallback imediato para apontar ambas para
    # a mesma coluna — isso evita duplicação quando a origem trouxe apenas uma
    # coluna de representatividade com nome genérico.
    if repr_contrib_col is None and repr_patr_col is not None:
        # mantém repr_patr_col definido, não sobrescreve repr_contrib_col
        pass
    if repr_patr_col is None and repr_contrib_col is not None:
        pass

    # Se não localizar a coluna de total corretamente, tenta heurística por substrings
    if contrib_total_col is None:
        for k, orig in cols_lower.items():
            if 'contrib' in k and 'total' in k:
                contrib_total_col = orig
                break

    if contrib_total_col is None:
        # fallback: lista colunas para depuração e retorna sem modificações
        print('Aviso: coluna de contribuições acumuladas não encontrada. Colunas:', df.columns.tolist())
        return df

    # Converte colunas numéricas de forma segura
    def safe_numeric(col, source_df=None):
        """Converte coluna para numérico de forma segura a partir de `source_df` ou `df` por padrão."""
        src = source_df if source_df is not None else df
        if col in src.columns:
            # Normaliza diferentes formatos numéricos:
            # - Se a string contém ',' assume-se formato pt_BR (milhar '.' e decimal ',')
            #   então removemos pontos e substituímos ',' por '.' para conversão.
            # - Se contém '.' e NÃO contém ',' assume-se que o ponto é decimal (ex: 1234.56)
            #   então removemos possíveis espaços e convertemos diretamente.
            s = src[col].astype(str).str.strip()

            has_comma = s.str.contains(',', regex=False)
            has_dot = s.str.contains('\.', regex=False)
            has_dot = s.str.contains('.', regex=False)

            # Caso com vírgula decimal típico do português
            s_pt = s.where(has_comma, None)
            if s_pt is not None:
                # Para as linhas que têm vírgula, removemos pontos de milhar e
                # trocamos vírgula por ponto para permitir conversão float.
                s = s.where(~has_comma, s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False))

            # Para as linhas que têm ponto mas não vírgula, presumimos ponto decimal
            # e apenas removemos espaços (não removemos o ponto).
            s = s.str.replace(' ', '', regex=False)

            return pd.to_numeric(s, errors='coerce').fillna(0)
        return pd.Series([0]*len(src))

    contrib_mes_num = safe_numeric(contrib_mes_col) if contrib_mes_col in df.columns else pd.Series([0]*len(df))
    contrib_total_num = safe_numeric(contrib_total_col)

    # Calcula totais (mantendo centavos quando presentes)
    total_mes = round(float(contrib_mes_num.sum()), 2) if not contrib_mes_num.empty else 0.0
    total_acumulado = round(float(contrib_total_num.sum()), 2) if not contrib_total_num.empty else 0.0

    # Cria a linha TOTAL
    total_row = {
        (patrocinador_col or 'Patrocinador'): 'TOTAL',
        (contrib_mes_col or 'contribuicao_no_mes'): total_mes,
        (repr_contrib_col or 'representatividade_contribuicao'): 100.0,
        contrib_total_col: total_acumulado,
        (repr_patr_col or 'representatividade_patrimonio'): 100.0
    }

    # Prepara df_com_total alinhando colunas
    df_com_total = pd.concat([pd.DataFrame([total_row]), df], ignore_index=True, sort=False)

    # Função auxiliar para formatar moeda sem depender do locale global
    def formatar_moeda(valor):
        return f"R$ {valor:_.2f}".replace('.', 'X').replace(',', '.').replace('_', ',').replace('X', ',')

    # Formatação segura: aplica sobre df_com_total (inclui a linha TOTAL) para evitar
    # desalinhamento de tamanhos entre Series quando concatenamos a linha TOTAL.
    if contrib_mes_col in df_com_total.columns:
        contrib_mes_numeric = safe_numeric(contrib_mes_col, source_df=df_com_total)
        df_com_total[contrib_mes_col] = contrib_mes_numeric.apply(lambda x: formatar_moeda(float(x)))
    else:
        # se não existir, cria coluna padronizada com tamanho correto
        df_com_total['contribuicao_no_mes'] = [formatar_moeda(x) for x in [total_mes] + [0]*(len(df_com_total)-1)]

    # Formata contrib total a partir do df_com_total também
    contrib_total_numeric = safe_numeric(contrib_total_col, source_df=df_com_total)
    df_com_total[contrib_total_col] = contrib_total_numeric.apply(lambda x: formatar_moeda(float(x)))

    # Formata percentuais se existirem
    # Função auxiliar para formatar colunas percentuais de forma segura
    def format_percent_column(df_, col):
        if col in df_.columns:
            s = df_[col].astype(str).str.replace('%', '', regex=False)
            # remove pontos de milhar e normaliza vírgula para ponto
            s = s.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            nums = pd.to_numeric(s, errors='coerce').fillna(0)
            df_[col] = nums.apply(lambda x: f'{x:.2f}%'.replace('.', ','))

    # Se as duas colunas apontarem para a mesma origem, duplicamos uma cópia para evitar
    # sobrescrever o mesmo campo ao renomear para dois rótulos distintos abaixo.
    if repr_contrib_col is not None and repr_patr_col is not None and repr_contrib_col == repr_patr_col:
        copy_name = f"{repr_contrib_col}_patr_copy"
        # evita sobrescrever se já existir
        if copy_name in df_com_total.columns:
            # se existir, usa esse nome como repr_patr_col
            repr_patr_col = copy_name
        else:
            df_com_total[copy_name] = df_com_total[repr_contrib_col]
            repr_patr_col = copy_name

    # Caso o usuário tenha solicitado que a representatividade da contribuição
    # seja a mesma que 'representatividade_mes_prec' e a representatividade do
    # patrimônio seja a mesma que 'representatividade_total_prec', garantimos
    # que esses nomes finais sejam usados quando as colunas explícitas existem.
    # (A renomeação abaixo fará o mapeamento para os rótulos exibidos.)

    format_percent_column(df_com_total, repr_contrib_col)
    format_percent_column(df_com_total, repr_patr_col)

    # Renomeia colunas para nomes de exibição finais (somente as que existem)
    rename_map = {}
    if patrocinador_col in df_com_total.columns:
        rename_map[patrocinador_col] = 'Patrocinador'
    # compatibilidade: se a coluna vier como 'EMPRESA' sem termos encontrados antes
    if 'EMPRESA' in df_com_total.columns and (patrocinador_col is None or patrocinador_col.upper() != 'EMPRESA'):
        rename_map['EMPRESA'] = 'Patrocinador'
    if contrib_mes_col in df_com_total.columns:
        rename_map[contrib_mes_col] = 'Contribuição no mês'
    if repr_contrib_col in df_com_total.columns:
        rename_map[repr_contrib_col] = 'Representatividade da contribuição'
    if contrib_total_col in df_com_total.columns:
        rename_map[contrib_total_col] = 'Contribuições acumuladas'
    if repr_patr_col in df_com_total.columns:
        rename_map[repr_patr_col] = 'Representatividade do patrimônio'

    df_com_total.rename(columns=rename_map, inplace=True)

    return df_com_total.fillna('')