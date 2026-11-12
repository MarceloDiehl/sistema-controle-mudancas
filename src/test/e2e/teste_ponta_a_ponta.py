# Teste de ponta a ponta do Controle de Demandas de Mudanças, com o servidor e o banco de verdade.
# Uso:  pip install playwright  &&  python -m playwright install chromium
#   1. Suba a aplicação com o banco de teste (H2 em memória, com os catálogos do script do banco):
#        mvnw.cmd test-compile spring-boot:test-run        (Linux/macOS: ./mvnw ...)
#   2. Em outro terminal:  python src/test/e2e/teste_ponta_a_ponta.py  [url]   (padrão: http://localhost:8088/)
# O servidor de teste começa vazio, só com o coordenador "admin" (senha inicial "admin-inicial"). O teste cria as
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
def nova_demanda(pg, sei, local, inicio, resp='coordenador', fim=None, desc='Demanda de teste'):
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
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.select_option('#d-status', 'acionada'); espera(pg)
    clk(pg, '#btn-salvar')
def pessoa(pg, login): return next(p for p in api(pg, 'pessoas') if p['login'] == login)
def inclui_pessoa(pg, nome, login, perfil='TECNICO'):
    pg.fill('#eq-nome', nome); pg.fill('#eq-login', login); pg.select_option('#eq-perfil', perfil); enviar(pg, 'form[data-form=equipe-add]')
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
    chk('Acesso do protótipo' not in pg.content() and pg.query_selector('[data-acao=proto-gestor]') is None, 'sem o acesso de demonstração do protótipo')
    entra(pg, 'admin', 'errada'); chk('incorretos' in texto(pg, '.login .erro'), 'senha errada é recusada')
    entra(pg, 'admin', 'admin-inicial')
    if pg.query_selector('form[data-form=senha]') is None:   # o servidor já tinha sido usado: entra com a senha do teste
        entra(pg, 'admin', SENHA_ADMIN)
    else:
        chk(True, 'primeiro acesso do coordenador exige criar a senha')
        pg.mouse.click(5, 5); pg.keyboard.press('Escape'); espera(pg); chk(pg.query_selector('form[data-form=senha]') is not None, 'a criação de senha não fecha por clique fora nem Esc')
        cria_senha(pg, 'curta'); chk('8 caracteres' in texto(pg, '.login .erro'), 'senha curta é recusada')
        cria_senha(pg, 'admin-inicial'); chk('diferente' in texto(pg, '.login .erro'), 'a nova senha precisa ser diferente da inicial')
        cria_senha(pg, SENHA_ADMIN)
    chk(pg.query_selector('.modal-camada') is None and pg.query_selector('[data-acao=nova]') is not None and 'Coordenador' in texto(pg, '.topo'), 'coordenador entra e vê a tela principal')
    clk(pg, '[data-acao=menu-conta]'); chk(all(pg.query_selector(f'[data-acao={a}]') for a in ('equipe', 'lixeira', 'config')), 'menu do coordenador com Equipe, Lixeira e Configuração'); clk(pg, '[data-acao=menu-conta]')

    # ------------------------------------------------------------------ tela principal
    abas = [e.inner_text() for e in pg.query_selector_all('.sit-aba .aba-nome')]
    chk(abas == ['Em aberto', 'Novas', 'Acionadas', 'Em Atendimento', 'Para Validação', 'Concluídas', 'Canceladas', 'Todas'], f'abas de situação {abas}')
    ordem = pg.evaluate("[...document.querySelectorAll('.filtros > *')].map(e => e.className.split(' ').find(c => ['campo-busca','filtro-local','filtro-resp','vistas'].includes(c)))")
    chk(ordem == ['campo-busca', 'filtro-local', 'filtro-resp', 'vistas'], f'abaixo das abas: pesquisa, Local, Responsável e visualização {ordem}')
    alt = pg.evaluate("['#busca', '.filtro-local', '.filtro-resp', '.filtros .vistas'].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)]; })")
    chk(len(set(map(tuple, alt))) == 1, f'pesquisa, seletores e visualização na mesma linha e altura {alt}')
    chk(pg.evaluate("document.querySelector('.topo').getBoundingClientRect().height") < 60, 'navbar baixo')
    clk(pg, '[data-acao=sobre]'); chk(texto(pg, '.sobre-ver') == 'Versão do Sistema: 1.0.0 · Novembro/2026', 'informações do sistema'); clk(pg, '[data-acao=fechar-modal]')

    # ------------------------------------------------------------------ equipe e contas
    clk(pg, '[data-acao=menu-conta]'); clk(pg, '[data-acao=equipe]')
    senha_ana = inclui_pessoa(pg, 'Ana Souza', 'ana.souza')
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
    larg_nova = pg.evaluate("(() => { const r = document.querySelector('.modal-n').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })()")
    chk(larg_eq == larg_nova, f'Equipe com a mesma largura e altura da Nova demanda {larg_eq} {larg_nova}')
    clk(pg, '.modal-n [data-acao=fechar-modal]')
    d1 = nova_demanda(pg, '8.2026.9745/000101-1', 'Canoas', em_dias(5), resp=ana)
    chk(pg.query_selector('.sucesso') is not None and 'atribuída a Ana Souza' in texto(pg, '.suc-desc'), 'inclusão mostra a confirmação com o responsável')
    x = dem(pg, d1); chk(x['situacao'] == 'nova' and x['responsavel'] == ana and x['regiao'] == 'Metropolitana', 'demanda gravada no banco, com a região do local')
    clk(pg, '[data-acao=abrir-nova]'); espera(pg, 400)
    chk(pg.query_selector('form[data-form=principal]') is not None, 'Abrir demanda leva à aba Tickets')
    pg.fill('#t-principal', '1234567'); enviar(pg, 'form[data-form=principal]'); chk('8 dígitos' in texto(pg, '.erro'), 'ticket principal com 7 dígitos é recusado')
    pg.fill('#t-principal', ''); pg.type('#t-principal', '1234567890'); chk(pg.input_value('#t-principal') == '12345678', 'o campo do ticket trava no oitavo dígito')
    pg.fill('#n-num', ''); pg.type('#n-num', '1234567890 / 98765432'); chk(pg.input_value('#n-num') == '12345678 / 98765432', 'no campo de subtickets, cada número trava no oitavo dígito')
    ticket(pg, '18315742'); chk(dem(pg, d1)['ticketPrincipal'] == '18315742', 'ticket principal registrado')
    sub(pg, 'CDS', '18313601 / 18313902', 'Mudança de Local', 2); chk(len(dem(pg, d1)['subtickets']) == 2 and '2 subtickets' in flash(pg), 'dois subtickets no mesmo campo')
    sub(pg, 'CDS', '1831360', 'Instalação'); chk('8 dígitos' in texto(pg, '.erro') and len(dem(pg, d1)['subtickets']) == 2, 'subticket com 7 dígitos não entra')
    # mudar serviço ou quantidade na tabela só marca a alteração; grava e vai ao histórico em Salvar alterações
    n_hist = len(dem(pg, d1)['historico'])
    pg.fill('#sq-0', '3'); pg.dispatch_event('#sq-0', 'change'); espera(pg)
    chk(dem(pg, d1)['subtickets'][0]['quantidade'] == 2 and pg.is_visible('#sujo-txt') and pg.query_selector('[data-acao=salvar-subs]') is not None, 'mudar a quantidade do subticket só marca a alteração, sem gravar')
    clk(pg, '[data-acao=aba][data-v=dados]'); chk(pg.query_selector('.confirma') is not None, 'sair da aba Tickets com alteração pendente pede confirmação')
    clk(pg, '.confirma [data-acao=fechar-modal]'); chk(pg.input_value('#sq-0') == '3', 'voltar mantém a alteração pendente')
    clk(pg, '[data-acao=salvar-subs]'); x = dem(pg, d1)
    chk(x['subtickets'][0]['quantidade'] == 3 and len(x['historico']) == n_hist + 1 and 'quantidade 3' in x['historico'][-1]['texto'] and pg.query_selector('[data-acao=salvar-subs]') is None, 'Salvar alterações grava o subticket e registra no histórico')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.select_option('#d-status', 'acionada'); espera(pg)
    chk(dem(pg, d1)['situacao'] == 'nova' and pg.is_enabled('#btn-salvar'), 'trocar o select não muda o status antes de salvar')
    clk(pg, '#btn-salvar'); x = dem(pg, d1)
    chk(x['situacao'] == 'acionada' and x['acionadaEm'] == HOJE.isoformat() and x['responsavel'] == ana, 'Acionada ao salvar, com a data do acionamento e o mesmo responsável')
    clk(pg, '[data-acao=aba][data-v=dados]'); pg.fill('#f-hora', '13:00'); clk(pg, '#btn-salvar')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=acionamento]')
    esperado = ('Ao Serviço de Gestão de Mudanças,\n\nEm atenção ao Agendamento, informo que a empresa contratada da DITIC já foi acionada para o atendimento da demanda:\n\n'
                f'Agendamento:\nData de Início: {br(em_dias(5))}\nHorário: 13hs\n\nTickets:\n\nCDS: 18313601 / 18313902\n\nEra o que cumpria informar.')
    chk(pg.input_value('#ac-texto') == esperado, 'informação de acionamento com Agendamento e Tickets em blocos')
    clk(pg, '.acion [data-acao=fechar-modal]')
    fecha(pg); clk(pg, '[data-acao=sit-aba][data-v=acionada]')
    chk('05 dias' in texto(pg, f'[data-acao=abrir][data-id="{d1}"]'), 'Acionada mostra a contagem de dias até o início')

    # para hoje: acionar leva direto a Em atendimento
    d2 = nova_demanda(pg, '8.2026.9745/000102-1', 'Pelotas', HOJE.isoformat(), resp=bruno); clk(pg, '[data-acao=fechar-modal]')
    abre(pg, d2); ticket(pg, '18320000'); aciona(pg)
    chk(dem(pg, d2)['situacao'] == 'atendimento' and 'Em Atendimento' in flash(pg), 'demanda para hoje: acionada e já Em atendimento')
    chk(pg.query_selector('.st-fixo') is not None and pg.query_selector('#d-status') is None, 'Em atendimento tem o status travado')
    clk(pg, '[data-acao=aba][data-v=hist]'); chk('automaticamente' in texto(pg, '.linha-tempo') and 'Sistema (automático)' in texto(pg, '.linha-tempo'), 'histórico mostra a mudança automática')
    fecha(pg)

    # Nova cuja data chegou, sem tickets: bolinha e contorno vermelhos
    d3 = nova_demanda(pg, '8.2026.9745/000103-1', 'Torres', em_dias(-1), resp=ana)
    chk('A data já passou' in texto(pg, '.sucesso'), 'demanda antiga: a confirmação avisa que a data já passou')
    clk(pg, '[data-acao=fechar-modal]'); clk(pg, '[data-acao=sit-aba][data-v=nova]')
    chk(pg.query_selector(f'.linha-dem.nv-venc[data-id="{d3}"] .nv-ponto.venc') is not None, 'Nova vencida ganha bolinha e contorno vermelhos')

    # ------------------------------------------------------------------ demanda antiga: tickets → Para Validação → relatório → concluir
    d4 = nova_demanda(pg, '8.2026.9745/000104-1', 'Canoas', em_dias(-10), resp=ana, fim=em_dias(-9)); clk(pg, '[data-acao=fechar-modal]')
    abre(pg, d4); ticket(pg, '18400000')
    sub(pg, 'CDS', '18400001', 'Mudança de Local', 2)
    chk(dem(pg, d4)['situacao'] == 'pendente', 'demanda antiga com ticket e subticket vai direto para Para Validação')
    sub(pg, 'WECOM', '18400002', 'Infraestrutura', 3)
    sub(pg, 'WECOM', '18400003', 'Infraestrutura', 1, metro=2)
    sub(pg, 'Selbetti', '18400004', 'Desinstalação', 1)
    chk(any(s['numero'] == '18400003' and s['metro'] == 2 for s in dem(pg, d4)['subtickets']), 'metro linear da Infraestrutura gravado')
    antes = len(dem(pg, d4)['subtickets']); sub(pg, 'CDS', '18313601', 'Instalação')
    chk(len(dem(pg, d4)['subtickets']) == antes and 'já está na demanda 8.2026.9745/000101-1' in texto(pg, '.erro') and 'já está' in flash(pg), 'subticket de outra demanda é bloqueado, com aviso')
    clk(pg, '[data-acao=menu-mais]'); clk(pg, '[data-acao=relatorio]'); espera(pg, 400)
    # CDS 2 × 160,00 + verba de 15 m (uma só, mesmo com quantidade 3) + 2 m × 164,18
    custo = pg.input_value('#rl-custo')
    chk(custo == 'R$ 3.111,06', f'custo: CDS + verba de 15 m (sem multiplicar pela quantidade) + metro linear informado ({custo})')
    desc = pg.input_value('#rl-itens')
    chk(desc.count('utiliza o valor de verba de R$2.462,70') == 1 and 'ticket 18400002' in desc, 'só o ticket sem metro linear leva a frase da verba')
    chk('Desinstalação de multifuncional Selbetti' in desc and 'Salas de Audiência Digital' in desc, 'textos próprios da Selbetti e da WECOM')
    chk(pg.input_value('#rl-origem') == 'Foro da Comarca de Canoas' and 'DMP' not in pg.input_value('#rl-destino'), 'a Desinstalação da Selbetti não conta para origem e destino')
    pg.uncheck('#rl-infra'); espera(pg)
    chk(pg.input_value('#rl-custo') == 'R$ 320,00' and pg.input_value('#rl-itens').count('O valor de Instalação de Infraestrutura (WECOM) referente ao Contrato de Salas de Audiências Digitais, não consta na soma') == 1 and 'verba' not in pg.input_value('#rl-itens'), 'desmarcar a Infraestrutura tira o valor e troca a frase por uma só, com dois tickets de Infraestrutura')
    with pg.expect_download() as dl: clk(pg, '[data-acao=baixar-relatorio]')
    pdf = open(dl.value.path(), 'rb').read()
    chk(pdf.startswith(b'%PDF') and dl.value.suggested_filename == 'Relatório de execução - 8.2026.9745-000104-1.pdf', 'PDF baixado com o nome do SEI')
    chk(b'Era o que cabia informar.' in pdf, 'PDF termina com "Era o que cabia informar."')
    chk(any('Relatório de execução' in h['texto'] for h in dem(pg, d4)['historico']), 'gerar o PDF registra no histórico')
    clk(pg, '.relat [data-acao=fechar-modal]')
    clk(pg, '[data-acao=concluir-dem]'); clk(pg, '.confirma [data-acao=confirmar]')
    x = dem(pg, d4); chk(x['situacao'] == 'concluida' and x['responsavel'] is None and x['tecnico'] == ana, 'concluída fica com o Setor e guarda quem atendeu')
    clk(pg, '[data-acao=aba][data-v=dados]')
    chk(pg.is_disabled('#f-desc') and pg.query_selector('form[data-form=principal]') is None, 'demanda concluída fica somente leitura')
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
    chk('Somente consulta' in texto(pg, '.det-id') and pg.query_selector('#d-status') is None and pg.is_disabled('#f-desc'), 'sem login, o card abre só para consulta')
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
    clk(pg, '[data-acao=menu-conta]'); chk('1 pedido' in texto(pg, '[data-acao=equipe]'), 'menu do coordenador avisa o pedido pendente'); clk(pg, '[data-acao=equipe]')
    chk('Carla Dias' in texto(pg, '.sol-bloco'), 'pedido aparece em Equipe')
    clk(pg, '[data-acao=sol-aprovar]'); senha_carla = texto(pg, '.senha-tmp').strip()
    chk(len(senha_carla) == 10 and pessoa(pg, 'carla')['perfil'] == 'TECNICO', 'aprovar cria a conta com senha temporária')
    clk(pg, '.confirma [data-acao=fechar-modal]')

    # ------------------------------------------------------------------ desativar quem tem demandas: transfere antes
    pg.evaluate(f"document.querySelector('[data-acao=eq-desativar][data-v=\"{ana}\"]').click()"); espera(pg)
    chk(pg.query_selector('form[data-form=equipe-transf]') is not None, 'desativar quem tem demandas em aberto pede a transferência')
    pg.select_option('#tr-dest', bruno); enviar(pg, 'form[data-form=equipe-transf]')
    chk(not pessoa(pg, 'ana.souza')['ativo'] and all(d['responsavel'] != ana for d in api(pg, 'mudancas') if d['situacao'] in ('nova', 'acionada', 'atendimento', 'pendente')), 'ninguém desativado fica com demanda em aberto')
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
