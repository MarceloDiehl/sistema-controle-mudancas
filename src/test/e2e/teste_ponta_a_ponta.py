# Teste de ponta a ponta do Controle de Demandas de Mudanças, com o servidor e o banco de verdade.
# Uso:  pip install playwright  &&  python -m playwright install chromium
#   1. Suba a aplicação com o banco de teste (H2 em memória, com os catálogos do script do banco):
#        mvnw.cmd test-compile spring-boot:test-run        (Linux/macOS: ./mvnw ...)
#   2. Em outro terminal:  python src/test/e2e/teste_ponta_a_ponta.py  [url]   (padrão: http://localhost:8088/)
# O servidor de teste começa vazio, só com o administrador "admin" (senha inicial "admin-inicial"). O teste cria as
# próprias pessoas e demandas pelas telas e confere o resultado na API. Para repetir, reinicie o servidor de teste.
import sys, datetime, re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8088/'
SENHA_ADMIN = 'Senha-do-Admin-1'
ok = []; falhas = []
HOJE = datetime.date.today()
def em_dias(n): return (HOJE + datetime.timedelta(days=n)).isoformat()
def br(iso): return '/'.join(reversed(iso.split('-')))
def chk(cond, nome): (ok if cond else falhas).append(nome); print(('OK   ' if cond else 'FALHA ') + nome)
def espera(pg, ms=250):
    pg.wait_for_timeout(ms)
    pg.wait_for_function("!document.body.classList.contains('ocupado')", timeout=10000)
    pg.wait_for_timeout(120)
def clk(pg, sel, n=0):
    pg.evaluate(f"(()=>{{const e=document.querySelectorAll({sel!r})[{n}]; if(!e) throw new Error('nao achei '+{sel!r}); e.click();}})()"); espera(pg)
def enviar(pg, form): pg.evaluate(f"document.querySelector({form!r}).requestSubmit()"); espera(pg, 400)
def texto(pg, sel): e = pg.query_selector(sel); return e.inner_text() if e else ''
def flash(pg): return texto(pg, '.flash')
# leitura direta na API, com a sessão do navegador
def api(pg, caminho): return pg.evaluate("async (c) => { const r = await fetch('api/' + c, { credentials: 'same-origin' }); return r.ok ? r.json() : { status: r.status }; }", caminho)
def dem(pg, i): return api(pg, f'mudancas/{i}')
def ids(pg): return [d['id'] for d in api(pg, 'mudancas')]
def entra(pg, usuario, senha):
    if pg.query_selector('form[data-form=login]') is None: clk(pg, '[data-acao=login]')
    pg.fill('#l-usr', usuario); pg.fill('#l-sen', senha); enviar(pg, 'form[data-form=login]')
def cria_senha(pg, nova, atual=None):
    if atual: pg.fill('#s-atual', atual)
    pg.fill('#s-nova', nova); pg.fill('#s-conf', nova); enviar(pg, 'form[data-form=senha]')
def sai(pg): clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=sair]')
def data(pg, campo, iso): pg.fill(campo, br(iso))
def nova_demanda(pg, sei, local, inicio, resp, fim=None, desc='Demanda de teste'):
    clk(pg, '[data-acao=nova]')
    pg.fill('#n-sei', sei); pg.fill('#n-local', local); pg.keyboard.press('Escape')
    if inicio: data(pg, '#n-ini', inicio)
    if fim: data(pg, '#n-fim', fim)
    pg.fill('#n-desc', desc)
    pg.check(f'input[name=n-resp][value="{resp}"]', force=True)
    enviar(pg, 'form[data-form=nova]')
    i = max(ids(pg)); return i
def abre(pg, i):
    pg.evaluate(f"document.querySelector('[data-acao=sit-aba][data-v=todas]').click()"); espera(pg)
    pg.fill('#busca', ''); espera(pg)
    for _ in range(20):
        e = pg.query_selector(f'[data-acao=abrir][data-id="{i}"]')
        if e: e.click(); espera(pg, 400); return
        nx = pg.query_selector('.folhas .page-item:not(.disabled) [aria-label="Próxima folha"]')
        if not nx: break
        nx.click(); espera(pg)
    raise Exception(f'demanda {i} não está na lista')
def fecha(pg): clk(pg, '[data-acao=fechar-det]')
def ticket(pg, n):
    clk(pg, '[data-acao=aba][data-v=tickets]'); pg.fill('#t-principal', n); enviar(pg, 'form[data-form=principal]')
def sub(pg, emp, nums, serv, qtd=1, metro=None):
    clk(pg, '[data-acao=aba][data-v=tickets]')
    pg.select_option('#n-emp', emp); pg.fill('#n-num', nums); pg.select_option('#n-fin', serv); pg.fill('#n-qtd', str(qtd))
    if metro: pg.fill('#n-metro', str(metro))
    enviar(pg, 'form[data-form=sub]')
def aciona(pg):
    clk(pg, '[data-acao=aba][data-v=dados]'); clk(pg, '[data-acao=status-escolher][data-v=acionada]')
    clk(pg, '#btn-salvar')
def pessoa(pg, login): return next(p for p in api(pg, 'pessoas') if p['login'] == login)
def inclui_pessoa(pg, nome, login):
    pg.fill('#eq-nome', nome); pg.fill('#eq-login', login); enviar(pg, 'form[data-form=equipe-add]')
    senha = texto(pg, '.senha-tmp').strip()
    chk(pg.query_selector('.senha-tmp [data-acao=copiar-senha]') is not None, 'a senha temporária tem o botão de copiar')
    clk(pg, '.confirma [data-acao=fechar-modal]'); return senha

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True); pg = ctx.new_page()
    erros = []; pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(URL); espera(pg, 600)

    # ------------------------------------------------------------------ entrada
    chk(pg.query_selector('form[data-form=login]') is None and pg.query_selector('.sit-abas') is not None, 'sem login, a tela abre na consulta, sem pedir para entrar')
    chk(pg.evaluate("fetch(document.querySelector('link[rel=icon]').href).then(r => r.ok && r.headers.get('content-type').includes('svg'))"), 'favicon carregado')
    chk(pg.query_selector('[data-acao=login]') is not None and pg.query_selector('[data-acao=nova]') is None, 'sem login: botão Entrar no topo e nenhuma Nova demanda')
    chk(api(pg, 'precos').get('status') == 401 and api(pg, 'lixeira').get('status') == 401, 'sem login, a API não entrega valores nem a lixeira')
    clk(pg, '[data-acao=login]'); chk(pg.query_selector('form[data-form=login]') is not None and pg.query_selector('.login .fechar-canto') is not None, 'Entrar abre a entrada, que fecha pelo X')
    chk('Entre com o usuário e senha cadastrados.' in texto(pg, '.login') and 'Cadastrar novo usuário' in texto(pg, '.login-ajuda') and 'Procure o administrador' not in texto(pg, '.login-ajuda'), 'entrada com os textos novos e a dica da senha escondida')
    clk(pg, '[data-acao=esqueci-senha]'); chk('Procure o administrador' in texto(pg, '.login-ajuda'), 'Esqueci minha senha mostra a orientação')
    chk('Acesso do protótipo' not in pg.content() and pg.query_selector('[data-acao=proto-gestor]') is None, 'sem o acesso de demonstração do protótipo')
    entra(pg, 'admin', 'errada'); chk('incorretos' in texto(pg, '.login .erro'), 'senha errada é recusada')
    entra(pg, 'admin', 'admin-inicial')
    if pg.query_selector('form[data-form=senha]') is None:   # o servidor já tinha sido usado: entra com a senha do teste
        entra(pg, 'admin', SENHA_ADMIN)
    else:
        chk(True, 'primeiro acesso do administrador exige criar a senha')
        pg.mouse.click(5, 5); pg.keyboard.press('Escape'); espera(pg); chk(pg.query_selector('form[data-form=senha]') is not None, 'a criação de senha não fecha por clique fora nem Esc')
        cria_senha(pg, 'curta'); chk('8 caracteres' in texto(pg, '.login .erro'), 'senha curta é recusada')
        cria_senha(pg, 'admin-inicial'); chk('diferente' in texto(pg, '.login .erro'), 'a nova senha precisa ser diferente da inicial')
        cria_senha(pg, SENHA_ADMIN)
    chk(pg.query_selector('.modal-camada') is None and pg.query_selector('[data-acao=nova]') is not None and 'Administrador' in texto(pg, '.topo'), 'administrador entra e vê a tela principal')
    clk(pg, '[data-acao=menu-conta]'); chk(all(pg.query_selector(f'[data-acao={a}]') for a in ('equipe', 'lixeira', 'config')), 'menu do administrador com Equipe, Lixeira e Configuração'); clk(pg, '[data-acao=menu-conta]')

    # ------------------------------------------------------------------ tela principal
    abas = [e.inner_text() for e in pg.query_selector_all('.sit-aba .aba-nome')]
    clk(pg, '[data-acao=sit-aba][data-v=nova]'); pg.wait_for_timeout(450)
    chk(pg.evaluate("(() => { const c = document.querySelector('.sit-cursor').getBoundingClientRect(); const a = document.querySelector('.sit-aba[aria-selected=true]').getBoundingClientRect(); return Math.abs(c.left - a.left) < 2 && Math.abs(c.width - a.width) < 2; })()"), 'a peça das abas desliza e para sobre a aba escolhida')
    clk(pg, '[data-acao=sit-aba][data-v=abertas]')
    chk(abas == ['Em aberto', 'Pendentes', 'Acionadas', 'Em Atendimento', 'Para Validação', 'Concluídas', 'Canceladas', 'Todas'], f'abas de situação {abas}')
    ordem = pg.evaluate("[...document.querySelectorAll('.filtros > *')].map(e => e.className.split(' ').find(c => ['campo-busca','filtro-local','filtro-resp','filtro-periodo','filtro-comigo','vistas'].includes(c)))")
    chk(ordem == ['campo-busca', 'filtro-local', 'filtro-resp', 'filtro-periodo', 'filtro-comigo', 'vistas'], f'abaixo das abas: pesquisa, Local, Responsável, Período, Minhas demandas e visualização {ordem}')
    alt = pg.evaluate("['#busca', '.filtro-local', '.filtro-resp', '.filtro-comigo', '.filtro-periodo', '.filtros .vistas'].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)]; })")
    chk(len(set(map(tuple, alt))) == 1, f'pesquisa, seletores e visualização na mesma linha e altura {alt}')
    chk(pg.evaluate("document.querySelector('.topo').getBoundingClientRect().height") < 60, 'navbar baixo')
    hs = pg.evaluate("['.sit-abas', '#busca', '.l-cab', '.l-pe'].map(s => Math.round(document.querySelector(s).getBoundingClientRect().height))")
    chk(len(set(hs)) == 1, f'abas, filtros, linha de ordenação e paginação com a mesma altura {hs}')
    cab = [e.inner_text().strip() for e in pg.query_selector_all('.l-cab .h-txt')]
    chk(cab == ['Expediente', 'Local', 'Data de Agendamento', 'Ticket', 'Status', 'Complexidade', 'Responsável'], f'cabeçalho da lista com Data de Agendamento e Complexidade {cab}')
    clk(pg, '[data-acao=sobre]'); chk(texto(pg, '.sobre-ver') == 'Versão do Sistema: 1.0.0 · Novembro/2026', 'informações do sistema'); clk(pg, '[data-acao=fechar-modal]')

    # ------------------------------------------------------------------ equipe e contas
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]')
    chk(pg.query_selector('#eq-perfil') is None and 'Coordenador' not in texto(pg, '.modal-content.equipe'), 'Equipe sem escolha de perfil e sem o nome Coordenador')
    chk(pg.get_attribute('#eq-nome', 'maxlength') == '30' and pg.get_attribute('#eq-login', 'maxlength') == '20', 'nome com até 30 letras e usuário com até 20')
    senha_ana = inclui_pessoa(pg, 'Ana Souza', 'ana.souza')
    chk(pessoa(pg, 'ana.souza')['perfil'] == 'TECNICO', 'conta nova é sempre de técnico')
    chk(re.fullmatch(r'[A-Za-z2-9]{10}', senha_ana or '') is not None, 'incluir pessoa mostra a senha temporária uma vez')
    larg_eq = pg.evaluate("(() => { const r = document.querySelector('.modal-content.equipe').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })()")
    chk(pg.query_selector('.modal-content.equipe') is not None, 'fechar a senha temporária volta à Equipe')
    senha_bruno = inclui_pessoa(pg, 'Bruno Lima', 'bruno')
    pg.fill('#eq-nome', 'ana souza'); pg.fill('#eq-login', 'outra'); enviar(pg, 'form[data-form=equipe-add]')
    chk('mesmo nome' in flash(pg) or 'nome' in flash(pg), 'nome repetido na Equipe é recusado')
    chk('aguardando o primeiro acesso' in texto(pg, '.eq-lista'), 'Equipe mostra o usuário, o perfil e a situação do acesso')
    clk(pg, '[data-acao=fechar-modal]')
    ana = pessoa(pg, 'ana.souza')['id']; bruno = pessoa(pg, 'bruno')['id']

    # ------------------------------------------------------------------ nova demanda e acionamento
    clk(pg, '[data-acao=nova]'); chk('Data para Conclusão (opcional)' in texto(pg, 'label[for=n-fim]'), 'rótulo Data para Conclusão (opcional)')
    pg.fill('#n-sei', '8.2026.9745/000100-1'); pg.fill('#n-local', 'Foro Centl'); pg.wait_for_timeout(150)
    chk(texto(pg, '.combo-vazio').strip() == 'Nenhum local encontrado.', 'local fora da lista: só "Nenhum local encontrado."')
    pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Teste'); enviar(pg, 'form[data-form=nova]')
    chk('na lista' in texto(pg, '.modal-n .erro') and not api(pg, 'mudancas'), 'local que não está na lista não é aceito')
    clk(pg, '.modal-n [data-acao=fechar-modal]')
    clk(pg, '[data-acao=nova]')
    chk(pg.input_value('#n-cx') == 'normal' and [o.inner_text() for o in pg.query_selector_all('#n-cx option')] == ['Baixa', 'Normal', 'Alta'], 'Nova demanda: Complexidade Baixa, Normal ou Alta, com Normal escolhida')
    chk(pg.query_selector('input[name=n-resp][value=coordenador]') is None and pg.query_selector('input[name=n-resp]:checked') is None, 'Nova demanda: sem Administrador e nenhum técnico pré-selecionado')
    pg.fill('#n-sei', '8.2026.9745/000100-1'); pg.fill('#n-local', 'Canoas'); pg.keyboard.press('Escape'); pg.fill('#n-desc', 'Teste'); enviar(pg, 'form[data-form=nova]')
    chk('técnico responsável' in texto(pg, '.modal-n .erro') and not api(pg, 'mudancas'), 'sem técnico escolhido a demanda não é incluída')
    larg_nova = pg.evaluate("(() => { const r = document.querySelector('.modal-n').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })()")
    chk(larg_eq == larg_nova, f'Equipe com a mesma largura e altura da Nova demanda {larg_eq} {larg_nova}')
    clk(pg, '.modal-n [data-acao=fechar-modal]')
    d1 = nova_demanda(pg, '8.2026.9745/000101-1', 'Canoas', em_dias(5), resp=ana)
    chk(pg.query_selector('.sucesso') is not None and 'atribuída a Ana Souza' in texto(pg, '.suc-desc'), 'inclusão mostra a confirmação com o responsável')
    x = dem(pg, d1); chk(x['situacao'] == 'nova' and x['responsavel'] == ana and x['regiao'] == 'Metropolitana', 'demanda gravada no banco, com a região do local')
    clk(pg, '[data-acao=abrir-nova]'); espera(pg, 400)
    chk(pg.query_selector('form[data-form=principal]') is not None, 'Abrir demanda leva à aba Tickets')
    pg.fill('#t-principal', '123456'); enviar(pg, 'form[data-form=principal]'); chk('7 dígitos' in texto(pg, '.erro'), 'ticket principal com 6 dígitos é recusado')
    pg.fill('#t-principal', ''); pg.type('#t-principal', '1234567890'); chk(pg.input_value('#t-principal') == '1234567', 'o campo do ticket trava no sétimo dígito')
    pg.fill('#n-num', ''); pg.type('#n-num', '1234567890 / 9876543'); chk(pg.input_value('#n-num') == '1234567 / 9876543', 'no campo de subtickets, cada número trava no sétimo dígito')
    ticket(pg, '1831574'); chk(dem(pg, d1)['ticketPrincipal'] == '1831574', 'ticket principal registrado')
    sub(pg, 'CDS', '1831360 / 1831390', 'Mudança de Local', 2); chk(len(dem(pg, d1)['subtickets']) == 2 and '2 subtickets' in flash(pg), 'dois subtickets no mesmo campo')
    sub(pg, 'CDS', '183136', 'Instalação'); chk('7 dígitos' in texto(pg, '.erro') and len(dem(pg, d1)['subtickets']) == 2, 'subticket com 6 dígitos não entra')
    # mudar serviço ou quantidade na tabela só marca a alteração; grava e vai ao histórico em Salvar alterações
    n_hist = len(dem(pg, d1)['historico'])
    pg.fill('#sq-0', '3'); pg.dispatch_event('#sq-0', 'change'); espera(pg)
    chk(dem(pg, d1)['subtickets'][0]['quantidade'] == 2 and pg.is_visible('#sujo-txt') and pg.query_selector('[data-acao=salvar-subs]') is not None, 'mudar a quantidade do subticket só marca a alteração, sem gravar')
    clk(pg, '[data-acao=aba][data-v=dados]'); chk(pg.query_selector('.confirma') is not None, 'sair da aba Tickets com alteração pendente pede confirmação')
    clk(pg, '.confirma [data-acao=fechar-modal]'); chk(pg.input_value('#sq-0') == '3', 'voltar mantém a alteração pendente')
    clk(pg, '[data-acao=salvar-subs]'); x = dem(pg, d1)
    chk(x['subtickets'][0]['quantidade'] == 3 and len(x['historico']) == n_hist + 1 and 'quantidade 3' in x['historico'][-1]['texto'] and pg.query_selector('[data-acao=salvar-subs]') is None, 'Salvar alterações grava o subticket e registra no histórico')
    # descrição opcional do subticket: o + abre o campo; grava com Salvar alterações
    chk(pg.query_selector('#sd-0') is None, 'sem descrição, o campo do subticket fica fechado')
    clk(pg, '[data-acao=sub-desc][data-i="0"]'); pg.type('#sd-0', 'S')
    chk(pg.query_selector('[data-acao=salvar-subs]') is not None, 'a primeira letra da descrição já mostra o Salvar alterações')
    pg.type('#sd-0', 'ala 1001, 2º andar'); espera(pg)
    chk(pg.input_value('#sd-0') == 'Sala 1001, 2º andar', 'a digitação continua no campo depois que o botão aparece')
    chk(dem(pg, d1)['subtickets'][0]['descricao'] == '' and pg.query_selector('[data-acao=salvar-subs]') is not None, 'a descrição do subticket fica pendente até salvar')
    clk(pg, '[data-acao=salvar-subs]'); x = dem(pg, d1)
    chk(x['subtickets'][0]['descricao'] == 'Sala 1001, 2º andar' and x['historico'][-1]['texto'].endswith('descrição incluída.') and pg.query_selector('#sd-0') is None, 'descrição do subticket gravada, no histórico e recolhida depois de salvar')
    chk(pg.query_selector('[data-acao=sub-desc][data-i="0"].tem-desc') is not None, 'subticket com descrição mostra o + destacado')
    clk(pg, '[data-acao=sub-desc][data-i="0"]'); chk(pg.input_value('#sd-0') == 'Sala 1001, 2º andar', 'o + mostra a descrição salva')
    clk(pg, '[data-acao=sub-desc][data-i="0"]'); chk(pg.query_selector('#sd-0') is None, 'o - recolhe a descrição')
    clk(pg, '[data-acao=sub-desc][data-i="0"]'); chk(pg.get_attribute('#sd-0', 'maxlength') == '1000' and '/1000' in texto(pg, '#sd-0-cont') and not pg.get_attribute('#sd-0', 'placeholder'), 'descrição do subticket com até 1000 caracteres e sem texto de exemplo')
    clk(pg, '[data-acao=sub-desc][data-i="0"]')
    # remover subticket pede confirmação
    sub(pg, 'CDS', '1831399', 'Instalação'); n_sub = len(dem(pg, d1)['subtickets'])
    clk(pg, f'[data-acao=sub-del][data-i="{n_sub - 1}"]')
    chk(pg.query_selector('.confirma') is not None and 'Remover Subticket' in texto(pg, '.confirma') and len(dem(pg, d1)['subtickets']) == n_sub, 'remover subticket abre a confirmação, sem remover ainda')
    clk(pg, '.confirma [data-acao=fechar-modal]'); chk(pg.query_selector('.confirma') is None and len(dem(pg, d1)['subtickets']) == n_sub, 'Voltar não remove')
    clk(pg, f'[data-acao=sub-del][data-i="{n_sub - 1}"]'); clk(pg, '.confirma [data-acao=confirmar]')
    chk(len(dem(pg, d1)['subtickets']) == n_sub - 1 and 'removido' in flash(pg), 'confirmar remove o subticket')
    # o card também se arrasta pelo cabeçalho e fica no lugar ao trocar de aba
    posd = lambda: pg.evaluate("(() => { const r = document.querySelector('.det').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; })()")
    q0 = posd(); h = pg.locator('#det-titulo').bounding_box()
    pg.mouse.move(h['x'] + 10, h['y'] + 5); pg.mouse.down(); pg.mouse.move(h['x'] - 90, h['y'] + 35, steps=5); pg.mouse.up(); q1 = posd()
    chk(q1 == [q0[0] - 100, q0[1] + 30], f'arrastar o cabeçalho move o card {q0} → {q1}')
    l2 = pg.locator('.det-l2 .l2-it').last.bounding_box()
    pg.mouse.move(l2['x'] + 5, l2['y'] + 5); pg.mouse.down(); pg.mouse.move(l2['x'] - 95, l2['y'] + 45, steps=5); pg.mouse.up()
    chk(posd() == q1, 'abaixo do nome da comarca (SEI, ticket, datas) o card não se arrasta')
    clk(pg, '[data-acao=aba][data-v=hist]'); chk(posd() == q1, 'o card fica onde foi deixado ao trocar de aba'); clk(pg, '[data-acao=aba][data-v=tickets]')
    clk(pg, '[data-acao=aba][data-v=dados]'); clk(pg, '[data-acao=status-escolher][data-v=acionada]')
    chk(dem(pg, d1)['situacao'] == 'nova' and pg.is_enabled('#btn-salvar'), 'trocar o select não muda o status antes de salvar')
    clk(pg, '#btn-salvar'); x = dem(pg, d1)
    chk(x['situacao'] == 'acionada' and x['acionadaEm'] == HOJE.isoformat() and x['responsavel'] == ana, 'Acionada ao salvar, com a data do acionamento e o mesmo responsável')
    # acionamento por engano: volta para Pendente e pode ser acionada de novo
    chk(pg.query_selector('.det-l1 .st-sel, .det-l1 .st-fixo') is None and 'etapa 2 de 5' in (pg.get_attribute('.st-trilha', 'aria-label') or '') and len(pg.query_selector_all('.st-trilha .st-ponto.feito')) == 1, 'o status saiu do título e a trilha mostra a etapa Acionada')
    clk(pg, '[data-acao=aba][data-v=dados]'); clk(pg, '[data-acao=status-escolher][data-v=nova]')
    chk('Pendente ao salvar' in texto(pg, '.st-trilha') and pg.query_selector('.st-ponto.alvo') is not None, 'escolher Voltar para Pendente só marca a mudança, até salvar')
    clk(pg, '[data-acao=status-desfazer]'); chk(pg.query_selector('.st-ponto.alvo') is None and pg.query_selector('[data-acao=status-escolher][data-v=nova]') is not None, 'o x desfaz a escolha de status')
    clk(pg, '[data-acao=status-escolher][data-v=nova]'); clk(pg, '#btn-salvar'); x = dem(pg, d1)
    chk(x['situacao'] == 'nova' and x['acionadaEm'] is None and x['ticketPrincipal'] == '1831574' and 'Pendente' in flash(pg), 'Acionada volta para Pendente, com o ticket mantido')
    chk('Pendente' in texto(pg, '.st-trilha .st-nome') and 'Marcar como Acionada' in texto(pg, '.st-trilha'), 'o status aparece como Pendente, com o próximo passo')
    clk(pg, '[data-acao=status-escolher][data-v=acionada]'); clk(pg, '#btn-salvar')
    chk(dem(pg, d1)['situacao'] == 'acionada', 'e é acionada de novo')
    # complexidade: no cabeçalho do card, editável em Detalhes e no histórico
    chk('Normal' in texto(pg, '.det-l2') and pg.query_selector('.det-l2 .cx-barras.cx-normal') is not None and 'Região' not in texto(pg, '.det-l2'), 'cabeçalho do card mostra as barras de complexidade (Normal)')
    pg.select_option('#f-cx', 'alta'); espera(pg); clk(pg, '#btn-salvar'); x = dem(pg, d1)
    chk(x['complexidade'] == 'alta' and x['historico'][-1]['texto'] == 'Complexidade alterada: Normal → Alta.' and pg.query_selector('.det-l2 .cx-barras.cx-alta') is not None, 'Complexidade alterada em Detalhes, com registro no histórico')
    chk(pg.get_attribute('#f-info', 'maxlength') == '250' and '/250' in texto(pg, '#f-info-cont'), 'Informações adicionais com até 250 caracteres')
    chk(not pg.get_attribute('#f-info', 'placeholder') and not pg.get_attribute('#f-desc', 'placeholder'), 'Descrição e Informações adicionais sem texto de exemplo')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.fill('#f-hora', '13:00'); clk(pg, '#btn-salvar')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=acionamento]')
    esperado = ('Ao Serviço de Gestão de Mudanças,\n\nEm atenção ao Agendamento (), informo que a empresa contratada da DITIC já foi acionada para o atendimento da demanda:\n\n'
                f'Agendamento:\nData de Início: {br(em_dias(5))}\nHorário: 13hs\n\nTickets:\n\nCDS: 1831360 / 1831390\n\nEra o que cumpria informar.')
    chk(pg.input_value('#ac-texto') == esperado, 'informação de acionamento com Agendamento e Tickets em blocos')
    clk(pg, '.acion [data-acao=fechar-modal]')
    fecha(pg); clk(pg, '[data-acao=sit-aba][data-v=acionada]')
    chk(pg.query_selector(f'.linha-dem[data-id="{d1}"] .c-cx .cx-barras.cx-alta') is not None and 'Alta' in texto(pg, f'.linha-dem[data-id="{d1}"] .c-cx'), 'a lista mostra a complexidade na coluna própria')
    chk('05 dias' in texto(pg, f'[data-acao=abrir][data-id="{d1}"]'), 'Acionada mostra a contagem de dias até o início')

    # para hoje: acionar leva direto a Em atendimento
    d2 = nova_demanda(pg, '8.2026.9745/000102-1', 'Pelotas', HOJE.isoformat(), resp=bruno); clk(pg, '[data-acao=fechar-modal]')
    abre(pg, d2); ticket(pg, '1832000'); aciona(pg)
    chk(dem(pg, d2)['situacao'] == 'atendimento' and 'Em Atendimento' in flash(pg), 'demanda para hoje: acionada e já Em atendimento')
    chk(pg.query_selector('[data-acao=status-escolher]') is None and 'vai para validação' not in texto(pg, '.st-trilha'), 'Em atendimento é automática: sem botão e sem a frase da próxima etapa')
    clk(pg, '[data-acao=aba][data-v=hist]'); chk('automaticamente' in texto(pg, '.linha-tempo') and 'Sistema (automático)' in texto(pg, '.linha-tempo'), 'histórico mostra a mudança automática')
    fecha(pg)

    # Nova cuja data chegou, sem tickets: bolinha e contorno vermelhos
    d3 = nova_demanda(pg, '8.2026.9745/000103-1', 'Torres', em_dias(-1), resp=ana)
    chk('A data já passou' in texto(pg, '.sucesso'), 'demanda antiga: a confirmação avisa que a data já passou')
    clk(pg, '[data-acao=fechar-modal]'); clk(pg, '[data-acao=sit-aba][data-v=nova]')
    chk(pg.query_selector(f'.linha-dem.nv-venc[data-id="{d3}"] .nv-ponto.venc') is not None, 'Pendente vencida ganha bolinha e contorno vermelhos')
    clk(pg, '[data-acao=vista][data-v=postits]')
    dentro = pg.evaluate(f"""(() => {{ const p = document.querySelector('.postit[data-id="{d3}"]'); const b = p && p.querySelector('.pi-topo .nv-ponto.venc'); if (!b) return false;
      const a = p.getBoundingClientRect(), r = b.getBoundingClientRect(), s = p.querySelector('.pi-sei').getBoundingClientRect();
      return r.left >= a.left && r.top >= a.top && r.right <= a.left + 40 && r.right <= s.left; }})()""")
    chk(dentro, 'no post-it, a bolinha fica dentro, no canto esquerdo, antes do SEI'); clk(pg, '[data-acao=vista][data-v=linhas]')

    # a hora fica só dentro do card
    clk(pg, '[data-acao=sit-aba][data-v=todas]')
    chk(pg.query_selector('.linha-dem .c-hora') is None and '13:00' not in texto(pg, f'[data-acao=abrir][data-id="{d1}"]'), 'a hora não aparece ao lado da data na lista')
    clk(pg, '[data-acao=vista][data-v=postits]'); chk('13:00' not in texto(pg, '.rolagem'), 'nem no post-it'); clk(pg, '[data-acao=vista][data-v=linhas]')
    abre(pg, d1); chk('13:00' in texto(pg, '.det-l2'), 'dentro do card, a hora aparece'); fecha(pg)
    # Período: atalhos, datas digitadas, calendário e validação
    linhas = lambda: sorted(int(e.get_attribute('data-id')) for e in pg.query_selector_all('.linha-dem'))
    clk(pg, '[data-acao=periodo-pop]'); clk(pg, '[data-acao=periodo-atalho][data-v=hoje]')
    chk(linhas() == [d2] and pg.inner_text('.filtro-periodo .filtro-nome').strip() == br(HOJE.isoformat()), f'Período "Hoje": só a demanda de hoje {linhas()}')
    clk(pg, '[data-acao=periodo-pop]'); pg.fill('#per-de', br(em_dias(6))); pg.fill('#per-ate', br(em_dias(4))); clk(pg, '[data-acao=periodo-aplicar]')
    chk('antes da inicial' in texto(pg, '.pop-periodo .erro'), 'Período com a data final antes da inicial é recusado')
    pg.fill('#per-de', br(em_dias(4))); pg.fill('#per-ate', br(em_dias(6))); clk(pg, '[data-acao=periodo-aplicar]')
    chk(linhas() == [d1], f'Período digitado: só a demanda dentro dele {linhas()}')
    clk(pg, '[data-acao=periodo-pop]')
    bordas = pg.evaluate("[...document.querySelectorAll('.per-atalho, .per-datas .data-campo')].map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right)]; })")
    chk(len(bordas) == 6 and all(b == bordas[i % 2] for i, b in enumerate(bordas)), f'atalhos do Período alinhados às bordas dos campos De e Até {bordas}')
    clk(pg, '.pop-periodo .data-btn'); chk(pg.query_selector('#cal-pop') is not None and pg.query_selector('.pop-periodo') is not None, 'o calendário abre dentro do Período sem fechá-lo')
    clk(pg, '#cal-pop [data-acao=cal-hoje]'); chk(pg.input_value('#per-de') == br(HOJE.isoformat()), 'escolher no calendário preenche a data')
    clk(pg, '.pop-periodo [data-acao=periodo-limpar]'); chk(pg.query_selector('.filtro-periodo.ativo') is None and len(linhas()) == 3, 'Limpar tira o filtro de período')
    # a linha de filtros não se mexe ao escolher filtros ou ligar Minhas demandas
    caixas = lambda: pg.evaluate("['#busca', '.filtro-local', '.filtro-resp', '.filtro-periodo', '.filtro-comigo', '.filtros .vistas'].map(s => { const b = document.querySelector(s).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.width)]; })")
    antes_f = caixas()
    clk(pg, '[data-acao=comigo]'); m1 = caixas(); clk(pg, '[data-acao=comigo]')
    clk(pg, '[data-acao=periodo-pop]'); clk(pg, '[data-acao=periodo-atalho][data-v=prox30]'); m2 = caixas(); clk(pg, '[data-acao=periodo-pop]'); clk(pg, '.pop-periodo [data-acao=periodo-limpar]')
    clk(pg, '[data-acao=resp-pop]'); clk(pg, '.op-resp'); m3 = caixas(); clk(pg, '.filtro-resp .filtro-limpa')
    chk(antes_f == m1 == m2 == m3, f'os filtros não mudam de tamanho nem de lugar ao serem escolhidos {antes_f} {m1} {m2} {m3}')
    # Comigo: o administrador vê a carga do Administrador
    clk(pg, '[data-acao=comigo]')
    chk(pg.query_selector('.filtro-comigo.ativo') is not None and all('Administrador' in e.inner_text() for e in pg.query_selector_all('.linha-dem')), 'Minhas demandas (administrador): só as demandas com o Administrador')
    clk(pg, '[data-acao=comigo]'); chk(pg.query_selector('.filtro-comigo.ativo') is None and len(linhas()) == 3, 'um segundo clique desliga Minhas demandas')
    clk(pg, '[data-acao=sit-aba][data-v=abertas]')

    # ------------------------------------------------------------------ Para Validação remarcada volta para Acionada
    d5 = nova_demanda(pg, '8.2026.9745/000105-1', 'Canoas', em_dias(-6), resp=ana, fim=em_dias(-5)); clk(pg, '[data-acao=fechar-modal]')
    abre(pg, d5); ticket(pg, '1850000'); sub(pg, 'CDS', '1850001', 'Mudança de Local')
    chk(dem(pg, d5)['situacao'] == 'pendente', 'demanda com o período passado está em Para Validação')
    clk(pg, '[data-acao=aba][data-v=dados]'); data(pg, '#f-ini', em_dias(4)); data(pg, '#f-fim', em_dias(5)); clk(pg, '#btn-salvar')
    chk(dem(pg, d5)['situacao'] == 'acionada' and 'voltou para Acionada' in flash(pg), 'Para Validação remarcada para o futuro volta para Acionada, com aviso')
    data(pg, '#f-ini', em_dias(0)); clk(pg, '#btn-salvar')
    chk(dem(pg, d5)['situacao'] == 'atendimento', 'remarcada para hoje, fica Em Atendimento')
    l2 = pg.evaluate("(() => { const l = document.querySelector('.det-l2'); const t = [...l.children].map(c => c.getBoundingClientRect()); return [Math.round(document.querySelector('.modal-content.det').getBoundingClientRect().width), Math.max(...t.map(r => r.bottom)) - Math.min(...t.map(r => r.top))]; })()")
    chk(l2[0] == 1140 and l2[1] < 30, f'card com 1140 px e cabeçalho com início e fim numa linha só {l2}')
    medida = lambda sel: pg.evaluate(f"(() => {{ const r = document.querySelector({sel!r}).getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; }})()")
    m_card = medida('.modal-content.det'); fecha(pg)
    clk(pg, '[data-acao=nova]'); m_nova = medida('.modal-content.modal-n'); clk(pg, '[data-acao=fechar-modal]')
    chk(m_card == m_nova == [1140, 800], f'Nova Demanda com a mesma medida do card {m_card} {m_nova}')

    # ------------------------------------------------------------------ demanda antiga: tickets → Para Validação → relatório → concluir
    d4 = nova_demanda(pg, '8.2026.9745/000104-1', 'Canoas', em_dias(-10), resp=ana, fim=em_dias(-9)); clk(pg, '[data-acao=fechar-modal]')
    abre(pg, d4); ticket(pg, '1840000')
    sub(pg, 'CDS', '1840001', 'Mudança de Local', 2)
    chk(dem(pg, d4)['situacao'] == 'pendente', 'demanda antiga com ticket e subticket vai direto para Para Validação')
    sub(pg, 'WECOM', '1840002', 'Infraestrutura', 3)
    sub(pg, 'WECOM', '1840003', 'Infraestrutura', 1, metro=2)
    sub(pg, 'Selbetti', '1840004', 'Desinstalação', 1)
    chk(any(s['numero'] == '1840003' and s['metro'] == 2 for s in dem(pg, d4)['subtickets']), 'metro linear da Infraestrutura gravado')
    antes = len(dem(pg, d4)['subtickets']); sub(pg, 'CDS', '1831360', 'Instalação')
    chk(len(dem(pg, d4)['subtickets']) == antes and 'já está na demanda 8.2026.9745/000101-1' in texto(pg, '.erro') and 'já está' in flash(pg), 'subticket de outra demanda é bloqueado, com aviso')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]'); espera(pg, 400)
    # CDS 2 × 160,00 + verba de 15 m (uma só, mesmo com quantidade 3) + 2 m × 164,18
    custo = pg.input_value('#rl-custo')
    chk(custo == 'R$ 3.111,06', f'custo: CDS + verba de 15 m (sem multiplicar pela quantidade) + metro linear informado ({custo})')
    # o relatório é uma janela solta: sem fundo esmaecido, arrastável, e o card de baixo continua em uso
    chk(pg.query_selector('.modal-camada') is None and pg.query_selector('.janela.relat') is not None, 'relatório abre sem esmaecer o fundo')
    caixa = lambda: pg.evaluate("(() => { const r = document.querySelector('.janela').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; })()")
    p0 = caixa(); h = pg.locator('.janela .modal-header h2').bounding_box()
    pg.mouse.move(h['x'] + 20, h['y'] + 5); pg.mouse.down(); pg.mouse.move(h['x'] - 180, h['y'] + 45, steps=5); pg.mouse.up(); p1 = caixa()
    chk(p1[0] == p0[0] - 200 and p1[1] == p0[1] + 40, f'arrastar pelo cabeçalho move a janela {p0} → {p1}')
    pg.fill('#rl-exec', '01/01/2026')
    clk(pg, '.det [data-acao=aba][data-v=hist]'); espera(pg); clk(pg, '.det [data-acao=aba][data-v=tickets]'); espera(pg)
    chk(pg.query_selector('.det form[data-form=sub]') is not None and pg.input_value('#rl-exec') == '01/01/2026' and caixa() == p1, 'com o relatório aberto, o card troca de aba e o relatório guarda o que foi editado')
    desc = pg.input_value('#rl-itens')
    chk(desc.count('utiliza o valor de verba de R$2.462,70') == 1 and 'ticket 1840002' in desc, 'só o ticket sem metro linear leva a frase da verba')
    chk('Desinstalação de multifuncional Selbetti' in desc and 'Salas de Audiência Digital' in desc, 'textos próprios da Selbetti e da WECOM')
    chk(pg.input_value('#rl-origem') == 'Foro da Comarca de Canoas' and 'DMP' not in pg.input_value('#rl-destino'), 'a Desinstalação da Selbetti não conta para origem e destino')
    pg.uncheck('#rl-infra'); espera(pg)
    chk(pg.input_value('#rl-custo') == 'R$ 320,00' and pg.input_value('#rl-itens').count('O valor de Instalação de Infraestrutura (WECOM) referente ao Contrato de Salas de Audiências Digitais, não consta na soma') == 1 and 'verba' not in pg.input_value('#rl-itens'), 'desmarcar a Infraestrutura tira o valor e troca a frase por uma só, com dois tickets de Infraestrutura')
    with pg.expect_download() as dl: clk(pg, '[data-acao=baixar-relatorio]')
    pdf = open(dl.value.path(), 'rb').read()
    chk(pdf.startswith(b'%PDF') and dl.value.suggested_filename == 'Relatório de execução - 8.2026.9745-000104-1.pdf', 'PDF baixado com o nome do SEI')
    chk(b'Era o que cabia informar.' in pdf, 'PDF termina com "Era o que cabia informar."')
    chk(any('Relatório de execução' in h['texto'] for h in dem(pg, d4)['historico']), 'gerar o PDF registra no histórico')
    clk(pg, '.relat [data-acao=fechar-janela]'); chk(pg.query_selector('.janela') is None, 'Fechar tira a janela do relatório')
    clk(pg, '[data-acao=concluir-dem]'); clk(pg, '.confirma [data-acao=confirmar]')
    x = dem(pg, d4); chk(x['situacao'] == 'concluida' and x['responsavel'] is None and x['tecnico'] == ana, 'concluída fica com o Setor e guarda quem atendeu')
    clk(pg, '[data-acao=aba][data-v=dados]')
    chk(pg.is_disabled('#f-desc') and pg.query_selector('form[data-form=principal]') is None, 'demanda concluída fica somente leitura')
    clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=relatorio]') is not None, 'concluída: Mais ações tem Gerar relatório'); clk(pg, '[data-acao=menu-mais]')
    # pelo endereço da rede (http://IP:8088) o navegador não oferece a área de transferência moderna: a cópia usa o caminho antigo
    pg.evaluate("Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true })")
    pg.click('.det-l2 .mini-copia[data-acao=copiar]', timeout=5000); espera(pg)
    chk('Copiado' in flash(pg), 'copiar funciona também fora de https/localhost')
    pg.evaluate("Object.defineProperty(window, 'isSecureContext', { value: true, configurable: true })")
    fecha(pg)

    # ------------------------------------------------------------------ configuração de valores
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=config]')
    chk(pg.is_disabled('#cfg-salvar') and len(pg.query_selector_all('.cfg-tab tbody tr')) == 7, 'Configuração com as 7 regiões e Salvar inativo')
    pg.fill('#pw-metro', '200,00'); pg.dispatch_event('#pw-metro', 'change'); espera(pg)
    clk(pg, '#cfg-salvar'); clk(pg, '.confirma [data-acao=confirmar]')
    chk('Valores Atualizados' in texto(pg, '.confirma'), 'salvar valores pede confirmação e mostra o resultado')
    clk(pg, '.confirma [data-acao=fechar-modal]')
    chk(float(api(pg, 'precos')['wecom']['metro']) == 200.0, 'novo valor gravado no banco')
    pg.fill('#pw-metro', '164,18'); pg.dispatch_event('#pw-metro', 'change'); espera(pg); clk(pg, '#cfg-salvar'); clk(pg, '.confirma [data-acao=confirmar]'); clk(pg, '.confirma [data-acao=fechar-modal]')
    clk(pg, '[data-acao=cfg-fechar]')

    # ------------------------------------------------------------------ cancelar, excluir e restaurar (coordenador)
    abre(pg, d3); clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=cancelar]')
    clk(pg, '.confirma [data-acao=confirmar]'); chk('motivo' in texto(pg, '.confirma .erro').lower(), 'cancelar exige motivo')
    pg.fill('#mc-motivo', 'Pedido retirado'); clk(pg, '.confirma [data-acao=confirmar]')
    chk(dem(pg, d3)['situacao'] == 'cancelada', 'coordenador cancela com motivo')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=excluir]'); pg.fill('#mc-motivo', 'Duplicada'); clk(pg, '.confirma [data-acao=confirmar]')
    chk(d3 not in ids(pg) and any(l['id'] == d3 for l in api(pg, 'lixeira')), 'excluída vai para a lixeira')
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=lixeira]'); chk('Duplicada' in texto(pg, '.lixeira') and 'restam 30 dias' in texto(pg, '.lixeira'), 'lixeira mostra o motivo e os dias restantes')
    clk(pg, f'[data-acao=restaurar][data-id="{d3}"]'); chk(d3 in ids(pg), 'restaurar devolve a demanda'); clk(pg, '[data-acao=fechar-modal]')

    # ------------------------------------------------------------------ o técnico entra com a senha temporária
    sai(pg); chk(pg.query_selector('form[data-form=login]') is None and pg.query_selector('[data-acao=login]') is not None and pg.query_selector('[data-acao=nova]') is None and 'saiu' in flash(pg), 'sair volta à consulta, sem a Nova demanda')
    # consulta sem login: o card abre, mas nada se altera
    abre(pg, d1)
    chk('somente consulta' in texto(pg, '.st-trilha') and pg.query_selector('[data-acao=status-escolher]') is None and pg.is_disabled('#f-desc'), 'sem login, o card abre só para consulta')
    clk(pg, '[data-acao=aba][data-v=hist]'); chk(pg.query_selector('form[data-form=nota]') is None and 'Empresas acionadas' in texto(pg, '.linha-tempo'), 'sem login, o histórico aparece, sem registrar andamento')
    clk(pg, '[data-acao=menu-mais]'); chk(pg.query_selector('[data-acao=acionamento]') is None and pg.query_selector('[data-acao=copiar-tickets]') is not None, 'sem login, Mais ações só copia os tickets'); clk(pg, '[data-acao=menu-mais]')
    clk(pg, '[data-acao=aba][data-v=tickets]'); chk(pg.query_selector('form[data-form=principal]') is None and pg.query_selector('form[data-form=sub]') is None, 'sem login, os tickets não se alteram')
    fecha(pg)
    chk(all(p.get('login') is None for p in api(pg, 'pessoas')), 'sem login, a lista de pessoas não mostra o usuário de ninguém')
    entra(pg, 'ana.souza', senha_ana); chk(pg.query_selector('form[data-form=senha]') is not None, 'senha temporária exige criar a senha pessoal')
    cria_senha(pg, 'senha-da-ana-1')
    chk('Ana Souza' in texto(pg, '.topo'), 'técnico entra depois de criar a senha')
    clk(pg, '[data-acao=menu-conta]'); chk(not any(pg.query_selector(f'[data-acao={a}]') for a in ('equipe', 'lixeira', 'config')), 'menu do técnico sem Equipe, Lixeira e Configuração'); clk(pg, '[data-acao=menu-conta]')
    abre(pg, d2); clk(pg, '[data-acao=menu-mais]')
    chk(pg.query_selector('[data-acao=cancelar]') is None and pg.query_selector('[data-acao=excluir]') is None, 'técnico não tem Cancelar nem Excluir'); clk(pg, '[data-acao=menu-mais]')
    # qualquer técnico edita a demanda de outro; a troca de responsável vai ao histórico
    pg.select_option('#f-resp', ana); clk(pg, '#btn-salvar')
    chk(dem(pg, d2)['responsavel'] == ana and any('Responsável alterado: Bruno Lima → Ana Souza' in h['texto'] for h in dem(pg, d2)['historico']), 'técnico troca o responsável de uma demanda de outro')
    hist = dem(pg, d2)['historico'][-1]; chk(hist['usuario'] == ana, 'o histórico grava o autor real')
    fecha(pg); clk(pg, '[data-acao=sit-aba][data-v=todas]'); clk(pg, '[data-acao=comigo]')
    chk(len(pg.query_selector_all('.linha-dem')) > 0 and all('Ana' in e.inner_text() for e in pg.query_selector_all('.linha-dem')), 'Minhas demandas (técnico): só as demandas da própria pessoa')
    clk(pg, '[data-acao=comigo]'); clk(pg, '[data-acao=sit-aba][data-v=abertas]'); abre(pg, d2)
    clk(pg, '[data-acao=aba][data-v=hist]'); pg.fill('#h-nota', 'Solicitado ao DMP'); enviar(pg, 'form[data-form=nota]')
    chk(dem(pg, d2)['historico'][-1]['texto'] == 'Solicitado ao DMP', 'registrar andamento')
    fecha(pg)
    chk(pg.evaluate("fetch('api/precos', { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-XSRF-TOKEN': decodeURIComponent((document.cookie.match(/XSRF-TOKEN=([^;]+)/) || [])[1] || '') }, body: '{}' }).then(r => r.status)") == 403, 'o servidor recusa a Configuração para o técnico')
    chk(pg.evaluate("fetch('api/mudancas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }).then(r => r.status)") == 403, 'alteração sem o token CSRF é recusada')

    # ------------------------------------------------------------------ pedido de acesso pela tela de entrada
    sai(pg); clk(pg, '[data-acao=login]'); clk(pg, '[data-acao=pedir-acesso]')
    pg.fill('#pa-nome', 'Carla Dias'); pg.fill('#pa-usr', 'carla'); enviar(pg, 'form[data-form=pedido]')
    chk('Pedido Enviado' in texto(pg, '.login'), 'pedido de acesso enviado pela tela de entrada')
    clk(pg, '[data-acao=pedir-voltar]'); entra(pg, 'admin', SENHA_ADMIN)
    clk(pg, '[data-acao=menu-conta]'); chk('1 pedido' in texto(pg, '[data-acao=equipe]'), 'menu do administrador avisa o pedido pendente'); clk(pg, '[data-acao=equipe]')
    chk('Carla Dias' in texto(pg, '.sol-bloco'), 'pedido aparece em Equipe')
    clk(pg, '[data-acao=sol-aprovar]'); senha_carla = texto(pg, '.senha-tmp').strip()
    chk(len(senha_carla) == 10 and pessoa(pg, 'carla')['perfil'] == 'TECNICO', 'aprovar cria a conta com senha temporária')
    clk(pg, '.confirma [data-acao=fechar-modal]')

    # ------------------------------------------------------------------ excluir: quem nunca fez nada sai de vez
    chk(pg.query_selector('.sol-acoes select') is None, 'aprovar o pedido não pede perfil')
    carla = pessoa(pg, 'carla')['id']
    clk(pg, f'[data-acao=eq-excluir][data-v="{carla}"]'); chk('Excluir' in texto(pg, '.confirma'), 'excluir pede confirmação')
    clk(pg, '.confirma [data-acao=confirmar]')
    chk(all(p['login'] != 'carla' for p in api(pg, 'pessoas')) and pg.query_selector('.modal-content.equipe') is not None, 'conta sem nenhum registro é apagada e a Equipe continua aberta')
    adm = api(pg, 'sessao')['id']
    chk(pg.query_selector(f'[data-acao=eq-excluir][data-v="{adm}"]') is None, 'o administrador não tem o botão Excluir')

    # ------------------------------------------------------------------ excluir quem tem demandas: transfere antes
    pg.evaluate(f"document.querySelector('[data-acao=eq-excluir][data-v=\"{ana}\"]').click()"); espera(pg)
    chk(pg.query_selector('form[data-form=equipe-transf]') is not None, 'excluir quem tem demandas em aberto pede a transferência')
    pg.select_option('#tr-dest', bruno); enviar(pg, 'form[data-form=equipe-transf]')
    chk(not pessoa(pg, 'ana.souza')['ativo'] and all(d['responsavel'] != ana for d in api(pg, 'mudancas') if d['situacao'] in ('nova', 'acionada', 'atendimento', 'pendente')), 'ninguém excluído fica com demanda em aberto; quem tem histórico fica só desativado')
    chk(dem(pg, d1)['responsavel'] == bruno, 'as demandas marcadas foram para quem foi escolhido')
    clk(pg, '[data-acao=fechar-modal]')

    # ------------------------------------------------------------------ telas menores
    pg.set_viewport_size({'width': 390, 'height': 844}); espera(pg, 300)
    chk(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), 'celular: sem rolagem horizontal')
    for w in (640, 390):
        pg.set_viewport_size({'width': w, 'height': 844}); pg.fill('#busca', 'zzzz'); espera(pg, 300)
        chk(pg.evaluate("Math.abs(document.querySelector('.rodape').getBoundingClientRect().bottom - innerHeight) < 2"), f'{w} px: com a lista vazia, o rodapé fica no fim da janela')
        nv = pg.evaluate("(() => { const r = document.querySelector('.btn-nova').getBoundingClientRect(); return [r.width, r.height]; })()")
        chk(nv[0] == nv[1], f'{w} px: botão Nova demanda redondo {nv}')
        for menu, pop in (('local-pop', '.pop-local'), ('resp-pop', '.pop-resp')):
            clk(pg, f'[data-acao={menu}]')
            chk(pg.evaluate(f"(() => {{ const r = document.querySelector('{pop}').getBoundingClientRect(); return r.left >= 8 && r.right <= innerWidth - 8; }})()"), f'{w} px: o menu {menu.split("-")[0]} fica dentro da janela')
            pg.keyboard.press('Escape'); espera(pg)
        pg.fill('#busca', ''); espera(pg)
        clk(pg, '[data-acao=nova]')
        chk(pg.evaluate("(() => { const r = document.querySelector('.modal-n').getBoundingClientRect(); return r.left >= 10 && innerWidth - r.right >= 10 && innerHeight - r.bottom >= 10; })()"), f'{w} px: o modal fica afastado das bordas')
        clk(pg, '.modal-n [data-acao=fechar-modal]')
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]')
    chk(pg.evaluate("document.querySelector('.modal-content.equipe').scrollWidth <= document.querySelector('.modal-content.equipe').clientWidth + 1"), 'celular: Equipe cabe na largura')
    clk(pg, '[data-acao=fechar-modal]')

    chk(not erros, 'nenhum erro de JavaScript' + (': ' + '; '.join(erros) if erros else ''))
    b.close()
print(f'\n{len(ok)} ok, {len(falhas)} falhas')
sys.exit(1 if falhas else 0)
