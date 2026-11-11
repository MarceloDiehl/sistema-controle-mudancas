# Teste de ponta a ponta do protótipo (Controle de Demandas de Mudanças).
# Uso:  pip install playwright  &&  python -m playwright install chromium
#       python testes/teste_ponta_a_ponta.py            (abre o index.html desta pasta)
#       python testes/teste_ponta_a_ponta.py <url>      (ou outro endereço, ex.: http://localhost:8080/)
# Passa pelos fluxos principais (abas, filtros, nova demanda, tickets, status ao salvar, automação por data,
# relatório PDF, conclusão pelo técnico, cancelamento, exclusão, lixeira, equipe) e confere o resultado no
# localStorage. O sistema começa vazio: as demandas usadas aqui são criadas pelo próprio teste, só no navegador dele.
import sys, pathlib, json, datetime
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else (pathlib.Path(__file__).resolve().parent.parent / 'index.html').as_uri()
CH = 'ditic-dsup-mudancas-v5'; ok = []; falhas = []
def sair_do_campo(pg): pg.evaluate('document.activeElement.blur()')  # como no clique real, o campo perde o foco antes de salvar
def em_dias(n): return (datetime.date.today() + datetime.timedelta(days=n)).isoformat()
def br(iso): return '/'.join(reversed(iso.split('-')))
def topo(pg): return pg.evaluate("[document.querySelector('#det-titulo').getBoundingClientRect().top, document.querySelector('.det-l2').getBoundingClientRect().top, document.querySelector('.abas').getBoundingClientRect().top]")
def motivo(pg, txt): pg.fill('#mc-motivo', txt); clk(pg, '.confirma [data-acao=confirmar]')
def muda(pg, i, js): pg.evaluate(f"(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); const d=o.demandas.find(x=>x.id==={i}); {js}; localStorage.setItem('{CH}', JSON.stringify(o));}})()"); pg.reload(); pg.wait_for_timeout(400)
def massa():
    base = lambda i, sit, resp, local: {'id': i, 'sei': f'8.2026.9745/{i:06d}-1', 'descricao': f'Demanda de teste {i}', 'comarca': local, 'responsavel': resp, 'inicio': None, 'fim': None, 'situacao': sit, 'ticketPrincipal': None, 'subtickets': [], 'informacoes': '', 'historico': [], 'criadaEm': '2026-01-01', 'passou': [resp] if resp else [], 'aviso': None}
    tecs = ['tecnico1', 'tecnico2', 'tecnico3']; ls = [base(i, 'nova', tecs[i % 3], 'Pelotas' if i % 4 == 0 else 'Canoas') for i in range(1, 25)]
    ls += [dict(base(30 + i, 'concluida', None, 'Ijuí'), tecnico='tecnico1', ticketPrincipal='180000', acionadaEm='2026-01-02', subtickets=[{'empresa': 'CDS', 'numero': '180001', 'finalidade': 'Mudança de Local', 'quantidade': 3}]) for i in range(3)]
    ls.append(dict(base(900, 'acionada', 'tecnico1', 'Guaíba'), ticketPrincipal='190000', inicio='2099-01-10', acionadaEm='2026-01-02'))
    ls.append(dict(base(901, 'cancelada', 'tecnico1', 'Ijuí')))
    equipe = [{'id': i, 'nome': i.capitalize(), 'curto': i.capitalize(), 'ini': i[:2].upper(), 'cor': '#3E7C8A', 'ativo': True} for i in tecs]
    ls.append(dict(base(902, 'nova', 'tecnico1', 'Torres'), inicio='2026-01-05', descricao='Data vencida'))
    return {'demandas': ls, 'excluidas': [], 'equipe': equipe}
def chk(cond, nome): (ok if cond else falhas).append(nome); print(('OK   ' if cond else 'FALHA ') + nome)
def st(pg): return pg.evaluate(f"JSON.parse(localStorage.getItem('{CH}'))")
def dem(pg, i): return next(d for d in st(pg)['demandas'] if d['id'] == i)
def clk(pg, sel, n=0): pg.evaluate(f"(()=>{{const e=document.querySelectorAll({sel!r})[{n}]; if(!e) throw new Error('nao achei '+{sel!r}); e.click();}})()"); pg.wait_for_timeout(180)
def flash(pg): e = pg.query_selector('.flash'); return e.inner_text() if e else ''
def entra(pg, usuario):  # técnico entra pelo formulário (no protótipo, qualquer senha)
    clk(pg, '[data-acao=login]'); pg.fill('#l-usr', usuario); pg.fill('#l-sen', 'x'); pg.evaluate("document.querySelector('form.login').requestSubmit()"); pg.wait_for_timeout(300)
def sai(pg): clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=sair]')
def opcoes(pg): return [o.get_attribute('value') for o in pg.query_selector_all('#d-status option')]
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True); pg = ctx.new_page()
    erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(URL); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(500)
    chk(len(pg.query_selector_all('.linha-dem')) == 0 and pg.query_selector('.vazio-lista') is not None, 'sistema começa sem nenhuma demanda')
    clk(pg, '[data-acao=resp-pop]'); chk(len(pg.query_selector_all('.op-resp')) == 1 and 'Sem responsável' not in pg.inner_text('.pop-resp'), 'sistema novo sem técnicos: só o Coordenador, sem a opção Sem responsável'); clk(pg, '[data-acao=resp-pop]')
    chk(pg.inner_text('h1') == 'Filtro de Demanda', 'título Filtro de Demanda')
    for vista in ('linhas', 'postits'):
        clk(pg, f'[data-acao=vista][data-v={vista}]'); dif = pg.evaluate("(()=>{const a=document.querySelector('.rolagem').getBoundingClientRect();const c=document.querySelector('.vazio-lista');const r=document.createRange();r.selectNodeContents(c);const b=r.getBoundingClientRect();return Math.abs((a.top+a.height/2)-(b.top+b.height/2))})()"); chk(dif < 3, 'lista vazia centralizada em ' + vista)
    clk(pg, '[data-acao=vista][data-v=linhas]')
    clk(pg, '[data-acao=sobre]'); ver = pg.inner_text('.sobre-ver'); chk(ver == 'Versão do Sistema: 1.0.0 · Novembro/2026', 'créditos na versão 1.0.0, sem protótipo e sem parênteses'); clk(pg, '[data-acao=fechar-modal]')
    pg.evaluate("([c, v]) => localStorage.setItem(c, v)", [CH, json.dumps(massa())]); pg.reload(); pg.wait_for_timeout(500)
    chk(len(pg.query_selector_all('.linha-dem')) == 10, 'folha com 10 linhas')
    chk(pg.query_selector('[data-acao=nova]') is not None, 'Nova demanda aparece para todos')
    clk(pg, '[data-acao=nova]'); chk(pg.query_selector('form.login') is not None and pg.query_selector('form[data-form=nova]') is None, 'sem login, Nova demanda pede para entrar'); clk(pg, '.login [data-acao=fechar-modal]')
    clk(pg, '[data-acao=abrir]'); chk(pg.is_disabled('#f-desc') and pg.query_selector('#d-status') is None and 'entre para alterar' in pg.inner_text('.det-id') and pg.query_selector('form[data-form=principal]') is None, 'sem login, o card é só para consulta')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=acionamento]'); chk(pg.query_selector('form.login') is not None, 'sem login, gerar texto pede para entrar'); clk(pg, '.login [data-acao=fechar-modal]'); clk(pg, '[data-acao=fechar-det]')
    abas = [e.inner_text() for e in pg.query_selector_all('.sit-aba .aba-nome')]; chk(abas == ['Em aberto', 'Novas', 'Acionadas', 'Em Atendimento', 'Para Validação', 'Concluídas', 'Canceladas'], 'nomes das abas de status')
    chk('Data passou' not in pg.content(), 'não existe mais o selo Data passou')
    # abas
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); chk(all(c.get_attribute('data-sit') == 'concluida' for c in pg.query_selector_all('.linha-dem')), 'aba Concluídas filtra')
    chk(not pg.query_selector('[data-v=todas]'), 'não existe aba Todas')
    clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    pg.fill('#busca', 'Pelotas'); pg.wait_for_timeout(300); chk(len(pg.query_selector_all('.linha-dem')) >= 1 and all('Pelotas' in c.inner_text() for c in pg.query_selector_all('.linha-dem')), 'busca por local')
    pg.fill('#busca', ''); pg.wait_for_timeout(300)
    clk(pg, '[data-acao=vista][data-v=postits]'); chk(len(pg.query_selector_all('.postit')) == 8, 'post-its: 8 por folha'); clk(pg, '[data-acao=vista][data-v=linhas]')
    clk(pg, '[data-acao=folha][data-v="2"]'); chk('11–20' in pg.inner_text('.l-pe'), 'paginação vai para a folha 2'); clk(pg, '[data-acao=folha][data-v="1"]')
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); pg.fill('#busca', 'Pelotas'); pg.wait_for_timeout(300); clk(pg, '[data-acao=resp-pop]')
    conta = lambda v: int(pg.inner_text(f'[data-acao=resp-escolher][data-v={v}] .op-n'))
    chk(conta('tecnico1') == sum(1 for d in st(pg)['demandas'] if d['responsavel'] == 'tecnico1'), 'filtro de responsável conta todos os cards, independente de aba e pesquisa')
    clk(pg, '[data-acao=resp-pop]'); pg.fill('#busca', ''); pg.wait_for_timeout(300); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    clk(pg, '[data-acao=resp-pop]'); clk(pg, '[data-acao=resp-escolher][data-v=tecnico2]'); chk(all('Tecnico2' in c.inner_text() for c in pg.query_selector_all('.linha-dem')), 'filtro de responsável'); clk(pg, '.filtro-limpa')
    # técnico entra com o próprio usuário: altera, mas não cancela
    entra(pg, 'tecnico1'); chk(st(pg)['usuario'] == 'tecnico1' and pg.query_selector('form[data-form=senha]') is None and 'Tecnico1' in pg.inner_text('.topo'), 'técnico entra com o usuário da Equipe')
    clk(pg, '[data-acao=menu-conta]'); chk(pg.query_selector('[data-acao=equipe]') is None and pg.query_selector('[data-acao=lixeira]') is None and pg.query_selector('[data-acao=config]') is None, 'menu do técnico sem Equipe, Lixeira e Configuração'); clk(pg, '[data-acao=menu-conta]')
    clk(pg, '[data-acao=sit-aba][data-v=nova]'); prim = int(pg.get_attribute('.linha-dem', 'data-id')); clk(pg, '[data-acao=abrir]')
    ops = opcoes(pg); chk(ops == ['nova', 'acionada'], 'técnico só vê Nova/Acionada no status')
    clk(pg, '[data-acao=menu-mais]'); chk(not pg.query_selector('[data-acao=cancelar]') and not pg.query_selector('[data-acao=excluir]'), 'técnico não tem Cancelar/Excluir')
    clk(pg, '[data-acao=menu-mais]')
    # status só muda ao salvar; fechar pergunta antes de descartar
    pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(200); chk(dem(pg, prim)['situacao'] == 'nova' and pg.is_enabled('#btn-salvar'), 'trocar o select não muda o status antes de salvar')
    clk(pg, '[data-acao=fechar-det]'); chk(pg.query_selector('.confirma') is not None, 'fechar com status não salvo pede confirmação'); clk(pg, '.confirma [data-acao=confirmar]')
    chk(dem(pg, prim)['situacao'] == 'nova', 'descartar mantém o status original')
    # acionada não volta e, para o técnico, fica travada
    clk(pg, '[data-acao=sit-aba][data-v=acionada]'); clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'técnico: Acionada não volta para Nova'); clk(pg, '[data-acao=fechar-det]')
    # login coordenador
    sai(pg); clk(pg, '[data-acao=login]'); chk(pg.query_selector('form.login') is not None, 'modal de login abre'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300)
    chk(pg.query_selector('form[data-form=senha]') is not None and not st(pg)['usuario'], 'primeiro acesso exige criar senha antes de entrar')
    pg.mouse.click(5, 5); pg.keyboard.press('Escape'); pg.wait_for_timeout(150); chk(pg.query_selector('form[data-form=senha]') is not None, 'troca de senha não fecha por clique fora nem Esc')
    pg.fill('#s-nova', 'curta'); pg.fill('#s-conf', 'curta'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(200); chk('8 caracteres' in pg.inner_text('.erro'), 'senha curta é recusada')
    pg.fill('#s-nova', 'senhaNova123'); pg.fill('#s-conf', 'outraSenha123'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(200); chk('não são iguais' in pg.inner_text('.erro'), 'confirmação diferente é recusada')
    pg.fill('#s-nova', 'senhaNova123'); pg.fill('#s-conf', 'senhaNova123'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(300)
    chk(st(pg)['usuario'] == 'admin' and st(pg)['senhaDefinida'] and 'senhaNova123' not in json.dumps(st(pg)) and pg.query_selector('[data-acao=nova]') is not None, 'coordenador define a senha, entra e vê Nova demanda')
    clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'coordenador: Acionada sem select de status (cancelar só em Mais ações)'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=nova]'); clk(pg, '[data-acao=abrir]'); chk(opcoes(pg) == ['nova', 'acionada'], 'select de status sem Cancelada, Em atendimento e Para validação')
    pg.mouse.click(5, 5); pg.wait_for_timeout(150); chk(pg.query_selector('.det') is not None, 'clique fora não fecha o card'); pg.keyboard.press('Escape'); pg.wait_for_timeout(150); chk(pg.query_selector('.det') is not None, 'Esc não fecha o card')
    t0 = topo(pg); clk(pg, '[data-acao=aba][data-v=tickets]'); t1 = topo(pg); clk(pg, '[data-acao=aba][data-v=hist]'); t2 = topo(pg); chk(t0 == t1 == t2, f'cabeçalho não se move ao trocar de aba {t0} {t1}'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'coordenador: Concluída é final, sem select de status')
    # demanda Concluída: somente consulta; só registra andamento e não pode ser excluída
    conc = int(pg.get_attribute('.linha-dem', 'data-id')); chk(pg.is_disabled('#f-desc') and pg.is_disabled('#f-ini') and pg.query_selector('#btn-salvar') is None, 'encerrada: Detalhes somente leitura, sem Salvar')
    clk(pg, '[data-acao=aba][data-v=tickets]'); chk(not pg.query_selector('form[data-form=principal]') and not pg.query_selector('form[data-form=sub]') and not pg.query_selector('[data-acao=tk-alterar]') and not pg.query_selector('[data-acao=sub-del]') and pg.is_disabled('#sq-0') and pg.is_disabled('#sf-0'), 'encerrada: Tickets somente leitura')
    pg.evaluate("(()=>{const e=document.getElementById('sq-0'); e.disabled=false; e.value='99'; e.dispatchEvent(new Event('change',{bubbles:true}));})()"); pg.wait_for_timeout(200); chk(dem(pg, conc)['subtickets'][0]['quantidade'] == 3, 'encerrada: alteração forçada é recusada')
    clk(pg, '[data-acao=aba][data-v=hist]'); pg.fill('#h-nota', 'Anotação depois de concluir'); pg.evaluate("document.querySelector('form[data-form=nota]').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, conc)['historico'][-1]['texto'] == 'Anotação depois de concluir', 'encerrada: ainda registra andamento no histórico')
    clk(pg, '[data-acao=menu-mais]'); chk(not pg.query_selector('[data-acao=excluir]') and not pg.query_selector('[data-acao=cancelar]'), 'Concluída: coordenador não pode excluir nem cancelar'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=cancelada]'); clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'coordenador: Cancelada é final, sem select de status'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    # nova demanda
    clk(pg, '[data-acao=nova]'); pg.mouse.click(5, 5); pg.wait_for_timeout(150); chk(pg.query_selector('form[data-form=nova]') is not None, 'clique fora não fecha a Nova demanda')
    rots = [e.inner_text() for e in pg.query_selector_all('.grade-ini .campo > label')][1:]; chk(rots == ['Data de Início', 'Data para Conclusão', 'Hora'], f'campos de data e hora na ordem pedida {rots}')
    pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(200)
    chk(len(pg.query_selector_all('.modal .erro')) >= 2, 'nova demanda valida campos obrigatórios')
    pg.fill('#n-sei', '8202697450000999'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Teste de ponta a ponta')
    clk(pg, '[data-acao=cal-abrir]'); chk(pg.query_selector('#cal-pop') is not None, 'calendário abre'); clk(pg, '[data-acao=cal-hoje]'); chk(pg.input_value('#n-ini') == br(em_dias(0)), 'calendário: Hoje preenche a data')
    pg.fill('#n-ini', br(em_dias(2)))  # para o futuro: no dia do início, com tickets, a Nova já entraria Em atendimento
    pg.fill('#n-hora', '09:00')
    pg.evaluate("document.querySelector('input[name=n-resp][value=tecnico1]').click()"); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    chk(pg.query_selector('.sucesso') is not None, 'nova demanda incluída (tela de sucesso)')
    nid = max(d['id'] for d in st(pg)['demandas']); nd = dem(pg, nid)
    chk(nd['sei'] == '8.2026.9745/000099-9' and nd['responsavel'] == 'tecnico1' and nd['situacao'] == 'nova' and nd['aviso']['tipo'] == 'nova', 'dados da nova demanda (SEI formatado, Tecnico1, Nova, bolinha)'); chk(nd['hora'] == '09:00' and 'horaFim' not in nd, 'grava uma hora só, a do início')
    clk(pg, '[data-acao=abrir-nova]'); pg.wait_for_timeout(200)
    # salvar Acionada sem ticket: leva à aba Tickets e mantém o status escolhido
    pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(200); clk(pg, '#btn-salvar')
    chk(dem(pg, nid)['situacao'] == 'nova' and pg.query_selector('#t-principal') is not None and pg.input_value('#d-status') == 'acionada', 'salvar Acionada sem ticket pede o ticket e mantém a escolha')
    # tickets
    chk(pg.input_value('#n-emp') == '', 'select de empresa começa sem nenhuma pré-selecionada')
    pg.fill('#n-num', '189100'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(200); chk('Escolha a empresa' in pg.inner_text('.add-sub ~ .erro') and not dem(pg, nid)['subtickets'], 'empresa é obrigatória'); pg.fill('#n-num', '')
    for errado in ('1899001', '18900'):
        pg.fill('#t-principal', errado); pg.evaluate("document.querySelector('form[data-form=principal]').requestSubmit()"); pg.wait_for_timeout(200)
        chk(not dem(pg, nid)['ticketPrincipal'] and '6 dígitos' in pg.inner_text('.det .erro'), f'ticket principal com {len(errado)} dígitos é recusado')
    pg.fill('#t-principal', '189001'); pg.evaluate("document.querySelector('form[data-form=principal]').requestSubmit()"); pg.wait_for_timeout(250)
    chk(dem(pg, nid)['ticketPrincipal'] == '189001', 'ticket principal registrado')
    pg.select_option('#n-emp', 'CDS'); pg.select_option('#n-fin', 'Mudança de Local'); pg.fill('#n-num', '189101 / 1891020'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(200)
    chk(not dem(pg, nid)['subtickets'] and '6 dígitos' in pg.inner_text('.add-sub ~ .erro'), 'subticket com mais de 6 dígitos é recusado, mesmo junto de um certo')
    pg.select_option('#n-emp', 'CDS'); pg.fill('#n-num', '189101 / 189102'); pg.select_option('#n-fin', 'Mudança de Local'); pg.fill('#n-qtd', '7')
    pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250)
    subs = dem(pg, nid)['subtickets']; chk(len(subs) == 2 and subs[0]['quantidade'] == 7 and subs[0]['empresa'] == 'CDS', 'dois subtickets CDS com quantidade 7')
    pg.select_option('#n-emp', 'WECOM'); serv_wecom = [o.inner_text() for o in pg.query_selector_all('#n-fin option')]; pg.select_option('#n-emp', 'CADI'); serv_cadi = [o.inner_text() for o in pg.query_selector_all('#n-fin option')]
    chk('Infraestrutura' in serv_wecom and 'Habilitação de Pontos de Rede' in serv_cadi, 'serviços novos da WECOM e da CADI')
    pg.fill('#n-num', '189103'); pg.select_option('#n-fin', 'Habilitação de Pontos de Rede'); pg.fill('#n-qtd', '2'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250)
    # status acionada
    chk(dem(pg, nid)['situacao'] == 'nova', 'registrar ticket não salva o status escolhido')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.fill('#f-ini', br(em_dias(2))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, nid); chk(x['situacao'] == 'acionada' and x['acionadaEm'] and not any('SLA' in h['texto'] for h in x['historico']), 'acionar grava a data do acionamento, sem registro de SLA')
    chk(x['aviso'] and x['aviso']['tipo'] == 'status' and x['aviso']['para'] == 'tecnico1', 'mudar o status acende a bolinha para o responsável')
    clk(pg, '[data-acao=fechar-det]'); chk(dem(pg, nid)['aviso'] is not None, 'bolinha continua depois de fechar o card em que o status mudou')
    pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); chk(dem(pg, nid)['aviso'] is None, 'bolinha some assim que o card é aberto'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    s90 = {'empresa': 'CADI', 'numero': '199999', 'finalidade': 'Configuração', 'quantidade': 1}
    muda(pg, 900, f"d.subtickets=[{json.dumps(s90)}]; d.situacao='nova'; d.acionadaEm=null; d.inicio='{em_dias(1)}'")
    pg.fill('#busca', '000900'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); chk(dem(pg, 900)['situacao'] == 'acionada', 'acionar na véspera é aceito'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # demanda para o mesmo dia: aciona e entra Em atendimento, sem sair do responsável
    s_cds = {'empresa': 'CDS', 'numero': '199998', 'finalidade': 'Instalação', 'quantidade': 1}
    # só com o ticket principal (sem subticket) ela não avança sozinha: continua Nova até alguém acionar
    muda(pg, 1, f"d.subtickets=[]; d.ticketPrincipal='199990'; d.inicio='{em_dias(0)}'"); tec1 = dem(pg, 1)['responsavel']; chk(dem(pg, 1)['situacao'] == 'nova', 'mesmo dia, sem subticket: continua Nova')
    pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); x = dem(pg, 1)
    chk(x['situacao'] == 'atendimento' and x['responsavel'] == tec1 and x['acionadaEm'] and x['aviso']['para'] == tec1, 'mesmo dia: acionar entra Em atendimento e a carga fica com o responsável')
    chk(not any('SLA' in h['texto'] for h in x['historico']) and 'SLA' not in flash(pg), 'mesmo dia: sem aviso nem registro de SLA'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    muda(pg, 2, f"d.subtickets=[{json.dumps(s_cds)}]; d.ticketPrincipal='199991'; d.inicio='{em_dias(1)}'")
    pg.fill('#busca', '000002'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); x = dem(pg, 2); chk(x['situacao'] == 'acionada' and not any('SLA' in h['texto'] for h in x['historico']), 'acionar na véspera com subticket não registra SLA'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # chega o dia: Em atendimento, com a carga no responsável e tudo editável
    muda(pg, nid, f"d.inicio='{em_dias(0)}'"); x = dem(pg, nid); chk(x['situacao'] == 'atendimento' and x['responsavel'] == 'tecnico1' and x['aviso']['tipo'] == 'atendimento' and x['aviso']['para'] == 'tecnico1', 'na data, entra Em atendimento e continua com o responsável')
    pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    chk(all(pg.is_enabled(s) for s in ('#f-sei', '#f-local', '#f-desc', '#f-ini', '#f-hora', '#f-fim', '#f-resp', '#f-info')) and pg.query_selector('#d-status') is None, 'Em atendimento: dados editáveis; só o status é automático')
    pg.select_option('#f-resp', 'tecnico2'); pg.fill('#f-info', 'Acompanhar atendimento'); pg.fill('#f-desc', 'Teste editado em atendimento'); sair_do_campo(pg); clk(pg, '#btn-salvar'); x = dem(pg, nid); chk(x['responsavel'] == 'tecnico2' and x['informacoes'] == 'Acompanhar atendimento' and x['descricao'] == 'Teste editado em atendimento' and x['aviso'] and x['aviso']['para'] == 'tecnico2', 'Em atendimento: muda responsável (com bolinha), descrição e informações')
    clk(pg, '[data-acao=aba][data-v=tickets]'); chk(pg.query_selector('form[data-form=sub]') is not None and pg.query_selector('[data-acao=sub-del]') is not None and pg.query_selector('[data-acao=tk-alterar]') is not None and pg.is_enabled('#sq-0') and pg.is_enabled('#sf-0'), 'Em atendimento: inclui, altera e remove tickets')
    pg.select_option('#n-emp', 'Selbetti'); pg.fill('#n-num', '189104'); pg.select_option('#n-fin', 'Instalação'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250); chk(any(s['numero'] == '189104' for s in dem(pg, nid)['subtickets']), 'Em atendimento: subticket novo incluído')
    clk(pg, '[data-acao=aba][data-v=dados]')
    # acionamento
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=acionamento]'); txt = pg.input_value('#ac-texto')
    chk('CDS: 189101 / 189102' in txt and 'Era o que cumpria informar.' in txt, 'texto de acionamento com subtickets'); clk(pg, '[data-acao=fechar-modal]')
    # automação: data passada -> Para validação, sem sair do responsável
    pg.evaluate(f"(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); const d=o.demandas.find(x=>x.id==={nid}); d.inicio='2026-01-10'; d.fim=null; localStorage.setItem('{CH}', JSON.stringify(o));}})()")
    pg.reload(); pg.wait_for_timeout(500); x = dem(pg, nid)
    chk(x['situacao'] == 'pendente' and x['responsavel'] == 'tecnico2' and x['aviso']['tipo'] == 'pendente' and x['aviso']['para'] == 'tecnico2', 'automático: data passada vira Para Validação e continua com o responsável')
    chk(any('automaticamente' in h['texto'] and h['usuario'] == 'sistema' for h in x['historico']), 'histórico registra mudança automática')
    # abre a pendente
    clk(pg, '[data-acao=sit-aba][data-v=pendente]'); pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'Pendente: status travado')
    # relatório
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]'); itens = pg.input_value('#rl-itens')
    chk('em total de 07 serviços' in itens and 'contratada CDS através do ticket 189101' in itens, 'relatório: item com quantidade e ticket')
    chk('Habilitação de pontos de rede para multifuncionais Selbetti, em total de 02 serviços. A atividade foi executada pela contratada CADI através do ticket 189103.' in itens, 'relatório: pontos de rede da CADI para multifuncionais Selbetti')
    chk('Instalação de nova multifuncional Selbetti, em total de 01 serviço. A atividade foi executada pela contratada Selbetti através do ticket 189104.' in itens, 'relatório: Selbetti descrita como multifuncional')
    txt = pg.inner_text('.relat'); chk('conferir os dados antes de gerar o relatório' in txt and 'Um item por parágrafo' not in txt and 'modelo-mestre' not in txt, 'relatório: texto de orientação novo, sem a dica dos itens')
    with pg.expect_download() as dl: clk(pg, '[data-acao=baixar-relatorio]')
    f = dl.value; caminho = f.path(); head = open(caminho, 'rb').read(5)
    chk(head == b'%PDF-' and f.suggested_filename.startswith('Relatório de execução'), 'PDF baixado (' + f.suggested_filename + ')')
    clk(pg, '[data-acao=fechar-modal]')
    # sem devolução: o técnico gera o relatório e conclui
    clk(pg, '[data-acao=fechar-det]'); sai(pg); entra(pg, 'tecnico2')
    clk(pg, '[data-acao=abrir]'); chk(dem(pg, nid)['aviso'] is None, 'bolinha some quando o técnico abre')
    chk('Aguardando a conclusão' in pg.inner_text('.det-id') and pg.query_selector('[data-acao=devolver-gestor]') is None, 'Para Validação: aguardando a conclusão, sem Devolver ao coordenador')
    clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=relatorio]') is not None and pg.query_selector('[data-acao=devolver-tec]') is None and pg.query_selector('[data-acao=cancelar]') is None, 'técnico gera o relatório; não há devolução nem cancelamento'); clk(pg, '[data-acao=menu-mais]')
    clk(pg, '[data-acao=concluir-dem]'); clk(pg, '.confirma [data-acao=confirmar]'); x = dem(pg, nid)
    chk(x['situacao'] == 'concluida' and x['responsavel'] is None and x['tecnico'] == 'tecnico2' and x['historico'][-2]['usuario'] == 'tecnico2', 'técnico conclui: fica com o setor, atendida por ele')
    sai(pg); clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300)
    chk(pg.query_selector('form[data-form=senha]') is None, 'segundo acesso não pede nova senha')
    # cancelar e excluir outra
    pg.fill('#busca', ''); clk(pg, '[data-acao=sit-aba][data-v=nova]'); outra = int(pg.get_attribute('.linha-dem', 'data-id')); clk(pg, '[data-acao=abrir]')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=cancelar]')
    txt = pg.inner_text('#mc-txt'); chk(txt == 'A ação não poderá ser desfeita.', 'texto do modal de cancelamento'); chk(pg.get_attribute('#mc-motivo', 'maxlength') == '100', 'motivo do cancelamento com até 100 caracteres')
    clk(pg, '.confirma [data-acao=confirmar]'); chk(dem(pg, outra)['situacao'] == 'nova' and pg.query_selector('.confirma .erro') is not None, 'cancelar sem motivo é recusado')
    motivo(pg, 'Setor desistiu da mudança'); x = dem(pg, outra); chk(x['situacao'] == 'cancelada' and x['motivoCancelamento'] == 'Setor desistiu da mudança' and 'Setor desistiu da mudança' in x['historico'][-1]['texto'], 'coordenador cancela demanda com motivo no histórico')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=excluir]'); clk(pg, '.confirma [data-acao=confirmar]'); chk(any(d['id'] == outra for d in st(pg)['demandas']), 'excluir sem motivo é recusado')
    motivo(pg, 'Cadastro duplicado'); s = st(pg); chk(not any(d['id'] == outra for d in s['demandas']) and s['excluidas'][-1]['id'] == outra and s['lixeira'][-1]['id'] == outra and s['lixeira'][-1]['motivoExclusao'] == 'Cadastro duplicado', 'excluir leva para a lixeira, com motivo')
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=lixeira]'); chk('Cadastro duplicado' in pg.inner_text('.lixeira') and 'restam 30 dias' in pg.inner_text('.lixeira'), 'lixeira mostra motivo e prazo')
    clk(pg, '[data-acao=restaurar]'); s = st(pg); chk(any(d['id'] == outra for d in s['demandas']) and not s['lixeira'] and dem(pg, outra)['situacao'] == 'cancelada', 'restaurar devolve a demanda como estava'); clk(pg, '[data-acao=fechar-modal]')
    # 30 dias na lixeira: some sem retorno
    pg.evaluate(f"(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); const i=o.demandas.findIndex(x=>x.id==={outra}); const d=o.demandas.splice(i,1)[0]; d.excluidaEm='{em_dias(-30)}T08:00'; d.excluidaPor='admin'; d.motivoExclusao='x'; o.lixeira.push(d); localStorage.setItem('{CH}', JSON.stringify(o));}})()"); pg.reload(); pg.wait_for_timeout(400)
    s = st(pg); chk(not s['lixeira'] and not any(d['id'] == outra for d in s['demandas']) and 'removida' in s['excluidas'][-1]['texto'], 'depois de 30 dias a lixeira remove a demanda')
    # o menu do gestor não tem mais Movimentações do dia
    clk(pg, '[data-acao=menu-conta]'); chk(pg.query_selector('[data-acao=movimentos]') is None and pg.query_selector('[data-acao=lixeira]') is not None and 'Movimentações' not in pg.inner_text('.topo'), 'menu do coordenador sem Movimentações do dia'); clk(pg, '[data-acao=menu-conta]')
    # equipe
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); pg.fill('#eq-nome', 'Ana Teste'); pg.evaluate("document.querySelector('form[data-form=equipe-add]').requestSubmit()"); pg.wait_for_timeout(250)
    chk(any(u['nome'] == 'Ana Teste' for u in st(pg)['equipe']), 'equipe: incluir pessoa')
    clk(pg, '[data-acao=eq-transferir][data-v=tecnico2]'); pg.select_option('#tr-dest', 'ana-teste'); pg.evaluate("document.querySelector('form[data-form=equipe-transf]').requestSubmit()"); pg.wait_for_timeout(250)
    chk(not any(d['responsavel'] == 'tecnico2' and d['situacao'] in ('nova', 'acionada') for d in st(pg)['demandas']), 'equipe: transferir demandas em aberto')
    clk(pg, '[data-acao=fechar-modal]')
    # Nova com data vencida: bolinha e data em vermelho
    muda(pg, 5, f"d.inicio='{em_dias(-3)}'; d.fim=null"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000005'); pg.wait_for_timeout(300)
    chk(pg.query_selector('.linha-dem .nv-ponto.venc') is not None and pg.query_selector('.c-data.vencida') is not None and pg.evaluate("getComputedStyle(document.querySelector('.c-data.vencida')).fontWeight") == '700', 'Nova vencida: bolinha vermelha e data em negrito vermelho')
    clk(pg, '[data-acao=vista][data-v=postits]'); chk(pg.query_selector('.postit .nv-ponto.venc') is not None and pg.query_selector('.pi-data .vencida') is not None, 'Nova vencida: sinal também no post-it'); clk(pg, '[data-acao=vista][data-v=linhas]')
    pg.fill('#busca', '000010'); pg.wait_for_timeout(300); chk(pg.query_selector('.nv-ponto.venc') is None, 'demanda sem data vencida não tem o sinal vermelho'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # demanda antiga: Nova aceita data passada e segue pelas regras de sempre
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000052'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Demanda antiga'); pg.fill('#n-ini', br(em_dias(-10))); pg.fill('#n-fim', br(em_dias(-8))); pg.evaluate("document.querySelector('input[name=n-resp][value=tecnico1]').click()"); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    ant = max(d['id'] for d in st(pg)['demandas']); x = dem(pg, ant)
    chk(pg.query_selector('.sucesso') is not None and 'A data já passou' in pg.inner_text('.sucesso .suc-nota') and x['situacao'] == 'nova' and x['inicio'] == em_dias(-10), 'Nova demanda aceita data passada, entra Nova e avisa sem bloquear')
    clk(pg, '[data-acao=abrir-nova]'); pg.wait_for_timeout(200)
    pg.fill('#t-principal', '188001'); pg.evaluate("document.querySelector('form[data-form=principal]').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, ant)['situacao'] == 'nova', 'antiga: só com o ticket principal continua Nova')
    pg.select_option('#n-emp', 'CDS'); pg.select_option('#n-fin', 'Mudança de Local'); pg.fill('#n-num', '188002'); pg.fill('#n-qtd', '2'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(300); x = dem(pg, ant)
    chk(x['situacao'] == 'pendente' and x['responsavel'] == 'tecnico1' and x['acionadaEm'] == em_dias(-10) and sum('automaticamente' in h['texto'] for h in x['historico']) == 2, 'antiga: com ticket principal e subticket vai sozinha até Para Validação, acionamento na Data de Início')
    pg.select_option('#n-emp', 'CDS'); pg.select_option('#n-fin', 'Instalação'); pg.fill('#n-num', '188003'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250); chk(len(dem(pg, ant)['subtickets']) == 2, 'antiga: em Para Validação ainda recebe subtickets')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.fill('#f-fim', br(em_dias(3))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, ant)['fim'] == em_dias(-8) and 'anterior a hoje' in pg.inner_text('.det .erro'), 'Para Validação: Data para Conclusão não vai para hoje ou depois')
    pg.fill('#f-fim', br(em_dias(-7))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, ant); chk(x['fim'] == em_dias(-7) and x['situacao'] == 'pendente', 'Para Validação: datas corrigidas no passado são aceitas')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]'); chk(pg.input_value('#rl-acion') == br(em_dias(-10)), 'antiga: relatório com a data do acionamento na Data de Início'); clk(pg, '[data-acao=fechar-modal]')
    clk(pg, '[data-acao=concluir-dem]'); clk(pg, '.confirma [data-acao=confirmar]'); chk(dem(pg, ant)['situacao'] == 'concluida', 'antiga: concluída e registrada no sistema'); clk(pg, '[data-acao=fechar-det]')
    # Nova de período passado acionada à mão vai direto para Para Validação
    muda(pg, 5, f"d.inicio='{em_dias(-6)}'; d.fim=null; d.ticketPrincipal='188010'; d.subtickets=[]"); pg.fill('#busca', '000005'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    pg.fill('#f-ini', br(em_dias(-5))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 5)['inicio'] == em_dias(-5) and dem(pg, 5)['situacao'] == 'nova', 'Nova aceita mudar a data para o passado')
    pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); x = dem(pg, 5); chk(x['situacao'] == 'pendente' and x['acionadaEm'] == em_dias(-5) and 'Para Validação' in flash(pg), 'acionar Nova de período passado leva a Para Validação')
    clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # sem data e com SEI repetido
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000051'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Sem nenhuma data'); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    novo = dem(pg, max(d['id'] for d in st(pg)['demandas'])); chk(pg.query_selector('.sucesso') is not None and novo['inicio'] is None and novo['sei'] == '8.2026.9745/000005-1' and sum(1 for d in st(pg)['demandas'] if d['sei'] == novo['sei']) == 2, 'cria demanda sem data e com SEI repetido'); clk(pg, '.sucesso [data-acao=fechar-modal]')
    # Em atendimento: as datas se editam direto nos Detalhes, por qualquer pessoa
    salva = lambda: (pg.evaluate("document.getElementById('form-dados').requestSubmit()"), pg.wait_for_timeout(250))
    pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    pg.fill('#f-fim', br(em_dias(5))); sair_do_campo(pg); salva(); x = dem(pg, 1); chk(x['fim'] == em_dias(5) and x['situacao'] == 'atendimento' and 'Agendamento alterado' in x['historico'][-1]['texto'], 'Em atendimento: Data para Conclusão alterada nos Detalhes, com registro no histórico')
    pg.fill('#f-ini', br(em_dias(1))); sair_do_campo(pg); salva(); chk(dem(pg, 1)['inicio'] == em_dias(0) and 'depois de hoje' in pg.inner_text('.det .erro'), 'Em atendimento: Data de Início não vai para depois de hoje')
    clk(pg, '[data-acao=fechar-det]'); (clk(pg, '.confirma [data-acao=confirmar]') if pg.query_selector('.confirma') else None)
    sai(pg); entra(pg, 'tecnico3'); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=alterar-conclusao]') is None, 'não existe mais Alterar Data para Conclusão'); clk(pg, '[data-acao=menu-mais]')
    pg.fill('#f-desc', 'Editada pelo técnico'); sair_do_campo(pg); salva(); x = dem(pg, 1); chk(x['descricao'] == 'Editada pelo técnico' and x['historico'][-1]['usuario'] == 'tecnico3' and x['responsavel'] != 'tecnico3', 'outro técnico edita o card Em atendimento; o histórico registra quem fez')
    clk(pg, '[data-acao=fechar-det]'); sai(pg); clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # acionar exige data; demanda acionada não perde a data nem vai para o passado
    muda(pg, 3, "d.inicio=null; d.fim=null; d.ticketPrincipal='199992'; d.situacao='nova'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000003'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar')
    chk(dem(pg, 3)['situacao'] == 'nova' and 'Data de Início' in flash(pg) and pg.input_value('#d-status') == 'acionada', 'acionar sem data é recusado e mantém a escolha'); pg.select_option('#d-status', 'nova'); pg.wait_for_timeout(150); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    muda(pg, 900, f"d.situacao='acionada'; d.inicio='{em_dias(10)}'; d.fim=null"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    pg.fill('#f-ini', br(em_dias(-5))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, 900); chk(x['situacao'] == 'acionada' and x['inicio'] == em_dias(10) and 'passado' in pg.inner_text('.det .erro'), 'demanda acionada recusa data no passado')
    pg.fill('#f-ini', ''); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 900)['inicio'] == em_dias(10) and 'precisa ter' in pg.inner_text('.det .erro'), 'demanda acionada não pode perder a data'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '.confirma [data-acao=confirmar]')
    # contagem de dias até o início
    for n, txt in ((2, '02 dias'), (1, '01 dia'), (120, '120 dias'), (2000, '999 dias')):
        muda(pg, 900, f"d.inicio='{em_dias(n)}'"); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); chk(txt == pg.inner_text('.c-ag .prazo'), f'contagem até o início: {txt}')
    muda(pg, 900, f"d.inicio='{em_dias(2)}'; d.fim='{em_dias(4)}'"); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); chk(pg.inner_text('.c-ag .prazo') == '02 dias' and pg.query_selector('.pi-data') is None, 'contagem também em período de vários dias'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Em atendimento e Para validação nunca sem responsável
    muda(pg, 1, "d.responsavel='ana-teste'"); pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); chk('' not in [o.get_attribute('value') for o in pg.query_selector_all('#f-resp option')] and 'Sem responsável' not in pg.inner_text('#f-resp'), 'Responsável: sem a opção Sem responsável'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); clk(pg, '[data-acao=eq-transferir][data-v=ana-teste]'); chk('Deixar sem responsável' not in pg.inner_text('.equipe') and pg.query_selector('#tr-dest option[value=admin]') is not None, 'Transferir: sem "Deixar sem responsável", com o Coordenador como destino'); pg.select_option('#tr-dest', 'admin'); pg.evaluate("document.querySelector('form[data-form=equipe-transf]').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, 1); chk(x['responsavel'] == 'admin' and x['tecnico'] == 'ana-teste', 'Transferir para o Coordenador'); clk(pg, '[data-acao=fechar-modal]')
    # demanda gravada sem responsável (dado antigo) passa ao gestor ao abrir o sistema
    muda(pg, 3, f"d.situacao='nova'; d.responsavel=null; d.inicio='{em_dias(5)}'; d.fim=null; d.ticketPrincipal='199992'"); chk(dem(pg, 3)['responsavel'] == 'admin', 'demanda sem responsável fica com o coordenador')
    clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000003'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#f-resp', 'tecnico1'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); sair_do_campo(pg); clk(pg, '#btn-salvar'); x = dem(pg, 3); chk(x['situacao'] == 'acionada' and x['responsavel'] == 'tecnico1', 'troca o responsável e aciona'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Nova já dentro do período não mostra "Hoje"
    muda(pg, 4, f"d.situacao='nova'; d.inicio='{em_dias(-3)}'; d.fim='{em_dias(5)}'; d.ticketPrincipal=null; d.subtickets=[]"); pg.fill('#busca', '000004'); pg.wait_for_timeout(300); chk(dem(pg, 4)['situacao'] == 'nova' and pg.query_selector('.c-ag .prazo') is None and pg.query_selector('.linha-dem.nv-venc .nv-ponto.venc') is not None, 'Nova sem tickets na Data de Início: continua Nova, com sinal e contorno vermelhos')
    muda(pg, 4, f"d.inicio='{em_dias(0)}'; d.fim=null"); pg.fill('#busca', '000004'); pg.wait_for_timeout(300); chk(pg.query_selector('.linha-dem.nv-venc') is not None, 'sinal vermelho já no dia do início')
    muda(pg, 4, "d.ticketPrincipal='199994'"); chk(dem(pg, 4)['situacao'] == 'nova', 'só o ticket principal não basta: continua Nova')
    s4 = {'empresa': 'CDS', 'numero': '199995', 'finalidade': 'Instalação', 'quantidade': 1}
    muda(pg, 4, f"d.ticketEm={{data:'{em_dias(-1)}T10:00',usuario:'admin'}}; d.subtickets=[{json.dumps(s4)}]"); x = dem(pg, 4); chk(x['situacao'] == 'atendimento' and x['acionadaEm'] == em_dias(-1) and x['aviso']['tipo'] == 'atendimento' and any('Nova → Em atendimento' in h['texto'] and h['usuario'] == 'sistema' for h in x['historico']), 'Nova com ticket principal e subticket entra Em atendimento sozinha (acionamento = registro do ticket)')
    pg.fill('#busca', '000004'); pg.wait_for_timeout(300); chk(pg.query_selector('.linha-dem') is not None and pg.query_selector('.linha-dem.nv-venc') is None, 'Em atendimento sem o sinal vermelho')
    muda(pg, 8, f"d.situacao='nova'; d.inicio='{em_dias(-4)}'; d.fim='{em_dias(-2)}'; d.ticketPrincipal='199996'; d.subtickets=[{json.dumps(s4)}]"); chk(dem(pg, 8)['situacao'] == 'pendente', 'Nova com tickets e período já terminado vai até Para Validação'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # relatório também em Concluída
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=relatorio]') is not None, 'Concluída: coordenador ainda gera o relatório'); clk(pg, '[data-acao=relatorio]'); chk(pg.query_selector('#rl-itens') is not None, 'Concluída: relatório abre'); clk(pg, '[data-acao=fechar-modal]'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    # relatório sem subticket
    muda(pg, 7, f"d.situacao='pendente'; d.responsavel='admin'; d.tecnico='tecnico1'; d.inicio='{em_dias(-3)}'; d.fim=null; d.subtickets=[]; d.ticketPrincipal='199993'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000007'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]')
    chk('não tem subtickets' in pg.inner_text('.relat .ac-aviso'), 'relatório sem subticket mostra aviso'); clk(pg, '[data-acao=fechar-modal]')
    clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Coordenador como responsável na Nova Demanda
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000071'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Para o coordenador'); pg.evaluate("document.querySelector('input[name=n-resp][value=admin]').click()"); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    novo = dem(pg, max(d['id'] for d in st(pg)['demandas'])); chk(novo['responsavel'] == 'admin' and 'atribuída ao Coordenador' in pg.inner_text('.sucesso') and 'atribuída ao Coordenador' in novo['historico'][0]['texto'], 'Nova Demanda pode ser atribuída ao Coordenador'); clk(pg, '.sucesso [data-acao=fechar-modal]')
    # WECOM: serviços e campo Metro Linear
    muda(pg, 21, f"d.situacao='nova'; d.responsavel='tecnico1'; d.inicio='{em_dias(5)}'; d.fim=null; d.ticketPrincipal='199995'; d.subtickets=[]"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000021'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=aba][data-v=tickets]')
    pg.select_option('#n-emp', 'WECOM'); pg.wait_for_timeout(100); ops = [o.inner_text() for o in pg.query_selector_all('#n-fin option')]; chk(ops[1:] == ['Instalação', 'Realocação', 'Infraestrutura'], 'WECOM: Realocação no lugar de Mudança de Local/Prédio, sem Desinstalação')
    pg.select_option('#n-fin', 'Realocação'); pg.wait_for_timeout(100); chk(not pg.is_visible('#n-metro'), 'Metro Linear escondido na Realocação')
    pg.select_option('#n-fin', 'Infraestrutura'); pg.wait_for_timeout(100); chk(pg.is_visible('#n-metro'), 'Metro Linear aparece na Infraestrutura da WECOM')
    pg.select_option('#n-emp', 'CDS'); pg.wait_for_timeout(100); chk(not pg.is_visible('#n-metro'), 'Metro Linear escondido fora da WECOM')
    pg.select_option('#n-emp', 'WECOM'); pg.wait_for_timeout(100); pg.select_option('#n-fin', 'Instalação'); pg.wait_for_timeout(100); chk(not pg.is_visible('#n-metro'), 'Metro Linear escondido na Instalação da WECOM'); pg.select_option('#n-fin', 'Infraestrutura'); pg.wait_for_timeout(100); pg.fill('#n-num', '189201'); pg.fill('#n-metro', '12.5'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250); chk(not dem(pg, 21)['subtickets'] and 'inteiro' in pg.inner_text('.add-sub ~ .erro'), 'metro linear quebrado é recusado')
    pg.fill('#n-metro', '12'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 21)['subtickets'][0].get('metro') == 12, 'subticket guarda o metro linear')
    pg.fill('#sm-0', ''); sair_do_campo(pg); pg.wait_for_timeout(250); chk('metro' not in dem(pg, 21)['subtickets'][0], 'metro linear pode ficar em branco na tabela'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # custo do relatório: CDS por região e serviço; WECOM com Realocação e Instalação por quantidade e Infraestrutura por metro linear (ou verba de 15 m)
    subs_custo = [{'empresa': 'CDS', 'numero': '189301', 'finalidade': 'Mudança de Local', 'quantidade': 3}, {'empresa': 'WECOM', 'numero': '189302', 'finalidade': 'Realocação', 'quantidade': 1}, {'empresa': 'WECOM', 'numero': '189303', 'finalidade': 'Instalação', 'quantidade': 12}, {'empresa': 'WECOM', 'numero': '189304', 'finalidade': 'Infraestrutura', 'quantidade': 1}, {'empresa': 'WECOM', 'numero': '189305', 'finalidade': 'Infraestrutura', 'quantidade': 1, 'metro': 10}]
    muda(pg, 20, f"d.situacao='pendente'; d.responsavel='admin'; d.tecnico='tecnico1'; d.comarca='Canoas'; d.inicio='{em_dias(-3)}'; d.fim=null; d.ticketPrincipal='199994'; d.subtickets={json.dumps(subs_custo)}")
    def abre_relatorio(): clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000020'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]')
    def fecha_relatorio(): clk(pg, '[data-acao=fechar-modal]'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    abre_relatorio(); chk(pg.input_value('#rl-custo') == 'R$ 20.357,52', 'custo soma CDS da região, Realocação, Instalação por quantidade e Infraestrutura (metro linear e verba)')
    itens = pg.input_value('#rl-itens'); chk('em total de 03 serviços' in itens and 'em total de 01 serviço,' in itens and 'em total de 12 serviços' in itens, 'relatório: quantidade com dois dígitos')
    chk('Foro da Comarca' not in itens and 'Mudança de local de equipamentos de informática, em total de 03 serviços. A atividade foi executada pela contratada CDS através do ticket 189301.' in itens, 'item sem o local, que fica só no texto de abertura')
    chk('Instalação de novos equipamentos de informática, em total de 12 serviços, se tratando de contrato referente às Salas de Audiência Digital. A atividade foi executada pela contratada WECOM através do ticket 189303.' in itens and 'Instalação de Infraestrutura (redes lógicas, elétricas, canaletas e suportes para TV), em total de 01 serviço, se tratando de contrato referente às Salas de Audiência Digital. A atividade foi executada pela contratada WECOM através do ticket 189304.' in itens, 'itens da WECOM com o contrato das Salas de Audiência Digital')
    nota = pg.input_value('#rl-notas'); chk('A demanda referente a Instalação de Infraestrutura (WECOM), ticket 189304, utiliza o valor de verba de R$2.462,70 somado ao valor total do relatório. Valor estimado com base em uma média de 15 metros lineares de instalação. O valor por metro linear consiste em R$164,18.' == nota, 'frase da verba só para a Infraestrutura sem metro linear')
    chk(pg.is_checked('#rl-local'), 'Realocação marca Mudança de Local no quadro')
    with pg.expect_download() as dl: clk(pg, '[data-acao=baixar-relatorio]')
    pdf_b = open(dl.value.path(), 'rb').read(); chk(pdf_b[:5] == b'%PDF-' and b'0.6 w' not in pdf_b and b'/F2 10 Tf' in pdf_b and 'no Foro da Comarca de Canoas'.encode('cp1252') in pdf_b, 'PDF com linhas finas, local na abertura e a observação de custo'); fecha_relatorio()
    # local fora do catálogo: não soma e avisa
    muda(pg, 20, "d.comarca='Lugar sem região'"); abre_relatorio(); chk('189301' in pg.inner_text('.relat .ac-aviso') and pg.input_value('#rl-custo') == 'R$ 19.877,52', 'CDS sem região fica fora da soma, com aviso'); fecha_relatorio(); muda(pg, 20, "d.comarca='Canoas'")
    # Desinstalação da Selbetti não vai para lugar nenhum; a da CDS vai para o DMP
    s_sel = [{'empresa': 'CADI', 'numero': '187001', 'finalidade': 'Mudança de Local', 'quantidade': 1}, {'empresa': 'Selbetti', 'numero': '187002', 'finalidade': 'Desinstalação', 'quantidade': 1}]
    muda(pg, 20, f"d.subtickets={json.dumps(s_sel)}"); abre_relatorio(); chk('Carga CDS' not in pg.input_value('#rl-destino') and pg.is_checked('#rl-desinst'), 'Desinstalação da Selbetti não leva destino (continua marcada no quadro)'); fecha_relatorio()
    s_cds2 = s_sel + [{'empresa': 'CDS', 'numero': '187003', 'finalidade': 'Desinstalação', 'quantidade': 1}]
    muda(pg, 20, f"d.subtickets={json.dumps(s_cds2)}"); abre_relatorio(); chk('DMP – Carga CDS' in pg.input_value('#rl-destino'), 'Desinstalação da CDS leva o destino DMP – Carga CDS'); fecha_relatorio()
    muda(pg, 20, f"d.subtickets={json.dumps(subs_custo)}")
    # Configuração: o coordenador altera os valores
    def cfg_salvar(): pg.evaluate("document.querySelector('form[data-form=config]').requestSubmit()"); pg.wait_for_timeout(250)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=config]'); chk(pg.input_value('#pc-4-4') == '160,00' and pg.input_value('#pw-realocacao') == '4.121,86' and pg.input_value('#pw-instalacao') == '970,93' and pg.input_value('#pw-metro') == '164,18' and pg.query_selector('#pw-metrosEstimados') is None, 'Configuração mostra os valores atuais, sem Metros estimados')
    chk(pg.inner_text('#cfg-salvar') == 'Salvar Alterações' and pg.is_disabled('#cfg-salvar'), 'Salvar Alterações começa inativo')
    txt = pg.inner_text('.config'); chk(pg.inner_text('label[for=pw-metro]') == 'Infraestrutura' and 'Metros estimados' not in txt and 'Metro linear' not in txt and 'Instalação/Infraestrutura' not in txt and 'Exemplo' not in txt, 'WECOM: campos Realocação, Instalação e Infraestrutura, sem exemplo de cálculo')
    pg.fill('#pc-4-4', '161'); chk(not pg.is_disabled('#cfg-salvar'), 'Salvar Alterações ativa quando um campo muda'); pg.fill('#pc-4-4', '160,00'); chk(pg.is_disabled('#cfg-salvar'), 'voltar ao valor original inativa o botão de novo')
    pg.fill('#pw-metro', 'abc'); cfg_salvar(); chk(st(pg)['precos']['wecom']['metro'] == 164.18 and pg.get_attribute('#pw-metro', 'aria-invalid') == 'true' and 'Confira' in pg.inner_text('#cfg-erro') and pg.query_selector('.confirma') is None, 'Configuração recusa valor inválido e aponta o campo')
    pg.fill('#pw-metro', '200,00'); pg.fill('#pw-realocacao', '5.000,50'); pg.fill('#pc-4-4', '100'); cfg_salvar(); txt = pg.inner_text('.confirma'); chk('Salvar Alterações?' in txt and '3 valores' in txt and 'Sim' in txt and 'Não' in txt and st(pg)['precos']['wecom']['metro'] == 164.18, 'salvar pede Sim ou Não e ainda não grava')
    clk(pg, '.confirma [data-acao=fechar-modal]'); pg.wait_for_timeout(200); chk(pg.query_selector('.confirma') is None and pg.input_value('#pw-metro') == '200,00' and st(pg)['precos']['wecom']['metro'] == 164.18, 'Não volta ao modal com o que foi digitado')
    altura_conf = "document.querySelector('.confirma').getBoundingClientRect().height"
    cfg_salvar(); alt_conf = pg.evaluate(altura_conf); clk(pg, '.confirma [data-acao=confirmar]'); pg.wait_for_timeout(250); s = st(pg); chk(pg.evaluate(altura_conf) == alt_conf, 'Salvar Alterações e Valores Atualizados têm o mesmo tamanho'); chk(s['precos']['wecom']['realocacao'] == 5000.5 and s['precos']['cds']['Mudança de Local'][4] == 100 and 'Valores Atualizados' in pg.inner_text('.confirma') and len(pg.query_selector_all('.confirma .conf-btns button')) == 1, 'Sim salva e mostra Valores Atualizados, só com Fechar')
    clk(pg, '.confirma [data-acao=fechar-modal]'); pg.wait_for_timeout(200); chk(pg.query_selector('.confirma') is None and pg.query_selector('.config') is not None and pg.input_value('#pw-metro') == '200,00' and pg.is_disabled('#cfg-salvar'), 'Fechar volta à tela de valores, já com os novos'); clk(pg, '.modal-footer [data-acao=cfg-fechar]'); pg.wait_for_timeout(200)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=config]'); pg.fill('#pc-0-0', '300'); clk(pg, '.modal-footer [data-acao=cfg-fechar]'); pg.wait_for_timeout(200); chk('Descartar' in pg.inner_text('.confirma') and pg.query_selector('.config') is not None, 'fechar com alterações pede confirmação')
    clk(pg, '.confirma [data-acao=confirmar]'); pg.wait_for_timeout(200); chk(pg.query_selector('.config') is None and st(pg)['precos']['cds']['Instalação'][0] == 285, 'descartar não altera os valores')
    abre_relatorio(); chk(pg.input_value('#rl-custo') == 'R$ 21.951,66' and 'R$3.000,00' in pg.input_value('#rl-notas') and 'R$200,00' in pg.input_value('#rl-notas'), 'relatório e frase da verba usam os valores configurados'); fecha_relatorio()
    # só a demanda Acionada conta os dias
    for sit_, inicio_ in (('nova', em_dias(5)), ('atendimento', em_dias(-1)), ('pendente', em_dias(-5))):
        muda(pg, 22, f"d.situacao='{sit_}'; d.responsavel='admin'; d.inicio='{inicio_}'; d.fim=null; d.ticketPrincipal='199996'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000022'); pg.wait_for_timeout(300); chk(pg.query_selector('.c-ag .prazo') is None, f'sem contagem de dias em {sit_}'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # no card: a aba Tickets conta só os subtickets e a base dos blocos fica alinhada
    subs_aba = [{'empresa': 'CDS', 'numero': '189401', 'finalidade': 'Instalação', 'quantidade': 1}, {'empresa': 'CADI', 'numero': '189402', 'finalidade': 'Configuração', 'quantidade': 1}]
    muda(pg, 23, f"d.situacao='nova'; d.responsavel='tecnico1'; d.inicio='{em_dias(5)}'; d.fim=null; d.ticketPrincipal='199997'; d.subtickets={json.dumps(subs_aba)}"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000023'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    chk(pg.inner_text('#aba-tickets .qtd') == '2', 'aba Tickets não conta o ticket principal')
    base_bloco = "(() => { const c = document.querySelector('.det-corpo'); const b = [...c.querySelectorAll('.bloco')].pop(); return Math.round(c.getBoundingClientRect().bottom - b.getBoundingClientRect().bottom); })()"
    bases = []
    for aba_ in ('dados', 'tickets', 'hist'): clk(pg, f'[data-acao=aba][data-v={aba_}]'); pg.wait_for_timeout(150); bases.append(pg.evaluate(base_bloco))
    chk(len(set(bases)) == 1, f'base dos blocos alinhada nas três abas {bases}'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # período em vários dias, frase removida e lista de locais
    muda(pg, 900, "d.inicio='2099-11-12'; d.fim='2099-11-13'; d.hora='09:00'")
    clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000900'); pg.wait_for_timeout(300)
    chk('12/11/2099 até 13/11/2099' in pg.inner_text('.linha-dem'), 'lista mostra o período por extenso')
    clk(pg, '[data-acao=abrir]'); chk('12/11/2099 às 09:00 até 13/11/2099' in pg.inner_text('.det-l2'), 'card mostra o período com a hora do início')
    chk('Avança sozinha' not in pg.inner_text('.det-cab'), 'frase Avança sozinha pela data removida')
    pg.focus('#f-local'); pg.wait_for_timeout(150); ops = [o.inner_text() for o in pg.query_selector_all('#f-local-lista .combo-op')]
    chk(pg.input_value('#f-local') == 'Guaíba' and 'Agudo' in ops and not any('Foro da Comarca' in o for o in ops), 'lista de locais só com o nome da comarca')
    prevenido = pg.evaluate("(()=>{const e=new MouseEvent('mousedown',{bubbles:true,cancelable:true}); document.getElementById('f-local-lista').dispatchEvent(e); return e.defaultPrevented})()"); pg.wait_for_timeout(200)
    chk(prevenido and pg.evaluate("document.activeElement.id") == 'f-local' and pg.is_visible('#f-local-lista'), 'apertar a barra de rolagem não fecha a lista de locais')
    pg.keyboard.press('Escape'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # modais de tamanho único, com rolagem interna
    def altura(sel): return pg.evaluate(f"document.querySelector({sel!r}).getBoundingClientRect().height")
    def rola(sel): return pg.evaluate(f"(()=>{{const e=document.querySelector({sel!r}); return e.scrollHeight > e.clientHeight + 1}})()")
    def ajusta(pessoas, abertas=0, lixo=0):
        pg.evaluate(f"""(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); o.equipe=Array.from({{length:{pessoas}}},(_,i)=>({{id:'p'+i,nome:'Pessoa '+i,curto:'P'+i,ini:'P'+(i%10),cor:'#3E7C8A',ativo:true}}));
          let n=0; o.demandas.forEach(d=>{{ if(['nova','acionada'].includes(d.situacao)) d.responsavel = n++ < {abertas} ? 'p0' : null; }});
          o.lixeira=Array.from({{length:{lixo}}},(_,i)=>({{id:7000+i,sei:'',comarca:'Canoas',situacao:'nova',subtickets:[],historico:[],excluidaEm:'{em_dias(0)}T08:00',excluidaPor:'admin',motivoExclusao:'x'}}));
          localStorage.setItem('{CH}', JSON.stringify(o));}})()"""); pg.reload(); pg.wait_for_timeout(350)
    alts = {}
    for n in (0, 1, 5, 6, 25):
        ajusta(n); clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); alts[n] = altura('.modal-content.equipe')
        if n == 5: chk(not rola('.equipe .tabela-bloco .bloco-corpo') and len(pg.query_selector_all('.eq-linha')) == 5, 'Equipe: 5 pessoas sem barra de rolagem')
        if n == 6: chk(rola('.equipe .tabela-bloco .bloco-corpo'), 'Equipe: 6 pessoas com rolagem dentro de Pessoas')
        if n == 25: chk(not rola('.equipe .modal-body'), 'Equipe: a rolagem fica só no campo Pessoas')
        clk(pg, '[data-acao=fechar-modal]')
    chk(len(set(alts.values())) == 1, f'Equipe: altura única {alts}')
    alts = {}
    for k in (1, 20):
        ajusta(6, abertas=k); clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); clk(pg, '[data-acao=eq-transferir][data-v=p0]'); alts[k] = altura('.modal-content.equipe'); chk(rola('.equipe .tabela-bloco .bloco-corpo') == (k == 20), f'Transferir: rolagem interna só com muitas demandas ({k})'); clk(pg, '[data-acao=eq-voltar]'); clk(pg, '[data-acao=fechar-modal]')
    chk(len(set(alts.values())) == 1, f'Transferir: altura única {alts}')
    alts = {}
    for n in (0, 4, 60):
        ajusta(n); clk(pg, '[data-acao=nova]'); alts[n] = altura('.modal-n')
        if n == 60: chk(rola('.modal-n .grade-resp') and not rola('.modal-n .modal-body'), 'Nova demanda: rolagem só no campo de responsáveis')
        clk(pg, '.modal-n [data-acao=fechar-modal]')
    chk(len(set(alts.values())) == 1, f'Nova demanda: altura única {alts}')
    alts = {}
    for n in (0, 1, 40):
        ajusta(0, lixo=n); clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=lixeira]'); alts[n] = altura('.modal-content.lixeira')
        if n == 40: chk(rola('.lixeira .modal-body'), 'Lixeira: muitas demandas rolam por dentro')
        clk(pg, '[data-acao=fechar-modal]')
    chk(len(set(alts.values())) == 1, f'Lixeira: altura única {alts}')
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=lixeira]'); chk(pg.inner_text('.lixeira .modal-header p') == 'Demandas excluídas podem ser restauradas em até 30 dias.', 'texto da Lixeira'); clk(pg, '[data-acao=fechar-modal]')
    # desativar não deixa demanda órfã: as desmarcadas vão para o Coordenador
    if st(pg)['usuario'] != 'admin':
        sai(pg) if st(pg)['usuario'] else None; clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]')
    for nome_ in ('Caio Teste', 'Dora Teste'): pg.fill('#eq-nome', nome_); pg.evaluate("document.querySelector('form[data-form=equipe-add]').requestSubmit()"); pg.wait_for_timeout(250)
    clk(pg, '[data-acao=fechar-modal]')
    muda(pg, 10, f"d.situacao='nova'; d.responsavel='caio-teste'"); muda(pg, 11, f"d.situacao='nova'; d.responsavel='caio-teste'")
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); clk(pg, '[data-acao=eq-desativar][data-v=caio-teste]')
    chk('vão para o Coordenador' in pg.inner_text('.equipe'), 'Desativar avisa que as desmarcadas vão para o Coordenador')
    pg.evaluate("document.querySelectorAll('input[name=tr-d]').forEach((c) => { c.checked = c.value === '10'; })"); dest = next(o.get_attribute('value') for o in pg.query_selector_all('#tr-dest option') if o.get_attribute('value') not in ('', 'admin')); pg.select_option('#tr-dest', dest); pg.evaluate("document.querySelector('form[data-form=equipe-transf]').requestSubmit()"); pg.wait_for_timeout(300)
    s = st(pg); caio = next(u for u in s['equipe'] if u['id'] == 'caio-teste')
    chk(not caio['ativo'] and dem(pg, 10)['responsavel'] == dest and dem(pg, 11)['responsavel'] == 'admin' and 'Caio' in dem(pg, 11)['historico'][-1]['texto'], 'Desativar: a marcada vai para quem foi escolhido e a desmarcada para o Coordenador'); clk(pg, '[data-acao=fechar-modal]')
    muda(pg, 12, "d.situacao='nova'; d.responsavel='caio-teste'"); chk(dem(pg, 12)['responsavel'] == 'admin', 'dado antigo: demanda em aberto com pessoa desativada passa ao Coordenador')
    # ticket e SEI repetidos em outra demanda: avisa, mas não bloqueia
    usado = next(x['numero'] for d in st(pg)['demandas'] for x in d['subtickets'] if d['id'] != 13)
    muda(pg, 13, f"d.situacao='nova'; d.responsavel='admin'; d.inicio='{em_dias(9)}'; d.subtickets=[]"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000013'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=aba][data-v=tickets]')
    pg.select_option('#n-emp', 'CDS'); pg.select_option('#n-fin', 'Instalação'); pg.fill('#n-num', usado); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250)
    chk(any(x['numero'] == usado for x in dem(pg, 13)['subtickets']) and f'o ticket {usado} também está em' in flash(pg), 'subticket já usado em outra demanda: inclui e avisa')
    pg.fill('#t-principal', usado); pg.evaluate("document.querySelector('form[data-form=principal]').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 13)['ticketPrincipal'] == usado and 'também está em' in flash(pg), 'ticket principal já usado em outra demanda: registra e avisa')
    clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    sei_rep = dem(pg, 14)['sei']; clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', sei_rep.replace('.', '').replace('/', '').replace('-', '')); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'SEI repetido'); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    chk(pg.query_selector('.sucesso') is not None and 'Este SEI também está em outra demanda' in pg.inner_text('.sucesso'), 'Nova demanda com SEI repetido: inclui e avisa'); clk(pg, '.sucesso [data-acao=fechar-modal]')
    # coerência de todas as demandas que sobraram depois do teste inteiro
    hoje = em_dias(0); incoer = []
    for d in st(pg)['demandas']:
        sit_, fim_ = d['situacao'], d.get('fim') or d.get('inicio')
        regras = [
            (sit_ != 'concluida' and not d.get('responsavel'), 'sem responsável'),
            (sit_ == 'concluida' and d.get('responsavel'), 'concluída com responsável'),
            (sit_ in ('acionada', 'atendimento', 'pendente', 'concluida') and not d.get('ticketPrincipal'), 'saiu de Nova sem ticket principal'),
            (sit_ in ('acionada', 'atendimento', 'pendente') and not d.get('inicio'), 'saiu de Nova sem Data de Início'),
            (sit_ == 'acionada' and d.get('inicio') and d['inicio'] <= hoje, 'Acionada com o início já alcançado'),
            (sit_ == 'atendimento' and d.get('inicio') and (d['inicio'] > hoje or fim_ < hoje), 'Em atendimento fora do período'),
            (sit_ == 'pendente' and fim_ and fim_ >= hoje, 'Para Validação com o período ainda aberto'),
            (sit_ == 'nova' and d.get('inicio') and d['inicio'] <= hoje and d.get('ticketPrincipal') and d.get('subtickets'), 'Nova com tickets no período sem avançar'),
            (d.get('acionadaEm') and d.get('inicio') and d['acionadaEm'] > d['inicio'], 'acionamento depois do início'),
            (sit_ in ('nova', 'acionada', 'atendimento', 'pendente') and d.get('responsavel') not in (None, 'admin') and not next((u for u in st(pg)['equipe'] if u['id'] == d['responsavel']), {}).get('ativo'), 'em aberto com responsável desativado'),
        ]
        incoer += [f"{d['id']} ({sit_}): {msg}" for cond, msg in regras if cond]
    chk(not incoer, 'todas as demandas coerentes com as regras' + (': ' + '; '.join(incoer) if incoer else ''))
    chk(not erros, 'nenhum erro de JavaScript' + (': ' + '; '.join(erros) if erros else ''))
    b.close()
print(f'\n{len(ok)} ok, {len(falhas)} falhas'); [print(' -', f) for f in falhas]
sys.exit(1 if falhas else 0)
