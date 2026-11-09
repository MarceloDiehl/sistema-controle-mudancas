# Teste de ponta a ponta do protótipo (Controle de Demandas de Mudanças).
# Uso:  pip install playwright  &&  python -m playwright install chromium
#       python testes/teste_ponta_a_ponta.py            (abre o index.html desta pasta)
#       python testes/teste_ponta_a_ponta.py <url>      (ou outro endereço, ex.: http://localhost:8080/)
# Passa pelos fluxos principais (abas, filtros, nova demanda, tickets, status ao salvar, automação por data,
# relatório PDF, devolução, conclusão, cancelamento, exclusão, movimentações, equipe) e confere o resultado no
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
    ls += [dict(base(30 + i, 'concluida', None, 'Ijuí'), tecnico='tecnico1', ticketPrincipal='1800000', acionadaEm='2026-01-02', subtickets=[{'empresa': 'CDS', 'numero': '1800001', 'finalidade': 'Mudança de Local', 'quantidade': 3}]) for i in range(3)]
    ls.append(dict(base(900, 'acionada', 'tecnico1', 'Guaíba'), ticketPrincipal='1900000', inicio='2099-01-10', acionadaEm='2026-01-02'))
    ls.append(dict(base(901, 'cancelada', 'tecnico1', 'Ijuí')))
    equipe = [{'id': i, 'nome': i.capitalize(), 'curto': i.capitalize(), 'ini': i[:2].upper(), 'cor': '#3E7C8A', 'ativo': True} for i in tecs]
    ls.append(dict(base(902, 'nova', 'tecnico1', 'Torres'), inicio='2026-01-05', descricao='Data vencida'))
    return {'demandas': ls, 'excluidas': [], 'equipe': equipe}
def chk(cond, nome): (ok if cond else falhas).append(nome); print(('OK   ' if cond else 'FALHA ') + nome)
def st(pg): return pg.evaluate(f"JSON.parse(localStorage.getItem('{CH}'))")
def dem(pg, i): return next(d for d in st(pg)['demandas'] if d['id'] == i)
def clk(pg, sel, n=0): pg.evaluate(f"(()=>{{const e=document.querySelectorAll({sel!r})[{n}]; if(!e) throw new Error('nao achei '+{sel!r}); e.click();}})()"); pg.wait_for_timeout(180)
def flash(pg): e = pg.query_selector('.flash'); return e.inner_text() if e else ''
def opcoes(pg): return [o.get_attribute('value') for o in pg.query_selector_all('#d-status option')]
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True); pg = ctx.new_page()
    erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(URL); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(500)
    chk(len(pg.query_selector_all('.linha-dem')) == 0 and pg.query_selector('.vazio-lista') is not None, 'sistema começa sem nenhuma demanda')
    clk(pg, '[data-acao=resp-pop]'); chk(len(pg.query_selector_all('.op-resp')) == 2, 'sistema novo sem técnicos: só Gestor e Sem responsável'); clk(pg, '[data-acao=resp-pop]')
    chk(pg.inner_text('h1') == 'Filtro de Demanda', 'título Filtro de Demanda')
    for vista in ('linhas', 'postits'):
        clk(pg, f'[data-acao=vista][data-v={vista}]'); dif = pg.evaluate("(()=>{const a=document.querySelector('.rolagem').getBoundingClientRect();const c=document.querySelector('.vazio-lista');const r=document.createRange();r.selectNodeContents(c);const b=r.getBoundingClientRect();return Math.abs((a.top+a.height/2)-(b.top+b.height/2))})()"); chk(dif < 3, 'lista vazia centralizada em ' + vista)
    clk(pg, '[data-acao=vista][data-v=linhas]')
    clk(pg, '[data-acao=sobre]'); ver = pg.inner_text('.sobre-ver'); chk(ver == 'Versão do Sistema: 1.0.0 · Novembro/2026', 'créditos na versão 1.0.0, sem protótipo e sem parênteses'); clk(pg, '[data-acao=fechar-modal]')
    pg.evaluate("([c, v]) => localStorage.setItem(c, v)", [CH, json.dumps(massa())]); pg.reload(); pg.wait_for_timeout(500)
    chk(len(pg.query_selector_all('.linha-dem')) == 10, 'folha com 10 linhas')
    chk(not pg.query_selector('[data-acao=nova]'), 'sem login não há Nova demanda')
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
    chk(conta('_sem') == 0, 'concluídas (com o setor) não contam como Sem responsável')
    clk(pg, '[data-acao=resp-pop]'); pg.fill('#busca', ''); pg.wait_for_timeout(300); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    clk(pg, '[data-acao=resp-pop]'); clk(pg, '[data-acao=resp-escolher][data-v=tecnico2]'); chk(all('Tecnico2' in c.inner_text() for c in pg.query_selector_all('.linha-dem')), 'filtro de responsável'); clk(pg, '.filtro-limpa')
    # técnico sem login: não cancela
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
    # login gestor
    clk(pg, '[data-acao=login]'); chk(pg.query_selector('form.login') is not None, 'modal de login abre'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300)
    chk(pg.query_selector('form[data-form=senha]') is not None and not st(pg)['usuario'], 'primeiro acesso exige criar senha antes de entrar')
    pg.mouse.click(5, 5); pg.keyboard.press('Escape'); pg.wait_for_timeout(150); chk(pg.query_selector('form[data-form=senha]') is not None, 'troca de senha não fecha por clique fora nem Esc')
    pg.fill('#s-nova', 'curta'); pg.fill('#s-conf', 'curta'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(200); chk('8 caracteres' in pg.inner_text('.erro'), 'senha curta é recusada')
    pg.fill('#s-nova', 'senhaNova123'); pg.fill('#s-conf', 'outraSenha123'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(200); chk('não são iguais' in pg.inner_text('.erro'), 'confirmação diferente é recusada')
    pg.fill('#s-nova', 'senhaNova123'); pg.fill('#s-conf', 'senhaNova123'); pg.evaluate("document.querySelector('form[data-form=senha]').requestSubmit()"); pg.wait_for_timeout(300)
    chk(st(pg)['usuario'] == 'admin' and st(pg)['senhaDefinida'] and 'senhaNova123' not in json.dumps(st(pg)) and pg.query_selector('[data-acao=nova]') is not None, 'gestor define a senha, entra e vê Nova demanda')
    clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'gestor: Acionada sem select de status (cancelar só em Mais ações)'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=nova]'); clk(pg, '[data-acao=abrir]'); chk(opcoes(pg) == ['nova', 'acionada'], 'select de status sem Cancelada, Em atendimento e Para validação')
    pg.mouse.click(5, 5); pg.wait_for_timeout(150); chk(pg.query_selector('.det') is not None, 'clique fora não fecha o card'); pg.keyboard.press('Escape'); pg.wait_for_timeout(150); chk(pg.query_selector('.det') is not None, 'Esc não fecha o card')
    t0 = topo(pg); clk(pg, '[data-acao=aba][data-v=tickets]'); t1 = topo(pg); clk(pg, '[data-acao=aba][data-v=hist]'); t2 = topo(pg); chk(t0 == t1 == t2, f'cabeçalho não se move ao trocar de aba {t0} {t1}'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'gestor: Concluída é final, sem select de status')
    # demanda Concluída: somente consulta; só registra andamento e não pode ser excluída
    conc = int(pg.get_attribute('.linha-dem', 'data-id')); chk(pg.is_disabled('#f-desc') and pg.is_disabled('#f-ini') and pg.query_selector('#btn-salvar') is None, 'encerrada: Detalhes somente leitura, sem Salvar')
    clk(pg, '[data-acao=aba][data-v=tickets]'); chk(not pg.query_selector('form[data-form=principal]') and not pg.query_selector('form[data-form=sub]') and not pg.query_selector('[data-acao=tk-alterar]') and not pg.query_selector('[data-acao=sub-del]') and pg.is_disabled('#sq-0') and pg.is_disabled('#sf-0'), 'encerrada: Tickets somente leitura')
    pg.evaluate("(()=>{const e=document.getElementById('sq-0'); e.disabled=false; e.value='99'; e.dispatchEvent(new Event('change',{bubbles:true}));})()"); pg.wait_for_timeout(200); chk(dem(pg, conc)['subtickets'][0]['quantidade'] == 3, 'encerrada: alteração forçada é recusada')
    clk(pg, '[data-acao=aba][data-v=hist]'); pg.fill('#h-nota', 'Anotação depois de concluir'); pg.evaluate("document.querySelector('form[data-form=nota]').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, conc)['historico'][-1]['texto'] == 'Anotação depois de concluir', 'encerrada: ainda registra andamento no histórico')
    clk(pg, '[data-acao=menu-mais]'); chk(not pg.query_selector('[data-acao=excluir]') and not pg.query_selector('[data-acao=cancelar]'), 'Concluída: gestor não pode excluir nem cancelar'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=fechar-det]')
    clk(pg, '[data-acao=sit-aba][data-v=cancelada]'); clk(pg, '[data-acao=abrir]'); chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'gestor: Cancelada é final, sem select de status'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    # nova demanda
    clk(pg, '[data-acao=nova]'); pg.mouse.click(5, 5); pg.wait_for_timeout(150); chk(pg.query_selector('form[data-form=nova]') is not None, 'clique fora não fecha a Nova demanda')
    rots = [e.inner_text() for e in pg.query_selector_all('.grade-ini .campo > label')][1:]; chk(rots == ['Data de Início', 'Data para Conclusão', 'Hora'], f'campos de data e hora na ordem pedida {rots}')
    pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(200)
    chk(len(pg.query_selector_all('.modal .erro')) >= 2, 'nova demanda valida campos obrigatórios')
    pg.fill('#n-sei', '8202697450000999'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Teste de ponta a ponta')
    clk(pg, '[data-acao=cal-abrir]'); chk(pg.query_selector('#cal-pop') is not None, 'calendário abre'); clk(pg, '[data-acao=cal-hoje]')
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
    pg.fill('#n-num', '1899100'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(200); chk('Escolha a empresa' in pg.inner_text('.add-sub ~ .erro') and not dem(pg, nid)['subtickets'], 'empresa é obrigatória'); pg.fill('#n-num', '')
    pg.fill('#t-principal', '1899001'); pg.evaluate("document.querySelector('form[data-form=principal]').requestSubmit()"); pg.wait_for_timeout(250)
    chk(dem(pg, nid)['ticketPrincipal'] == '1899001', 'ticket principal registrado')
    pg.select_option('#n-emp', 'CDS'); pg.fill('#n-num', '1899101 / 1899102'); pg.select_option('#n-fin', 'Mudança de Local'); pg.fill('#n-qtd', '7')
    pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250)
    subs = dem(pg, nid)['subtickets']; chk(len(subs) == 2 and subs[0]['quantidade'] == 7 and subs[0]['empresa'] == 'CDS', 'dois subtickets CDS com quantidade 7')
    pg.select_option('#n-emp', 'WECOM'); serv_wecom = [o.inner_text() for o in pg.query_selector_all('#n-fin option')]; pg.select_option('#n-emp', 'CADI'); serv_cadi = [o.inner_text() for o in pg.query_selector_all('#n-fin option')]
    chk('Instalação de Infraestrutura' in serv_wecom and 'Habilitação de Pontos de Rede' in serv_cadi, 'serviços novos da WECOM e da CADI')
    pg.fill('#n-num', '1899103'); pg.select_option('#n-fin', 'Habilitação de Pontos de Rede'); pg.fill('#n-qtd', '2'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250)
    # status acionada
    chk(dem(pg, nid)['situacao'] == 'nova', 'registrar ticket não salva o status escolhido')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.fill('#f-ini', br(em_dias(2))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, nid); chk(x['situacao'] == 'acionada' and x['acionadaEm'] and not any('SLA' in h['texto'] for h in x['historico']), 'acionar grava a data do acionamento, sem registro de SLA')
    chk(x['aviso'] and x['aviso']['tipo'] == 'status' and x['aviso']['para'] == 'tecnico1', 'mudar o status acende a bolinha para o responsável')
    clk(pg, '[data-acao=fechar-det]'); chk(dem(pg, nid)['aviso'] is not None, 'bolinha continua depois de fechar o card em que o status mudou')
    pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); chk(dem(pg, nid)['aviso'] is None, 'bolinha some assim que o card é aberto'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    s90 = {'empresa': 'CADI', 'numero': '1999999', 'finalidade': 'Configuração', 'quantidade': 1}
    muda(pg, 900, f"d.subtickets=[{json.dumps(s90)}]; d.situacao='nova'; d.acionadaEm=null; d.inicio='{em_dias(1)}'")
    pg.fill('#busca', '000900'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); chk(dem(pg, 900)['situacao'] == 'acionada', 'acionar na véspera é aceito'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # demanda para o mesmo dia: aciona, vai para o gestor e entra Em atendimento
    s_cds = {'empresa': 'CDS', 'numero': '1999998', 'finalidade': 'Instalação', 'quantidade': 1}
    muda(pg, 1, f"d.subtickets=[{json.dumps(s_cds)}]; d.ticketPrincipal='1999990'; d.inicio='{em_dias(0)}'"); tec1 = dem(pg, 1)['responsavel']
    pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); x = dem(pg, 1)
    chk(x['situacao'] == 'atendimento' and x['responsavel'] == 'admin' and x['tecnico'] == tec1 and x['acionadaEm'], 'mesmo dia: acionar não trava, vai para o gestor e entra Em atendimento')
    chk(not any('SLA' in h['texto'] for h in x['historico']) and 'SLA' not in flash(pg), 'mesmo dia: sem aviso nem registro de SLA'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    muda(pg, 2, f"d.subtickets=[{json.dumps(s_cds)}]; d.ticketPrincipal='1999991'; d.inicio='{em_dias(1)}'")
    pg.fill('#busca', '000002'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar'); x = dem(pg, 2); chk(x['situacao'] == 'acionada' and not any('SLA' in h['texto'] for h in x['historico']), 'acionar na véspera com subticket não registra SLA'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # chega o dia: Em atendimento, dados travados
    muda(pg, nid, f"d.inicio='{em_dias(0)}'"); x = dem(pg, nid); chk(x['situacao'] == 'atendimento' and x['responsavel'] == 'admin', 'na data, entra Em atendimento com o gestor')
    pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    chk(all(pg.is_disabled(s) for s in ('#f-sei', '#f-local', '#f-desc', '#f-ini', '#f-hora', '#f-fim')) and pg.is_enabled('#f-resp') and pg.is_enabled('#f-info') and pg.query_selector('#d-status') is None, 'Em atendimento: dados travados; responsável e informações liberados')
    pg.select_option('#f-resp', 'tecnico1'); pg.fill('#f-info', 'Acompanhar atendimento'); sair_do_campo(pg); clk(pg, '#btn-salvar'); x = dem(pg, nid); chk(x['responsavel'] == 'tecnico1' and x['informacoes'] == 'Acompanhar atendimento' and x['aviso'] and x['aviso']['para'] == 'tecnico1', 'Em atendimento: muda responsável (com bolinha) e informações')
    clk(pg, '[data-acao=aba][data-v=tickets]'); chk(pg.query_selector('form[data-form=sub]') is not None and not pg.query_selector('[data-acao=sub-del]') and not pg.query_selector('[data-acao=tk-alterar]') and pg.is_disabled('#sq-0') and pg.is_disabled('#sf-0'), 'Em atendimento: inclui ticket novo, mas os registrados ficam travados')
    pg.select_option('#n-emp', 'Selbetti'); pg.fill('#n-num', '1899104'); pg.select_option('#n-fin', 'Instalação'); pg.evaluate("document.querySelector('form[data-form=sub]').requestSubmit()"); pg.wait_for_timeout(250); chk(any(s['numero'] == '1899104' for s in dem(pg, nid)['subtickets']), 'Em atendimento: subticket novo incluído')
    clk(pg, '[data-acao=aba][data-v=dados]')
    # acionamento
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=acionamento]'); txt = pg.input_value('#ac-texto')
    chk('CDS: 1899101 / 1899102' in txt and 'Era o que cumpria informar.' in txt, 'texto de acionamento com subtickets'); clk(pg, '[data-acao=fechar-modal]')
    # automação: data passada -> pendente com o gestor
    pg.evaluate(f"(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); const d=o.demandas.find(x=>x.id==={nid}); d.inicio='2026-01-10'; d.fim=null; localStorage.setItem('{CH}', JSON.stringify(o));}})()")
    pg.reload(); pg.wait_for_timeout(500); x = dem(pg, nid)
    chk(x['situacao'] == 'pendente' and x['responsavel'] == 'admin' and x['tecnico'] == 'tecnico1', 'automático: data passada vira Pendente com o gestor')
    chk(any('automaticamente' in h['texto'] and h['usuario'] == 'sistema' for h in x['historico']), 'histórico registra mudança automática')
    # abre a pendente
    clk(pg, '[data-acao=sit-aba][data-v=pendente]'); pg.fill('#busca', '000099'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    chk(pg.query_selector('#d-status') is None and pg.query_selector('.st-fixo') is not None, 'Pendente: status travado')
    # relatório
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]'); itens = pg.input_value('#rl-itens')
    chk('em total de 7 serviços' in itens and 'contratada CDS através do ticket 1899101' in itens, 'relatório: item com quantidade e ticket')
    chk('Habilitação de pontos de rede, em total de 2 serviços' in itens, 'relatório: serviço de rede sem "de equipamentos de informática"')
    chk('não entra' in pg.inner_text('.relat'), 'relatório: com CDS a frase do contrato não entra')
    with pg.expect_download() as dl: clk(pg, '[data-acao=baixar-relatorio]')
    f = dl.value; caminho = f.path(); head = open(caminho, 'rb').read(5)
    chk(head == b'%PDF-' and f.suggested_filename.startswith('Relatório de execução'), 'PDF baixado (' + f.suggested_filename + ')')
    clk(pg, '[data-acao=fechar-modal]')
    # devolve ao técnico e volta
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=devolver-tec]'); x = dem(pg, nid)
    chk(x['situacao'] == 'pendente' and x['responsavel'] == 'tecnico1' and x['aviso']['tipo'] == 'retornou', 'devolvida ao técnico, ainda Pendente, com bolinha')
    clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=sair]')
    clk(pg, '[data-acao=abrir]'); chk(dem(pg, nid)['aviso'] is None, 'bolinha some quando o técnico abre')
    clk(pg, '[data-acao=devolver-gestor]'); x = dem(pg, nid)
    chk(x['responsavel'] == 'admin' and x['historico'][-2]['usuario'] == 'tecnico1', 'técnico devolve ao gestor (autor no histórico)')
    clk(pg, '[data-acao=fechar-det]')
    # conclui
    clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300)
    chk(pg.query_selector('form[data-form=senha]') is None, 'segundo acesso não pede nova senha')
    clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=concluir-dem]'); clk(pg, '.confirma [data-acao=confirmar]'); x = dem(pg, nid)
    chk(x['situacao'] == 'concluida' and x['responsavel'] is None, 'concluída: fica com o setor, sem atribuição')
    # cancelar e excluir outra
    pg.fill('#busca', ''); clk(pg, '[data-acao=sit-aba][data-v=nova]'); outra = int(pg.get_attribute('.linha-dem', 'data-id')); clk(pg, '[data-acao=abrir]')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=cancelar]')
    txt = pg.inner_text('#mc-txt'); chk(txt == 'A ação não poderá ser desfeita.', 'texto do modal de cancelamento'); chk(pg.get_attribute('#mc-motivo', 'maxlength') == '100', 'motivo do cancelamento com até 100 caracteres')
    clk(pg, '.confirma [data-acao=confirmar]'); chk(dem(pg, outra)['situacao'] == 'nova' and pg.query_selector('.confirma .erro') is not None, 'cancelar sem motivo é recusado')
    motivo(pg, 'Setor desistiu da mudança'); x = dem(pg, outra); chk(x['situacao'] == 'cancelada' and x['motivoCancelamento'] == 'Setor desistiu da mudança' and 'Setor desistiu da mudança' in x['historico'][-1]['texto'], 'gestor cancela demanda com motivo no histórico')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=excluir]'); clk(pg, '.confirma [data-acao=confirmar]'); chk(any(d['id'] == outra for d in st(pg)['demandas']), 'excluir sem motivo é recusado')
    motivo(pg, 'Cadastro duplicado'); s = st(pg); chk(not any(d['id'] == outra for d in s['demandas']) and s['excluidas'][-1]['id'] == outra and s['lixeira'][-1]['id'] == outra and s['lixeira'][-1]['motivoExclusao'] == 'Cadastro duplicado', 'excluir leva para a lixeira, com motivo')
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=lixeira]'); chk('Cadastro duplicado' in pg.inner_text('.lixeira') and 'restam 30 dias' in pg.inner_text('.lixeira'), 'lixeira mostra motivo e prazo')
    clk(pg, '[data-acao=restaurar]'); s = st(pg); chk(any(d['id'] == outra for d in s['demandas']) and not s['lixeira'] and dem(pg, outra)['situacao'] == 'cancelada', 'restaurar devolve a demanda como estava'); clk(pg, '[data-acao=fechar-modal]')
    # 30 dias na lixeira: some sem retorno
    pg.evaluate(f"(()=>{{const o=JSON.parse(localStorage.getItem('{CH}')); const i=o.demandas.findIndex(x=>x.id==={outra}); const d=o.demandas.splice(i,1)[0]; d.excluidaEm='{em_dias(-30)}T08:00'; d.excluidaPor='admin'; d.motivoExclusao='x'; o.lixeira.push(d); localStorage.setItem('{CH}', JSON.stringify(o));}})()"); pg.reload(); pg.wait_for_timeout(400)
    s = st(pg); chk(not s['lixeira'] and not any(d['id'] == outra for d in s['demandas']) and 'removida' in s['excluidas'][-1]['texto'], 'depois de 30 dias a lixeira remove a demanda')
    # movimentações
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=movimentos]'); chk('excluída' in pg.inner_text('.movs') and 'Cadastro duplicado' in pg.inner_text('.movs') and len(pg.query_selector_all('.mv-item')) > 3, 'movimentações do dia listam as mudanças e a exclusão')
    clk(pg, '[data-acao=mov-filtro][data-v=status]'); chk(all('Status' in i.inner_text() or 'registrada' in i.inner_text() or 'excluída' in i.inner_text() or 'restaurada' in i.inner_text() or 'removida' in i.inner_text() for i in pg.query_selector_all('.mv-item')), 'filtro Só status')
    clk(pg, '[data-acao=fechar-modal]')
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
    # datas anteriores a hoje
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000052'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Data passada'); pg.fill('#n-ini', br(em_dias(-1))); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(250)
    chk('anterior a hoje' in pg.inner_text('.modal-n') and pg.query_selector('.sucesso') is None, 'Nova demanda recusa Data de Início anterior a hoje'); clk(pg, '.modal-n [data-acao=fechar-modal]')
    pg.fill('#busca', '000005'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); ini5 = dem(pg, 5)['inicio']; pg.fill('#f-desc', 'Editada com data vencida'); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, 5); chk(x['descricao'] == 'Editada com data vencida' and x['inicio'] == ini5, 'Nova com data vencida ainda salva outros campos')
    pg.fill('#f-ini', br(em_dias(-1))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 5)['inicio'] == ini5 and 'anteriores a hoje' in pg.inner_text('.det .erro'), 'Nova recusa mudar a data para o passado'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '.confirma [data-acao=confirmar]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # sem data e com SEI repetido
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000051'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Sem nenhuma data'); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    novo = dem(pg, max(d['id'] for d in st(pg)['demandas'])); chk(pg.query_selector('.sucesso') is not None and novo['inicio'] is None and novo['sei'] == '8.2026.9745/000005-1' and sum(1 for d in st(pg)['demandas'] if d['sei'] == novo['sei']) == 2, 'cria demanda sem data e com SEI repetido'); clk(pg, '.sucesso [data-acao=fechar-modal]')
    # alterar a Data para Conclusão em Em atendimento (só o gestor, com motivo)
    pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); chk(pg.is_disabled('#f-fim'), 'Em atendimento: campo da data segue travado')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=alterar-conclusao]')
    envia = lambda: (pg.evaluate("document.querySelector('form[data-form=conclusao]').requestSubmit()"), pg.wait_for_timeout(220))
    fim0 = dem(pg, 1).get('fim'); pg.fill('#pr-fim', br(em_dias(-1))); pg.fill('#pr-motivo', 'x'); envia(); chk(dem(pg, 1).get('fim') == fim0 and 'passado' in pg.inner_text('.confirma .erro') or 'antes da data de início' in pg.inner_text('.confirma .erro'), 'alterar conclusão: recusa data passada')
    pg.fill('#pr-fim', br(em_dias(5))); pg.fill('#pr-motivo', ''); envia(); chk(dem(pg, 1).get('fim') == fim0 and 'motivo' in pg.inner_text('.confirma .erro'), 'alterar conclusão: exige motivo')
    pg.fill('#pr-motivo', 'Empresa pediu mais prazo'); envia(); x = dem(pg, 1); chk(x['fim'] == em_dias(5) and x['situacao'] == 'atendimento' and 'Empresa pediu mais prazo' in x['historico'][-1]['texto'] and pg.input_value('#f-fim') == br(em_dias(5)), 'alterar conclusão: grava a data e o motivo no histórico')
    clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=sair]'); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=alterar-conclusao]') is None, 'alterar conclusão: técnico não tem a opção'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=proto-gestor]'); pg.wait_for_timeout(300); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # acionar exige data; demanda acionada não perde a data nem vai para o passado
    muda(pg, 3, "d.inicio=null; d.fim=null; d.ticketPrincipal='1999992'; d.situacao='nova'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000003'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar')
    chk(dem(pg, 3)['situacao'] == 'nova' and 'Data de Início' in flash(pg) and pg.input_value('#d-status') == 'acionada', 'acionar sem data é recusado e mantém a escolha'); pg.select_option('#d-status', 'nova'); pg.wait_for_timeout(150); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    muda(pg, 900, f"d.situacao='acionada'; d.inicio='{em_dias(10)}'; d.fim=null"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]')
    pg.fill('#f-ini', br(em_dias(-5))); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, 900); chk(x['situacao'] == 'acionada' and x['inicio'] == em_dias(10) and 'passado' in pg.inner_text('.det .erro'), 'demanda acionada recusa data no passado')
    pg.fill('#f-ini', ''); sair_do_campo(pg); pg.evaluate("document.getElementById('form-dados').requestSubmit()"); pg.wait_for_timeout(250); chk(dem(pg, 900)['inicio'] == em_dias(10) and 'precisa ter' in pg.inner_text('.det .erro'), 'demanda acionada não pode perder a data'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '.confirma [data-acao=confirmar]')
    # contagem de dias até o início
    for n, txt in ((2, '02 dias'), (1, '01 dia'), (120, '120 dias'), (2000, '999 dias')):
        muda(pg, 900, f"d.inicio='{em_dias(n)}'"); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); chk(txt == pg.inner_text('.c-ag .prazo'), f'contagem até o início: {txt}')
    muda(pg, 900, f"d.inicio='{em_dias(2)}'; d.fim='{em_dias(4)}'"); pg.fill('#busca', '000900'); pg.wait_for_timeout(300); chk(pg.inner_text('.c-ag .prazo') == '02 dias' and pg.query_selector('.pi-data') is None, 'contagem também em período de vários dias'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Em atendimento e Para validação nunca sem responsável
    muda(pg, 1, "d.responsavel='ana-teste'"); pg.fill('#busca', '000001'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); chk('' not in [o.get_attribute('value') for o in pg.query_selector_all('#f-resp option')] and 'Sem responsável' not in pg.inner_text('#f-resp'), 'Em atendimento: sem a opção Sem responsável'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]'); clk(pg, '[data-acao=eq-transferir][data-v=ana-teste]'); chk('vão para o Gestor' in pg.inner_text('.equipe'), 'Transferir avisa sobre Em Atendimento e Para Validação'); pg.select_option('#tr-dest', '_sem'); pg.evaluate("document.querySelector('form[data-form=equipe-transf]').requestSubmit()"); pg.wait_for_timeout(250); x = dem(pg, 1); chk(x['responsavel'] == 'admin' and x['tecnico'] == 'ana-teste', 'Transferir para ninguém: Em atendimento vai para o gestor'); clk(pg, '[data-acao=fechar-modal]')
    # movimentações incluem a lixeira, sem repetir a exclusão
    hoje = em_dias(0); muda(pg, 6, f"d.situacao='nova'; d.historico.push({{data:'{hoje}T09:00',usuario:'admin',texto:'Nota da lixeira'}})"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000006'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=excluir]'); motivo(pg, 'Apagar teste'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=movimentos]'); txt = pg.inner_text('.movs'); chk('Nota da lixeira' in txt and txt.count('Motivo: Apagar teste') == 1, 'movimentações mantêm anotações de demanda na lixeira e mostram a exclusão uma vez')
    # entrar direto em outra aba não muda o tamanho do modal
    clk(pg, '[data-acao=mov-abrir]'); pg.wait_for_timeout(200); t0 = topo(pg); clk(pg, '[data-acao=aba][data-v=dados]'); t1 = topo(pg); clk(pg, '[data-acao=aba][data-v=tickets]'); t2 = topo(pg); chk(t0 == t1 == t2, f'modal não muda ao entrar direto no Histórico {t0} {t1}'); clk(pg, '[data-acao=fechar-det]')
    # acionar exige responsável
    muda(pg, 3, f"d.situacao='nova'; d.responsavel=null; d.inicio='{em_dias(5)}'; d.fim=null; d.ticketPrincipal='1999992'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000003'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); pg.select_option('#d-status', 'acionada'); pg.wait_for_timeout(150); clk(pg, '#btn-salvar')
    chk(dem(pg, 3)['situacao'] == 'nova' and 'responsável' in flash(pg), 'acionar sem responsável é recusado')
    pg.select_option('#f-resp', 'tecnico1'); pg.wait_for_timeout(150); sair_do_campo(pg); clk(pg, '#btn-salvar'); x = dem(pg, 3); chk(x['situacao'] == 'acionada' and x['responsavel'] == 'tecnico1', 'escolhido o responsável, a demanda é acionada'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Nova já dentro do período não mostra "Hoje"
    muda(pg, 4, f"d.situacao='nova'; d.inicio='{em_dias(-3)}'; d.fim='{em_dias(5)}'"); pg.fill('#busca', '000004'); pg.wait_for_timeout(300); chk(pg.query_selector('.c-ag .prazo') is None and pg.query_selector('.nv-ponto.venc') is None, 'Nova já dentro do período: sem selo Hoje e sem sinal vermelho'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # relatório também em Concluída
    clk(pg, '[data-acao=sit-aba][data-v=concluida]'); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=relatorio]') is not None, 'Concluída: gestor ainda gera o relatório'); clk(pg, '[data-acao=relatorio]'); chk(pg.query_selector('#rl-itens') is not None, 'Concluída: relatório abre'); clk(pg, '[data-acao=fechar-modal]'); clk(pg, '[data-acao=fechar-det]'); clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    # relatório sem subticket e devolução ao último técnico
    muda(pg, 7, f"d.situacao='pendente'; d.responsavel='admin'; d.tecnico='tecnico1'; d.inicio='{em_dias(-3)}'; d.fim=null; d.subtickets=[]; d.ticketPrincipal='1999993'"); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); pg.fill('#busca', '000007'); pg.wait_for_timeout(300); clk(pg, '[data-acao=abrir]'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]')
    chk('não tem subtickets' in pg.inner_text('.relat .ac-aviso'), 'relatório sem subticket mostra aviso'); clk(pg, '[data-acao=fechar-modal]')
    pg.select_option('#f-resp', 'tecnico2'); pg.wait_for_timeout(150); sair_do_campo(pg); clk(pg, '#btn-salvar'); pg.select_option('#f-resp', 'admin'); pg.wait_for_timeout(150); sair_do_campo(pg); clk(pg, '#btn-salvar'); clk(pg, '[data-acao=menu-mais]')
    chk(dem(pg, 7)['tecnico'] == 'tecnico2' and 'Tecnico2' in pg.inner_text('[data-acao=devolver-tec]'), 'devolução aponta o último técnico que tratou da demanda'); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=fechar-det]'); pg.fill('#busca', ''); pg.wait_for_timeout(250)
    # Gestor como responsável na Nova Demanda
    clk(pg, '[data-acao=nova]'); pg.fill('#n-sei', '8202697450000071'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Para o gestor'); pg.evaluate("document.querySelector('input[name=n-resp][value=admin]').click()"); pg.evaluate("document.querySelector('form[data-form=nova]').requestSubmit()"); pg.wait_for_timeout(300)
    novo = dem(pg, max(d['id'] for d in st(pg)['demandas'])); chk(novo['responsavel'] == 'admin' and 'atribuída a Gestor' in pg.inner_text('.sucesso') and 'atribuída a Gestor' in novo['historico'][0]['texto'], 'Nova Demanda pode ser atribuída ao Gestor'); clk(pg, '.sucesso [data-acao=fechar-modal]')
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
    chk(not erros, 'nenhum erro de JavaScript' + (': ' + '; '.join(erros) if erros else ''))
    b.close()
print(f'\n{len(ok)} ok, {len(falhas)} falhas'); [print(' -', f) for f in falhas]
sys.exit(1 if falhas else 0)
