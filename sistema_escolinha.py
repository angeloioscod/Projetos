"""
Sistema de Gestão — Escolinha de Futebol Nova Geração
Python 3 com tkinter e sqlite3.
"""
# PROJETO DE EXTENSÃO: SISTEMAS DE INFORMAÇÃO E SOCIEDADE
# Aluno: Ângelo Oliveira dos Santos
# Faculdade: Estácio
# Curso: Análise e Desenvolvimento de Sistemas
# Tema: Sistema de Gestão para a Escolinha de Futebol Nova Geração
#


import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES VISUAIS
# ─────────────────────────────────────────────
COR_FUNDO       = "#F0F4F8"   # azul-acinzentado muito claro
COR_PAINEL      = "#FFFFFF"
COR_VERDE       = "#2E7D32"   # verde campo de futebol
COR_VERDE_HOVER = "#1B5E20"
COR_TEXTO       = "#1A1A2E"
COR_SUBTEXTO    = "#5C6370"
COR_BORDA       = "#D0D7DE"
COR_LINHA_PAR   = "#EAF2EA"   # linhas alternadas na tabela

FONTE_TITULO    = ("Helvetica", 22, "bold")
FONTE_SECAO     = ("Helvetica", 14, "bold")
FONTE_LABEL     = ("Helvetica", 13)
FONTE_CAMPO     = ("Helvetica", 13)
FONTE_BTN       = ("Helvetica", 13, "bold")
FONTE_TABELA    = ("Helvetica", 12)
FONTE_CABECALHO = ("Helvetica", 12, "bold")

PAD = 16   # padding padrão


# ─────────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────────
def conectar():
    return sqlite3.connect("escolinha.db")

def inicializar_banco():
    con = conectar()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS alunos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            idade       INTEGER,
            responsavel TEXT,
            telefone    TEXT
        );

        CREATE TABLE IF NOT EXISTS frequencia (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id  INTEGER NOT NULL,
            data      TEXT    NOT NULL,
            presente  INTEGER NOT NULL DEFAULT 0,
            UNIQUE(aluno_id, data),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        );

        CREATE TABLE IF NOT EXISTS desempenho (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id  INTEGER NOT NULL UNIQUE,
            nota      REAL,
            status    TEXT,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        );
    """)
    con.commit()
    con.close()


# ─────────────────────────────────────────────
#  WIDGETS REUTILIZÁVEIS
# ─────────────────────────────────────────────
def botao(pai, texto, comando, cor=COR_VERDE, largura=22):
    btn = tk.Button(
        pai, text=texto, command=comando,
        bg=cor, fg="white", font=FONTE_BTN,
        relief="flat", cursor="hand2",
        padx=12, pady=8, width=largura,
        activebackground=COR_VERDE_HOVER, activeforeground="white"
    )
    return btn

def label(pai, texto, fonte=FONTE_LABEL, cor=COR_TEXTO):
    return tk.Label(pai, text=texto, font=fonte, bg=COR_PAINEL,
                    fg=cor, anchor="w")

def entrada(pai, var, largura=38):
    return tk.Entry(pai, textvariable=var, font=FONTE_CAMPO,
                    width=largura, relief="solid", bd=1,
                    highlightthickness=1, highlightcolor=COR_VERDE)

def separador(pai):
    return ttk.Separator(pai, orient="horizontal")

def card(pai, **kwargs):
    """Frame com aparência de cartão branco."""
    f = tk.Frame(pai, bg=COR_PAINEL, bd=0,
                 highlightbackground=COR_BORDA, highlightthickness=1,
                 **kwargs)
    return f


# ─────────────────────────────────────────────
#  ABA 1 — CADASTRO DE ALUNOS
# ─────────────────────────────────────────────
class AbaCadastro(tk.Frame):
    def __init__(self, pai):
        super().__init__(pai, bg=COR_FUNDO)
        self._vars()
        self._layout()
        self._carregar_lista()

    def _vars(self):
        self.v_nome  = tk.StringVar()
        self.v_idade = tk.StringVar()
        self.v_resp  = tk.StringVar()
        self.v_tel   = tk.StringVar()
        self.id_sel  = None   # id do aluno selecionado para edição

    def _layout(self):
        # ── título
        tk.Label(self, text="⚽  Cadastro de Alunos", font=FONTE_TITULO,
                 bg=COR_FUNDO, fg=COR_VERDE, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(PAD, 4))
        separador(self).pack(fill="x", padx=PAD)

        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        corpo.columnconfigure(0, weight=1)
        corpo.columnconfigure(1, weight=2)

        # ── formulário (coluna esquerda)
        form = card(corpo)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, PAD//2))

        tk.Label(form, text="Novo Aluno / Editar", font=FONTE_SECAO,
                 bg=COR_PAINEL, fg=COR_VERDE
                 ).pack(anchor="w", padx=PAD, pady=(PAD, 4))
        separador(form).pack(fill="x", padx=PAD)

        campos = [
            ("Nome completo *",      self.v_nome,  True),
            ("Idade",                self.v_idade, False),
            ("Nome do Responsável",  self.v_resp,  False),
            ("Telefone de Contato",  self.v_tel,   False),
        ]
        for txt, var, obrig in campos:
            label(form, txt + ("" if not obrig else "")).pack(
                anchor="w", padx=PAD, pady=(10, 0))
            entrada(form, var, largura=36).pack(
                padx=PAD, pady=(2, 0), fill="x")

        self.lbl_aviso = tk.Label(form, text="", font=("Helvetica", 11),
                                  bg=COR_PAINEL, fg="#C62828")
        self.lbl_aviso.pack(anchor="w", padx=PAD, pady=(6, 0))

        # botões
        bf = tk.Frame(form, bg=COR_PAINEL)
        bf.pack(fill="x", padx=PAD, pady=PAD)
        botao(bf, "💾  Salvar Aluno", self._salvar, largura=18
              ).pack(side="left", padx=(0, 8))
        botao(bf, "🗑  Excluir", self._excluir, cor="#B71C1C", largura=12
              ).pack(side="left")
        botao(bf, "✖  Limpar", self._limpar, cor="#546E7A", largura=12
              ).pack(side="left", padx=(8, 0))

        # ── lista (coluna direita)
        lista_frame = card(corpo)
        lista_frame.grid(row=0, column=1, sticky="nsew", padx=(PAD//2, 0))
        lista_frame.rowconfigure(1, weight=1)
        lista_frame.columnconfigure(0, weight=1)

        tk.Label(lista_frame, text="Alunos Cadastrados", font=FONTE_SECAO,
                 bg=COR_PAINEL, fg=COR_VERDE
                 ).grid(row=0, column=0, sticky="w", padx=PAD, pady=(PAD, 4))

        cols = ("nome", "idade", "responsavel", "telefone")
        self.tree = ttk.Treeview(lista_frame, columns=cols,
                                  show="headings", height=16)
        for c, t, w in [("nome","Nome",220),("idade","Idade",60),
                         ("responsavel","Responsável",180),("telefone","Telefone",130)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.tag_configure("par", background=COR_LINHA_PAR)
        self.tree.bind("<<TreeviewSelect>>", self._selecionar)
        sb = ttk.Scrollbar(lista_frame, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(PAD, 0), pady=PAD)
        sb.grid(row=1, column=1, sticky="ns", pady=PAD, padx=(0, 4))

        self._estilo_tree()

    def _estilo_tree(self):
        s = ttk.Style()
        s.configure("Treeview", font=FONTE_TABELA, rowheight=30,
                     background=COR_PAINEL, fieldbackground=COR_PAINEL)
        s.configure("Treeview.Heading", font=FONTE_CABECALHO,
                     background=COR_VERDE, foreground="white")
        s.map("Treeview", background=[("selected", "#A5D6A7")])

    def _salvar(self):
        nome = self.v_nome.get().strip()
        if not nome:
            self.lbl_aviso.config(text="⚠ O campo Nome é obrigatório.")
            return
        self.lbl_aviso.config(text="")
        try:
            idade = int(self.v_idade.get()) if self.v_idade.get().strip() else None
        except ValueError:
            self.lbl_aviso.config(text="⚠ Idade deve ser um número.")
            return

        con = conectar()
        cur = con.cursor()
        if self.id_sel:
            cur.execute("""UPDATE alunos SET nome=?,idade=?,responsavel=?,telefone=?
                           WHERE id=?""",
                        (nome, idade, self.v_resp.get().strip(),
                         self.v_tel.get().strip(), self.id_sel))
            msg = f"Aluno '{nome}' atualizado com sucesso!"
        else:
            cur.execute("""INSERT INTO alunos(nome,idade,responsavel,telefone)
                           VALUES(?,?,?,?)""",
                        (nome, idade, self.v_resp.get().strip(),
                         self.v_tel.get().strip()))
            msg = f"Aluno '{nome}' cadastrado com sucesso!"
        con.commit()
        con.close()
        messagebox.showinfo("✔ Sucesso", msg)
        self._limpar()
        self._carregar_lista()

    def _excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione um aluno na lista para excluir.")
            return
        nome = self.v_nome.get()
        if not messagebox.askyesno("Confirmar exclusão",
                                   f"Deseja excluir o aluno '{nome}'?\n"
                                   "Frequência e desempenho também serão removidos."):
            return
        con = conectar()
        cur = con.cursor()
        cur.execute("DELETE FROM frequencia  WHERE aluno_id=?", (self.id_sel,))
        cur.execute("DELETE FROM desempenho  WHERE aluno_id=?", (self.id_sel,))
        cur.execute("DELETE FROM alunos      WHERE id=?",       (self.id_sel,))
        con.commit()
        con.close()
        messagebox.showinfo("✔ Excluído", f"Aluno '{nome}' removido.")
        self._limpar()
        self._carregar_lista()

    def _limpar(self):
        self.id_sel = None
        for v in (self.v_nome, self.v_idade, self.v_resp, self.v_tel):
            v.set("")
        self.lbl_aviso.config(text="")

    def _selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree.item(iid, "values")
        # iid é o id do aluno
        self.id_sel = int(iid)
        self.v_nome.set(vals[0])
        self.v_idade.set(vals[1] if vals[1] != "None" else "")
        self.v_resp.set(vals[2])
        self.v_tel.set(vals[3])

    def _carregar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        con = conectar()
        rows = con.execute(
            "SELECT id,nome,idade,responsavel,telefone FROM alunos ORDER BY nome"
        ).fetchall()
        con.close()
        for i, r in enumerate(rows):
            tag = "par" if i % 2 == 0 else ""
            self.tree.insert("", "end", iid=str(r[0]),
                             values=(r[1], r[2] or "", r[3] or "", r[4] or ""),
                             tags=(tag,))


# ─────────────────────────────────────────────
#  ABA 2 — FREQUÊNCIA
# ─────────────────────────────────────────────
class AbaFrequencia(tk.Frame):
    def __init__(self, pai):
        super().__init__(pai, bg=COR_FUNDO)
        self._hoje = date.today().isoformat()
        self._checks = {}   # aluno_id → BooleanVar
        self._layout()

    def _layout(self):
        tk.Label(self, text="📋  Frequência do Dia", font=FONTE_TITULO,
                 bg=COR_FUNDO, fg=COR_VERDE, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(PAD, 2))
        tk.Label(self, text=f"Data de hoje:  {self._formatar_data(self._hoje)}",
                 font=("Helvetica", 13), bg=COR_FUNDO, fg=COR_SUBTEXTO, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(0, 4))
        separador(self).pack(fill="x", padx=PAD)

        conteiner = card(self)
        conteiner.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        conteiner.columnconfigure(0, weight=1)
        conteiner.rowconfigure(1, weight=1)

        # cabeçalho
        cab = tk.Frame(conteiner, bg=COR_VERDE)
        cab.grid(row=0, column=0, sticky="ew")
        for col, txt, w in [(0,"Nome do Aluno",400),(1,"Presente hoje?",160)]:
            tk.Label(cab, text=txt, font=FONTE_CABECALHO, bg=COR_VERDE,
                     fg="white", width=w//10, anchor="w", padx=8, pady=8
                     ).grid(row=0, column=col, sticky="ew", padx=2)

        # scroll
        canvas = tk.Canvas(conteiner, bg=COR_PAINEL, highlightthickness=0)
        sb = ttk.Scrollbar(conteiner, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        sb.grid(row=1, column=1, sticky="ns")

        self._frame_lista = tk.Frame(canvas, bg=COR_PAINEL)
        self._win_id = canvas.create_window((0, 0), window=self._frame_lista,
                                             anchor="nw")
        self._frame_lista.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._win_id, width=e.width))
        self._canvas = canvas

        # rodapé
        rod = tk.Frame(conteiner, bg=COR_PAINEL, pady=PAD)
        rod.grid(row=2, column=0, columnspan=2, sticky="ew")
        botao(rod, "💾  Salvar Frequência de Hoje", self._salvar, largura=30
              ).pack(side="left", padx=PAD)
        botao(rod, "🔄  Recarregar Lista", self.carregar, cor="#546E7A", largura=20
              ).pack(side="left")

        self.carregar()

    def carregar(self):
        for w in self._frame_lista.winfo_children():
            w.destroy()
        self._checks.clear()

        con = conectar()
        alunos = con.execute(
            "SELECT id, nome FROM alunos ORDER BY nome"
        ).fetchall()
        presentes = {r[0] for r in con.execute(
            "SELECT aluno_id FROM frequencia WHERE data=? AND presente=1",
            (self._hoje,)
        ).fetchall()}
        con.close()

        if not alunos:
            tk.Label(self._frame_lista,
                     text="Nenhum aluno cadastrado ainda.\nAcesse a aba Cadastro para adicionar alunos.",
                     font=FONTE_LABEL, bg=COR_PAINEL, fg=COR_SUBTEXTO,
                     justify="center"
                     ).pack(pady=40)
            return

        for i, (aid, nome) in enumerate(alunos):
            bg = COR_LINHA_PAR if i % 2 == 0 else COR_PAINEL
            row = tk.Frame(self._frame_lista, bg=bg)
            row.pack(fill="x")
            tk.Label(row, text=nome, font=FONTE_CAMPO, bg=bg,
                     fg=COR_TEXTO, anchor="w", padx=PAD, pady=10
                     ).pack(side="left", fill="x", expand=True)
            var = tk.BooleanVar(value=(aid in presentes))
            cb = tk.Checkbutton(row, variable=var, bg=bg,
                                activebackground=bg,
                                text="  Presente", font=FONTE_LABEL,
                                fg=COR_VERDE, selectcolor=bg, cursor="hand2")
            cb.pack(side="right", padx=PAD)
            self._checks[aid] = var

    def _salvar(self):
        if not self._checks:
            messagebox.showwarning("Atenção", "Nenhum aluno para registrar.")
            return
        con = conectar()
        for aid, var in self._checks.items():
            con.execute("""
                INSERT INTO frequencia(aluno_id, data, presente)
                VALUES(?,?,?)
                ON CONFLICT(aluno_id, data) DO UPDATE SET presente=excluded.presente
            """, (aid, self._hoje, 1 if var.get() else 0))
        con.commit()
        con.close()
        messagebox.showinfo("✔ Salvo", "Frequência registrada com sucesso!")

    @staticmethod
    def _formatar_data(iso):
        y, m, d = iso.split("-")
        meses = ["","Jan","Fev","Mar","Abr","Mai","Jun",
                 "Jul","Ago","Set","Out","Nov","Dez"]
        return f"{d} de {meses[int(m)]} de {y}"


# ─────────────────────────────────────────────
#  ABA 3 — DESEMPENHO ESCOLAR
# ─────────────────────────────────────────────
class AbaDesempenho(tk.Frame):
    def __init__(self, pai):
        super().__init__(pai, bg=COR_FUNDO)
        self._alunos = []    # lista de (id, nome)
        self.v_aluno  = tk.StringVar()
        self.v_nota   = tk.StringVar()
        self.v_status = tk.StringVar(value="Aprovado")
        self._layout()
        self._carregar_alunos()

    def _layout(self):
        tk.Label(self, text="📊  Desempenho Escolar", font=FONTE_TITULO,
                 bg=COR_FUNDO, fg=COR_VERDE, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(PAD, 4))
        separador(self).pack(fill="x", padx=PAD)

        # centraliza o formulário
        centro = tk.Frame(self, bg=COR_FUNDO)
        centro.pack(expand=True)

        form = card(centro)
        form.pack(padx=PAD, pady=PAD, ipadx=PAD, ipady=PAD)

        tk.Label(form, text="Lançar / Atualizar Nota", font=FONTE_SECAO,
                 bg=COR_PAINEL, fg=COR_VERDE
                 ).grid(row=0, column=0, columnspan=2, sticky="w",
                        padx=PAD, pady=(PAD, 4))
        separador(form).grid(row=1, column=0, columnspan=2,
                              sticky="ew", padx=PAD)

        # aluno
        label(form, "Aluno").grid(row=2, column=0, sticky="w",
                                   padx=PAD, pady=(14, 0))
        self.combo_aluno = ttk.Combobox(form, textvariable=self.v_aluno,
                                         state="readonly", font=FONTE_CAMPO,
                                         width=35)
        self.combo_aluno.grid(row=3, column=0, columnspan=2,
                               padx=PAD, pady=(2, 0), sticky="ew")
        self.combo_aluno.bind("<<ComboboxSelected>>", self._ao_selecionar_aluno)

        # nota
        label(form, "Nota  (0 a 10)").grid(row=4, column=0, sticky="w",
                                             padx=PAD, pady=(14, 0))
        entrada(form, self.v_nota, largura=12).grid(row=5, column=0,
                                                     padx=PAD, pady=(2, 0), sticky="w")

        # status
        label(form, "Status Escolar").grid(row=6, column=0, sticky="w",
                                            padx=PAD, pady=(14, 0))
        status_frame = tk.Frame(form, bg=COR_PAINEL)
        status_frame.grid(row=7, column=0, columnspan=2, sticky="w",
                          padx=PAD, pady=(4, 0))
        cores_status = {
            "Aprovado":    "#2E7D32",
            "Recuperação": "#F57C00",
            "Alerta":      "#C62828",
        }
        for s in ["Aprovado", "Recuperação", "Alerta"]:
            tk.Radiobutton(
                status_frame, text=s, variable=self.v_status, value=s,
                font=FONTE_LABEL, bg=COR_PAINEL, fg=cores_status[s],
                activebackground=COR_PAINEL, selectcolor=COR_PAINEL,
                cursor="hand2"
            ).pack(side="left", padx=(0, 20))

        self.lbl_aviso = tk.Label(form, text="", font=("Helvetica", 11),
                                   bg=COR_PAINEL, fg="#C62828")
        self.lbl_aviso.grid(row=8, column=0, columnspan=2,
                             sticky="w", padx=PAD, pady=(8, 0))

        bf2 = tk.Frame(form, bg=COR_PAINEL)
        bf2.grid(row=9, column=0, columnspan=2, padx=PAD, pady=PAD, sticky="w")
        botao(bf2, "💾  Salvar Desempenho", self._salvar, largura=22
              ).pack(side="left", padx=(0, 10))
        botao(bf2, "↩  Voltar ao Cadastro", self._sair, cor="#546E7A", largura=20
              ).pack(side="left")

        # painel de histórico simplificado
        self.lbl_atual = tk.Label(form, text="", font=("Helvetica", 12),
                                   bg=COR_PAINEL, fg=COR_SUBTEXTO, justify="left")
        self.lbl_atual.grid(row=10, column=0, columnspan=2,
                             sticky="w", padx=PAD, pady=(0, PAD))

    def _carregar_alunos(self):
        con = conectar()
        self._alunos = con.execute(
            "SELECT id, nome FROM alunos ORDER BY nome"
        ).fetchall()
        con.close()
        self.combo_aluno["values"] = [a[1] for a in self._alunos]
        self.v_aluno.set("")
        self.v_nota.set("")
        self.v_status.set("Aprovado")
        self.lbl_atual.config(text="")

    def _ao_selecionar_aluno(self, _=None):
        aid = self._id_selecionado()
        if aid is None:
            return
        con = conectar()
        r = con.execute(
            "SELECT nota, status FROM desempenho WHERE aluno_id=?", (aid,)
        ).fetchone()
        con.close()
        if r:
            self.v_nota.set(str(r[0]) if r[0] is not None else "")
            self.v_status.set(r[1] or "Aprovado")
            self.lbl_atual.config(
                text=f"📌 Registro atual:  Nota {r[0]}  |  {r[1]}"
            )
        else:
            self.v_nota.set("")
            self.v_status.set("Aprovado")
            self.lbl_atual.config(text="(nenhum registro anterior)")

    def _id_selecionado(self):
        nome = self.v_aluno.get()
        for aid, n in self._alunos:
            if n == nome:
                return aid
        return None

    def _salvar(self):
        aid = self._id_selecionado()
        if aid is None:
            self.lbl_aviso.config(text="⚠ Selecione um aluno.")
            return
        nota_str = self.v_nota.get().replace(",", ".").strip()
        if nota_str == "":
            self.lbl_aviso.config(text="⚠ Informe a nota.")
            return
        try:
            nota = float(nota_str)
            if not (0 <= nota <= 10):
                raise ValueError
        except ValueError:
            self.lbl_aviso.config(text="⚠ Nota deve ser um número entre 0 e 10.")
            return
        self.lbl_aviso.config(text="")
        con = conectar()
        con.execute("""
            INSERT INTO desempenho(aluno_id, nota, status)
            VALUES(?,?,?)
            ON CONFLICT(aluno_id) DO UPDATE SET nota=excluded.nota, status=excluded.status
        """, (aid, nota, self.v_status.get()))
        con.commit()
        con.close()
        messagebox.showinfo("✔ Salvo", "Desempenho registrado com sucesso!")
        # Limpa o formulário após salvar
        self.v_aluno.set("")
        self.v_nota.set("")
        self.v_status.set("Aprovado")
        self.lbl_atual.config(text="")
        self.lbl_aviso.config(text="")

    def _sair(self):
        # Volta para a aba Cadastro (índice 0)
        nb = self.winfo_toplevel().nametowidget(self.winfo_parent())
        nb.select(0)

    def atualizar(self):
        """Chamado quando a aba recebe foco."""
        self._carregar_alunos()


# ─────────────────────────────────────────────
#  ABA 4 — RELATÓRIO GERAL
# ─────────────────────────────────────────────
class AbaRelatorio(tk.Frame):
    def __init__(self, pai):
        super().__init__(pai, bg=COR_FUNDO)
        self._layout()

    def _layout(self):
        tk.Label(self, text="📄  Relatório Geral", font=FONTE_TITULO,
                 bg=COR_FUNDO, fg=COR_VERDE, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(PAD, 2))
        tk.Label(self,
                 text="Visão completa de todos os alunos — nome, telefone, presenças e situação escolar.",
                 font=("Helvetica", 12), bg=COR_FUNDO, fg=COR_SUBTEXTO, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(0, 4))
        separador(self).pack(fill="x", padx=PAD)

        conteiner = card(self)
        conteiner.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        conteiner.rowconfigure(1, weight=1)
        conteiner.columnconfigure(0, weight=1)

        # barra de ações
        barra = tk.Frame(conteiner, bg=COR_PAINEL, pady=10)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD)
        botao(barra, "🔄  Atualizar Relatório", self.carregar, largura=24
              ).pack(side="left")
        self.lbl_total = tk.Label(barra, text="", font=FONTE_LABEL,
                                   bg=COR_PAINEL, fg=COR_SUBTEXTO)
        self.lbl_total.pack(side="right", padx=8)

        # treeview
        cols = ("nome", "telefone", "presencas", "nota", "status")
        self.tree = ttk.Treeview(conteiner, columns=cols,
                                  show="headings", height=20)
        spec = [
            ("nome",      "Nome do Aluno",     240, "w"),
            ("telefone",  "Telefone Resp.",     150, "center"),
            ("presencas", "Presenças",           90, "center"),
            ("nota",      "Nota",                70, "center"),
            ("status",    "Situação Escolar",   160, "center"),
        ]
        for c, t, w, anc in spec:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=anc, minwidth=60)

        self.tree.tag_configure("par",        background=COR_LINHA_PAR)
        self.tree.tag_configure("aprovado",   foreground="#2E7D32")
        self.tree.tag_configure("recuperacao",foreground="#E65100")
        self.tree.tag_configure("alerta",     foreground="#C62828")

        sb = ttk.Scrollbar(conteiner, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(PAD, 0), pady=4)
        sb.grid(row=1, column=1, sticky="ns", pady=4, padx=(0, 4))

        self.carregar()

    def carregar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        con = conectar()
        dados = con.execute("""
            SELECT
                a.nome,
                COALESCE(a.telefone, '—'),
                COALESCE(SUM(f.presente), 0) AS presencas,
                COALESCE(d.nota, '—'),
                COALESCE(d.status, '—')
            FROM alunos a
            LEFT JOIN frequencia f ON f.aluno_id = a.id
            LEFT JOIN desempenho d ON d.aluno_id = a.id
            GROUP BY a.id
            ORDER BY a.nome
        """).fetchall()
        con.close()

        self.lbl_total.config(text=f"Total de alunos: {len(dados)}")

        for i, r in enumerate(dados):
            nome, tel, pres, nota, status = r
            # tag de cor por status
            s = str(status).lower()
            tags = []
            if i % 2 == 0:
                tags.append("par")
            if "aprovado" in s:
                tags.append("aprovado")
            elif "recupe" in s:
                tags.append("recuperacao")
            elif "alerta" in s:
                tags.append("alerta")

            nota_fmt = f"{nota:.1f}" if isinstance(nota, float) else nota
            self.tree.insert("", "end",
                             values=(nome, tel, int(pres), nota_fmt, status),
                             tags=tuple(tags))


# ─────────────────────────────────────────────
#  JANELA PRINCIPAL
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Escolinha de Futebol Nova Geração")
        self.geometry("1024x720")
        self.minsize(900, 620)
        self.configure(bg=COR_FUNDO)
        self._estilo_notebook()
        self._montar_ui()

    def _estilo_notebook(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook",        background=COR_FUNDO, borderwidth=0)
        s.configure("TNotebook.Tab",
                    font=("Helvetica", 13, "bold"),
                    padding=(20, 10),
                    background="#C8E6C9",
                    foreground=COR_TEXTO)
        s.map("TNotebook.Tab",
              background=[("selected", COR_VERDE)],
              foreground=[("selected", "white")])
        s.configure("Treeview",        font=FONTE_TABELA, rowheight=30)
        s.configure("Treeview.Heading",font=FONTE_CABECALHO,
                    background=COR_VERDE, foreground="white", relief="flat")
        s.map("Treeview", background=[("selected", "#A5D6A7")],
                          foreground=[("selected", COR_TEXTO)])

    def _montar_ui(self):
        # ── cabeçalho
        cab = tk.Frame(self, bg=COR_VERDE, pady=12)
        cab.pack(fill="x")
        tk.Label(cab,
                 text="⚽  Escolinha de Futebol  Nova Geração",
                 font=("Helvetica", 18, "bold"),
                 bg=COR_VERDE, fg="white"
                 ).pack(side="left", padx=PAD)
        tk.Label(cab,
                 text=f"Hoje: {date.today().strftime('%d/%m/%Y')}",
                 font=("Helvetica", 13),
                 bg=COR_VERDE, fg="#C8E6C9"
                 ).pack(side="right", padx=PAD)

        # ── notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.aba_cadastro    = AbaCadastro(nb)
        self.aba_frequencia  = AbaFrequencia(nb)
        self.aba_desempenho  = AbaDesempenho(nb)
        self.aba_relatorio   = AbaRelatorio(nb)

        nb.add(self.aba_cadastro,   text="  👤  Cadastro  ")
        nb.add(self.aba_frequencia, text="  📋  Frequência  ")
        nb.add(self.aba_desempenho, text="  📊  Desempenho  ")
        nb.add(self.aba_relatorio,  text="  📄  Relatório  ")

        def ao_trocar_aba(event):
            idx = nb.index(nb.select())
            if idx == 1:   # Frequência
                self.aba_frequencia.carregar()
            elif idx == 2: # Desempenho
                self.aba_desempenho.atualizar()
            elif idx == 3: # Relatório
                self.aba_relatorio.carregar()

        nb.bind("<<NotebookTabChanged>>", ao_trocar_aba)

        # ── rodapé
        rod = tk.Frame(self, bg="#37474F", pady=4)
        rod.pack(fill="x", side="bottom")
        tk.Label(rod,
                 text="Sistema desenvolvido para a Escolinha Nova Geração  •  Dados salvos localmente em escolinha.db",
                 font=("Helvetica", 10), bg="#37474F", fg="#90A4AE"
                 ).pack()


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    inicializar_banco()
    app = App()
    app.mainloop()
