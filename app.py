import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime
import threading
import locale
import os

# Importa a função principal de geração que refatoramos
from main import executar_geracao_relatorio

class AppRelatorio:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Relatório Gerencial")
        self.root.geometry("600x450")
        
        # Armazena os caminhos dos arquivos gerados
        self.caminhos_arquivos = {}
        
        # --- Frame de Entrada ---
        frame_entrada = ttk.Frame(root, padding="10")
        frame_entrada.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_entrada, text="Ano:").pack(side='left', padx=(0, 5))
        self.ano_var = tk.StringVar(value=datetime.date.today().year)
        self.ano_entry = ttk.Entry(frame_entrada, textvariable=self.ano_var, width=10)
        self.ano_entry.pack(side='left', padx=5)

        ttk.Label(frame_entrada, text="Mês:").pack(side='left', padx=(10, 5))
        self.mes_var = tk.StringVar(value=datetime.date.today().month)
        self.mes_entry = ttk.Entry(frame_entrada, textvariable=self.mes_var, width=10)
        self.mes_entry.pack(side='left', padx=5)

        self.botao_gerar = ttk.Button(frame_entrada, text="Gerar Relatório", command=self.iniciar_geracao)
        self.botao_gerar.pack(side='right', padx=10)

        # --- Frame de Log (Saída) ---
        frame_saida = ttk.LabelFrame(root, text="Progresso", padding="10")
        frame_saida.pack(fill='both', expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(frame_saida, wrap=tk.WORD, state='disabled', height=15)
        self.log_text.pack(fill='both', expand=True)

        # --- Frame de Ações (Abrir Arquivos) ---
        frame_acoes = ttk.LabelFrame(root, text="Ações", padding="10")
        frame_acoes.pack(fill='x', padx=10, pady=(5, 10))

        self.botao_abrir_pdf = ttk.Button(frame_acoes, text="Abrir Relatório (PDF)", state='disabled', command=lambda: self.abrir_arquivo('pdf'))
        self.botao_abrir_pdf.pack(side='left', expand=True, padx=5)

        self.botao_abrir_excel = ttk.Button(frame_acoes, text="Abrir Planilha (Excel)", state='disabled', command=lambda: self.abrir_arquivo('excel'))
        self.botao_abrir_excel.pack(side='left', expand=True, padx=5)

        self.botao_abrir_txt = ttk.Button(frame_acoes, text="Abrir Queries (TXT)", state='disabled', command=lambda: self.abrir_arquivo('txt'))
        self.botao_abrir_txt.pack(side='left', expand=True, padx=5)


    def log(self, message):
        """Adiciona uma mensagem à caixa de texto de log na thread principal da GUI."""
        def append_message():
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.config(state='disabled')
            self.log_text.see(tk.END) # Rola para o final
        # Garante que a atualização da GUI ocorra na thread principal
        self.root.after(0, append_message)

    def iniciar_geracao(self):
        """Valida as entradas e inicia a geração do relatório em uma nova thread."""
        try:
            ano = int(self.ano_var.get())
            mes = int(self.mes_var.get())
            if not (2000 < ano < 2100 and 1 <= mes <= 12):
                raise ValueError("Data inválida.")
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um ano (ex: 2025) e um mês (1-12) válidos.")
            return

        # Desabilita o botão para evitar cliques duplos
        self.botao_gerar.config(state='disabled')
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END) # Limpa o log anterior
        self.log_text.config(state='disabled')
        
        # Limpa caminhos e desabilita botões de abrir
        self.caminhos_arquivos = {}
        self.atualizar_botoes_abrir()

        # Executa a tarefa pesada em uma thread separada para não travar a interface
        thread = threading.Thread(target=self.executar_tarefa, args=(ano, mes))
        thread.start()

    def abrir_arquivo(self, tipo_arquivo):
        """Abre um arquivo gerado usando o programa padrão do sistema."""
        caminho = self.caminhos_arquivos.get(tipo_arquivo)
        if caminho and os.path.exists(caminho):
            try:
                os.startfile(caminho)
            except Exception as e:
                messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo:\n{caminho}\n\nErro: {e}")
        else:
            messagebox.showwarning("Arquivo não encontrado", f"O arquivo do tipo '{tipo_arquivo}' não foi encontrado ou não foi gerado.")

    def atualizar_botoes_abrir(self):
        """Habilita ou desabilita os botões de abrir arquivo com base nos caminhos disponíveis."""
        self.botao_abrir_pdf.config(state='normal' if 'pdf' in self.caminhos_arquivos else 'disabled')
        self.botao_abrir_excel.config(state='normal' if 'excel' in self.caminhos_arquivos else 'disabled')
        self.botao_abrir_txt.config(state='normal' if 'txt' in self.caminhos_arquivos else 'disabled')

    def executar_tarefa(self, ano, mes):
        """Função que executa o processo de geração e reabilita o botão no final."""
        try:
            # Chama a função principal do main.py, passando nossa função de log
            self.caminhos_arquivos = executar_geracao_relatorio(ano, mes, log_callback=self.log)
        except Exception as e:
            self.log(f"ERRO CRÍTICO NA THREAD: {e}")
        finally:
            # Garante que o botão seja reabilitado na thread principal
            self.root.after(0, lambda: self.botao_gerar.config(state='normal'))
            # Atualiza os botões de abrir arquivo
            self.root.after(0, self.atualizar_botoes_abrir)


if __name__ == "__main__":
    app_root = tk.Tk()
    app = AppRelatorio(app_root)
    app_root.mainloop()
