/* =====================================================================================================
   Controle de Demandas de Mudanças · DITIC-DSUP · TJRS
   Protótipo das telas em JavaScript puro (sem frameworks; o visual usa o Bootstrap 5 local).
   Um arquivo só, em três partes:
     1. Catálogos (locais, regiões, serviços da CDS)
     2. Relatório de execução em PDF (gerador próprio, sem bibliotecas)
     3. Aplicação: estado, regras do fluxo, telas e eventos
   Estado em memória + localStorage do navegador. No sistema real, os pontos marcados com "API:" viram
   chamadas fetch para o back-end Spring Boot (ver README.md).
   Segurança: todo texto vindo de dados passa por esc() antes de entrar no HTML; nada de eval/new Function;
   nenhum recurso externo (funciona offline).
   ===================================================================================================== */
(function () {
  'use strict';

  // ================================================================== 1. catálogos
  /* Locais atendidos: Porto Alegre (prédios) e comarcas do interior */
  const CATALOGO_LOCAIS = {"poa": ["Tribunal de Justiça", "Tribunal de Justiça - Anexo", "Palácio da Justiça", "Foro Central - Prédio I", "Foro Central - Prédio II", "Foro Regional da Restinga", "Foro Regional da Tristeza", "Foro Regional da Zona Leste", "Foro Regional da Zona Norte", "Foro Regional do Alto Petrópolis", "Foro Regional do Partenon", "Foro Regional do Sarandi", "Transporte - Garagem"], "interior": ["Agudo", "Alegrete", "Alvorada", "Antônio Prado", "Arroio do Meio", "Arroio do Tigre", "Arroio Grande", "Arvorezinha", "Augusto Pestana", "Bagé", "Barra do Ribeiro", "Bento Gonçalves", "Bom Jesus", "Butiá", "Caçapava do Sul", "Cacequi", "Cachoeira do Sul", "Cachoeirinha", "Camaquã", "Campina das Missões", "Campo Bom", "Campo Novo", "Candelária", "Canela", "Canguçu", "Canoas", "Capão da Canoa", "Carazinho", "Carlos Barbosa", "Casca", "Catuipe", "Caxias do Sul", "Cerro Largo", "Charqueadas", "Constantina", "Coronel Bicaco", "Crissiumal", "Cruz Alta", "Dois Irmãos", "Dom Pedrito", "Eldorado do Sul", "Encantado", "Encruzilhada do Sul", "Erechim", "Espumoso", "Estância Velha", "Esteio", "Estrela", "Farroupilha", "Faxinal do Soturno", "Feliz", "Flores da Cunha", "Frederico Westphalen", "Garibaldi", "Gaurama", "General Câmara", "Getúlio Vargas", "Giruá", "Gramado", "Gravataí", "Guaíba", "Guaporé", "Guarani das Missões", "Herval", "Horizontina", "Ibirubá", "Igrejinha", "Ijuí", "Iraí", "Itaqui", "Ivoti", "Jaguarão", "Jaguari", "Júlio de Castilhos", "Lagoa Vermelha", "Lajeado", "Lavras do Sul", "Marau", "Marcelino Ramos", "Montenegro", "Mostardas", "Não Me Toque", "Nonoai", "Nova Petrópolis", "Nova Prata", "Novo Hamburgo", "Osório", "Palmares do Sul", "Palmeira das Missões", "Panambi", "Parobé", "Passo Fundo", "Pedro Osório", "Pelotas", "Pinheiro Machado", "Piratini", "Planalto", "Portão", "Porto Xavier", "Quaraí", "Restinga Seca", "Rio Grande", "Rio Pardo", "Rodeio Bonito", "Ronda Alta", "Rosário do Sul", "Salto do Jacuí", "Sananduva", "Santa Bárbara do Sul", "Santa Cruz do Sul", "Santa Maria", "Santa Rosa", "Santa Vitória do Palmar", "Santana do Livramento", "Santiago", "Santo Ângelo", "Santo Antônio da Patrulha", "Santo Antônio das Missões", "Santo Augusto", "Santo Cristo", "São Borja", "São Francisco de Assis", "São Francisco de Paula", "São Gabriel", "São Jerônimo", "São José do Norte", "São José do Ouro", "São Leopoldo", "São Lourenço do Sul", "São Luiz Gonzaga", "São Marcos", "São Pedro do Sul", "São Sebastião do Caí", "São Sepé", "São Valentim", "São Vicente do Sul", "Sapiranga", "Sapucaia do Sul", "Sarandi", "Seberi", "Sobradinho", "Soledade", "Tapejara", "Tapera", "Tapes", "Taquara", "Taquari", "Tenente Portela", "Terra de Areia", "Teutônia", "Torres", "Tramandai", "Três Coroas", "Três de Maio", "Três Passos", "Triunfo", "Tucunduva", "Tupanciretã", "Uruguaiana", "Vacaria", "Venâncio Aires", "Vera Cruz", "Veranópolis", "Viamão"]};
  /* Região de cada comarca do interior */
  const REGIAO_COMARCA = {"Agudo": "Centro Ocidental", "Alegrete": "Sudoeste", "Alvorada": "Metropolitana", "Antônio Prado": "Nordeste", "Arroio do Meio": "Centro Oriental", "Arroio do Tigre": "Centro Oriental", "Arroio Grande": "Sudeste", "Arvorezinha": "Nordeste", "Augusto Pestana": "Noroeste", "Bagé": "Sudoeste", "Barra do Ribeiro": "Metropolitana", "Bento Gonçalves": "Nordeste", "Bom Jesus": "Nordeste", "Butiá": "Metropolitana", "Caçapava do Sul": "Sudeste", "Cacequi": "Centro Ocidental", "Cachoeira do Sul": "Centro Oriental", "Cachoeirinha": "Metropolitana", "Camaquã": "Metropolitana", "Campina das Missões": "Noroeste", "Campo Bom": "Metropolitana", "Campo Novo": "Noroeste", "Candelária": "Centro Oriental", "Canela": "Metropolitana", "Canguçu": "Sudeste", "Canoas": "Metropolitana", "Capão da Canoa": "Metropolitana", "Carazinho": "Noroeste", "Carlos Barbosa": "Nordeste", "Casca": "Noroeste", "Catuipe": "Noroeste", "Caxias do Sul": "Nordeste", "Cerro Largo": "Noroeste", "Charqueadas": "Metropolitana", "Constantina": "Noroeste", "Coronel Bicaco": "Noroeste", "Crissiumal": "Noroeste", "Cruz Alta": "Noroeste", "Dois Irmãos": "Metropolitana", "Dom Pedrito": "Sudoeste", "Eldorado do Sul": "Metropolitana", "Encantado": "Centro Oriental", "Encruzilhada do Sul": "Sudeste", "Erechim": "Noroeste", "Espumoso": "Noroeste", "Estância Velha": "Metropolitana", "Esteio": "Metropolitana", "Estrela": "Centro Oriental", "Farroupilha": "Nordeste", "Faxinal do Soturno": "Centro Ocidental", "Feliz": "Metropolitana", "Flores da Cunha": "Nordeste", "Frederico Westphalen": "Noroeste", "Garibaldi": "Nordeste", "Gaurama": "Noroeste", "General Câmara": "Metropolitana", "Getúlio Vargas": "Noroeste", "Giruá": "Noroeste", "Gramado": "Metropolitana", "Gravataí": "Metropolitana", "Guaíba": "Metropolitana", "Guaporé": "Nordeste", "Guarani das Missões": "Noroeste", "Herval": "Sudeste", "Horizontina": "Noroeste", "Ibirubá": "Noroeste", "Igrejinha": "Metropolitana", "Ijuí": "Noroeste", "Iraí": "Noroeste", "Itaqui": "Sudoeste", "Ivoti": "Metropolitana", "Jaguarão": "Sudeste", "Jaguari": "Centro Ocidental", "Júlio de Castilhos": "Centro Ocidental", "Lagoa Vermelha": "Nordeste", "Lajeado": "Centro Oriental", "Lavras do Sul": "Sudoeste", "Marau": "Noroeste", "Marcelino Ramos": "Noroeste", "Montenegro": "Metropolitana", "Mostardas": "Metropolitana", "Não Me Toque": "Noroeste", "Nonoai": "Noroeste", "Nova Petrópolis": "Metropolitana", "Nova Prata": "Nordeste", "Novo Hamburgo": "Metropolitana", "Osório": "Metropolitana", "Palmares do Sul": "Metropolitana", "Palmeira das Missões": "Noroeste", "Panambi": "Noroeste", "Parobé": "Metropolitana", "Passo Fundo": "Noroeste", "Pedro Osório": "Sudeste", "Pelotas": "Sudeste", "Pinheiro Machado": "Sudeste", "Piratini": "Sudeste", "Planalto": "Noroeste", "Portão": "Metropolitana", "Porto Xavier": "Noroeste", "Quaraí": "Sudoeste", "Restinga Seca": "Centro Ocidental", "Rio Grande": "Sudeste", "Rio Pardo": "Centro Oriental", "Rodeio Bonito": "Noroeste", "Ronda Alta": "Noroeste", "Rosário do Sul": "Sudoeste", "Salto do Jacuí": "Noroeste", "Sananduva": "Noroeste", "Santa Bárbara do Sul": "Noroeste", "Santa Cruz do Sul": "Centro Oriental", "Santa Maria": "Centro Ocidental", "Santa Rosa": "Noroeste", "Santa Vitória do Palmar": "Sudeste", "Santana do Livramento": "Sudoeste", "Santiago": "Centro Ocidental", "Santo Ângelo": "Noroeste", "Santo Antônio da Patrulha": "Metropolitana", "Santo Antônio das Missões": "Noroeste", "Santo Augusto": "Noroeste", "Santo Cristo": "Noroeste", "São Borja": "Sudoeste", "São Francisco de Assis": "Sudoeste", "São Francisco de Paula": "Nordeste", "São Gabriel": "Sudoeste", "São Jerônimo": "Metropolitana", "São José do Norte": "Sudeste", "São José do Ouro": "Noroeste", "São Leopoldo": "Metropolitana", "São Lourenço do Sul": "Sudeste", "São Luiz Gonzaga": "Noroeste", "São Marcos": "Nordeste", "São Pedro do Sul": "Centro Ocidental", "São Sebastião do Caí": "Metropolitana", "São Sepé": "Centro Ocidental", "São Valentim": "Noroeste", "São Vicente do Sul": "Centro Ocidental", "Sapiranga": "Metropolitana", "Sapucaia do Sul": "Metropolitana", "Sarandi": "Noroeste", "Seberi": "Noroeste", "Sobradinho": "Centro Oriental", "Soledade": "Noroeste", "Tapejara": "Noroeste", "Tapera": "Noroeste", "Tapes": "Metropolitana", "Taquara": "Metropolitana", "Taquari": "Centro Oriental", "Tenente Portela": "Noroeste", "Terra de Areia": "Metropolitana", "Teutônia": "Centro Oriental", "Torres": "Metropolitana", "Tramandai": "Metropolitana", "Três Coroas": "Metropolitana", "Três de Maio": "Noroeste", "Três Passos": "Noroeste", "Triunfo": "Metropolitana", "Tucunduva": "Noroeste", "Tupanciretã": "Centro Ocidental", "Uruguaiana": "Sudoeste", "Vacaria": "Nordeste", "Venâncio Aires": "Centro Oriental", "Vera Cruz": "Centro Oriental", "Veranópolis": "Nordeste", "Viamão": "Metropolitana"};
  /* Os 6 tipos de serviço da CDS, como na tabela servicos do sistema de faturamento */
  const SERVICOS_CDS = ['Instalação', 'Desinstalação', 'Rollout AC', 'Rollout ABC', 'Mudança de Local', 'Mudança de Prédio'];

  // ================================================================== 2. relatório de execução (PDF)
  /* Relatório de execução de mudança: PDF gerado no navegador, sem bibliotecas (Helvetica padrão, A4) */
  const RelatorioPDF = (function () {
    const LARG = { H: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584,350,556,350,222,556,333,1000,556,556,333,1000,667,333,1000,350,611,350,350,222,222,333,333,350,556,1000,333,1000,500,333,944,350,500,667,278,333,556,556,556,556,260,556,333,737,370,556,584,333,737,333,400,584,333,333,333,556,537,278,333,333,365,556,834,834,834,611,667,667,667,667,667,667,1000,722,667,667,667,667,278,278,278,278,722,722,778,778,778,778,778,584,778,722,722,722,722,667,667,611,556,556,556,556,556,556,889,500,556,556,556,556,278,278,278,278,556,556,556,556,556,556,556,584,611,556,556,556,556,500,556,500], B: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,278,333,474,556,556,889,722,238,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611,333,278,333,584,556,333,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500,389,280,389,584,350,556,350,278,556,500,1000,556,556,333,1000,667,333,1000,350,611,350,350,278,278,500,500,350,556,1000,333,1000,556,333,944,350,500,667,278,333,556,556,556,556,280,556,333,737,370,556,584,333,737,333,400,584,333,333,333,611,556,278,333,333,365,556,834,834,834,611,722,722,722,722,722,722,1000,722,667,667,667,667,278,278,278,278,722,722,778,778,778,778,778,584,778,722,722,722,722,667,667,611,556,556,556,556,556,556,889,556,556,556,556,556,278,278,278,278,611,611,611,611,611,611,611,584,611,611,611,611,611,556,611,556] };

    // Unicode → WinAnsi (cp1252); o que não existe vira "?"
    const CP1252 = { 0x20AC: 0x80, 0x201A: 0x82, 0x0192: 0x83, 0x201E: 0x84, 0x2026: 0x85, 0x2020: 0x86, 0x2021: 0x87, 0x02C6: 0x88, 0x2030: 0x89, 0x0160: 0x8A, 0x2039: 0x8B, 0x0152: 0x8C, 0x017D: 0x8E, 0x2018: 0x91, 0x2019: 0x92, 0x201C: 0x93, 0x201D: 0x94, 0x2022: 0x95, 0x2013: 0x96, 0x2014: 0x97, 0x02DC: 0x98, 0x2122: 0x99, 0x0161: 0x9A, 0x203A: 0x9B, 0x0153: 0x9C, 0x017E: 0x9E, 0x0178: 0x9F };
    const cod = (ch) => { const c = ch.codePointAt(0); if (c < 128 || (c >= 0xA0 && c <= 0xFF)) return c; return CP1252[c] || 63; };
    const largura = (txt, f, t) => { let w = 0; for (const ch of String(txt)) w += LARG[f][cod(ch)] || 500; return (w * t) / 1000; };
    const escPdf = (txt) => { let o = ''; for (const ch of String(txt)) { const c = cod(ch); o += c === 40 || c === 41 || c === 92 ? '\\' + String.fromCharCode(c) : String.fromCharCode(c); } return o; };

    // quebra o texto em linhas que cabem na largura (respeita \n)
    function quebrar(txt, f, t, max) {
      const linhas = [];
      String(txt || '').split('\n').forEach((par) => {
        const pal = par.split(/ +/); let l = '';
        pal.forEach((p) => {
          const tenta = l ? l + ' ' + p : p;
          if (largura(tenta, f, t) <= max || !l) l = tenta; else { linhas.push(l); l = p; }
        });
        linhas.push(l);
      });
      return linhas;
    }

    // gerador mínimo de PDF (A4, Helvetica e Helvetica-Bold, texto e linhas)
    function NovoPdf() {
      const A = 842; const paginas = [];
      let atual = null;
      const api = {
        pagina() { atual = []; paginas.push(atual); return api; },
        texto(x, y, txt, o) {
          o = o || {}; const f = o.negrito ? 'B' : 'H'; const t = o.tam || 10;
          let xx = x; if (o.alinha === 'centro') xx = x - largura(txt, f, t) / 2; else if (o.alinha === 'direita') xx = x - largura(txt, f, t);
          atual.push('BT /' + (f === 'B' ? 'F2' : 'F1') + ' ' + t + ' Tf ' + xx.toFixed(2) + ' ' + (A - y).toFixed(2) + ' Td (' + escPdf(txt) + ') Tj ET');
        },
        linha(x1, y1, x2, y2) { atual.push('0.6 w ' + x1.toFixed(2) + ' ' + (A - y1).toFixed(2) + ' m ' + x2.toFixed(2) + ' ' + (A - y2).toFixed(2) + ' l S'); },
        caixa(x, y, w, h) { atual.push('0.6 w ' + x.toFixed(2) + ' ' + (A - y - h).toFixed(2) + ' ' + w.toFixed(2) + ' ' + h.toFixed(2) + ' re S'); },
        bytes() {
          const obj = []; const add = (s) => { obj.push(s); return obj.length; };
          const cat = add('<< /Type /Catalog /Pages 2 0 R >>');
          add(''); // páginas, preenchido abaixo
          const f1 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');
          const f2 = add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');
          const kids = [];
          paginas.forEach((p) => {
            const conteudo = p.join('\n');
            const c = add('<< /Length ' + conteudo.length + ' >>\nstream\n' + conteudo + '\nendstream');
            kids.push(add('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 ' + f1 + ' 0 R /F2 ' + f2 + ' 0 R >> >> /Contents ' + c + ' 0 R >>'));
          });
          obj[1] = '<< /Type /Pages /Kids [' + kids.map((k) => k + ' 0 R').join(' ') + '] /Count ' + kids.length + ' >>';
          let s = '%PDF-1.4\n%\xE2\xE3\xCF\xD3\n'; const offs = [];
          obj.forEach((o, i) => { offs.push(s.length); s += (i + 1) + ' 0 obj\n' + o + '\nendobj\n'; });
          const xref = s.length;
          s += 'xref\n0 ' + (obj.length + 1) + '\n0000000000 65535 f \n' + offs.map((o) => String(o).padStart(10, '0') + ' 00000 n \n').join('');
          s += 'trailer\n<< /Size ' + (obj.length + 1) + ' /Root ' + cat + ' 0 R /Info << /Title (' + escPdf('Relatório de Execução de Mudança') + ') /Producer (DITIC-DSUP Controle de Mudanças) >> >>\nstartxref\n' + xref + '\n%%EOF';
          const b = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i) & 255;
          return b;
        }
      };
      return api;
    }

    // ------------------------------------------------------------------ relatório no layout do modelo-mestre
    // r = { acionamento, execucao, servicos: {predio, desinst, local, inst}, origem: [], destino: [], custo, itens: [], global }
    function gerarRelatorioPDF(r) {
      const pdf = NovoPdf().pagina();
      const L = 85; const R = 510; const W = R - L; const M = L + W / 2; const Q = W / 4;
      const T = 10; // tamanho da tabela
      let y = 78;
      pdf.texto(297.5, y, 'RELATÓRIO DE EXECUÇÃO DE MUDANÇA/INSTALAÇÃO', { negrito: true, tam: 11, alinha: 'centro' });
      y += 25;
      ['Direção de Tecnologia da Informação e Comunicação', 'Departamento de Suporte', 'Serviço de Projetos e Contrato de Suporte'].forEach((l) => { pdf.texto(297.5, y, l, { negrito: true, tam: 10.5, alinha: 'centro' }); y += 13; });
      let topo = y - 4;
      // linha de duas células com texto centralizado (quebra se precisar)
      const duas = (a, b, negrito) => {
        const la = quebrar(a, negrito ? 'B' : 'H', T, W / 2 - 12); const lb = quebrar(b, negrito ? 'B' : 'H', T, W / 2 - 12);
        const n = Math.max(la.length, lb.length); const h = n * 12 + 5;
        la.forEach((l, i) => pdf.texto(L + W / 4, topo + 12 + i * 12, l, { negrito, tam: T, alinha: 'centro' }));
        lb.forEach((l, i) => pdf.texto(M + W / 4, topo + 12 + i * 12, l, { negrito, tam: T, alinha: 'centro' }));
        pdf.caixa(L, topo, W, h); pdf.linha(M, topo, M, topo + h); topo += h;
      };
      const quatro = (vals, negrito) => {
        const h = 17;
        vals.forEach((v, i) => pdf.texto(L + Q * i + Q / 2, topo + 12, v, { negrito, tam: T, alinha: 'centro' }));
        pdf.caixa(L, topo, W, h); [1, 2, 3].forEach((i) => pdf.linha(L + Q * i, topo, L + Q * i, topo + h)); topo += h;
      };
      duas('Data do Acionamento:', 'Data da Execução', true);
      duas(r.acionamento || ' ', r.execucao || ' ', false);
      quatro(['Mudança de Prédio', 'Desinstalação', 'Mudança de Local', 'Instalação'], false);
      const s = r.servicos || {};
      quatro([s.predio, s.desinst, s.local, s.inst].map((x) => (x ? '( X )' : '(   )')), true);
      duas('Local de origem:', 'Local de destino:', true);
      // listas a), b)…
      const lista = (itens, x0, largMax) => {
        const out = []; itens.filter(Boolean).forEach((it, i) => { quebrar(it, 'H', T, largMax - 30).forEach((l, j) => out.push([j ? '' : String.fromCharCode(97 + i) + ')', l])); });
        return out;
      };
      const lo = lista(r.origem || [], L, W / 2); const ld = lista(r.destino || [], M, W / 2);
      const hl = Math.max(80, Math.max(lo.length, ld.length) * 12.5 + 14);
      lo.forEach(([m, l], i) => { if (m) pdf.texto(L + 14, topo + 15 + i * 12.5, m, { tam: T }); pdf.texto(L + 32, topo + 15 + i * 12.5, l, { tam: T }); });
      ld.forEach(([m, l], i) => { if (m) pdf.texto(M + 14, topo + 15 + i * 12.5, m, { tam: T }); pdf.texto(M + 32, topo + 15 + i * 12.5, l, { tam: T }); });
      pdf.caixa(L, topo, W, hl); pdf.linha(M, topo, M, topo + hl); topo += hl;
      duas('Custo (aproximado):', r.custo || ' ', false);
      // corpo do relatório, numa caixa que segue até o fim (quebra de página se precisar)
      const LH = 18; const TB = 10.5; let cx = topo; let yy = topo + 16;
      const fechaCaixa = (fim) => { pdf.caixa(L, cx, W, fim - cx); };
      const garante = () => { if (yy > 790) { fechaCaixa(800); pdf.pagina(); cx = 60; yy = 76; } };
      quebrar('Em atendimento à demanda solicitada a esse DITIC-DSUP, referente às mudanças de equipamentos de informática, informo que foram realizadas:', 'H', TB, W - 12)
        .forEach((l) => { garante(); pdf.texto(L + 5, yy, l, { tam: TB }); yy += LH; });
      yy += LH * 0.6;
      (r.itens || []).filter((x) => String(x).trim()).forEach((it, i) => {
        quebrar(it.trim(), 'H', TB, R - (L + 46) - 8).forEach((l, j) => { garante(); if (!j) pdf.texto(L + 28, yy, (i + 1) + ' -', { tam: TB }); pdf.texto(L + 46, yy, l, { tam: TB }); yy += LH; });
      });
      yy += LH * 0.6;
      if (r.global) { garante(); pdf.texto(L + 46, yy, 'Custo incluído no valor global do contrato.', { tam: TB }); yy += LH; }
      garante(); pdf.texto(L + 46, yy, 'Era o que cabia informar.', { tam: TB }); yy += LH;
      fechaCaixa(Math.max(yy + 6, cx === 60 ? yy + 6 : 755));
      return pdf.bytes();
    }

    return { gerar: gerarRelatorioPDF };
  })();

  // ================================================================== 3. aplicação

  // ------------------------------------------------------------------ catálogos
  // Equipe: técnicos que recebem demandas. Cadastro mantido pelo gestor; técnicos não têm login.
  // O sistema começa sem nenhum técnico: até o gestor cadastrar a equipe, só ele existe.
  // API: GET/POST/PUT /api/equipe (tabela responsavel: id, nome, iniciais, cor, ativo)
  const CORES_EQUIPE = ['#3E7C8A', '#8A6B3D', '#7B6397', '#5A6370', '#4F7A4A', '#A0573C', '#3D5F8F', '#8C4F72'];
  // Login: só o gestor (Administrador) entra no sistema. API: tabela usuario (login, senha_hash, perfil = GESTOR)
  // 'gestor' é o id usado nas versões anteriores do protótipo; fica como apelido para o histórico antigo.
  const GESTORES = [{ id: 'admin', nome: 'Administrador', curto: 'Gestor', ini: 'AD', cor: '#374151', gestor: true, apelidos: ['gestor', 'administrador'] }];
  const EMPRESAS = ['CADI', 'CDS', 'Selbetti', 'WECOM'];
  // SLA: dias corridos mínimos entre o acionamento da empresa e a data de agendamento.
  // Não trava o acionamento (há demandas para o mesmo dia): fora do prazo, avisa e registra no histórico.
  const SLA_ACIONAMENTO = { CDS: 2, WECOM: 2, CADI: 1, Selbetti: 1 };
  // demanda excluída fica na lixeira por este número de dias
  const DIAS_LIXEIRA = 30;
  // situações em aberto (ainda dão trabalho para alguém)
  const ABERTAS = ['nova', 'acionada', 'atendimento', 'pendente'];
  const SITUACOES = [
    { id: 'nova', nome: 'Novas', um: 'Nova', cor: 'nova', dica: 'Mostrar só as demandas novas, ainda sem acionamento' },
    { id: 'acionada', nome: 'Acionadas', um: 'Acionada', cor: 'acio', dica: 'Mostrar só as demandas acionadas' },
    { id: 'atendimento', nome: 'Em Atendimento', um: 'Em atendimento', cor: 'aten' },
    { id: 'pendente', nome: 'Para Validação', um: 'Para validação', cor: 'pend', dica: 'Para validação: o atendimento terminou e aguarda o gestor' },
    { id: 'concluida', nome: 'Concluídas', um: 'Concluída', cor: 'conc' },
    { id: 'cancelada', nome: 'Canceladas', um: 'Cancelada', cor: 'canc' }
  ];
  const LOCAIS = CATALOGO_LOCAIS;
  const REGIAO = REGIAO_COMARCA;
  // finalidade do subticket: serviços de cada empresa
  const SERVICOS = {
    CADI: ['Mudança de Local', 'Configuração', 'Habilitação de Pontos de Rede'],
    CDS: SERVICOS_CDS,
    Selbetti: ['Mudança de Local', 'Instalação', 'Desinstalação', 'Mudança de Prédio'],
    WECOM: ['Instalação', 'Desinstalação', 'Mudança de Local', 'Mudança de Prédio', 'Instalação de Infraestrutura']
  };
  const opcoesServ = (emp, sel) => `<option value="">Escolher serviço…</option>${(SERVICOS[emp] || []).map((x) => `<option ${sel === x ? 'selected' : ''}>${x}</option>`).join('')}`;
  function regiaoDe(c) { return LOCAIS.poa.includes(c) ? 'Metropolitana' : (REGIAO[c] || null); }
  const RE_SEI = /^\d\.\d{4}\.\d{4}\/\d{6}-\d$/;
  const CHAVE = 'ditic-dsup-mudancas-v5';
  // linhas: 10 por folha; post-its: 8 (4 × 2)
  const porFolha = () => (E.vista === 'postits' ? 8 : 10);
  const DIAS_SEMANA = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];

  // ------------------------------------------------------------------ estado
  const copia = (o) => JSON.parse(JSON.stringify(o));
  function carregar() {
    try { const s = localStorage.getItem(CHAVE); if (s) return JSON.parse(s); } catch (e) { /* sem armazenamento */ }
    return null;
  }
  // a chave antiga guardava os cards de exemplo, que saíram do sistema
  try { localStorage.removeItem('ditic-dsup-mudancas-v3'); } catch (e) { /* sem armazenamento */ }
  const salvo = carregar();
  const E = {
    _anim: {}, _k: {},
    demandas: (salvo && Array.isArray(salvo.demandas)) ? salvo.demandas : [],
    equipe: (salvo && Array.isArray(salvo.equipe)) ? salvo.equipe : [],
    usuario: (salvo && GESTORES.some((g) => g.id === salvo.usuario)) ? salvo.usuario : null,
    excluidas: (salvo && Array.isArray(salvo.excluidas)) ? salvo.excluidas : [],
    lixeira: (salvo && Array.isArray(salvo.lixeira)) ? salvo.lixeira : [],
    senhaDefinida: !!(salvo && salvo.senhaDefinida), // primeiro acesso: o gestor precisa criar uma senha
    sitAtivas: new Set((salvo && Array.isArray(salvo.sitAtivas) && salvo.sitAtivas.length === 1 && SITUACOES.some((x) => x.id === salvo.sitAtivas[0])) ? salvo.sitAtivas : ABERTAS),
    busca: '', filtroResp: '', filtroLocal: '', localQ: '', ordCol: 'ag', ordDir: 'desc', folha: 1,
    vista: (salvo && salvo.vista === 'postits') ? 'postits' : 'linhas',
    aberta: null, aba: 'dados',
    modal: null, modalDados: null,
    menu: null, toast: null, destaque: null,
    statusRascunho: null, // status escolhido no select e ainda não salvo
    erros: {}
  };
  function persistir() {
    try {
      localStorage.setItem(CHAVE, JSON.stringify({ demandas: E.demandas, equipe: E.equipe, usuario: E.usuario, sitAtivas: [...E.sitAtivas], vista: E.vista, excluidas: E.excluidas, lixeira: E.lixeira, senhaDefinida: E.senhaDefinida }));
    } catch (e) { /* ignora */ }
  }

  // ------------------------------------------------------------------ utilidades
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const SISTEMA = { id: 'sistema', nome: 'Sistema (automático)', curto: 'Sistema', ini: 'SI', cor: '#9AA3AE' };
  const TECNICO = { id: 'tecnico', nome: 'Técnico (sem login)', curto: 'Técnico', ini: 'TC', cor: '#7A8594' };
  const usr = (id) => E.equipe.find((u) => u.id === id) || GESTORES.find((u) => u.id === id || (u.apelidos || []).includes(id)) || (id === 'sistema' ? SISTEMA : id === 'tecnico' ? TECNICO : undefined);
  const porNome = (a, b) => normal(a.nome).localeCompare(normal(b.nome));
  const ativos = () => E.equipe.filter((u) => u.ativo).sort(porNome);
  const abertasDe = (id) => E.demandas.filter((d) => d.responsavel === id && ABERTAS.includes(d.situacao));
  const nomeUsr = (id) => (usr(id) ? usr(id).nome : (id || 'Sem responsável'));
  const sit = (id) => SITUACOES.find((s) => s.id === id);
  // em telas estreitas as abas rolam: mantém a ativa à vista
  function mostrarAbaAtiva() {
    const box = document.querySelector('.sit-abas'); const b = box && box.querySelector('.sit-aba[aria-selected="true"]');
    if (box && !box.dataset.ouve) { box.dataset.ouve = '1'; box.addEventListener('scroll', () => bordasAbas(box), { passive: true }); }
    if (box) bordasAbas(box);
    if (!b || box.scrollWidth <= box.clientWidth) return;
    const e = b.offsetLeft - box.offsetLeft; const d = e + b.offsetWidth;
    if (e < box.scrollLeft + 16) box.scrollLeft = Math.max(0, e - 16);
    else if (d > box.scrollLeft + box.clientWidth - 28) box.scrollLeft = d - box.clientWidth + 28;
    bordasAbas(box);
  }
  // esmaece só o lado que ainda tem abas escondidas
  function bordasAbas(box) {
    box.classList.toggle('rola-esq', box.scrollLeft > 2);
    box.classList.toggle('rola-dir', box.scrollLeft + box.clientWidth < box.scrollWidth - 2);
  }
  // aba ativa do filtro de situação: 'abertas' (em desenvolvimento: as 4 situações em aberto) ou o id de uma situação
  function abaSit() { return E.sitAtivas.size === 1 ? [...E.sitAtivas][0] : 'abertas'; }
  const num4 = (n) => String(n).padStart(4, '0');
  const pad = (n) => String(n).padStart(2, '0');
  function hojeISO() { const d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function agoraISO() { const d = new Date(); return hojeISO() + 'T' + pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function br(iso) { if (!iso) return ''; const [y, m, d] = iso.slice(0, 10).split('-'); return d + '/' + m + '/' + y; }
  function brHora(iso) { return br(iso) + (iso.length > 10 ? ' às ' + iso.slice(11, 16) : ''); }
  function semana(iso) { return DIAS_SEMANA[new Date(iso.slice(0, 10) + 'T12:00').getDay()]; }
  function dias(iso) { const a = new Date(iso.slice(0, 10) + 'T12:00'); const b = new Date(hojeISO() + 'T12:00'); return Math.round((a - b) / 864e5); }
  function agendaTexto(d) {
    if (!d.inicio) return 'Sem data agendada';
    if (!d.fim || d.fim === d.inicio) return br(d.inicio);
    return br(d.inicio) + ' até ' + br(d.fim);
  }
  const variosDias = (d) => !!d.fim && d.fim !== d.inicio;
  // a hora é a do início, no primeiro dia: 12/11/2026 às 09:00 até 13/11/2026
  function agendaComHora(d) {
    if (!d.inicio || !d.hora) return agendaTexto(d);
    return br(d.inicio) + ' às ' + d.hora + (variosDias(d) ? ' até ' + br(d.fim) : '');
  }
  function agendaCurta(d) { return d.inicio ? semana(d.inicio) + ', ' + agendaTexto(d) : 'Sem data'; }
  const demanda = (id) => E.demandas.find((d) => d.id === id);
  // sem login quem altera é o técnico: o autor é quem está com a demanda
  function registrar(d, texto, autor) { d.historico.push({ data: agoraISO(), usuario: autor || E.usuario || (d.responsavel && d.responsavel !== 'admin' ? d.responsavel : 'tecnico'), texto }); }
  const normal = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  function fmtSei(v) {
    const g = String(v || '').replace(/\D/g, '').slice(0, 16);
    let o = g.slice(0, 1);
    if (g.length > 1) o += '.' + g.slice(1, 5);
    if (g.length > 5) o += '.' + g.slice(5, 9);
    if (g.length > 9) o += '/' + g.slice(9, 15);
    if (g.length > 15) o += '-' + g.slice(15, 16);
    return o;
  }
  // cor só no formato #RRGGBB (vem do cadastro da equipe; nada de texto livre dentro do style)
  const corOk = (c) => (/^#[0-9a-f]{6}$/i.test(String(c)) ? c : '#5A6370');
  function avatar(id, cls) {
    const u = usr(id);
    return u ? `<span class="avatar ${cls || ''} ${u.ativo === false ? 'inativo' : ''}" style="background:${corOk(u.cor)}" title="${esc(u.nome)}${u.ativo === false ? ' (inativo)' : ''}">${esc(u.ini)}</span>` : `<span class="avatar vazio ${cls || ''}">?</span>`;
  }
  // ------------------------------------------------------------------ caixa de cada pessoa
  // aviso = { tipo: 'nova' | 'retornou' | 'atendimento' | 'pendente' | 'status', para: id de quem recebe, em }; some quando o card é aberto
  function avisar(d, tipo, para) { d.aviso = para ? { tipo, para, em: agoraISO() } : null; }
  // muda o responsável e avisa quem recebe: NOVA na primeira vez que a demanda entra na caixa de alguém, RETORNOU nas outras
  function atribuir(d, novo) {
    novo = novo || null;
    // Em atendimento e Para validação nunca ficam sem responsável: no mínimo, o gestor
    if (!novo && TRAVADOS.includes(d.situacao)) { if (d.responsavel && d.responsavel !== 'admin') d.tecnico = d.responsavel; novo = 'admin'; }
    if (!d.passou) d.passou = d.responsavel ? [d.responsavel] : [];
    if (novo === d.responsavel) return;
    d.responsavel = novo;
    if (!novo) { if (d.aviso && d.aviso.tipo !== 'pendente') d.aviso = null; return; }
    avisar(d, d.passou.length ? 'retornou' : 'nova', novo);
    if (!d.passou.includes(novo)) d.passou.push(novo);
  }
  // Carga de cada demanda: Cadastrada e Acionada ficam com o técnico; Em atendimento e Pendente ficam com o gestor;
  // Concluída fica com o setor, sem atribuição. O técnico que atendeu fica guardado em d.tecnico (e no histórico).
  const nomeResp = (id) => (id === 'admin' ? 'Gestor' : id ? nomeUsr(id) : 'sem responsável');
  function regResp(d, de, para, motivo, autor) { registrar(d, 'Responsável alterado: ' + nomeResp(de) + ' → ' + (para === 'setor' ? 'Setor' : nomeResp(para)) + (motivo ? ' (' + motivo + ')' : '') + '.', autor); }
  function paraGestor(d, autor) {
    if (d.responsavel === 'admin') return;
    const ant = d.responsavel;
    if (ant) d.tecnico = ant;
    d.responsavel = 'admin';
    regResp(d, ant, 'admin', 'carga do gestor', autor);
  }
  function paraSetor(d, autor) {
    const t = d.responsavel && d.responsavel !== 'admin' ? d.responsavel : d.tecnico;
    if (t) d.tecnico = t;
    const ant = d.responsavel;
    d.responsavel = null; d.aviso = null;
    if (ant) regResp(d, ant, 'setor', 'concluída, sem atribuição', autor);
    return t;
  }
  const avisoVisivel = (d) => d.aviso || null;
  function textoAviso(a) {
    const quem = a.para === 'admin' ? 'o gestor' : (usr(a.para) ? usr(a.para).curto : '');
    if (a.tipo === 'pendente') return 'Para validação · com ' + quem + ' · ainda não aberta';
    if (a.tipo === 'status') return 'Status alterado · com ' + quem + ' · ainda não aberta';
    if (a.tipo === 'atendimento') return 'Em atendimento · com ' + quem + ' · ainda não aberta';
    return (a.tipo === 'nova' ? 'Nova para ' : 'Retornou para ') + quem + ' · ainda não aberta';
  }
  // quem está com a demanda: técnico, Gestor ou Setor (concluídas)
  function avatarCarga(d, cls) {
    if (d.situacao === 'concluida' && !d.responsavel) return `<span class="avatar ${cls || 'sm'} setor" title="Setor${d.tecnico ? ' · atendida por ' + esc(nomeUsr(d.tecnico)) : ''}">${svg(cls === 'xs' ? 10 : 12, '<path d="M4 20V9l8-5 8 5v11"/><path d="M9 20v-6h6v6"/>', 2)}</span>`;
    return avatar(d.responsavel, cls || 'sm');
  }
  function cargaHtml(d) {
    const u = usr(d.responsavel);
    const nome = d.situacao === 'concluida' && !d.responsavel ? '<span class="resp-nome setor">Setor</span>' : `<span class="resp-nome">${u ? esc(u.curto) : 'Sem responsável'}</span>`;
    return nome + avatarCarga(d);
  }
  // Nova cujo período já terminou sem acionamento: bolinha vermelha e data em vermelho
  const vencida = (d) => d.situacao === 'nova' && !!d.inicio && (d.fim || d.inicio) < hojeISO();
  const pontoAviso = (d) => {
    const a = avisoVisivel(d); const v = vencida(d);
    const azul = a ? `<span class="nv-ponto ${v ? 'par' : ''}" title="${esc(textoAviso(a))}"><span class="visually-hidden">${esc(textoAviso(a))}</span></span>` : '';
    return azul + (v ? `<span class="nv-ponto venc ${a ? 'par' : ''}" title="Data vencida, demanda ainda não acionada"><span class="visually-hidden">Data vencida, demanda ainda não acionada</span></span>` : '');
  };
  // o card foi aberto: a demanda foi vista e a bolinha sai (chamado só no momento da abertura, em desenhar())
  function marcarVisto() {
    const d = E.aberta && demanda(E.aberta);
    if (d && d.aviso) { d.aviso = null; persistir(); }
  }

  // ------------------------------------------------------------------ status automáticos pela data de agendamento
  // Acionada → Em atendimento no dia de início; Acionada/Em atendimento → Pendente de conclusão um dia depois do fim
  // (vai para o gestor). Pendente não volta mais: só avança para Concluída (o gestor pode devolver ao técnico, ainda Pendente).
  // API: no sistema real isto roda no servidor (tarefa agendada diária, ex.: @Scheduled no Spring), não no navegador
  function automatizar() {
    const hoje = hojeISO(); let n = 0;
    E.demandas.forEach((d) => {
      if (!d.inicio) return;
      const fim = d.fim || d.inicio;
      if (['acionada', 'atendimento'].includes(d.situacao) && fim < hoje) {
        const de = sit(d.situacao).um;
        d.situacao = 'pendente';
        registrar(d, 'Status alterado automaticamente: ' + de + ' → Para validação (o atendimento previsto terminou em ' + br(fim) + ').', 'sistema');
        paraGestor(d, 'sistema');
        avisar(d, 'pendente', 'admin'); n++;
      } else if (d.situacao === 'acionada' && d.inicio <= hoje) {
        d.situacao = 'atendimento';
        registrar(d, 'Status alterado automaticamente: Acionada → Em atendimento (início do agendamento em ' + br(d.inicio) + ').', 'sistema');
        paraGestor(d, 'sistema');
        avisar(d, 'atendimento', 'admin'); n++;
      }
    });
    return n + limparLixeira();
  }

  // ------------------------------------------------------------------ lixeira
  // API: no sistema real a remoção definitiva roda no servidor, junto da tarefa agendada diária
  const diasRestantes = (x) => DIAS_LIXEIRA + dias(x.excluidaEm);
  function limparLixeira() {
    const vencidas = E.lixeira.filter((x) => diasRestantes(x) <= 0);
    if (!vencidas.length) return 0;
    vencidas.forEach((x) => E.excluidas.push({ data: agoraISO(), usuario: 'sistema', id: x.id, sei: x.sei, comarca: x.comarca, situacao: x.situacao, texto: 'Demanda removida definitivamente da lixeira (' + DIAS_LIXEIRA + ' dias sem restauração).' }));
    E.lixeira = E.lixeira.filter((x) => diasRestantes(x) > 0);
    return vencidas.length;
  }

  function prazo(d) {
    if (!ABERTAS.includes(d.situacao)) return '';
    if (!d.inicio) return d.situacao === 'nova' ? '<span class="badge prazo">A agendar</span>' : '';
    const ini = dias(d.inicio); const fim = dias(d.fim || d.inicio);
    if (d.situacao === 'pendente') return fim < 0 ? '<span class="badge prazo pend">Há ' + (-fim) + (fim === -1 ? ' dia' : ' dias') + '</span>' : '';
    if (d.situacao === 'atendimento') return fim <= 0 ? '<span class="badge prazo aten">Último dia</span>' : (ini <= 0 ? '<span class="badge prazo aten">Até ' + br(d.fim || d.inicio).slice(0, 5) + '</span>' : '<span class="badge prazo">Em ' + ini + (ini === 1 ? ' dia' : ' dias') + '</span>');
    if (fim < 0) return d.situacao === 'acionada' ? '<span class="badge prazo">Há ' + (-fim) + (fim === -1 ? ' dia' : ' dias') + '</span>' : '';
    if (ini <= 0) return '<span class="badge prazo hoje">Hoje</span>';
    // contagem até o início: 02 dias, 01 dia, 120 dias (no máximo 3 dígitos)
    const n = Math.min(ini, 999);
    return '<span class="badge prazo">' + String(n).padStart(2, '0') + (n === 1 ? ' dia' : ' dias') + '</span>';
  }

  // ------------------------------------------------------------------ ícones
  const svg = (w, body, extra) => `<svg width="${w}" height="${w}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${extra || 2}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;
  const I = {
    mais: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/></svg>',
    busca: svg(15, '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>', 2.2),
    local: svg(14, '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'),
    agenda: svg(14, '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),
    check: svg(13, '<path d="m5 12.5 4.5 4.5L19 7.5"/>', 2.6),
    fechar: svg(18, '<path d="M6 6l12 12M18 6 6 18"/>'),
    copiar: svg(14, '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>'),
    pontos: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>',
    lixo: svg(15, '<path d="M4 7h16"/><path d="M9 7V4.8h6V7"/><path d="M6.5 7l.9 12.2a1.5 1.5 0 0 0 1.5 1.3h6.2a1.5 1.5 0 0 0 1.5-1.3L17.5 7"/>', 1.9),
    baixar: svg(15, '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>'),
    texto: svg(14, '<path d="M4 6h16M4 11h16M4 16h10"/>'),
    alerta: svg(16, '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.4h.01"/>'),
    triangulo: svg(22, '<path d="M10.3 4.2 2.6 17.5A2 2 0 0 0 4.3 20.5h15.4a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4M12 17h.01"/>', 1.9),
    usuario: svg(18, '<circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 19.5c1.3-3.2 4-4.9 7.2-4.9s5.9 1.7 7.2 4.9"/>', 1.8),
    usuarioP: svg(16, '<circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 19.5c1.3-3.2 4-4.9 7.2-4.9s5.9 1.7 7.2 4.9"/>', 1.8),
    cadeadoP: svg(16, '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>', 1.8),
    olho: svg(17, '<path d="M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>', 1.8),
    sair: svg(16, '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 17l-5-5 5-5M5 12h11"/>', 1.9),
    cadeado: svg(22, '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>', 1.8),
    setaBaixo: svg(14, '<path d="m6 9 6 6 6-6"/>', 2.2),
    checkG: svg(44, '<path d="m5 12.5 4.5 4.5L19 7.5"/>', 2.2),
    ticket: svg(14, '<path d="M3 8a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 0-2 2H5a2 2 0 0 0-2-2v-2a2 2 0 0 0 0-4z"/><path d="M14 6v12" stroke-dasharray="2 2.2"/>', 1.8),
    pessoa: svg(14, '<circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 19.5c1.3-3.2 4-4.9 7.2-4.9s5.9 1.7 7.2 4.9"/>', 1.9),
    vLinhas: svg(17, '<path d="M9 6.5h11M9 12h11M9 17.5h11"/><path d="M4.5 6.5h.01M4.5 12h.01M4.5 17.5h.01" stroke-width="2.8"/>', 2),
    vPostits: svg(17, '<rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1.5"/><rect x="13" y="3.5" width="7.5" height="7.5" rx="1.5"/><rect x="3.5" y="13" width="7.5" height="7.5" rx="1.5"/><path d="M13 13h7.5v4.5L17.5 20.5H13z"/>', 1.9),
    xP: svg(12, '<path d="M6 6l12 12M18 6 6 18"/>', 2.4)
  };

  // concluída fica com o setor: não é uma demanda "sem responsável"
  const semResponsavel = (d) => !d.responsavel && d.situacao !== 'concluida';
  // filtro de responsável: lista própria, com o número de demandas de cada um num círculo na cor da pessoa
  function filtroResp() {
    // todos os cards que estão com cada um, independente de aba, pesquisa e demais filtros
    const n = (id) => E.demandas.filter((d) => (id === '_sem' ? semResponsavel(d) : d.responsavel === id)).length;
    const lista = ativos().concat(E.equipe.filter((x) => !x.ativo && (n(x.id) || E.filtroResp === x.id)).sort(porNome), [Object.assign({}, GESTORES[0], { nome: 'Gestor', ativo: true })]);
    const max = Math.max(1, ...lista.map((x) => n(x.id)));
    const sel = E.filtroResp; const u = usr(sel); const aberto = E.menu === 'resp';
    const linha = (id, nome, av) => {
      const q = n(id); const on = sel === id;
      return `<button type="button" role="option" aria-selected="${on}" class="dropdown-item op-resp ${on ? 'escolhido' : ''}" data-acao="resp-escolher" data-v="${id}">
        ${av}
        <span class="op-txt"><span class="op-nome">${esc(nome)}</span>${id === '_sem' ? '' : `<span class="carga" aria-hidden="true"><i style="width:${Math.round((q / max) * 100)}%;background:${usr(id) ? corOk(usr(id).cor) : 'var(--accent)'}"></i></span>`}</span>
        <span class="op-n">${q}</span>
        <span class="op-check" aria-hidden="true">${on ? I.check : ''}</span>
      </button>`;
    };
    return `<div class="menu-ancora filtro ${sel ? 'ativo' : ''} ${aberto ? 'aberto' : ''}">
      <button type="button" class="filtro-btn" data-acao="resp-pop" aria-haspopup="listbox" aria-expanded="${aberto}" aria-label="Filtrar por responsável${sel ? ': ' + esc(u ? u.nome : 'sem responsável') : ''}">
        ${sel ? (u ? avatar(u.id, 'xs') : '<span class="avatar xs vazio">?</span>') : `<span class="filtro-ico">${I.pessoa}</span>`}
        <span class="filtro-nome">${sel ? (u ? esc(u.curto) : 'Sem responsável') : 'Responsável'}</span>
        ${sel ? `<span class="badge filtro-n">${n(sel)}</span>` : `<span class="filtro-seta">${I.setaBaixo}</span>`}
      </button>
      ${sel ? `<button type="button" class="filtro-limpa" data-acao="resp-escolher" data-v="" aria-label="Limpar filtro de responsável" title="Limpar filtro">${I.xP}</button>` : ''}
      ${aberto ? `<div class="dropdown-menu show pop-resp" role="listbox" aria-label="Responsável">
        <div class="pop-cab"><span>Responsável</span><span>Demandas</span></div>
        ${lista.map((x) => linha(x.id, x.nome + (x.ativo ? '' : ' (inativo)'), avatar(x.id, 'sm'))).join('')}
        <hr class="dropdown-divider">
        ${linha('_sem', 'Sem responsável', '<span class="avatar sm vazio">?</span>')}
      </div>` : ''}
    </div>`;
  }

  // filtro de local: mesma aparência do de responsável, com busca e só os locais que têm demandas
  function filtroLocal() {
    const base = E.demandas.filter((d) => E.sitAtivas.has(d.situacao));
    const n = (l) => base.filter((d) => d.comarca === l).length;
    const usados = [...new Set(E.demandas.map((d) => d.comarca).filter(Boolean))];
    const locais = usados.sort((a, b) => normal(a).localeCompare(normal(b), 'pt-BR'));
    const sel = E.filtroLocal; const aberto = E.menu === 'local';
    const op = (l) => { const q = n(l); const on = sel === l;
      return `<button type="button" role="option" aria-selected="${on}" class="dropdown-item op-local ${on ? 'escolhido' : ''} ${q ? '' : 'zero'}" data-acao="local-escolher" data-v="${esc(l)}" data-busca="${esc(normal(l + ' ' + (REGIAO[l] || '')))}">
        <span class="op-nome">${esc(l)}${REGIAO[l] ? `<small>${esc(REGIAO[l])}</small>` : ''}</span><span class="op-n">${q}</span><span class="op-check" aria-hidden="true">${on ? I.check : ''}</span></button>`; };
    return `<div class="menu-ancora filtro filtro-local ${sel ? 'ativo' : ''} ${aberto ? 'aberto' : ''}">
      <button type="button" class="filtro-btn" data-acao="local-pop" aria-haspopup="listbox" aria-expanded="${aberto}" aria-label="Filtrar por local${sel ? ': ' + esc(sel) : ''}">
        <span class="filtro-ico">${I.local}</span>
        <span class="filtro-nome">${sel ? esc(sel) : 'Local'}</span>
        ${sel ? `<span class="badge filtro-n">${n(sel)}</span>` : `<span class="filtro-seta">${I.setaBaixo}</span>`}
      </button>
      ${sel ? `<button type="button" class="filtro-limpa" data-acao="local-escolher" data-v="" aria-label="Limpar filtro de local" title="Limpar filtro">${I.xP}</button>` : ''}
      ${aberto ? `<div class="dropdown-menu show pop-local">
        <div class="pop-busca">${I.busca}<input id="f-local-q" class="form-control" type="search" autocomplete="off" placeholder="Buscar comarca, prédio ou região" value="${esc(E.localQ)}" aria-label="Buscar local"></div>
        <div class="pop-rol" role="listbox" aria-label="Local">
          ${locais.map(op).join('')}
          <div class="pop-nada" hidden>Nenhum local com esse nome.</div>
        </div>
        <div class="pop-nota">Só aparecem locais que têm demandas.</div>
      </div>` : ''}
    </div>`;
  }
  function filtrarLocais() {
    const inp = document.getElementById('f-local-q'); if (!inp) return;
    const q = normal(inp.value.trim()); let vis = 0;
    document.querySelectorAll('.pop-local .op-local').forEach((b) => { const ok = !q || b.dataset.busca.includes(q); b.hidden = !ok; if (ok) vis++; });
    const nada = document.querySelector('.pop-local .pop-nada'); if (nada) nada.hidden = vis > 0;
  }

  // ------------------------------------------------------------------ filtros
  function visiveis() {
    const q = normal(E.busca.trim());
    let ls = E.demandas.filter((d) => E.sitAtivas.has(d.situacao));
    if (E.filtroResp) ls = ls.filter((d) => (E.filtroResp === '_sem' ? semResponsavel(d) : d.responsavel === E.filtroResp));
    if (E.filtroLocal) ls = ls.filter((d) => d.comarca === E.filtroLocal);
    if (q) {
      ls = ls.filter((d) => normal([d.sei, d.descricao, d.comarca, d.informacoes, num4(d.id), d.ticketPrincipal,
        d.subtickets.map((s) => s.numero + ' ' + s.empresa).join(' ')].join(' ')).includes(q));
    }
    const ordemSit = { nova: 0, acionada: 1, atendimento: 2, pendente: 3, concluida: 4, cancelada: 5 };
    const chave = {
      sei: (d) => d.sei || '',
      dem: (d) => normal(d.comarca),
      ag: (d) => (d.inicio ? d.inicio + (d.hora || '') : ''),
      tk: (d) => d.ticketPrincipal || '',
      st: (d) => ordemSit[d.situacao],
      resp: (d) => normal(usr(d.responsavel) ? usr(d.responsavel).curto : '')
    }[E.ordCol] || ((d) => d.inicio || '');
    const sinal = E.ordDir === 'desc' ? -1 : 1;
    ls.sort((a, b) => {
      const x = chave(a); const y = chave(b);
      // vazios (sem data, sem ticket, sem responsável) sempre no fim
      if ((x === '' || x == null) !== (y === '' || y == null)) return (x === '' || x == null) ? 1 : -1;
      const c = typeof x === 'number' ? x - y : String(x).localeCompare(String(y), 'pt-BR');
      return c * sinal || (b.inicio || '').localeCompare(a.inicio || '') || b.id - a.id;
    });
    return ls;
  }

  // ------------------------------------------------------------------ cabeçalho
  function telaTopo() {
    const u = usr(E.usuario);
    return `
<header class="topo"><div class="topo-in">
  <button type="button" class="marca" data-acao="inicio" aria-label="DITIC-DSUP, Controle de Mudanças, página inicial">
    <b>DITIC-DSUP</b><span>&nbsp;| <span class="longo">Controle de </span>Mudanças</span>
  </button>
  <div class="topo-acoes">
    ${ehGestor() ? `<button type="button" class="btn btn-primary btn-pill btn-nova" data-acao="nova" title="Nova demanda de mudança">${I.mais}<span>Nova demanda</span></button>
    <div class="sep-v" aria-hidden="true"></div>` : ''}
    ${telaConta()}
  </div>
</div></header>`;
  }

  function telaConta() {
    const u = usr(E.usuario);
    if (!u) return `<button type="button" class="btn btn-auth" data-acao="login">${I.usuario}Entrar</button>`;
    return `<div class="menu-ancora">
      <button type="button" class="conta" data-acao="menu-conta" aria-haspopup="menu" aria-expanded="${E.menu === 'conta'}" aria-label="Conta de ${esc(u.nome)}">
        ${avatar(u.id)}<span class="conta-txt"><b>${esc(u.nome)}</b><small>Controle de Mudanças</small></span>${I.setaBaixo}
      </button>
      ${E.menu === 'conta' ? `<div class="dropdown-menu show" role="menu">
        <div class="dropdown-header menu-cab">${avatar(u.id, 'g')}<span><b>${esc(u.nome)}</b><small>Controle de Mudanças</small></span></div>
        ${u.gestor ? `        <button type="button" role="menuitem" class="dropdown-item" data-acao="equipe">${svg(16, '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19c.9-3 3.1-4.6 5.5-4.6s4.6 1.6 5.5 4.6"/><circle cx="16.5" cy="9.5" r="2.6"/><path d="M15.5 14.6c2.3-.2 4.2 1.2 5 4"/>', 1.8)}<span style="flex:1">Equipe</span><small class="menu-n">${ativos().length} ${ativos().length === 1 ? "pessoa" : "pessoas"}</small></button>
        <button type="button" role="menuitem" class="dropdown-item" data-acao="movimentos">${svg(16, '<path d="M4 6h16M4 12h10M4 18h7"/><circle cx="18" cy="16.5" r="3.5"/><path d="M18 15v1.6l1 .8"/>', 1.9)}<span style="flex:1">Movimentações do dia</span></button>
        <button type="button" role="menuitem" class="dropdown-item" data-acao="lixeira">${I.lixo}<span style="flex:1">Lixeira</span><small class="menu-n">${E.lixeira.length}</small></button>` : ''}
        <hr class="dropdown-divider">
        <button type="button" role="menuitem" class="dropdown-item perigo" data-acao="sair">${I.sair}Sair da conta</button>
      </div>` : ''}
    </div>`;
  }

  // ------------------------------------------------------------------ lista
  function botoesFolhas(atual, total) {
    const ns = [];
    for (let i = 1; i <= total; i++) {
      if (total <= 7 || i === 1 || i === total || Math.abs(i - atual) <= 1) ns.push(i);
      else if (ns[ns.length - 1] !== '…') ns.push('…');
    }
    return `<nav aria-label="Folhas"><ul class="pagination folhas">
      <li class="page-item ${atual <= 1 ? 'disabled' : ''}"><button type="button" class="page-link" data-acao="folha" data-v="${atual - 1}" ${atual <= 1 ? 'disabled' : ''} aria-label="Folha anterior">${svg(14, '<path d="m15 6-6 6 6 6"/>', 2.2)}</button></li>
      ${ns.map((n) => n === '…' ? '<li class="page-item disabled"><span class="page-link ret">…</span></li>' : `<li class="page-item ${n === atual ? 'active' : ''}"><button type="button" class="page-link" data-acao="folha" data-v="${n}" ${n === atual ? 'aria-current="page"' : ''} aria-label="Folha ${n}">${n}</button></li>`).join('')}
      <li class="page-item ${atual >= total ? 'disabled' : ''}"><button type="button" class="page-link" data-acao="folha" data-v="${atual + 1}" ${atual >= total ? 'disabled' : ''} aria-label="Próxima folha">${svg(14, '<path d="m9 6 6 6-6 6"/>', 2.2)}</button></li>
    </ul></nav>`;
  }

  function telaPainel() {
    const base = E.demandas;
    const ls = visiveis();
    const POR_FOLHA = porFolha();
    const total = Math.max(1, Math.ceil(ls.length / POR_FOLHA));
    E.folha = Math.min(Math.max(1, E.folha), total);
    const ini = (E.folha - 1) * POR_FOLHA;
    const folha = ls.slice(ini, ini + POR_FOLHA);
    // todos os locais do catálogo, mais algum que exista só nas demandas
    const filtrando = E.busca || E.filtroResp || E.filtroLocal;
    return `
<main class="painel">
  <div class="titulo-linha">
    <h1>Filtro de Demanda</h1>
    <div class="nav sit-abas" role="tablist" aria-label="Filtrar por situação">
      ${(() => {
        const atual = abaSit();
        const nAb = base.filter((d) => ABERTAS.includes(d.situacao)).length;
        const aba = (id, nome, n, cor, dica) => `<button type="button" role="tab" class="nav-link sit-aba ${n ? '' : 'vazia'}" data-acao="sit-aba" data-v="${id}" aria-selected="${atual === id}" tabindex="${atual === id ? 0 : -1}" ${cor ? `style="--aba-cor:var(--${cor}-dot);--aba-bg:var(--${cor}-bg);--aba-ink:var(--${cor}-ink)"` : ''} title="${dica}">${cor ? '<span class="aba-dot" aria-hidden="true"></span>' : ''}<span class="aba-nome" data-t="${nome}">${nome}</span><span class="badge aba-n">${n}</span></button>`;
        const st = (x) => aba(x.id, x.nome, base.filter((d) => d.situacao === x.id).length, x.cor, x.dica || 'Mostrar só ' + x.nome.toLowerCase());
        const sep = '<span class="aba-sep" aria-hidden="true"></span>';
        return aba('abertas', 'Em aberto', nAb, '', 'Novas, acionadas, em atendimento e para validação')
          + sep + SITUACOES.filter((x) => ABERTAS.includes(x.id)).map(st).join('')
          + '<span class="aba-sep aba-grupo" aria-hidden="true"></span>' + SITUACOES.filter((x) => !ABERTAS.includes(x.id)).map(st).join('');
      })()}
    </div>
  </div>

  <div class="filtros" role="search">
    <div class="campo-busca">
      <label for="busca" class="visually-hidden">Pesquisar demandas</label>${I.busca}
      <input id="busca" class="form-control" type="search" autocomplete="off" data-campo="busca" value="${esc(E.busca)}" placeholder="Expediente SEI, ticket, local ou palavra-chave">
    </div>
    ${filtroLocal()}
    ${filtroResp()}
    <div class="btn-group vistas" role="group" aria-label="Visualização">
      <button type="button" class="vista-btn" data-acao="vista" data-v="linhas" aria-pressed="${E.vista === 'linhas'}" aria-label="Ver em linhas" title="Ver em linhas">${I.vLinhas}</button>
      <button type="button" class="vista-btn" data-acao="vista" data-v="postits" aria-pressed="${E.vista === 'postits'}" aria-label="Ver em post-its" title="Ver em post-its">${I.vPostits}</button>
    </div>
  </div>

  <section class="lista vista-${E.vista}" aria-label="Demandas">
    <div class="l-cab ${E.vista === 'postits' ? 'l-ord' : 'l-grade'}" role="row">${E.vista === 'postits' ? '<span class="ord-rot">Ordenar por</span>' : ''}
      ${[['sei', 'Expediente', ''], ['dem', 'Local', ''], ['ag', 'Data', ''], ['tk', 'Ticket', 'h-tk'], ['st', 'Status', ''], ['resp', 'Responsável', 'h-resp']].map(([c, t, cls]) => {
        const at = E.ordCol === c;
        const prox = at ? (E.ordDir === 'asc' ? 'decrescente' : 'crescente') : (c === 'ag' ? 'decrescente' : 'crescente');
        return `<span class="h-col ${cls} ${at ? 'ativa' : ''}" role="columnheader" aria-sort="${at ? (E.ordDir === 'asc' ? 'ascending' : 'descending') : 'none'}">
          <button type="button" class="h-ord" data-acao="ordenar" data-v="${c}" aria-label="${t}: ordenar em ordem ${prox}" title="Ordenar em ordem ${prox}">
            <span class="h-txt">${t}</span>
            <span class="seta-ord ${at ? E.ordDir : ''}" aria-hidden="true">${svg(11, '<path d="M12 5v14M6 13l6 6 6-6"/>', 2.4)}</span>
          </button>
        </span>`;
      }).join('')}
    </div>
    <div class="rolagem ${E.vista === 'postits' ? 'postits' : ''}">
      ${folha.length ? folha.map(E.vista === 'postits' ? telaPostit : telaLinha).join('') : `<div class="vazio-lista">
        <span class="vazio-ico">${svg(26, '<rect x="4" y="5" width="16" height="14" rx="2.5"/><path d="M4 10h16M9 14.5h6"/>', 1.7)}</span>
        <b>Nenhuma demanda por aqui</b>
        <span>Ajuste a pesquisa ou escolha outra situação nas abas acima.</span>
        ${filtrando ? '<button type="button" class="btn btn-sm" data-acao="limpar">Limpar pesquisa e filtros</button>' : (ehGestor() ? `<button type="button" class="btn btn-sm" data-acao="nova">${I.mais}Nova demanda</button>` : '')}
      </div>`}
    </div>
    <div class="l-pe">
      <span class="esq">
        <span>${ls.length ? `Mostrando ${ini + 1}–${ini + folha.length} de ${ls.length} ${ls.length === 1 ? 'demanda' : 'demandas'}` : 'Nenhuma demanda'}</span>
        ${filtrando ? '<button type="button" class="link" data-acao="limpar">Limpar pesquisa e filtros</button>' : ''}
        ${flash('pagina')}
      </span>
      ${botoesFolhas(E.folha, total)}
    </div>
  </section>
</main>`;
  }

  function telaLinha(d) {
    const s = sit(d.situacao); const u = usr(d.responsavel);
    return `
<article class="linha-dem l-grade ${E.destaque === d.id ? 'destaque' + (E._anim.destaque ? ' pulsa' : '') : ''}" data-sit="${esc(d.situacao)}" data-acao="abrir" data-id="${d.id}" tabindex="0" role="button" title="${esc(d.descricao)}" aria-label="Demanda ${esc(d.sei || num4(d.id))}, ${esc(d.comarca)}, ${esc(s.um)}">
  <div class="cel c-sei">
    <span class="sei">${esc(d.sei || 'Fora do SEI')}</span>
    ${d.sei ? `<button type="button" class="mini-copia" data-acao="copiar" data-v="${esc(d.sei)}" aria-label="Copiar expediente ${esc(d.sei)}" title="Copiar número">${I.copiar}</button>` : ''}
  </div>
  ${pontoAviso(d)}
  <div class="cel c-dem"><span class="ico">${I.local}</span><span class="local">${esc(d.comarca || 'Local não informado')}</span></div>
  <div class="cel c-ag">${d.inicio ? `<span class="ico">${I.agenda}</span><span class="c-data ${vencida(d) ? 'vencida' : ''}">${esc(agendaTexto(d))}</span>${d.hora && !variosDias(d) ? `<span class="c-hora">${esc(d.hora)}</span>` : ''}` : '<span class="c-data vazia">Sem data</span>'}${prazo(d)}</div>
  <div class="cel c-tk">${d.ticketPrincipal ? `<span class="ico">${I.ticket}</span><span class="tk-num">${esc(d.ticketPrincipal)}</span>` : '<span class="tk-vazio">Sem ticket</span>'}</div>
  <div class="cel c-st"><span class="badge selo">${s.um}</span></div>
  <div class="cel c-resp">${cargaHtml(d)}</div>
</article>`;
  }

  // visualização em post-its: o mesmo conteúdo da linha, com a descrição à vista
  function telaPostit(d) {
    const s = sit(d.situacao); const u = usr(d.responsavel);
    return `
<article class="postit ${E.destaque === d.id ? 'destaque' + (E._anim.destaque ? ' pulsa' : '') : ''}" data-sit="${esc(d.situacao)}" data-acao="abrir" data-id="${d.id}" tabindex="0" role="button" aria-label="Demanda ${esc(d.sei || num4(d.id))}, ${esc(d.comarca)}, ${esc(s.um)}">
  ${pontoAviso(d)}
  <div class="pi-topo"><span class="pi-sei">${esc(d.sei || 'Fora do SEI')}</span>${avatarCarga(d)}</div>
  <h3 class="pi-local">${esc(d.comarca || 'Local não informado')}</h3>
  <p class="pi-desc">${esc(d.descricao || 'Sem descrição.')}</p>
  <div class="pi-pe">
    <div class="pi-linha"><span class="pi-data" title="${d.inicio ? esc(agendaComHora(d)) : ''}">${d.inicio ? `${I.agenda}<span class="${vencida(d) ? 'vencida' : ''}">${esc(agendaTexto(d))}</span>${d.hora && !variosDias(d) ? `<span class="c-hora">${esc(d.hora)}</span>` : ''}` : '<span class="vazia">Sem data</span>'}</span>${prazo(d)}</div>
    <div class="pi-linha"><span class="pi-tk">${d.ticketPrincipal ? `${I.ticket}<span>${esc(d.ticketPrincipal)}</span>` : '<span class="vazia">Sem ticket</span>'}</span><span class="badge selo">${s.um}</span></div>
  </div>
</article>`;
  }

  // ------------------------------------------------------------------ modal da demanda
  function bloco(titulo, aside, corpo, pe, cls) {
    return `<section class="card bloco ${cls || ''}">
      <header class="card-header bloco-cab"><h3>${titulo}</h3>${aside ? `<span class="bloco-aside">${aside}</span>` : ''}</header>
      <div class="card-body bloco-corpo">${corpo}</div>
      ${pe ? `<div class="card-footer bloco-pe">${pe}</div>` : ''}
    </section>`;
  }

  function telaDetalhe() {
    const d = demanda(E.aberta); if (!d) return '';
    const s = sit(d.situacao); const u = usr(d.responsavel);
    const abas = [['dados', 'Detalhes', ''], ['tickets', 'Tickets', d.subtickets.length + (d.ticketPrincipal ? 1 : 0)], ['hist', 'Histórico', d.historico.length]];
    return `
<div class="modal d-block det-fundo ${E._anim.det ? 'anim' : ''}" tabindex="-1" data-acao="fundo-modal">
<div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
<section class="modal-content det" data-sit="${esc(d.situacao)}" role="dialog" aria-modal="true" aria-labelledby="det-titulo">
  <header class="modal-header det-cab">
    <div class="det-id">
      <div class="det-l1"><h2 id="det-titulo">${esc(predio(d.comarca) || 'Local não informado')}</h2>${statusCab(d)}</div>
      <div class="det-l2">
        ${d.sei ? `<span class="mono">${esc(d.sei)}</span><button type="button" class="mini-copia vis" data-acao="copiar" data-v="${esc(d.sei)}" aria-label="Copiar expediente" title="Copiar número">${I.copiar}</button>` : '<span>Fora do SEI</span>'}
        <span class="sep" aria-hidden="true"></span><span class="l2-it ${d.ticketPrincipal ? 'l2-tk' : 'l2-sem'}">${I.ticket}${d.ticketPrincipal ? 'Ticket ' + esc(d.ticketPrincipal) : 'Sem ticket'}</span>
        <span class="sep" aria-hidden="true"></span><span class="l2-it">${I.agenda}${d.inicio ? esc(agendaComHora(d)) : 'A agendar'}</span>
        <span class="sep" aria-hidden="true"></span><span class="l2-it">Região: ${esc(regiaoDe(d.comarca) || 'não identificada')}</span>
        <span class="sep" aria-hidden="true"></span><span class="l2-it">${avatarCarga(d, 'xs')}${d.situacao === 'concluida' && !d.responsavel ? 'Setor' + (d.tecnico ? ' · atendida por ' + esc(nomeUsr(d.tecnico)) : '') : u ? esc(u.id === 'admin' ? 'Gestor' : u.nome) + (u.id === 'admin' && d.tecnico ? ' · técnico ' + esc(nomeUsr(d.tecnico)) : '') : 'Sem responsável'}</span>
      </div>
    </div>
    <button type="button" class="btn btn-icone" data-acao="fechar-det" aria-label="Fechar">${I.fechar}</button>
  </header>

  <nav class="nav nav-underline abas" role="tablist">
    ${abas.map(([id, rot, n]) => `<button type="button" role="tab" class="nav-link" id="aba-${id}" aria-selected="${E.aba === id}" data-acao="aba" data-v="${id}">${rot}${n !== '' ? ` <span class="badge qtd">${n}</span>` : ''}</button>`).join('')}
  </nav>
  <div class="modal-body det-corpo" role="tabpanel" aria-labelledby="aba-${E.aba}">
    ${E.aba === 'dados' ? abaDados(d) : E.aba === 'tickets' ? abaTickets(d) : abaHist(d)}
  </div>

  <footer class="modal-footer det-pe">
    <div class="menu-ancora">
      <button type="button" class="btn btn-link btn-suave" data-acao="menu-mais" aria-haspopup="menu" aria-expanded="${E.menu === 'mais'}">${I.pontos}Mais ações</button>
      ${E.menu === 'mais' ? `<div class="dropdown-menu show cima" role="menu">
        ${d.situacao === 'pendente' && ehGestor() ? `<button type="button" role="menuitem" class="dropdown-item" data-acao="relatorio" data-id="${d.id}">${I.baixar}Gerar relatório de mudança</button>` : ''}
        ${d.situacao === 'pendente' && ehGestor() && d.responsavel === 'admin' && d.tecnico ? `<button type="button" role="menuitem" class="dropdown-item" data-acao="devolver-tec" data-id="${d.id}">${svg(16, '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>', 2)}Devolver a ${esc(nomeUsr(d.tecnico))} (atendimento extra)</button>` : ''}
        ${d.situacao === 'atendimento' && ehGestor() ? `<button type="button" role="menuitem" class="dropdown-item" data-acao="alterar-conclusao" data-id="${d.id}">${I.agenda}Alterar Data para Conclusão</button>` : ''}
        <button type="button" role="menuitem" class="dropdown-item" data-acao="acionamento" data-id="${d.id}">${I.texto}Gerar informação de acionamento</button>
        <button type="button" role="menuitem" class="dropdown-item" data-acao="copiar-tickets" data-id="${d.id}">${I.copiar}Copiar tickets em texto</button>
        ${ehGestor() ? `<hr class="dropdown-divider">
        ${!['concluida', 'cancelada'].includes(d.situacao) ? `<button type="button" role="menuitem" class="dropdown-item perigo" data-acao="cancelar" data-id="${d.id}">${svg(16, '<circle cx="12" cy="12" r="8.5"/><path d="m6 6 12 12"/>', 2)}Cancelar demanda</button>` : ''}
        <button type="button" role="menuitem" class="dropdown-item perigo" data-acao="excluir" data-id="${d.id}">${I.lixo}Excluir demanda</button>` : ''}
      </div>` : ''}
    </div>
    ${flash('det')}
    <span class="esp"></span>
    ${(E.aba === 'dados' && podeEditar(d)) || E.statusRascunho ? `<span class="sujo" id="sujo-txt" ${E.sujo || E.statusRascunho ? '' : 'hidden'}>Alterações não salvas</span>` : ''}
    <button type="button" class="btn btn-link btn-lg" data-acao="fechar-det">Fechar</button>
    ${d.situacao === 'pendente' && !ehGestor() && d.responsavel && d.responsavel !== 'admin' ? `<button type="button" class="btn btn-outline-secondary btn-lg" data-acao="devolver-gestor" data-id="${d.id}">Devolver ao gestor</button>` : ''}
    ${d.situacao === 'pendente' && ehGestor() ? `<button type="button" class="btn btn-success btn-lg" data-acao="concluir-dem" data-id="${d.id}">${I.check}Concluir demanda</button>` : ''}
    ${E.aba === 'dados' && podeEditar(d) ? `<button type="submit" form="form-dados" id="btn-salvar" class="btn btn-primary btn-lg" ${E.sujo || E.statusRascunho ? '' : 'disabled'}>Salvar alterações</button>`
    : E.statusRascunho ? `<button type="button" id="btn-salvar" class="btn btn-primary btn-lg" data-acao="salvar-status">Salvar alterações</button>` : ''}
  </footer>
</section>
</div>
</div>`;
  }

  // no modal, comarca do interior aparece como prédio; Foro, Tribunal, Palácio etc. ficam como estão
  const RE_PREDIO = /^(foro|tribunal|pal[áa]cio|transporte|garagem|anexo|tj\b)/i;
  function predio(c) { c = String(c || '').trim(); return !c || RE_PREDIO.test(c) ? c : 'Foro da Comarca de ' + c; }
  function cidade(v) { return String(v || '').trim().replace(/^foro da comarca de\s+/i, ''); }
  // ------------------------------------------------------------------ data: digitar (dd/mm/aaaa) ou escolher no calendário
  const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
  function campoData(id, iso, invalido) {
    return `<div class="data-campo"><input id="${id}" data-rascunho data-mask="data" class="form-control" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="dd/mm/aaaa" value="${esc(br(iso || ''))}" ${invalido ? 'aria-invalid="true"' : ''}><button type="button" class="data-btn" data-acao="cal-abrir" data-v="${id}" aria-label="Escolher a data no calendário" title="Escolher no calendário" aria-haspopup="dialog">${I.agenda}</button></div>`;
  }
  // '' quando vazio; null quando o texto não é uma data válida
  function textoISO(t) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(String(t || '').trim()); if (!m) return null;
    const [dd, mm, aa] = [+m[1], +m[2], +m[3]]; const dt = new Date(aa, mm - 1, dd);
    if (aa < 2000 || aa > 2100 || dt.getMonth() !== mm - 1 || dt.getDate() !== dd) return null;
    return aa + '-' + pad(mm) + '-' + pad(dd);
  }
  function dataISO(id) { const t = val(id); return t ? textoISO(t) : ''; }
  // horário do atendimento (hh:mm, 24 h); a máscara monta os dois-pontos
  function campoHora(id, hora, invalido) {
    return `<div class="data-campo"><input id="${id}" data-rascunho data-mask="hora" class="form-control" inputmode="numeric" autocomplete="off" maxlength="5" placeholder="hh:mm" value="${esc(hora || '')}" ${invalido ? 'aria-invalid="true"' : ''}><span class="hora-ico" aria-hidden="true">${svg(15, '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', 1.9)}</span></div>`;
  }
  // '' quando vazio; null quando inválido
  function horaVal(id) { const t = val(id); if (!t) return ''; const m = /^(\d{2}):(\d{2})$/.exec(t); return m && +m[1] < 24 && +m[2] < 60 ? t : null; }
  function erroDatas(ini, fim) {
    if (ini === null || fim === null) return 'Data inválida. Use o formato dd/mm/aaaa ou escolha no calendário.';
    if (fim && !ini) return 'Informe a data de início antes da data para conclusão.';
    if (ini && fim && fim < ini) return 'A data para conclusão não pode ser antes da data de início.';
    return '';
  }
  let CAL = null;
  function abrirCal(id) {
    const inp = document.getElementById(id); if (!inp) return;
    const par = /-fim$/.test(id) ? document.getElementById(id.replace(/-fim$/, '-ini')) : null;
    const iso = textoISO(inp.value) || (par && textoISO(par.value)) || hojeISO();
    CAL = { id, ano: +iso.slice(0, 4), mes: +iso.slice(5, 7) - 1 };
    desenharCal();
  }
  function fecharCal() { CAL = null; const c = document.getElementById('cal-pop'); if (c) c.remove(); document.querySelectorAll('.data-btn[aria-expanded]').forEach((b) => b.removeAttribute('aria-expanded')); }
  function desenharCal() {
    const velho = document.getElementById('cal-pop');
    if (!CAL) { if (velho) velho.remove(); return; }
    const inp = document.getElementById(CAL.id); if (!inp) { fecharCal(); return; }
    const sel = textoISO(inp.value); const hoje = hojeISO();
    const prim = new Date(CAL.ano, CAL.mes, 1); const ini = prim.getDay(); const nDias = new Date(CAL.ano, CAL.mes + 1, 0).getDate();
    let cel = '';
    const total = Math.ceil((ini + nDias) / 7) * 7;
    for (let i = 0; i < total; i++) {
      const dt = new Date(CAL.ano, CAL.mes, i - ini + 1);
      const iso = dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate());
      const fora = dt.getMonth() !== CAL.mes;
      cel += `<button type="button" class="cal-dia ${fora ? 'fora' : ''} ${iso === hoje ? 'hoje' : ''} ${iso === sel ? 'escolhido' : ''}" data-acao="cal-dia" data-v="${iso}" aria-label="${dt.getDate()} de ${MESES[dt.getMonth()].toLowerCase()} de ${dt.getFullYear()}" ${iso === sel ? 'aria-pressed="true"' : ''}>${dt.getDate()}</button>`;
    }
    const html = `<div class="cal-cab">
        <button type="button" class="cal-nav" data-acao="cal-mes" data-v="-1" aria-label="Mês anterior">${svg(15, '<path d="m15 6-6 6 6 6"/>', 2.2)}</button>
        <span class="cal-tit" aria-live="polite">${MESES[CAL.mes]} ${CAL.ano}</span>
        <button type="button" class="cal-nav" data-acao="cal-mes" data-v="1" aria-label="Próximo mês">${svg(15, '<path d="m9 6 6 6-6 6"/>', 2.2)}</button>
      </div>
      <div class="cal-sem" aria-hidden="true">${['D', 'S', 'T', 'Q', 'Q', 'S', 'S'].map((x) => `<span>${x}</span>`).join('')}</div>
      <div class="cal-grade">${cel}</div>
      <div class="cal-pe"><button type="button" class="link" data-acao="cal-limpar">Limpar</button><button type="button" class="link" data-acao="cal-hoje">Hoje</button></div>`;
    const c = velho || Object.assign(document.createElement('div'), { id: 'cal-pop', className: 'cal' });
    c.setAttribute('role', 'dialog'); c.setAttribute('aria-label', 'Calendário');
    c.innerHTML = html; if (!velho) document.body.appendChild(c);
    const btn = inp.parentElement.querySelector('.data-btn'); if (btn) btn.setAttribute('aria-expanded', 'true');
    // posição fixa junto do campo (não é cortado pela rolagem do modal); abre para cima se faltar espaço
    const r = inp.parentElement.getBoundingClientRect(); const w = c.offsetWidth; const h = c.offsetHeight;
    const left = Math.max(8, Math.min(r.right - w, window.innerWidth - w - 8));
    const top = (r.bottom + 6 + h > window.innerHeight - 8 && r.top - 6 - h > 8) ? r.top - 6 - h : r.bottom + 6;
    c.style.left = left + 'px'; c.style.top = top + 'px';
  }
  function escolherData(iso) {
    const inp = CAL && document.getElementById(CAL.id); if (!inp) return;
    inp.value = iso ? br(iso) : ''; inp.removeAttribute('aria-invalid');
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    fecharCal(); inp.focus();
  }

  // campo de local com lista que filtra enquanto digita (substitui o datalist do navegador)
  function combo(id, valor, invalido) {
    return `<div class="combo"><input id="${id}" data-rascunho data-combo class="form-control" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="${id}-lista" autocomplete="off" spellcheck="false" value="${esc(valor)}" placeholder="Digite a comarca ou o prédio" ${invalido ? 'aria-invalid="true"' : ''}><span class="combo-seta" aria-hidden="true">${I.setaBaixo}</span><ul class="combo-lista" id="${id}-lista" role="listbox" hidden></ul></div>`;
  }
  function opcoesResp(sel, obrigatorio) {
    const atual = usr(sel); const extra = atual && atual.ativo === false ? [atual] : [];
    return `${obrigatorio ? '' : '<option value="">Sem responsável</option>'}${ativos().concat(extra).map((u) => `<option value="${u.id}" ${sel === u.id ? 'selected' : ''}>${esc(u.nome)}${u.ativo === false ? ' (inativo)' : ''}</option>`).join('')}<option value="admin" ${sel === 'admin' ? 'selected' : ''}>Gestor</option>`;
  }


  function abaDados(d) {
    const er = E.erros;
    // Em atendimento e Para validação: só o responsável e as informações adicionais continuam editáveis
    const trava = TRAVADOS.includes(d.situacao) ? 'disabled' : '';
    return `
<form id="form-dados" data-form="dados" novalidate><fieldset class="pilha-blocos" ${podeEditar(d) ? '' : 'disabled'}>
  <fieldset class="trava-grupo" ${trava}>${bloco('Expediente', '', `
    <div class="linha-sei">
      <div class="campo">
        <label class="form-label" for="f-sei">Número do SEI</label>
        <input id="f-sei" data-rascunho data-mask="sei" class="form-control mono" inputmode="numeric" value="${esc(d.sei)}" placeholder="8.2026.9745/000000-0" ${er.sei ? 'aria-invalid="true"' : ''}>
        ${er.sei ? `<span class="erro">${esc(er.sei)}</span>` : ''}
      </div>
      <div class="campo">
        <label class="form-label" for="f-local">Comarca ou prédio</label>
        ${combo('f-local', d.comarca)}
      </div>
    </div>
    <div class="campo">
      <span class="rotulo-l"><label class="form-label" for="f-desc">Descrição</label><span class="cont" id="f-desc-cont">${(d.descricao || '').length}/250</span></span>
      <textarea id="f-desc" data-rascunho data-cont="250" class="form-control txt txt-desc" rows="3" maxlength="250">${esc(d.descricao)}</textarea>
    </div>`)}</fieldset>
  ${bloco('Atendimento', '', `
    <div class="linha-atend-det">
      <div class="campo">
        <label class="form-label" for="f-resp">Responsável</label>
        <select id="f-resp" data-rascunho class="form-select sel-g" ${!ehGestor() ? 'disabled title="Só o gestor atribui a demanda (entre como gestor)"' : ''}>${opcoesResp(d.responsavel, TRAVADOS.includes(d.situacao))}</select>
      </div>
      <fieldset class="trava-grupo" ${trava}>
        <div class="campo"><label class="form-label" for="f-ini">Data de Início</label>${campoData('f-ini', d.inicio, E.erros.data)}</div>
        <div class="campo"><label class="form-label" for="f-fim">Data para Conclusão</label>${campoData('f-fim', d.fim, E.erros.data)}</div>
        <div class="campo"><label class="form-label" for="f-hora">Hora</label>${campoHora('f-hora', d.hora, E.erros.hora)}</div>
      </fieldset>
      ${E.erros.data || E.erros.hora ? `<span class="erro campo-info">${esc(E.erros.data || E.erros.hora)}</span>` : ''}
      <div class="campo campo-info">
        <span class="rotulo-l"><label class="form-label" for="f-info">Informações adicionais</label><span class="cont" id="f-info-cont">${(d.informacoes || '').length}/100</span></span>
        <textarea id="f-info" data-rascunho data-cont="100" class="form-control txt txt-info" rows="2" maxlength="100" placeholder="Ex.: Solicitado ao DMP em 01/04">${esc(d.informacoes || '')}</textarea>
      </div>
    </div>`)}
</fieldset></form>`;
  }

  // quando e por quem o ticket principal foi registrado
  function infoTicket(d) {
    if (d.ticketEm) return d.ticketEm;
    const h = d.historico.find((x) => d.ticketPrincipal && x.texto.includes(d.ticketPrincipal));
    return h ? { data: h.data, usuario: h.usuario } : { data: d.criadaEm, usuario: d.responsavel };
  }
  function blocoTicket(d) {
    const ro = !podeEditar(d); const semAlterar = ro || TRAVADOS.includes(d.situacao);
    if (ro && !d.ticketPrincipal) return bloco('Ticket Principal', '', '<p class="vazio-bloco">Nenhum ticket principal registrado.</p>');
    if (d.ticketPrincipal && (!E.editTk || semAlterar)) {
      const inf = infoTicket(d);
      return bloco('Ticket Principal', `<span class="badge tag-ok">${I.check}Registrado</span>`, `
        <div class="tk-reg ${E.recemTk ? 'anim' : ''}">
          <span class="tk-reg-ico">${I.check}</span>
          <div class="tk-reg-txt">
            <span class="tk-reg-num mono">${esc(d.ticketPrincipal)}</span>
            <small>Ticket do 4Biz registrado em ${esc(br(inf.data))} por ${esc(nomeUsr(inf.usuario))}</small>
          </div>
          <button type="button" class="btn btn-icone" data-acao="copiar" data-v="${esc(d.ticketPrincipal)}" aria-label="Copiar número do ticket" title="Copiar">${I.copiar}</button>
          ${semAlterar ? '' : '<button type="button" class="btn btn-outline-secondary" data-acao="tk-alterar">Alterar</button>'}
        </div>`);
    }
    return bloco('Ticket Principal', d.ticketPrincipal ? 'Alterando o número' : '<span class="badge tag-pend">Pendente</span>', `
      ${d.ticketPrincipal ? '' : '<p class="bloco-dica">Abra o ticket principal no 4Biz e registre o número aqui. Depois disso a demanda pode ser marcada como acionada.</p>'}
      <form class="linha-form" data-form="principal" novalidate>
        <label for="t-principal" class="visually-hidden">Número do ticket principal</label>
        <input id="t-principal" data-rascunho class="form-control mono inp-tk" inputmode="numeric" value="${esc(d.ticketPrincipal || '')}" placeholder="Número do ticket, ex.: 1831576" ${E.erros.principal ? 'aria-invalid="true"' : ''}>
        <span class="linha-form-btns">
          ${d.ticketPrincipal ? '<button type="button" class="btn btn-link btn-lg" data-acao="tk-cancelar">Cancelar</button>' : ''}
          <button type="submit" class="btn btn-primary btn-lg">${d.ticketPrincipal ? 'Salvar número' : 'Registrar ticket'}</button>
        </span>
      </form>
      ${E.erros.principal ? `<span class="erro">${esc(E.erros.principal)}</span>` : ''}`);
  }

  function abaTickets(d) {
    // Em atendimento e Para validação: dá para incluir ticket novo, mas os já registrados ficam travados
    const ro = !podeEditar(d); const fixos = ro || TRAVADOS.includes(d.situacao); const trava = fixos ? 'disabled' : '';
    const tabela = d.subtickets.length ? `<table class="table tabela">
      <thead><tr><th>Empresa</th><th>Ticket</th><th>Serviço</th><th class="th-qtd">Qtd.</th><th><span class="visually-hidden">Ações</span></th></tr></thead>
      <tbody>${d.subtickets.map((s, i) => `<tr>
        <td><span class="badge emp-tag">${esc(s.empresa)}</span></td>
        <td class="mono">${esc(s.numero)}</td>
        <td><label class="visually-hidden" for="sf-${i}">Serviço</label><select id="sf-${i}" class="form-select sel-tab ${s.finalidade ? '' : 'falta'}" data-campo-sub="finalidade" data-i="${i}" ${trava}>${opcoesServ(s.empresa, s.finalidade)}${s.finalidade && !(SERVICOS[s.empresa] || []).includes(s.finalidade) ? `<option selected>${esc(s.finalidade)}</option>` : ''}</select></td>
        <td class="td-qtd"><label class="visually-hidden" for="sq-${i}">Quantidade</label><input id="sq-${i}" type="number" min="1" max="999" class="form-control inp-qtd ${s.quantidade ? '' : 'falta'}" value="${esc(s.quantidade || '')}" placeholder="—" data-campo-sub="quantidade" data-i="${i}" ${trava}></td>
        <td class="td-acao"><span class="acoes-sub">
          ${fixos ? '' : `<button type="button" class="btn btn-icone perigo-h" data-acao="sub-del" data-i="${i}" aria-label="Remover subticket ${esc(s.numero)}" title="Remover">${I.lixo}</button>`}
        </span></td>
      </tr>`).join('')}</tbody></table>` : '<p class="vazio-bloco">Nenhum subticket incluído ainda.</p>';
    return `
${blocoTicket(d)}
${bloco('Subtickets', d.subtickets.length ? d.subtickets.length + (d.subtickets.length > 1 ? ' subtickets' : ' subticket') : '', `
  ${ro ? '' : `<div class="bloco-barra">
    ${d.situacao === 'nova' && d.inicio ? `<p class="bloco-dica">${esc(textoSLA(d))}</p>` : ''}
    <form class="add-sub" data-form="sub" novalidate>
      <span class="campo"><label class="form-label" for="n-emp">Empresa</label>
      <select id="n-emp" data-rascunho class="form-select sel-g" ${E.erros.emp ? 'aria-invalid="true"' : ''}><option value="">Escolher empresa…</option>${EMPRESAS.map((e) => `<option ${E.ultimaEmp === e ? 'selected' : ''}>${e}</option>`).join('')}</select></span>
      <span class="campo"><label class="form-label" for="n-num">Número do subticket</label>
      <input id="n-num" data-rascunho class="form-control mono" inputmode="numeric" placeholder="Ex.: 1831365 / 1831398" ${E.erros.sub ? 'aria-invalid="true"' : ''}></span>
      <span class="campo"><label class="form-label" for="n-fin">Serviço</label>
      <select id="n-fin" data-rascunho class="form-select sel-g" ${E.erros.fin ? 'aria-invalid="true"' : ''}>${opcoesServ(E.ultimaEmp || '', '')}</select></span>
      <span class="campo campo-qtd"><label class="form-label" for="n-qtd">Quantidade</label>
      <input id="n-qtd" data-rascunho type="number" min="1" max="999" class="form-control" value="1" ${E.erros.qtd ? 'aria-invalid="true"' : ''}></span>
      <button type="submit" class="btn btn-primary btn-lg">${I.mais}Incluir</button>
    </form>
    ${E.erros.sub ? `<span class="erro">${esc(E.erros.sub)}</span>` : ''}
  </div>`}
  ${tabela}`, '', 'tabela-bloco')}`;
  }

  function abaHist(d) {
    const ls = [...d.historico].reverse();
    return bloco('Histórico', ls.length + ' registro' + (ls.length > 1 ? 's' : ''), `
<form class="linha-form" data-form="nota" novalidate>
  <label class="visually-hidden" for="h-nota">Registrar andamento</label>
  <input id="h-nota" data-rascunho class="form-control" placeholder="Registrar andamento, ex.: Solicitado ao DMP em 26/10" autocomplete="off">
  <button type="submit" class="btn btn-outline-secondary btn-lg">Registrar</button>
</form>
<ol class="linha-tempo">
  ${ls.map((h, i) => `<li class="${i === 0 ? 'ultimo' : ''}"><span class="ponto" aria-hidden="true"></span><div class="conteudo"><p>${esc(h.texto)}</p><small>${esc(nomeUsr(h.usuario))} · ${esc(brHora(h.data))}</small></div></li>`).join('')}
</ol>`);
  }

  // ------------------------------------------------------------------ outros modais
  function telaModal() {
    if (!E.modal) return '';
    const m = { nova: modalNova, sobre: modalSobre, confirmar: modalConfirmar, login: modalLogin, equipe: modalEquipe, acionamento: modalAcionamento, relatorio: modalRelatorio, movimentos: modalMovimentos, lixeira: modalLixeira, senha: modalSenha, conclusao: modalConclusao }[E.modal];
    return `<div class="modal d-block modal-camada ${E.modal === 'confirmar' || E.modal === 'conclusao' ? 'modal-topo' : ''} ${E._anim.modal ? 'anim' : ''}" tabindex="-1" data-acao="fundo-modal"><div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">${m ? m() : ''}</div></div>`;
  }

  function modalNova() {
    const er = E.erros; const v = E.modalDados || {};
    const resp = v.responsavel !== undefined ? v.responsavel : '';
    const suc = v.sucesso ? demanda(v.sucesso) : null;
    return `
<form class="modal-content modal-n" role="dialog" aria-modal="true" aria-labelledby="mn-tit" data-form="nova" novalidate>
  <div class="camada ${suc ? 'oculta' : ''}">
    <header class="modal-header"><div><h2 class="modal-title" id="mn-tit">Nova Demanda</h2><p>Dados do expediente SEI e de quem vai atender.</p></div>
      <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
    <div class="modal-body corpo-blocos">
      ${bloco('Informações Iniciais', '', `
        <div class="grade-ini">
          <div class="campo">
            <span class="rotulo-l"><label class="form-label" for="n-sei">Número do SEI</label><label class="check check-mini"><input id="n-semsei" data-rascunho type="checkbox" ${v.semSei ? 'checked' : ''} data-acao="sem-sei"><span>Fora do SEI</span></label></span>
            <input id="n-sei" data-rascunho data-mask="sei" class="form-control mono" inputmode="numeric" value="${esc(v.sei || '')}" placeholder="8.2026.9745/000000-0" ${er.sei ? 'aria-invalid="true"' : ''} ${v.semSei ? 'disabled' : ''} autocomplete="off">
            ${er.sei ? `<span class="erro">${esc(er.sei)}</span>` : ''}
          </div>
          <div class="campo">
            <label class="form-label" for="n-local">Comarca ou prédio</label>
            ${combo('n-local', v.comarca || '', er.local)}
            ${er.local ? `<span class="erro">${esc(er.local)}</span>` : ''}
          </div>
          <div class="campo"><label class="form-label" for="n-ini">Data de Início</label>${campoData('n-ini', v.inicio, er.data)}</div>
          <div class="campo"><label class="form-label" for="n-fim">Data para Conclusão</label>${campoData('n-fim', v.fim, er.data && v.fim !== '')}</div>
          <div class="campo"><label class="form-label" for="n-hora">Hora</label>${campoHora('n-hora', v.hora, er.hora)}</div>
        </div>
        ${er.data || er.hora ? `<span class="erro">${esc(er.data || er.hora)}</span>` : '<p class="dica-datas">Sem a data para conclusão, o atendimento é de um dia só. Datas e horário podem ser definidos depois.</p>'}
        <div class="campo">
          <span class="rotulo-l"><label class="form-label" for="n-desc">Descrição</label><span class="cont" id="n-desc-cont">${(v.descricao || '').length}/250</span></span>
          <textarea id="n-desc" data-rascunho data-cont="250" class="form-control txt txt-desc" rows="4" maxlength="250" placeholder="Ex.: Adequação de leiaute da sala 1001 - Cartório da 5ª Vara Cível" ${er.desc ? 'aria-invalid="true"' : ''}>${esc(v.descricao || '')}</textarea>
          ${er.desc ? `<span class="erro">${esc(er.desc)}</span>` : ''}
        </div>`)}
      ${bloco('Atribuição da Demanda', '', `
        <fieldset class="campo resp-campo">
          <legend class="rotulo">Responsável</legend>
          <div class="grade-resp" role="radiogroup">
            ${ativos().map((u) => `<label class="tile-resp"><input type="radio" name="n-resp" value="${u.id}" ${resp === u.id ? 'checked' : ''}>${avatar(u.id, 'sm')}<span>${esc(u.curto)}</span></label>`).join('')}
            <label class="tile-resp"><input type="radio" name="n-resp" value="" ${!resp ? 'checked' : ''}><span class="avatar sm vazio">?</span><span>Definir depois</span></label>
          </div>
        </fieldset>`)}
    </div>
    <footer class="modal-footer">
      ${flash('nova')}<span class="esp"></span>
      <button type="button" class="btn btn-link btn-lg" data-acao="fechar-modal">Cancelar</button>
      <button type="submit" class="btn btn-primary btn-lg">Incluir demanda</button>
    </footer>
  </div>
  ${suc ? telaSucesso(suc) : ''}
</form>`;
  }

  // confirmação da inclusão, no mesmo desenho do Acervo
  function telaSucesso(d) {
    const u = usr(d.responsavel);
    return `
<div class="sucesso ${E._anim.suc ? 'anim' : ''}" role="status">
  <span class="suc-ico">${I.checkG}</span>
  <h2 class="suc-tit">Demanda Incluída com Sucesso</h2>
  <p class="suc-desc">${esc(predio(d.comarca))}${u ? ' · atribuída a ' + esc(u.nome) : ''}</p>
  <div class="suc-campo">
    <span class="suc-rot">${d.sei ? 'Expediente SEI' : 'Número da demanda'}</span>
    <div class="suc-valor"><span class="mono">${esc(d.sei || num4(d.id))}</span><button type="button" class="btn btn-outline-secondary btn-sm" data-acao="copiar" data-v="${esc(d.sei || num4(d.id))}">Copiar</button></div>
  </div>
  <div class="suc-flash">${flash('suc')}</div>
  <div class="suc-btns">
    <button type="button" class="btn btn-link btn-lg" data-acao="incluir-outra">Incluir outra</button>
    <button type="button" class="btn btn-outline-secondary btn-lg" data-acao="abrir-nova" data-id="${d.id}">Abrir demanda</button>
    <button type="button" class="btn btn-primary btn-lg" data-acao="fechar-modal">${I.check}Concluir</button>
  </div>
</div>`;
  }

  function modalSobre() {
    return `
<div class="modal-content modal-m sobre-sis" role="dialog" aria-modal="true" aria-labelledby="ms-tit">
  <header class="modal-header"><h2 class="modal-title" id="ms-tit">Informações do Sistema</h2>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="modal-body">
    <div class="sobre-id">
      <p class="sobre-nome">Controle de Demandas de Mudanças · DITIC-DSUP</p>
      <p class="sobre-ver">Versão do Sistema: 1.0.0 · Novembro/2026</p>
    </div>
    <div class="termos">
      <h3>Termos de Uso e Propriedade Técnica</h3>
      <p><strong>Autoria e Propriedade</strong><br>Este software foi desenvolvido por Marcelo Luis da Silva Diehl para uso exclusivo do Departamento de Suporte (DSUP) da Direção de Tecnologia da Informação e Comunicação (DITIC) do Tribunal de Justiça do Rio Grande do Sul (TJRS). A propriedade intelectual do código-fonte pertence ao autor, sendo o direito de uso cedido integralmente ao Tribunal de Justiça do Rio Grande do Sul (TJRS) para fins institucionais.</p>
      <p><strong>Limites de Uso e Distribuição</strong><br>Ambiente Restrito: O uso desta aplicação é restrito à rede privada e aos servidores autorizados pelo DITIC-DSUP. É expressamente proibida a hospedagem ou execução em servidores externos não homologados pelo departamento, exceto manutenção em repositório de versionamento do autor do projeto mediante ocultação de dados sensíveis ou confidenciais.</p>
      <p><strong>Finalidade</strong><br>A ferramenta destina-se exclusivamente ao registro, acompanhamento e documentação das demandas de mudança de equipamentos de informática do setor.</p>
      <p><strong>Modificações e Manutenção (Código Aberto Setorial)</strong><br>É permitida a leitura, cópia e modificação do código-fonte por outros membros e colaboradores técnicos do departamento, visando a continuidade, correção de bugs e evolução das funcionalidades.</p>
      <p>Toda e qualquer modificação derivada deve manter os créditos do autor original e ser devidamente documentada no histórico de versionamento interno.</p>
      <p><strong>Isenção de Responsabilidade</strong><br>O software é fornecido "no estado em que se encontra" (as is). O autor não se responsabiliza por resultados derivados de entradas de dados incorretas ou por usos que firam as políticas de segurança da informação do TJRS. Todos os dados de entrada e de saída do programa deverão ser conferidos pelo usuário.</p>
    </div>
  </div>
  <footer class="modal-footer">${flash('sobre')}<span class="esp"></span><button type="button" class="btn btn-primary btn-lg" data-acao="fechar-modal">Fechar</button></footer>
</div>`;
  }

  function modalLogin() {
    const v = E.modalDados || {};
    return `
<form class="modal-content modal-p login" role="dialog" aria-modal="true" aria-labelledby="ml-tit" data-form="login" novalidate>
  <button type="button" class="btn btn-icone fechar-canto" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button>
  <div class="login-cab">
    <span class="cadeado">${I.cadeado}</span>
    <h2 id="ml-tit">Entrar no Controle de Mudanças</h2>
    <p>${v.motivo ? esc(v.motivo) : 'Acesso do gestor do DSUP, para incluir, distribuir e concluir demandas. Os técnicos atualizam as demandas sem login.'}</p>
  </div>
  <div class="campo">
    <label class="form-label" for="l-usr">Usuário da rede</label>
    <span class="com-ico">${I.usuarioP}<input id="l-usr" data-rascunho class="form-control" placeholder="Usuário da rede" autocomplete="username" value="${esc(v.usr || '')}" ${E.erros.login ? 'aria-invalid="true"' : ''}></span>
  </div>
  <div class="campo">
    <label class="form-label" for="l-sen">Senha</label>
    <span class="com-ico">${I.cadeadoP}<input id="l-sen" data-rascunho class="form-control" type="password" autocomplete="current-password"><button type="button" class="olho" data-acao="ver-senha" aria-label="Mostrar senha">${I.olho}</button></span>
    ${E.erros.login ? `<span class="erro">${esc(E.erros.login)}</span>` : ''}
  </div>
  <button type="submit" class="btn btn-primary w-100 btn-bloco">Entrar</button>
  <div class="proto-box">
    <span><b>Acesso do protótipo</b><small>Usuário <code>admin</code>, qualquer senha. O primeiro acesso pede uma nova senha.</small></span>
    <button type="button" class="btn btn-outline-secondary" data-acao="proto-gestor">Entrar como gestor</button>
  </div>
</form>`;
  }

  // primeiro acesso: o login só termina depois de criar a senha. Fechar pelo X desiste de entrar.
  function modalSenha() {
    const er = E.erros.senha;
    return `
<form class="modal-content modal-p login" role="dialog" aria-modal="true" aria-labelledby="sn-tit" data-form="senha" novalidate>
  <button type="button" class="btn btn-icone fechar-canto" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button>
  <div class="login-cab">
    <span class="cadeado">${I.cadeado}</span>
    <h2 id="sn-tit">Crie uma Nova Senha</h2>
    <p>Este é o primeiro acesso. Para continuar, defina uma senha pessoal com pelo menos 8 caracteres.</p>
  </div>
  <div class="campo">
    <label class="form-label" for="s-nova">Nova senha</label>
    <span class="com-ico">${I.cadeadoP}<input id="s-nova" data-rascunho class="form-control" type="password" autocomplete="new-password" ${er ? 'aria-invalid="true"' : ''}></span>
  </div>
  <div class="campo">
    <label class="form-label" for="s-conf">Confirmar a nova senha</label>
    <span class="com-ico">${I.cadeadoP}<input id="s-conf" data-rascunho class="form-control" type="password" autocomplete="new-password" ${er ? 'aria-invalid="true"' : ''}></span>
    ${er ? `<span class="erro">${esc(er)}</span>` : ''}
  </div>
  <button type="submit" class="btn btn-primary w-100 btn-bloco">Salvar e entrar</button>
</form>`;
  }
  function entrar(id, depois, msg) {
    E.usuario = id; E.modal = null; E.modalDados = null; E.limparRascunho = true; E.menu = null;
    aviso(msg); mudou();
    if (depois) depois();
  }

  // pede login antes de qualquer alteração; depois de entrar, segue o que a pessoa ia fazer
  function precisaLogin(motivo, depois) {
    if (E.usuario) return false;
    E.modal = 'login'; E.modalDados = { motivo: motivo || 'Esta ação é do gestor. Entre com o usuário do gestor.', depois }; E.erros = {}; E.limparRascunho = true;
    desenhar(); setTimeout(() => { const el = document.getElementById('l-usr'); if (el) el.focus(); }, 0);
    return true;
  }

  // Perfis: o gestor entra (login) e faz tudo; o técnico não tem login e atualiza as demandas sem entrar
  const ehGestor = () => E.usuario === 'admin';
  // Concluída e Cancelada ficam só para consulta (no histórico ainda se registra andamento)
  const podeEditar = (d) => !!d && !FINAIS.includes(d.situacao);
  function precisaGestor(motivo, depois) {
    if (!E.usuario) return precisaLogin(motivo || 'Esta ação é do gestor. Entre com o usuário do gestor.', depois);
    if (ehGestor()) return false;
    aviso('Somente o gestor pode fazer isso.', true); desenhar(); return true;
  }
  function precisaEditar(d) {
    if (podeEditar(d)) return false;
    if (d) { aviso('Demanda encerrada: somente consulta.', true); desenhar(); }
    return true;
  }

  // Em atendimento e Para validação os dados registrados não mudam mais
  function precisaDestravar(d) {
    if (!d || !TRAVADOS.includes(d.situacao)) return false;
    aviso('Em Atendimento e Para Validação, os dados registrados ficam travados.', true); desenhar(); return true;
  }

  // ------------------------------------------------------------------ equipe
  const cores = (nome, sel) => `<span class="cores" role="radiogroup" aria-label="Cor">${CORES_EQUIPE.map((c) => `<label class="cor-op" style="--c:${corOk(c)}" title="${c}"><input type="radio" name="${nome}" value="${c}" ${sel === c ? 'checked' : ''}><span></span></label>`).join('')}</span>`;
  function iniciaisDe(nome) { const p = String(nome).trim().split(/\s+/).filter(Boolean); return ((p[0] || '?')[0] + (p.length > 1 ? p[p.length - 1][0] : (p[0] || '?')[1] || '')).toUpperCase(); }
  function proximaCor() { const usadas = E.equipe.filter((u) => u.ativo).map((u) => u.cor); return CORES_EQUIPE.find((c) => !usadas.includes(c)) || CORES_EQUIPE[E.equipe.length % CORES_EQUIPE.length]; }

  function modalEquipe() {
    const v = E.modalDados || {};
    if (v.transf) return modalTransferir(v.transf);
    const lista = E.equipe.slice().sort((a, b) => (b.ativo - a.ativo) || porNome(a, b));
    const linha = (u) => {
      const ab = abertasDe(u.id).length; const tot = E.demandas.filter((d) => d.responsavel === u.id).length;
      if (v.editar === u.id) {
        return `<li class="list-group-item eq-linha editando"><form class="eq-edit" data-form="equipe-edit" data-id="${u.id}" novalidate>
          ${avatar(u.id)}
          <span class="campo"><label class="visually-hidden" for="ed-nome">Nome</label><input id="ed-nome" data-rascunho class="form-control" value="${esc(u.nome)}" maxlength="60" ${E.erros.eqEdit ? 'aria-invalid="true"' : ''}></span>
          ${cores('ed-cor', u.cor)}
          <span class="eq-acoes"><button type="button" class="btn btn-link" data-acao="eq-cancelar">Cancelar</button><button type="submit" class="btn btn-primary">Salvar</button></span>
        </form>${E.erros.eqEdit ? `<span class="erro eq-erro">${esc(E.erros.eqEdit)}</span>` : ''}</li>`;
      }
      return `<li class="list-group-item eq-linha ${u.ativo ? '' : 'inativa'}">
        ${avatar(u.id)}
        <span class="eq-nome"><b>${esc(u.nome)}</b>${u.ativo ? '' : '<span class="badge tag-inativo">Inativo</span>'}</span>
        <span class="eq-carga"><b>${ab}</b> em aberto<span class="eq-tot">· ${tot} no total</span></span>
        <span class="eq-acoes">
          ${u.ativo ? `<button type="button" class="btn btn-icone" data-acao="eq-editar" data-v="${u.id}" aria-label="Editar ${esc(u.nome)}" title="Editar">${svg(15, '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>', 1.9)}</button>` : '<span></span>'}
          ${ab ? `<button type="button" class="btn btn-outline-secondary btn-sm" data-acao="eq-transferir" data-v="${u.id}">${svg(14, '<path d="M4 8h13l-3-3M20 16H7l3 3"/>', 2)}Transferir</button>` : '<span></span>'}
          ${u.ativo ? `<button type="button" class="btn btn-sm btn-link eq-desat" data-acao="eq-desativar" data-v="${u.id}">Desativar</button>` : `<button type="button" class="btn btn-sm btn-outline-secondary" data-acao="eq-reativar" data-v="${u.id}">Reativar</button>`}
        </span>
      </li>`;
    };
    return `
<div class="modal-content modal-m equipe" role="dialog" aria-modal="true" aria-labelledby="eq-tit">
  <header class="modal-header"><div><h2 class="modal-title" id="eq-tit">Equipe</h2><p>Pessoas que recebem demandas.</p></div>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="modal-body corpo-blocos">
    ${bloco('Incluir Pessoa', '', `
      <form class="eq-add" data-form="equipe-add" novalidate>
        <span class="campo"><label class="form-label" for="eq-nome">Nome</label><input id="eq-nome" data-rascunho class="form-control" maxlength="60" ${E.erros.eqAdd ? 'aria-invalid="true"' : ''}></span>
        <span class="campo"><span class="rotulo">Cor</span>${cores('eq-cor', proximaCor())}</span>
        <button type="submit" class="btn btn-primary btn-lg">${I.mais}Incluir</button>
      </form>
      ${E.erros.eqAdd ? `<span class="erro">${esc(E.erros.eqAdd)}</span>` : ''}`)}
    ${bloco('Pessoas', `${ativos().length} ${ativos().length === 1 ? 'ativa' : 'ativas'}${E.equipe.length > ativos().length ? ' · ' + (E.equipe.length - ativos().length) + (E.equipe.length - ativos().length === 1 ? ' inativa' : ' inativas') : ''}`, lista.length ? `<ul class="list-group list-group-flush eq-lista">${lista.map(linha).join('')}</ul>` : '<p class="vazio-bloco">Nenhuma pessoa cadastrada. Inclua os técnicos acima.</p>', '', 'tabela-bloco')}
  </div>
  <footer class="modal-footer">${flash('equipe')}<span class="esp"></span><button type="button" class="btn btn-primary btn-lg" data-acao="fechar-modal">Fechar</button></footer>
</div>`;
  }

  function modalTransferir(t) {
    const de = usr(t.de); const ls = abertasDe(t.de).sort((a, b) => (a.inicio || '9').localeCompare(b.inicio || '9'));
    const marcadas = t.marcadas || ls.map((d) => d.id);
    const destinos = ativos().filter((u) => u.id !== t.de);
    return `
<form class="modal-content modal-m equipe" role="dialog" aria-modal="true" aria-labelledby="tr-tit" data-form="equipe-transf" novalidate>
  <header class="modal-header"><div><h2 class="modal-title" id="tr-tit">${t.desativar ? 'Desativar ' + esc(de.curto) : 'Transferir Demandas'}</h2><p>${t.desativar
    ? esc(de.nome) + ' tem ' + ls.length + (ls.length === 1 ? ' demanda' : ' demandas') + ' em aberto. Escolha quem assume antes de desativar.'
    : 'Passe as demandas em aberto de ' + esc(de.nome) + ' para outra pessoa da equipe.'}</p></div>
    <button type="button" class="btn btn-icone" data-acao="eq-voltar" aria-label="Voltar">${I.fechar}</button></header>
  <div class="modal-body corpo-blocos">
    <div class="tr-de-para">
      <span class="tr-pessoa">${avatar(de.id)}<span><small>De</small><b>${esc(de.nome)}</b></span></span>
      <span class="tr-seta" aria-hidden="true">${svg(18, '<path d="M5 12h14M13 6l6 6-6 6"/>', 2)}</span>
      <span class="campo tr-para"><label class="form-label" for="tr-dest">Para</label>
        <select id="tr-dest" data-rascunho class="form-select sel-g" ${E.erros.transf ? 'aria-invalid="true"' : ''}><option value="">Escolher pessoa…</option>${destinos.map((u) => `<option value="${u.id}" ${t.para === u.id ? 'selected' : ''}>${esc(u.nome)} · ${abertasDe(u.id).length} em aberto</option>`).join('')}<option value="_sem" ${t.para === '_sem' ? 'selected' : ''}>Deixar sem responsável</option></select>
      </span>
    </div>
    ${E.erros.transf ? `<span class="erro">${esc(E.erros.transf)}</span>` : ''}
    ${bloco('Demandas em aberto', `<button type="button" class="link" data-acao="tr-todas">${marcadas.length === ls.length ? 'Desmarcar todas' : 'Marcar todas'}</button>`, `<ul class="tr-lista">${ls.map((d) => `<li><label class="tr-item">
        <input type="checkbox" name="tr-d" value="${d.id}" ${marcadas.includes(d.id) ? 'checked' : ''}>
        <span class="tr-sei mono">${esc(d.sei || 'Fora do SEI')}</span>
        <span class="tr-local">${esc(d.comarca)}</span>
        <span class="tr-data">${d.inicio ? esc(agendaTexto(d)) : 'Sem data'}</span>
        <span class="badge tr-sit" data-sit="${esc(d.situacao)}">${esc(sit(d.situacao).um)}</span>
      </label></li>`).join('')}</ul>`, '', 'tabela-bloco')}
    ${ls.some((x) => TRAVADOS.includes(x.situacao)) ? '<p class="tr-nota">Em Atendimento e Para Validação não ficam sem responsável: nesse caso, vão para o Gestor.</p>' : ''}
    ${t.desativar ? '<p class="tr-nota">As demandas desmarcadas continuam com a pessoa desativada; dá para transferi-las depois pela Equipe.</p>' : ''}
  </div>
  <footer class="modal-footer">
    <button type="button" class="btn btn-link btn-lg" data-acao="eq-voltar">Voltar</button><span class="esp"></span>
    <button type="submit" class="btn btn-primary btn-lg" id="tr-ok">${t.desativar ? 'Transferir e desativar' : 'Transferir'}</button>
  </footer>
</form>`;
  }

  // texto padrão para o SEI: agendamento + subtickets por empresa
  function horaSEI(h) { if (!h) return ', horário a definir'; const [hh, mm] = h.split(':'); return ', ' + Number(hh) + 'h' + (mm !== '00' ? mm : ''); }
  function textoAcionamento(d) {
    const emp = EMPRESAS.map((e) => [e, d.subtickets.filter((x) => x.empresa === e).map((x) => x.numero)]).filter(([, ls]) => ls.length);
    const varias = emp.length !== 1;
    const ag = !d.inicio ? 'Agendamento: a definir.'
      : !d.fim || d.fim === d.inicio ? 'Agendamento: ' + br(d.inicio) + horaSEI(d.hora) + '.'
      : 'Agendamento Inicial: ' + br(d.inicio) + horaSEI(d.hora) + '\nAgendamento Final: ' + br(d.fim);
    return 'Ao Serviço de Gestão de Mudanças,\n\n'
      + 'Em atenção ao Agendamento, informo que ' + (varias ? 'as empresas contratadas da DITIC já foram acionadas' : 'a empresa contratada da DITIC já foi acionada') + ' para o atendimento da demanda:\n\n'
      + ag + '\n\n'
      + (emp.length ? emp.map(([e, ls]) => e + ': ' + ls.join(' / ')).join('\n') + '\n\n' : '')
      + 'Era o que cumpria informar.';
  }
  function modalAcionamento() {
    const d = demanda(E.modalDados && E.modalDados.id); if (!d) return '';
    const semSub = !d.subtickets.length;
    return `
<div class="modal-content modal-m acion" role="dialog" aria-modal="true" aria-labelledby="ac-tit">
  <header class="modal-header"><div><h2 class="modal-title" id="ac-tit">Informação de Acionamento</h2><p>Texto gerado automaticamente, cabe revisão.</p></div>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="modal-body corpo-blocos">
    ${semSub ? `<p class="alert alert-warning ac-aviso">${I.alerta}<span>Esta demanda ainda não tem subtickets das empresas. Inclua na aba Tickets para que apareçam no texto.</span></p>` : ''}
    ${!d.inicio ? `<p class="alert alert-warning ac-aviso">${I.alerta}<span>A demanda está sem data de agendamento.</span></p>` : ''}
    <label class="visually-hidden" for="ac-texto">Texto da informação</label>
    <textarea id="ac-texto" data-rascunho class="form-control txt ac-texto" rows="12" spellcheck="false">${esc(textoAcionamento(d))}</textarea>
  </div>
  <footer class="modal-footer">${flash('acionamento')}<span class="esp"></span>
    <button type="button" class="btn btn-link btn-lg" data-acao="fechar-modal">Fechar</button>
    <button type="button" class="btn btn-primary btn-lg" data-acao="copiar-acionamento">${I.copiar}Copiar texto</button>
  </footer>
</div>`;
  }

  // ------------------------------------------------------------------ relatório de execução de mudança (PDF, modelo-mestre)
  // data do acionamento: gravada quando a demanda vira Acionada; nas antigas, vem do histórico
  function dataAcionamento(d) {
    if (d.acionadaEm) return br(d.acionadaEm);
    const h = d.historico.slice().reverse().find((x) => /→ Acionada|para Acionada|Empresas acionadas/i.test(x.texto));
    return h ? br(String(h.data).slice(0, 10)) : '';
  }
  function montarRelatorio(d) {
    const tem = (serv) => d.subtickets.some((x) => x.finalidade === serv);
    const sv = { predio: tem('Mudança de Prédio'), desinst: tem('Desinstalação'), local: tem('Mudança de Local'), inst: tem('Instalação') };
    const lugar = predio(d.comarca) || d.comarca || '';
    const origem = []; const destino = [];
    if (sv.inst) origem.push('DMP');
    if (sv.local || sv.predio || sv.desinst) origem.push(lugar);
    if (sv.local || sv.predio || sv.inst || !(sv.desinst)) destino.push(lugar);
    if (sv.desinst) destino.push('DMP – Carga CDS');
    // um item por subticket, na ordem das empresas
    // serviços de rede não são "de equipamentos de informática" no texto do relatório
    const SO_REDE = ['Instalação de Infraestrutura', 'Habilitação de Pontos de Rede'];
    const frase = (serv) => (serv || 'Atendimento').replace(/ de (Local|Prédio|Infraestrutura|Pontos de Rede)$/, (m) => m.toLowerCase()) + (SO_REDE.includes(serv) ? '' : ' de equipamentos de informática');
    const itens = [];
    EMPRESAS.forEach((e) => d.subtickets.filter((x) => x.empresa === e).forEach((x) => {
      const q = x.quantidade;
      itens.push(frase(x.finalidade) + (q ? ', em total de ' + q + (q === 1 ? ' serviço' : ' serviços') : '') + ', no ' + lugar + '. A atividade foi executada pela contratada ' + e + ' através do ticket ' + x.numero + '.');
    }));
    const pago = d.subtickets.some((x) => ['CDS', 'WECOM'].includes(x.empresa));
    return { acionamento: dataAcionamento(d), execucao: d.inicio ? agendaTexto(d) : '', servicos: sv, origem: [...new Set(origem)], destino: [...new Set(destino)], custo: pago ? '' : '-', itens, global: !pago };
  }
  function modalRelatorio() {
    const d = demanda(E.modalDados && E.modalDados.id); if (!d) return '';
    const r = montarRelatorio(d); const sv = r.servicos;
    const ck = (id, rot, on) => `<label class="check rl-ck"><input type="checkbox" id="${id}" data-rascunho ${on ? 'checked' : ''}><span>${rot}</span></label>`;
    return `
<div class="modal-content modal-m relat" role="dialog" aria-modal="true" aria-labelledby="rl-tit">
  <header class="modal-header"><div><h2 class="modal-title" id="rl-tit">Relatório de Execução de Mudança</h2><p>Preenchido automaticamente com os dados da demanda, cabe revisão. O PDF segue o modelo-mestre do DSUP.</p></div>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="modal-body corpo-blocos">
    ${bloco('Datas e serviços', '', `
      <div class="row duplo">
        <div class="col-md-6 campo"><label class="form-label" for="rl-acion">Data do acionamento</label><input id="rl-acion" data-rascunho class="form-control" value="${esc(r.acionamento)}" placeholder="dd/mm/aaaa"></div>
        <div class="col-md-6 campo"><label class="form-label" for="rl-exec">Data da execução</label><input id="rl-exec" data-rascunho class="form-control" value="${esc(r.execucao)}" placeholder="dd/mm/aaaa"></div>
      </div>
      <div class="campo"><span class="rotulo">Serviços realizados</span><div class="rl-servs">${ck('rl-predio', 'Mudança de Prédio', sv.predio)}${ck('rl-desinst', 'Desinstalação', sv.desinst)}${ck('rl-local', 'Mudança de Local', sv.local)}${ck('rl-inst', 'Instalação', sv.inst)}</div></div>`)}
    ${bloco('Locais e custo', '', `
      <div class="row duplo">
        <div class="col-md-6 campo"><label class="form-label" for="rl-origem">Local de origem <em>(um por linha)</em></label><textarea id="rl-origem" data-rascunho class="form-control txt" rows="3">${esc(r.origem.join('\n'))}</textarea></div>
        <div class="col-md-6 campo"><label class="form-label" for="rl-destino">Local de destino <em>(um por linha)</em></label><textarea id="rl-destino" data-rascunho class="form-control txt" rows="3">${esc(r.destino.join('\n'))}</textarea></div>
      </div>
      <div class="campo rl-custo"><label class="form-label" for="rl-custo">Custo (aproximado)</label><input id="rl-custo" data-rascunho class="form-control" value="${esc(r.custo)}" placeholder="R$ 0,00"></div>`)}
    ${bloco('Serviços executados', r.itens.length + (r.itens.length === 1 ? ' item' : ' itens'), `
      <div class="campo"><label for="rl-itens" class="visually-hidden">Itens</label><textarea id="rl-itens" data-rascunho class="form-control txt" rows="6">${esc(r.itens.join('\n\n'))}</textarea>
      <span class="dica-datas">Um item por parágrafo (separados por uma linha em branco); a numeração entra no PDF. ${r.global ? 'Sem CDS nem WECOM: entra a frase “Custo incluído no valor global do contrato.”' : 'Com CDS ou WECOM há valor a pagar, então a frase do valor global do contrato não entra.'}</span></div>`)}
  </div>
  <footer class="modal-footer">${flash('relatorio')}<span class="esp"></span>
    <button type="button" class="btn btn-link btn-lg" data-acao="fechar-modal">Fechar</button>
    <button type="button" class="btn btn-primary btn-lg" data-acao="baixar-relatorio">${I.baixar}Baixar PDF</button>
  </footer>
</div>`;
  }
  // salva o arquivo: no claude.ai pelo recurso de downloads; fora dele, pelo download do navegador
  async function salvarArquivo(nome, bytes) {
    const blob = new Blob([bytes], { type: 'application/pdf' });
    try {
      const dl = window.claude && window.claude.use ? await window.claude.use('downloads') : null;
      if (dl) { await dl.save({ filename: nome, data: blob }); return 'ok'; }
    } catch (e) { if (e && e.code === 'declined') return 'recusado'; if (e && e.code === 'rate_limited') return 'ocupado'; }
    const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = nome; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
    return 'ok';
  }
  async function baixarRelatorio() {
    const d = demanda(E.modalDados && E.modalDados.id); if (!d) return;
    const ln = (id) => val(id).split('\n').map((x) => x.trim()).filter(Boolean);
    const chk = (id) => { const x = document.getElementById(id); return !!(x && x.checked); };
    const r = {
      acionamento: val('rl-acion'), execucao: val('rl-exec'),
      servicos: { predio: chk('rl-predio'), desinst: chk('rl-desinst'), local: chk('rl-local'), inst: chk('rl-inst') },
      origem: ln('rl-origem'), destino: ln('rl-destino'), custo: val('rl-custo'),
      itens: val('rl-itens').split(/\n\s*\n/).map((x) => x.replace(/\s*\n\s*/g, ' ').trim()).filter(Boolean),
      global: montarRelatorio(d).global
    };
    const nome = 'Relatório de execução - ' + (d.sei ? d.sei.replace(/\//g, '-') : 'demanda ' + num4(d.id)) + '.pdf';
    const res = await salvarArquivo(nome, RelatorioPDF.gerar(r));
    if (res === 'ok') { registrar(d, 'Relatório de execução de mudança gerado (PDF).'); persistir(); aviso('Relatório gerado.'); }
    else aviso(res === 'recusado' ? 'Download cancelado.' : 'Já há um download aguardando confirmação.', true);
    desenhar();
  }

  const RE_STATUS = /Status alterado|Demanda registrada|excluída|restaurada|Demanda removida/i;
  function modalMovimentos() {
    if (!ehGestor()) return '';
    const v = E.modalDados || {}; const dia = v.dia || hojeISO(); const so = v.so || 'todas';
    const todos = [];
    // inclui as demandas da lixeira; a linha da exclusão vem do registro em E.excluidas, para não aparecer duas vezes
    E.demandas.concat(E.lixeira).forEach((d) => d.historico.forEach((h) => { if (String(h.data).slice(0, 10) === dia && !/^Demanda excluída\./.test(h.texto)) todos.push({ h, d }); }));
    (E.excluidas || []).forEach((x) => { if (x.data.slice(0, 10) === dia) todos.push({ h: { data: x.data, usuario: x.usuario, texto: x.texto || ('Demanda excluída (estava ' + ((sit(x.situacao) || {}).um || '').toLowerCase() + ').' + (x.motivo ? ' Motivo: ' + x.motivo + '.' : '')) }, d: null, x }); });
    todos.sort((a, b) => String(b.h.data).localeCompare(String(a.h.data)));
    const nStatus = todos.filter((t) => RE_STATUS.test(t.h.texto)).length;
    const ls = so === 'status' ? todos.filter((t) => RE_STATUS.test(t.h.texto)) : todos;
    const nDem = new Set(ls.map((t) => (t.d || t.x).id)).size;
    const hora = (iso) => (String(iso).length > 10 ? String(iso).slice(11, 16) : '—');
    const rot = dia === hojeISO() ? 'Hoje, ' + br(dia) : br(dia);
    const linha = (t) => {
      const ref = t.d || t.x;
      const alvo = `<span class="mv-sei mono">${esc(ref.sei || 'Fora do SEI')}</span><span class="mv-local">${esc(ref.comarca || '')}</span>`;
      return `<li class="list-group-item mv-item ${RE_STATUS.test(t.h.texto) ? 'mv-status' : ''}">
        <span class="mv-hora mono">${hora(t.h.data)}</span>
        <span class="mv-corpo">${t.d && demanda(t.d.id) ? `<button type="button" class="mv-dem" data-acao="mov-abrir" data-id="${t.d.id}" data-sit="${esc(t.d.situacao)}">${alvo}</button>` : `<span class="mv-dem excl">${alvo}</span>`}<span class="mv-txt">${esc(t.h.texto)}</span></span>
        <span class="mv-quem">${avatar(t.h.usuario, 'xs')}<span>${esc(t.h.usuario === 'admin' ? 'Gestor' : (usr(t.h.usuario) ? usr(t.h.usuario).curto : nomeUsr(t.h.usuario)))}</span></span>
      </li>`;
    };
    return `
<div class="modal-content modal-m movs" role="dialog" aria-modal="true" aria-labelledby="mv-tit">
  <header class="modal-header"><div><h2 class="modal-title" id="mv-tit">Movimentações do Dia</h2><p>Tudo o que mudou nas demandas, com hora e autor. Visível só para o gestor.</p></div>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="mv-barra">
    <div class="mv-dia"><button type="button" class="btn btn-icone" data-acao="mov-dia" data-v="-1" aria-label="Dia anterior">${svg(16, '<path d="m15 6-6 6 6 6"/>', 2.2)}</button><b>${rot}</b><button type="button" class="btn btn-icone" data-acao="mov-dia" data-v="1" aria-label="Próximo dia" ${dia >= hojeISO() ? 'disabled' : ''}>${svg(16, '<path d="m9 6 6 6-6 6"/>', 2.2)}</button></div>
    <div class="btn-group vistas mv-filtro" role="group" aria-label="Mostrar">
      <button type="button" class="vista-btn mv-op" data-acao="mov-filtro" data-v="todas" aria-pressed="${so === 'todas'}">Todas <span>${todos.length}</span></button>
      <button type="button" class="vista-btn mv-op" data-acao="mov-filtro" data-v="status" aria-pressed="${so === 'status'}">Só status <span>${nStatus}</span></button>
    </div>
  </div>
  <div class="modal-body mv-corpo-lista">
    ${ls.length ? `<p class="mv-resumo">${ls.length} ${ls.length === 1 ? 'movimentação' : 'movimentações'} em ${nDem} ${nDem === 1 ? 'demanda' : 'demandas'}</p><ol class="list-group list-group-flush mv-lista">${ls.map(linha).join('')}</ol>` : '<p class="vazio-bloco">Nenhuma movimentação neste dia.</p>'}
  </div>
  <footer class="modal-footer">${flash('movimentos')}<span class="esp"></span><button type="button" class="btn btn-primary btn-lg" data-acao="fechar-modal">Fechar</button></footer>
</div>`;
  }

  // API: GET /api/lixeira
  function modalLixeira() {
    if (!ehGestor()) return '';
    const ls = E.lixeira.slice().sort((a, b) => String(b.excluidaEm).localeCompare(String(a.excluidaEm)));
    const linha = (x) => {
      const r = diasRestantes(x);
      return `<li class="list-group-item lx-item">
        <span class="mv-corpo">
          <span class="mv-dem excl"><span class="mv-sei mono">${esc(x.sei || 'Fora do SEI')}</span><span class="mv-local">${esc(x.comarca || '')}</span></span>
          <span class="mv-txt">Motivo: ${esc(x.motivoExclusao)}</span>
          <small class="lx-meta">Excluída em ${esc(brHora(x.excluidaEm))} · estava ${esc(sit(x.situacao).um.toLowerCase())} · ${r === 1 ? 'resta 1 dia' : 'restam ' + r + ' dias'}</small>
        </span>
        <button type="button" class="btn btn-outline-secondary btn-sm" data-acao="restaurar" data-id="${x.id}">Restaurar</button>
      </li>`;
    };
    return `
<div class="modal-content modal-m lixeira" role="dialog" aria-modal="true" aria-labelledby="lx-tit">
  <header class="modal-header"><div><h2 class="modal-title" id="lx-tit">Lixeira</h2><p>Demandas excluídas podem ser restauradas em até ${DIAS_LIXEIRA} dias.</p></div>
    <button type="button" class="btn btn-icone" data-acao="fechar-modal" aria-label="Fechar">${I.fechar}</button></header>
  <div class="modal-body">
    ${ls.length ? `<ol class="list-group list-group-flush lx-lista">${ls.map(linha).join('')}</ol>` : '<p class="vazio-bloco">A lixeira está vazia.</p>'}
  </div>
  <footer class="modal-footer">${flash('lixeira')}<span class="esp"></span><button type="button" class="btn btn-primary btn-lg" data-acao="fechar-modal">Fechar</button></footer>
</div>`;
  }

  // Em atendimento os dados travam; só o gestor altera a Data para Conclusão, com motivo
  function modalConclusao() {
    const d = demanda(E.modalDados && E.modalDados.id); if (!d) return '';
    const er = E.erros.conclusao; const atual = d.fim || d.inicio;
    return `
<form class="modal-content modal-p confirma" role="dialog" aria-modal="true" aria-labelledby="pr-tit" aria-describedby="pr-txt" data-form="conclusao" novalidate>
  <span class="conf-ico">${I.triangulo}</span>
  <h2 id="pr-tit">Alterar Data para Conclusão</h2>
  <p id="pr-txt">A data atual é ${esc(br(atual))}.</p>
  <div class="campo conf-motivo"><label class="form-label" for="pr-fim">Nova Data para Conclusão</label>${campoData('pr-fim', atual, !!er)}</div>
  <div class="campo conf-motivo">
    <span class="rotulo-l"><label class="form-label" for="pr-motivo">Motivo</label><span class="cont" id="pr-motivo-cont">0/100</span></span>
    <textarea id="pr-motivo" data-rascunho data-cont="100" class="form-control txt" rows="2" maxlength="100" ${er ? 'aria-invalid="true"' : ''}></textarea>
    ${er ? `<span class="erro">${esc(er)}</span>` : ''}
  </div>
  <div class="conf-btns"><button type="button" class="btn btn-outline-secondary btn-lg" data-acao="fechar-modal">Voltar</button><button type="submit" class="btn btn-primary btn-lg">Salvar</button></div>
</form>`;
  }

  function modalConfirmar() {
    const c = E.modalDados; const erM = E.erros.motivo;
    return `
<div class="modal-content modal-p confirma ${c.perigo ? 'perigo' : c.ok ? 'ok' : ''}" role="alertdialog" aria-modal="true" aria-labelledby="mc-tit" aria-describedby="mc-txt">
  <span class="conf-ico">${c.perigo ? I.triangulo : c.ok ? svg(22, '<path d="m5 12.5 4.5 4.5L19 7.5"/>', 2.4) : I.alerta}</span>
  <h2 id="mc-tit">${esc(c.titulo)}</h2>
  <p id="mc-txt">${esc(c.texto)}</p>
  ${c.motivo ? `<div class="campo conf-motivo">
    <span class="rotulo-l"><label class="form-label" for="mc-motivo">Motivo</label><span class="cont" id="mc-motivo-cont">0/100</span></span>
    <textarea id="mc-motivo" data-rascunho data-cont="100" class="form-control txt" rows="2" maxlength="100" ${erM ? 'aria-invalid="true"' : ''}></textarea>
    ${erM ? `<span class="erro">${esc(erM)}</span>` : ''}
  </div>` : ''}
  <div class="conf-btns"><button type="button" class="btn btn-outline-secondary btn-lg" data-acao="fechar-modal">${esc(c.voltar || 'Voltar')}</button><button type="button" class="btn btn-lg ${c.perigo ? 'btn-danger' : c.ok ? 'btn-success' : 'btn-primary'}" data-acao="confirmar">${esc(c.botao)}</button></div>
</div>`;
  }

  // mensagens de confirmação: aparecem dentro da tela em uso, em verde com check
  function ondeFlash() {
    if (E.modal === 'nova') return (E.modalDados && E.modalDados.sucesso) ? 'suc' : 'nova';
    if (E.modal === 'sobre' || E.modal === 'equipe' || E.modal === 'acionamento' || E.modal === 'relatorio' || E.modal === 'movimentos' || E.modal === 'lixeira') return E.modal;
    if (E.aberta) return 'det';
    return 'pagina';
  }
  function flash(onde) {
    if (!E.toast || ondeFlash() !== onde) return '';
    return `<span class="flash ${E.toast.alerta ? 'aviso' : ''} ${E._anim.toast ? 'anim' : ''}" role="status">${E.toast.alerta ? I.alerta : I.check}<span>${esc(E.toast.msg)}</span></span>`;
  }

  // ------------------------------------------------------------------ desenho
  const app = document.getElementById('app');
  function desenhar() {
    const foco = document.activeElement; const idFoco = foco && foco.id;
    let sel = null; try { if (idFoco && foco.selectionStart != null) sel = [foco.selectionStart, foco.selectionEnd]; } catch (e) { /* */ }
    // camadas que acabaram de abrir ganham animação; as que já estavam abertas só são redesenhadas, sem piscar
    const k = { det: E.aberta ? String(E.aberta) : '', modal: E.modal || '', suc: (E.modalDados && E.modalDados.sucesso) || '', toast: E.toast ? E.toast.id : '', destaque: E.destaque || '' };
    const ant = E._k || {};
    // card recém-aberto: apaga a bolinha e o select de empresa volta a começar vazio
    if (k.det && k.det !== ant.det) { E.ultimaEmp = ''; E.detAltDe = null; marcarVisto(); }
    E._anim = { det: !!k.det && k.det !== ant.det, modal: !!k.modal && k.modal !== ant.modal, suc: !!k.suc && k.suc !== ant.suc, toast: !!k.toast && k.toast !== ant.toast, destaque: !!k.destaque && k.destaque !== ant.destaque };
    // posição de rolagem de cada área, para nada pular depois do clique
    const rol = {};
    ['.rolagem', '.det-corpo', '.modal-camada .modal-body'].forEach((q) => { const el = document.querySelector(q); if (el) rol[q] = el.scrollTop; });
    const mesmaTela = ant.det === k.det && ant.aba === E.aba && ant.modal === k.modal;
    // preserva o que a pessoa está digitando quando a tela é redesenhada (ex.: um aviso aparece)
    const chave = (E.aberta || '') + '|' + E.aba + '|' + (E.aberta ? '' : (E.modal || ''));
    const rasc = {};
    if (!E.limparRascunho && E.chaveRasc === chave) {
      app.querySelectorAll('[data-rascunho]').forEach((el) => { rasc[el.id] = el.type === 'checkbox' ? el.checked : el.value; });
      app.querySelectorAll('input[type=radio]:checked').forEach((el) => { rasc['radio:' + el.name] = el.value; });
    }
    app.innerHTML = `<div class="moldura">${telaTopo()}${telaPainel()}<footer class="rodape"><button type="button" class="credito" data-acao="sobre">© 2026 DITIC-DSUP | Tribunal de Justiça - RS</button></footer></div>${telaDetalhe()}${telaModal()}`;
    Object.keys(rasc).forEach((k) => {
      if (k.startsWith('radio:')) { const r = app.querySelector(`input[name="${k.slice(6)}"][value="${rasc[k]}"]`); if (r) r.checked = true; return; }
      const el = document.getElementById(k); if (el) { if (el.type === 'checkbox') el.checked = rasc[k]; else el.value = rasc[k]; }
    });
    trocarFinalidade(); atualizaTransf(); filtrarLocais(); ajustaPostits(); ajustaTextos(); if (CAL) desenharCal(); alturaDetalhe(); mostrarAbaAtiva();
    E.chaveRasc = chave; E.limparRascunho = false; E.recemTk = false; k.aba = E.aba; E._k = k;
    Object.keys(rol).forEach((q) => { const el = document.querySelector(q); if (el && (q === '.rolagem' ? !E.zerarLista : mesmaTela)) el.scrollTop = rol[q]; });
    E.zerarLista = false;
    document.body.classList.toggle('modal-open', !!(E.aberta || E.modal));
    if (idFoco) {
      const el = document.getElementById(idFoco);
      if (el) { el.focus({ preventScroll: true }); if (sel) try { el.setSelectionRange(sel[0], sel[1]); } catch (e) { /* */ } }
    }
  }
  let tToast, tDestaque;
  function aviso(msg, alerta) {
    E.toast = { msg, alerta, id: Date.now() + Math.random() }; clearTimeout(tToast);
    tToast = setTimeout(() => { E.toast = null; document.querySelectorAll('.flash').forEach((t) => { t.classList.add('sai'); setTimeout(() => t.remove(), 250); }); }, 4000);
  }
  function destacar(id) {
    E.destaque = id; clearTimeout(tDestaque);
    tDestaque = setTimeout(() => { E.destaque = null; document.querySelectorAll('.linha-dem.destaque').forEach((c) => c.classList.remove('destaque')); }, 6000);
  }
  function mudou() { automatizar(); persistir(); desenhar(); }
  function marcarSujo() {
    if (E.sujo) return; E.sujo = true;
    const b = document.getElementById('btn-salvar'); if (b) b.disabled = false;
    const t = document.getElementById('sujo-txt'); if (t) t.hidden = false;
  }
  // pergunta antes de perder alterações não salvas nos detalhes; o status escolhido continua valendo ao trocar de aba,
  // porque o select fica no cabeçalho (ex.: escolher Acionada e ir registrar o ticket)
  function guardar(fn, trocaAba) {
    if ((E.sujo && E.aberta && E.aba === 'dados') || (E.statusRascunho && !trocaAba)) {
      E.modal = 'confirmar';
      E.modalDados = { titulo: 'Descartar Alterações?', texto: 'Você mudou os detalhes desta demanda e ainda não salvou.', botao: 'Descartar', perigo: true, acao: () => { E.sujo = false; if (!trocaAba) E.statusRascunho = null; E.limparRascunho = true; fn(); } };
      desenhar(); return;
    }
    E.sujo = false; fn();
  }
  function irPara(id) {
    // leva a lista até a folha onde a demanda está
    const ls = visiveis(); const i = ls.findIndex((d) => d.id === id);
    if (i >= 0) E.folha = Math.floor(i / porFolha()) + 1;
  }

  // ------------------------------------------------------------------ regras do fluxo
  // API: PATCH /api/mudancas/{id}/situacao
  function setSituacao(d, nova, texto) { d.situacao = nova; E.statusRascunho = null; if (FINAIS.includes(nova)) { E.sujo = false; E.editTk = false; E.limparRascunho = true; } if (nova === 'acionada') d.acionadaEm = hojeISO(); registrar(d, texto || ('Situação alterada para ' + sit(nova).um + '.')); }
  function irAba(id, aba, foco, msg) {
    E.aberta = id; E.aba = aba; E.sujo = false; E.menu = null; E.erros = {};
    if (msg) aviso(msg, true);
    desenhar(); const el = foco && document.getElementById(foco); if (el) el.focus();
  }
  // regras do select de status: Em atendimento e Pendente nunca são escolhidos à mão, mudam sozinhos pela data;
  // depois de acionada, a demanda não volta para Nova; cancelar fica só em Mais ações (gestor); Concluída e Cancelada são finais
  const TRAVADOS = ['atendimento', 'pendente'];
  const FINAIS = ['concluida', 'cancelada'];
  function destinosStatus(d) {
    if (TRAVADOS.includes(d.situacao) || FINAIS.includes(d.situacao)) return [];
    const r = [];
    if (d.situacao !== 'acionada') r.push('acionada');
    return r;
  }
  // o select só guarda a escolha; a mudança acontece em Salvar alterações
  function escolherStatus(d, novo) { E.statusRascunho = novo === d.situacao ? null : novo; desenhar(); }
  function salvarStatus(d) {
    const novo = E.statusRascunho;
    if (!destinosStatus(d).includes(novo)) { E.statusRascunho = null; aviso('Esta mudança de status não é mais permitida.', true); mudou(); return; }
    const rot = sit(novo).um;
    if (novo === 'acionada') {
      if (!d.ticketPrincipal) { irAba(d.id, 'tickets', 't-principal', 'Para marcar como Acionada, registre antes o ticket principal e salve.'); return; }
      // sem data, a automação nunca levaria a demanda adiante
      if (!d.inicio) { irAba(d.id, 'dados', 'f-ini', 'Para marcar como Acionada, informe a Data de Início e salve.'); return; }
      // com o agendamento já vencido, a regra automática levaria direto para Pendente: pede uma nova data
      if (d.inicio && (d.fim || d.inicio) < hojeISO()) { irAba(d.id, 'dados', 'f-ini', 'O agendamento já passou. Informe a nova data e salve.'); return; }
    }
    // o SLA não impede o acionamento: fora do prazo, fica o aviso e o registro no histórico
    const fora = novo === 'acionada' ? foraDoSLA(d) : [];
    const noPrazo = fora.length ? ' Acionada fora do SLA: ' + fora.map((e) => e + ' (até ' + br(limiteSLA(d, e)) + ')').join(', ') + '.' : '';
    setSituacao(d, novo, (novo === 'acionada' ? 'Empresas acionadas. ' : '') + 'Status alterado: ' + sit(d.situacao).um + ' → ' + rot + '.' + noPrazo);
    if (d.responsavel) avisar(d, 'status', d.responsavel);
    // agendada para hoje: automatizar(), em mudou(), já leva para Em atendimento e para a carga do gestor
    const jaHoje = novo === 'acionada' && d.inicio && d.inicio <= hojeISO();
    aviso((jaHoje ? 'Demanda acionada e já Em Atendimento, com o gestor.' : 'Status alterado para ' + rot + '.') + (fora.length ? ' Fora do SLA: ' + fora.join(', ') + '.' : ''), fora.length > 0);
    destacar(d.id); mudou();
  }
  function somarDias(iso, n) { const x = new Date(iso + 'T12:00'); x.setDate(x.getDate() + n); return x.getFullYear() + '-' + pad(x.getMonth() + 1) + '-' + pad(x.getDate()); }
  const diaSeguinte = (iso) => somarDias(iso, 1);
  // último dia em que a empresa ainda pode ser acionada para esta demanda
  const limiteSLA = (d, emp) => somarDias(d.inicio, -SLA_ACIONAMENTO[emp]);
  // empresas dos subtickets cujo prazo de acionamento já venceu
  function foraDoSLA(d) {
    if (!d.inicio) return [];
    const hoje = hojeISO();
    return EMPRESAS.filter((e) => d.subtickets.some((s) => s.empresa === e) && limiteSLA(d, e) < hoje);
  }
  function textoSLA(d) {
    const grupo = (dias) => { const ls = EMPRESAS.filter((e) => SLA_ACIONAMENTO[e] === dias); return ls.join(' e ') + ' até ' + br(limiteSLA(d, ls[0])); };
    return 'Prazo para acionar: ' + grupo(2) + ' · ' + grupo(1) + '.';
  }
  function statusCab(d) {
    if (TRAVADOS.includes(d.situacao)) {
      const quando = d.situacao === 'atendimento' && d.inicio ? 'Vai para validação em ' + br(diaSeguinte(d.fim || d.inicio)).slice(0, 5)
        : d.situacao === 'pendente' ? (d.responsavel && d.responsavel !== 'admin' ? 'Com ' + nomeUsr(d.responsavel) + ' para atendimento extra' : 'Aguardando a conclusão pelo gestor') : '';
      return `<span class="badge st-fixo" title="Status automático: não pode ser alterado à mão">${I.cadeadoP}<span>${sit(d.situacao).um}</span></span>${quando ? `<span class="st-nota">${quando}</span>` : ''}`;
    }
    if (FINAIS.includes(d.situacao)) {
      return `<span class="badge st-fixo" data-sit="${esc(d.situacao)}" title="Status final: não pode ser alterado">${I.cadeadoP}<span>${esc(sit(d.situacao).um)}</span></span><span class="st-nota">Demanda encerrada · somente consulta</span>`;
    }
    const destinos = destinosStatus(d);
    if (!destinos.length) {
      return `<span class="badge st-fixo" data-sit="${esc(d.situacao)}" title="Status automático: avança sozinho pela data">${I.cadeadoP}<span>${esc(sit(d.situacao).um)}</span></span>`;
    }
    const ops = [d.situacao].concat(destinos);
    const marcado = ops.includes(E.statusRascunho) ? E.statusRascunho : d.situacao;
    return `<span class="st-sel-wrap"><label for="d-status" class="visually-hidden">Status</label><select id="d-status" class="st-sel" data-status="${d.id}" title="Escolha o status e clique em Salvar alterações">${SITUACOES.filter((x) => ops.includes(x.id)).map((x) => `<option value="${x.id}" ${x.id === marcado ? 'selected' : ''}>${x.um}</option>`).join('')}</select></span>`;
  }
  // botão Concluir demanda (só em Pendente), com confirmação
  function pedirConclusao(d) {
    if (d.situacao !== 'pendente') return;
    if (!d.ticketPrincipal) { irAba(d.id, 'tickets', 't-principal', 'Para concluir, registre antes o ticket principal.'); return; }
    E.modal = 'confirmar';
    E.modalDados = { titulo: 'Concluir Esta Demanda?', texto: 'A demanda passa para Concluída e sai da carga do gestor, ficando com o setor, sem atribuição. Essa ação não pode ser desfeita e fica registrada no histórico.', botao: 'Concluir demanda', ok: true, acao: () => { concluir(d); destacar(d.id); aviso('Demanda concluída.'); mudou(); } };
    desenhar();
  }
  // API: PATCH /api/mudancas/{id}/situacao { situacao: 'CONCLUIDA' } (só o gestor)
  function concluir(d) {
    const de = sit(d.situacao).um; const tec = d.responsavel && d.responsavel !== 'admin' ? d.responsavel : d.tecnico;
    setSituacao(d, 'concluida', 'Status alterado: ' + de + ' → Concluída' + (tec ? '. Atendida por ' + nomeUsr(tec) : '') + '.');
    paraSetor(d);
    destacar(d.id); aviso('Demanda ' + num4(d.id) + ' concluída.'); mudou();
  }

  function textoTickets(d) {
    const p = ['Ticket: ' + (d.ticketPrincipal || '-')];
    EMPRESAS.forEach((e) => { const ls = d.subtickets.filter((s) => s.empresa === e); p.push(e + ': ' + (ls.length ? ls.map((s) => s.numero).join(' / ') : '-')); });
    return p.join('\t');
  }
  function copiar(texto, msg) {
    const falha = () => { aviso('Não foi possível copiar. Selecione o texto e use Ctrl+C.', true); desenhar(); };
    try { navigator.clipboard.writeText(texto).then(() => { aviso(msg || 'Copiado.'); desenhar(); }, falha); } catch (e) { falha(); }
  }

  // ------------------------------------------------------------------ formulários
  const val = (id) => { const el = document.getElementById(id); return el ? el.value.trim() : ''; };

  function enviar(form) {
    const tipo = form.dataset.form;
    const d = demanda(E.aberta);
    E.erros = {};
    if (tipo === 'dados' && d) { // API: PUT /api/mudancas/{id} (sei, comarca, descricao, responsavel, inicio, fim, hora, informacoes)
      const trava = TRAVADOS.includes(d.situacao); // Em atendimento e Para validação: só responsável e informações adicionais
      const sei = val('f-sei'); const ini = dataISO('f-ini'); const fim = dataISO('f-fim'); const hora = horaVal('f-hora');
      if (!trava) {
        if (sei && !RE_SEI.test(sei)) E.erros.sei = 'Número incompleto. O formato é 8.AAAA.NNNN/NNNNNN-D.';
        const ed = erroDatas(ini, fim); if (ed) E.erros.data = ed;
        // demanda acionada não pode perder a data nem ir para o passado (cairia direto em Para validação)
        else if (d.situacao === 'acionada' && !ini) E.erros.data = 'Demanda acionada precisa ter Data de Início.';
        else if (d.situacao === 'acionada' && (fim || ini) < hojeISO()) E.erros.data = 'Em demanda acionada, o agendamento não pode estar no passado.';
        if (hora === null) E.erros.hora = 'Hora inválida. Use hh:mm, de 00:00 a 23:59.';
        if (Object.keys(E.erros).length) { desenhar(); return; }
      }
      const antes = { resp: d.responsavel, ini: d.inicio, fim: d.fim, hora: d.hora || '' };
      if (ehGestor()) atribuir(d, val('f-resp') || null);
      if (trava) d.informacoes = val('f-info');
      else Object.assign(d, { sei, comarca: cidade(val('f-local')), descricao: val('f-desc'), inicio: ini || null, fim: (fim && fim !== ini) ? fim : null, hora: hora || null, informacoes: val('f-info') });
      if (antes.resp !== d.responsavel) regResp(d, antes.resp, d.responsavel);
      if (antes.ini !== d.inicio || antes.fim !== d.fim || antes.hora !== (d.hora || '')) registrar(d, 'Agendamento alterado para ' + agendaComHora(d) + '.');
      else if (antes.resp === d.responsavel && E.sujo) registrar(d, 'Dados da demanda atualizados.');
      E.limparRascunho = true; E.sujo = false;
      if (E.statusRascunho) { persistir(); salvarStatus(d); return; }
      aviso('Alterações salvas.'); mudou(); return;
    }
    if (tipo === 'conclusao' && d) { // API: PATCH /api/mudancas/{id}/conclusao { data, motivo } (só o gestor, só Em atendimento)
      if (d.situacao !== 'atendimento') return;
      const nova = dataISO('pr-fim'); const motivo = val('pr-motivo'); const atual = d.fim || d.inicio;
      const erro = !nova ? 'Informe uma data válida.' : nova < d.inicio ? 'A data não pode ser antes da data de início.' : nova < hojeISO() ? 'A data não pode estar no passado.' : nova === atual ? 'Escolha uma data diferente da atual.' : !motivo ? 'Informe o motivo.' : '';
      if (erro) { E.erros.conclusao = erro; desenhar(); return; }
      d.fim = nova !== d.inicio ? nova : null;
      registrar(d, 'Data para Conclusão alterada: ' + br(atual) + ' → ' + br(nova) + '. Motivo: ' + motivo + '.');
      E.modal = null; E.modalDados = null; E.erros = {}; E.limparRascunho = true; E.sujo = false;
      aviso('Data para Conclusão alterada.'); mudou(); return;
    }
    if (tipo === 'principal' && d) { // API: PUT /api/mudancas/{id}/ticket { numero }
      if (TRAVADOS.includes(d.situacao) && d.ticketPrincipal) return; // travada: não troca o ticket já registrado
      const bruto = val('t-principal'); const n = bruto.replace(/\D/g, '');
      if (bruto && !/^\d{6,8}$/.test(n)) { E.erros.principal = 'Use só o número do ticket (6 a 8 dígitos).'; desenhar(); return; }
      if (!n) { E.erros.principal = 'Informe o número do ticket.'; desenhar(); return; }
      if ((d.ticketPrincipal || '') === n) { E.editTk = false; desenhar(); return; }
      d.ticketPrincipal = n || null;
      d.ticketEm = n ? { data: agoraISO(), usuario: E.usuario || 'admin' } : null;
      E.editTk = false; E.recemTk = !!n;
      registrar(d, n ? 'Ticket principal ' + n + ' registrado.' : 'Ticket principal removido.');
      E.limparRascunho = true; E.manterRolagem = true;
      aviso(d.situacao === 'nova' ? 'Ticket ' + n + ' registrado. Agora a demanda pode ser marcada como acionada.' : 'Ticket ' + n + ' registrado.');
      mudou(); return;
    }
    if (tipo === 'sub' && d) { // API: POST /api/mudancas/{id}/subtickets [{ empresa, numero, servico, quantidade }]
      const emp = val('n-emp'); const fin = val('n-fin');
      if (!emp) { E.erros.sub = 'Escolha a empresa.'; E.erros.emp = true; desenhar(); document.getElementById('n-emp').focus(); return; }
      const nums = (val('n-num').match(/\d{6,8}/g) || []);
      if (!nums.length) { E.erros.sub = 'Informe ao menos um número de ticket (6 a 8 dígitos).'; E.ultimaEmp = emp; desenhar(); document.getElementById('n-num').focus(); return; }
      if (!fin) { E.erros.sub = 'Escolha o serviço do subticket.'; E.erros.fin = true; E.ultimaEmp = emp; desenhar(); const el = document.getElementById('n-fin'); if (el) el.focus(); return; }
      const qtd = parseInt(val('n-qtd'), 10);
      if (!(qtd >= 1 && qtd <= 999)) { E.erros.sub = 'Informe a quantidade de serviços (1 a 999).'; E.erros.qtd = true; E.ultimaEmp = emp; desenhar(); const el = document.getElementById('n-qtd'); if (el) el.focus(); return; }
      const novos = nums.filter((n) => !d.subtickets.some((s) => s.numero === n));
      novos.forEach((n) => d.subtickets.push({ empresa: emp, numero: n, finalidade: fin, quantidade: qtd }));
      E.ultimaEmp = '';
      if (novos.length) registrar(d, 'Subticket' + (novos.length > 1 ? 's ' : ' ') + emp + ' ' + novos.join(', ') + (novos.length > 1 ? ' adicionados' : ' adicionado') + ' (' + fin + ', ' + qtd + (qtd === 1 ? ' serviço' : ' serviços') + ').');
      E.manterRolagem = true; E.limparRascunho = true;
      aviso(novos.length ? (novos.length > 1 ? novos.length + ' subtickets incluídos.' : 'Subticket incluído.') : 'Esses tickets já estavam na lista.', !novos.length);
      mudou(); const el = document.getElementById('n-num'); if (el) el.focus(); return;
    }
    if (tipo === 'nota' && d) { // API: POST /api/mudancas/{id}/historico { texto }
      const t = val('h-nota'); if (!t) return;
      registrar(d, t); E.limparRascunho = true; aviso('Andamento registrado.'); mudou(); return;
    }
    if (tipo === 'equipe-add') {
      const nome = val('eq-nome').replace(/\s+/g, ' ');
      const cor = (form.querySelector('input[name="eq-cor"]:checked') || {}).value || proximaCor();
      if (!nome) { E.erros.eqAdd = 'Informe o nome.'; desenhar(); return; }
      if (E.equipe.some((u) => normal(u.nome) === normal(nome))) { E.erros.eqAdd = 'Já existe alguém com esse nome na equipe.'; desenhar(); return; }
      // API: POST /api/equipe
      let id = normal(nome).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'pessoa'; while (usr(id)) id += '-2';
      E.equipe.push({ id, nome, curto: nome.split(' ')[0], ini: iniciaisDe(nome), cor: corOk(cor), ativo: true });
      E.limparRascunho = true; aviso(nome + ' incluído(a) na equipe.'); mudou(); return;
    }
    if (tipo === 'equipe-edit') {
      const u = usr(form.dataset.id); const nome = val('ed-nome').replace(/\s+/g, ' ');
      if (!nome) { E.erros.eqEdit = 'Informe o nome.'; desenhar(); return; }
      if (E.equipe.some((x) => x.id !== u.id && normal(x.nome) === normal(nome))) { E.erros.eqEdit = 'Já existe alguém com esse nome.'; desenhar(); return; }
      // API: PUT /api/equipe/{id}
      u.nome = nome; u.curto = nome.split(' ')[0]; u.ini = iniciaisDe(nome); u.cor = corOk((form.querySelector('input[name="ed-cor"]:checked') || {}).value || u.cor);
      E.modalDados = {}; E.limparRascunho = true; aviso('Dados de ' + u.curto + ' atualizados.'); mudou(); return;
    }
    if (tipo === 'equipe-transf') {
      const t = E.modalDados.transf; const para = val('tr-dest');
      const ids = [...form.querySelectorAll('input[name="tr-d"]:checked')].map((x) => Number(x.value));
      t.marcadas = ids; t.para = para;
      if (!para) { E.erros.transf = 'Escolha para quem transferir.'; desenhar(); return; }
      if (!ids.length && !t.desativar) { E.erros.transf = 'Marque ao menos uma demanda.'; desenhar(); return; }
      const de = usr(t.de); const novo = para === '_sem' ? null : para;
      // API: POST /api/equipe/{de}/transferir { para, demandas: [...] }
      ids.forEach((id) => { const d = demanda(id); atribuir(d, novo); registrar(d, 'Demanda transferida de ' + de.nome + ' para ' + nomeResp(d.responsavel) + '.'); });
      if (t.desativar) de.ativo = false;
      if (E.filtroResp === t.de && t.desativar) E.filtroResp = '';
      E.modalDados = {}; E.limparRascunho = true;
      aviso((ids.length ? ids.length + (ids.length === 1 ? ' demanda transferida' : ' demandas transferidas') : 'Nenhuma demanda transferida') + (t.desativar ? '; ' + de.curto + ' desativado(a).' : '.'));
      mudou(); return;
    }
    if (tipo === 'login') { // API: POST /api/login { usuario, senha } — no protótipo qualquer senha serve para 'admin'
      const login = normal(val('l-usr'));
      const u = GESTORES.find((g) => g.id === login || (g.apelidos || []).includes(login));
      if (!u || !val('l-sen')) { E.erros.login = !u ? 'Só o gestor entra no sistema. No protótipo, use o usuário admin.' : 'Informe a senha.'; E.modalDados = Object.assign(E.modalDados || {}, { usr: val('l-usr') }); desenhar(); return; }
      const depois = E.modalDados && E.modalDados.depois;
      if (!E.senhaDefinida) {
        E.modal = 'senha'; E.modalDados = { usuario: u.id, atual: document.getElementById('l-sen').value, depois }; E.erros = {}; E.limparRascunho = true;
        desenhar(); document.getElementById('s-nova').focus(); return;
      }
      entrar(u.id, depois, 'Você entrou como gestor.');
      return;
    }
    if (tipo === 'senha') { // API: POST /api/conta/senha { atual, nova } (grava o hash e zera deve_trocar_senha)
      const m = E.modalDados || {}; const nova = document.getElementById('s-nova').value; const conf = document.getElementById('s-conf').value;
      const erro = nova.length < 8 ? 'A nova senha precisa ter pelo menos 8 caracteres.' : nova !== conf ? 'As senhas não são iguais.' : nova === m.atual ? 'A nova senha precisa ser diferente da senha inicial.' : '';
      if (erro) { E.erros.senha = erro; desenhar(); document.getElementById('s-nova').focus(); return; }
      E.senhaDefinida = true;
      entrar(m.usuario, m.depois, 'Senha criada. Você entrou como gestor.');
      return;
    }
    if (tipo === 'nova') {
      if (E.modalDados && E.modalDados.sucesso) return;
      const semSei = document.getElementById('n-semsei').checked;
      const r = form.querySelector('input[name="n-resp"]:checked');
      const v = { sei: semSei ? '' : val('n-sei'), semSei, comarca: cidade(val('n-local')), descricao: val('n-desc'), responsavel: r ? r.value : '', inicio: dataISO('n-ini'), fim: dataISO('n-fim'), hora: horaVal('n-hora'), informacoes: '' };
      E.modalDados = v;
      if (!semSei && !v.sei) E.erros.sei = 'Informe o número do expediente ou marque “Demanda fora do SEI”.';
      else if (!semSei && !RE_SEI.test(v.sei)) E.erros.sei = 'Número incompleto. O formato é 8.AAAA.NNNN/NNNNNN-D.';
      if (!v.comarca) E.erros.local = 'Informe a comarca ou o prédio.';
      if (!v.descricao) E.erros.desc = 'Descreva a demanda.';
      const ed = erroDatas(v.inicio, v.fim); if (ed) E.erros.data = ed;
      if (v.hora === null) E.erros.hora = 'Hora inválida. Use hh:mm, de 00:00 a 23:59.';
      if (v.inicio === null) v.inicio = ''; if (v.fim === null) v.fim = ''; if (v.hora === null) v.hora = val('n-hora');
      if (Object.keys(E.erros).length) { E.limparRascunho = true; desenhar(); const pri = form.querySelector('[aria-invalid="true"]'); if (pri) pri.focus(); return; }
      // API: POST /api/mudancas
      const id = Math.max(0, ...E.demandas.map((x) => x.id), ...E.excluidas.map((x) => x.id)) + 1; // não reaproveita número de demanda na lixeira
      const nova = { id, sei: v.sei, descricao: v.descricao, comarca: v.comarca, responsavel: v.responsavel || null, inicio: v.inicio || null, fim: (v.fim && v.fim !== v.inicio) ? v.fim : null, hora: v.hora || null, situacao: 'nova', ticketPrincipal: null, subtickets: [], informacoes: v.informacoes, historico: [], criadaEm: hojeISO(), passou: [], aviso: null };
      registrar(nova, 'Demanda registrada a partir do expediente SEI' + (v.responsavel ? ' e atribuída a ' + nomeUsr(v.responsavel) : '') + '.');
      if (nova.responsavel) { avisar(nova, 'nova', nova.responsavel); nova.passou = [nova.responsavel]; }
      E.demandas.push(nova);
      E.sitAtivas.add('nova');
      irPara(id); destacar(id);
      E.modalDados = { sucesso: id };
      mudou();
    }
  }

  // ------------------------------------------------------------------ eventos
  document.addEventListener('submit', (ev) => {
    const f = ev.target.closest('form[data-form]'); if (!f) return; ev.preventDefault();
    const tf = f.dataset.form;
    if (tf === 'nova' || tf === 'conclusao' || tf.startsWith('equipe')) { if (precisaGestor()) return; }
    else if (tf !== 'login' && tf !== 'senha' && tf !== 'nota' && precisaEditar(demanda(E.aberta))) return;
    enviar(f);
  });

  document.addEventListener('click', (ev) => {
    if (CAL && !ev.target.closest('#cal-pop') && !ev.target.closest('.data-btn')) fecharCal();
    const cal = ev.target.closest('#cal-pop [data-acao], .data-btn[data-acao]');
    if (cal) {
      const ac = cal.dataset.acao; const vv = cal.dataset.v;
      if (ac === 'cal-abrir') { if (CAL && CAL.id === vv) fecharCal(); else abrirCal(vv); }
      else if (ac === 'cal-mes') { CAL.mes += Number(vv); if (CAL.mes < 0) { CAL.mes = 11; CAL.ano--; } if (CAL.mes > 11) { CAL.mes = 0; CAL.ano++; } desenharCal(); }
      else if (ac === 'cal-dia') escolherData(vv);
      else if (ac === 'cal-hoje') escolherData(hojeISO());
      else if (ac === 'cal-limpar') escolherData('');
      return;
    }
    if (ev.target.closest('#cal-pop')) return;
    const alvo = ev.target.closest('[data-acao]'); if (!alvo) { if (E.menu && !ev.target.closest('.dropdown-menu')) { E.menu = null; desenhar(); } return; }
    const a = alvo.dataset.acao; const id = alvo.dataset.id ? Number(alvo.dataset.id) : null; const v = alvo.dataset.v;
    // clicar fora do modal não fecha nada; só recolhe um menu que esteja aberto
    if (a === 'fundo-modal') { if (E.menu) { E.menu = null; desenhar(); } return; }
    if (a !== 'menu-mais' && a !== 'resp-pop' && a !== 'local-pop' && a !== 'menu-conta' && E.menu) E.menu = null;
    const SO_GESTOR = ['relatorio', 'concluir-dem', 'cancelar', 'excluir', 'devolver-tec', 'movimentos', 'equipe', 'nova', 'lixeira', 'restaurar', 'alterar-conclusao'];
    const EDITA = ['sub-del', 'tk-alterar', 'devolver-gestor'];
    if (SO_GESTOR.includes(a) && precisaGestor()) return;
    if (EDITA.includes(a) && precisaEditar(demanda(E.aberta))) return;
    if ((a === 'sub-del' || a === 'tk-alterar') && precisaDestravar(demanda(E.aberta))) return;
    const d = demanda(E.aberta);
    switch (a) {
      case 'inicio': E.aberta = null; window.scrollTo(0, 0); desenhar(); break;
      case 'menu-conta': E.menu = E.menu === 'conta' ? null : 'conta'; desenhar(); break;
      case 'login': E.menu = null; E.modal = 'login'; E.modalDados = null; E.erros = {}; E.limparRascunho = true; desenhar(); setTimeout(() => { const el = document.getElementById('l-usr'); if (el) el.focus(); }, 0); break;
      case 'ver-senha': { const el = document.getElementById('l-sen'); if (el) { el.type = el.type === 'password' ? 'text' : 'password'; alvo.setAttribute('aria-label', el.type === 'password' ? 'Mostrar senha' : 'Ocultar senha'); } break; }
      case 'sair': E.usuario = null; E.menu = null; E.filtroResp = ''; aviso('Você saiu da conta.'); mudou(); break;
      case 'eq-editar': if (precisaGestor()) break; E.modalDados = { editar: v }; E.erros = {}; E.limparRascunho = true; desenhar(); { const el = document.getElementById('ed-nome'); if (el) { el.focus(); el.select(); } } break;
      case 'eq-cancelar': E.modalDados = {}; E.erros = {}; E.limparRascunho = true; desenhar(); break;
      case 'eq-transferir': if (precisaGestor()) break; E.modalDados = { transf: { de: v } }; E.erros = {}; E.limparRascunho = true; desenhar(); break;
      case 'eq-voltar': E.modalDados = {}; E.erros = {}; E.limparRascunho = true; desenhar(); break;
      case 'eq-desativar': {
        if (precisaGestor()) break; const u = usr(v);
        if (abertasDe(v).length) { E.modalDados = { transf: { de: v, desativar: true } }; E.erros = {}; E.limparRascunho = true; desenhar(); break; }
        u.ativo = false; aviso(u.curto + ' desativado(a). Não aparece mais para receber demandas.'); mudou(); break;
      }
      case 'eq-reativar': { if (precisaGestor()) break; const u = usr(v); u.ativo = true; aviso(u.curto + ' reativado(a).'); mudou(); break; }
      case 'tr-todas': {
        const cbs = [...document.querySelectorAll('input[name="tr-d"]')]; const todas = cbs.every((c) => c.checked);
        cbs.forEach((c) => { c.checked = !todas; }); alvo.textContent = todas ? 'Marcar todas' : 'Desmarcar todas'; atualizaTransf(); break;
      }
      case 'proto-gestor': { const a = document.getElementById('l-usr'); const b = document.getElementById('l-sen'); if (a) a.value = 'admin'; if (b) b.value = 'admin'; const f = document.querySelector('form.login'); if (f) f.requestSubmit(); break; }
      case 'equipe': E.menu = null; if (precisaGestor('A Equipe é mantida pelo gestor. Entre para incluir, editar ou desativar pessoas.', () => { E.modal = 'equipe'; E.modalDados = {}; desenhar(); })) break; E.modal = 'equipe'; E.modalDados = {}; E.erros = {}; E.limparRascunho = true; desenhar(); break;
      case 'nova':
        if (precisaGestor('Para incluir uma demanda, entre com o usuário do gestor.', () => { const b = document.querySelector('[data-acao=nova]'); if (b) b.click(); })) break;
        E.modal = 'nova'; E.modalDados = null; E.erros = {}; E.limparRascunho = true; desenhar(); setTimeout(() => { const el = document.getElementById('n-sei'); if (el) el.focus(); }, 0); break;
      case 'incluir-outra': E.modalDados = null; E.erros = {}; E.limparRascunho = true; desenhar(); setTimeout(() => { const el = document.getElementById('n-sei'); if (el) el.focus(); }, 0); break;
      case 'abrir-nova': E.modal = null; E.modalDados = null; E.aberta = id; E.aba = 'tickets'; desenhar(); setTimeout(() => { const el = document.getElementById('t-principal'); if (el) el.focus(); }, 0); break;
      case 'ordenar': {
        const dir = alvo.dataset.dir;
        if (dir) { E.ordCol = v; E.ordDir = dir; }
        else if (E.ordCol === v) E.ordDir = E.ordDir === 'asc' ? 'desc' : 'asc';
        else { E.ordCol = v; E.ordDir = v === 'ag' ? 'desc' : 'asc'; }
        E.folha = 1; E.zerarLista = true; desenhar(); break;
      }
      case 'resp-pop': E.menu = E.menu === 'resp' ? null : 'resp'; desenhar(); break;
      case 'local-pop': E.menu = E.menu === 'local' ? null : 'local'; E.localQ = ''; desenhar(); { const q = document.getElementById('f-local-q'); if (q) q.focus(); } break;
      case 'local-escolher': E.filtroLocal = v || ''; E.menu = null; E.localQ = ''; E.folha = 1; desenhar(); break;
      case 'vista': if (E.vista !== v) { const prim = (E.folha - 1) * porFolha(); E.vista = v; E.folha = Math.floor(prim / porFolha()) + 1; E.zerarLista = true; persistir(); desenhar(); } break;
      case 'resp-escolher': E.filtroResp = v || ''; E.menu = null; E.folha = 1; desenhar(); break;
      case 'menu-mais': E.menu = E.menu === 'mais' ? null : 'mais'; desenhar(); break;
      case 'sobre': E.modal = 'sobre'; E.modalDados = null; desenhar(); break;
      // abas: Em aberto (em desenvolvimento) ou uma situação por vez
      case 'sit-aba': E.folha = 1;
        E.sitAtivas = new Set(v === 'abertas' ? ABERTAS : [v]);
        mudou(); break;
      case 'limpar': E.folha = 1; E.busca = ''; E.filtroResp = ''; E.filtroLocal = ''; desenhar(); break;
      case 'folha': E.folha = Number(v); E.zerarLista = true; desenhar(); break;
      case 'tk-alterar': E.editTk = true; E.erros = {}; desenhar(); { const el = document.getElementById('t-principal'); if (el) { el.focus(); el.select(); } } break;
      case 'tk-cancelar': E.editTk = false; E.erros = {}; E.limparRascunho = true; desenhar(); break;
      case 'abrir': E.editTk = false; E.aberta = id; E.aba = 'dados'; E.erros = {}; E.sujo = false; E.statusRascunho = null; desenhar(); break;
      case 'salvar-status': if (d && E.statusRascunho) salvarStatus(d); break;
      case 'fechar-det': guardar(() => { E.aberta = null; E.erros = {}; desenhar(); }); break;
      case 'aba': if (v === E.aba) break; guardar(() => { E.aba = v; E.erros = {}; E.editTk = false; desenhar(); }, true); break;
      // API: POST /api/mudancas/{id}/devolver-tecnico
      case 'devolver-tec': { const x = demanda(id) || d; if (!x || !x.tecnico) break; const t = usr(x.tecnico);
        if (!t || t.ativo === false) { aviso('O técnico não está mais ativo na Equipe. Atribua pelo campo Responsável.', true); desenhar(); break; }
        x.responsavel = t.id; registrar(x, 'Demanda para validação devolvida a ' + t.nome + ' para atendimento extra.'); regResp(x, 'admin', t.id, 'atendimento extra'); avisar(x, 'retornou', t.id);
        if (!(x.passou || []).includes(t.id)) (x.passou = x.passou || []).push(t.id);
        E.menu = null; aviso('Demanda devolvida a ' + t.curto + ', ainda para validação.'); mudou(); break; }
      // API: POST /api/mudancas/{id}/devolver-gestor
      case 'devolver-gestor': { const x = demanda(id) || d; if (!x) break; const t = x.responsavel;
        x.responsavel = 'admin'; registrar(x, 'Atendimento extra concluído por ' + nomeUsr(t) + '; demanda devolvida ao gestor.', t); regResp(x, t, 'admin', 'carga do gestor', t); avisar(x, 'pendente', 'admin');
        aviso('Demanda devolvida ao gestor.'); mudou(); break; }
      // API: DELETE /api/mudancas/{id} { motivo } (vai para a lixeira; o servidor guarda o registro da exclusão)
      case 'excluir': { const x = demanda(id) || d; if (!x) break; E.menu = null;
        E.modal = 'confirmar'; E.erros = {};
        E.modalDados = { titulo: 'Excluir a Demanda ' + (x.sei || num4(x.id)) + '?', texto: 'Ela vai para a Lixeira e pode ser restaurada em até ' + DIAS_LIXEIRA + ' dias. Depois disso, é removida sem retorno.', motivo: true, botao: 'Excluir demanda', perigo: true,
          acao: (motivo) => {
            registrar(x, 'Demanda excluída. Motivo: ' + motivo + '.');
            E.excluidas.push({ data: agoraISO(), usuario: E.usuario, id: x.id, sei: x.sei, comarca: x.comarca, situacao: x.situacao, motivo });
            E.lixeira.push(Object.assign(x, { excluidaEm: agoraISO(), excluidaPor: E.usuario, motivoExclusao: motivo }));
            E.demandas = E.demandas.filter((y) => y.id !== x.id); E.aberta = null; E.statusRascunho = null; E.sujo = false; aviso('Demanda enviada para a Lixeira.'); mudou();
          } };
        desenhar(); document.getElementById('mc-motivo').focus(); break; }
      case 'alterar-conclusao': { const x = demanda(id) || d; if (!x || x.situacao !== 'atendimento') break; E.menu = null; E.modal = 'conclusao'; E.modalDados = { id: x.id }; E.erros = {}; desenhar(); document.getElementById('pr-fim').focus(); break; }
      case 'lixeira': E.menu = null; E.modal = 'lixeira'; E.modalDados = null; desenhar(); break;
      // API: POST /api/lixeira/{id}/restaurar
      case 'restaurar': { const i = E.lixeira.findIndex((x) => x.id === id); if (i < 0) break;
        const x = E.lixeira.splice(i, 1)[0]; delete x.excluidaEm; delete x.excluidaPor; delete x.motivoExclusao;
        registrar(x, 'Demanda restaurada da lixeira.');
        if (x.responsavel) avisar(x, 'retornou', x.responsavel);
        E.demandas.push(x); aviso('Demanda restaurada.'); mudou(); break; }
      // API: GET /api/movimentacoes?dia=AAAA-MM-DD
      case 'movimentos': E.menu = null; E.modal = 'movimentos'; E.modalDados = { dia: hojeISO(), so: 'todas' }; desenhar(); break;
      case 'mov-dia': { const m = E.modalDados || {}; const x = new Date((m.dia || hojeISO()) + 'T12:00'); x.setDate(x.getDate() + Number(v)); const nd = x.getFullYear() + '-' + pad(x.getMonth() + 1) + '-' + pad(x.getDate()); if (nd <= hojeISO()) { m.dia = nd; desenhar(); } break; }
      case 'mov-filtro': if (E.modalDados) { E.modalDados.so = v; desenhar(); } break;
      case 'mov-abrir': if (demanda(id)) { E.modal = null; E.modalDados = null; E.aberta = id; E.aba = 'hist'; E.erros = {}; desenhar(); } break;
      case 'concluir-dem': { const x = demanda(id) || d; if (x) pedirConclusao(x); break; }
      case 'cancelar':
        if (!d) break; E.menu = null;
        E.modal = 'confirmar'; E.erros = {};
        E.modalDados = { titulo: 'Cancelar a Demanda ' + num4(d.id) + '?', texto: 'A ação não poderá ser desfeita.', motivo: true, botao: 'Cancelar demanda', perigo: true,
          acao: (motivo) => { setSituacao(d, 'cancelada', 'Status alterado: ' + sit(d.situacao).um + ' → Cancelada. Motivo: ' + motivo + '.'); d.motivoCancelamento = motivo; if (d.responsavel) avisar(d, 'status', d.responsavel); aviso('Demanda cancelada.'); mudou(); } };
        desenhar(); document.getElementById('mc-motivo').focus(); break;
      case 'confirmar': {
        const c = E.modalDados || {}; const motivo = c.motivo ? val('mc-motivo') : '';
        if (c.motivo && !motivo) { E.erros.motivo = 'Informe o motivo.'; desenhar(); document.getElementById('mc-motivo').focus(); break; }
        const fn = c.acao; E.modal = null; E.modalDados = null; E.erros = {}; if (fn) fn(motivo); else desenhar(); break;
      }
      case 'fechar-modal': if (E.modal === 'equipe') E.toast = null; E.modal = null; E.modalDados = null; E.erros = {}; desenhar(); break;
      case 'copiar': copiar(v, 'Copiado: ' + v); break;
      case 'relatorio': if (!d) break; E.menu = null; E.modal = 'relatorio'; E.modalDados = { id: d.id }; E.limparRascunho = true; desenhar(); break;
      case 'baixar-relatorio': baixarRelatorio(); break;
      case 'acionamento': if (!d) break; E.menu = null; E.modal = 'acionamento'; E.modalDados = { id: d.id }; E.limparRascunho = true; desenhar(); break;
      case 'copiar-acionamento': { const t = document.getElementById('ac-texto'); const x = demanda(E.modalDados && E.modalDados.id); if (!t) break; copiar(t.value, 'Texto copiado. É só colar no SEI.'); if (x) { registrar(x, 'Informação de acionamento gerada e copiada.'); persistir(); } break; }
      case 'copiar-tickets': if (d) copiar(textoTickets(d), 'Tickets copiados em texto.'); break;
      // API: DELETE /api/mudancas/{id}/subtickets/{numero}
      case 'sub-del': if (!d) break; { const s = d.subtickets.splice(Number(alvo.dataset.i), 1)[0]; registrar(d, 'Subticket ' + s.empresa + ' ' + s.numero + ' removido.'); E.manterRolagem = true; aviso('Subticket removido.'); mudou(); } break;
      case 'sem-sei': { const el = document.getElementById('n-sei'); if (el) { el.disabled = alvo.checked; if (alvo.checked) { el.value = ''; } } } break;
    }
  });

  window.addEventListener('resize', () => mostrarAbaAtiva());
  // abas de situação: setas, Home e End trocam de aba (padrão de tablist)
  document.addEventListener('keydown', (ev) => {
    const tab = ev.target.closest && ev.target.closest('.sit-aba');
    if (!tab || !['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(ev.key)) return;
    const ls = [...document.querySelectorAll('.sit-aba')]; const i = ls.indexOf(tab);
    const j = ev.key === 'Home' ? 0 : ev.key === 'End' ? ls.length - 1 : (i + (ev.key === 'ArrowRight' ? 1 : -1) + ls.length) % ls.length;
    ev.preventDefault(); ev.stopImmediatePropagation(); ls[j].click();
    const nova = document.querySelector('.sit-aba[aria-selected="true"]'); if (nova) nova.focus();
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && CAL) { const id = CAL.id; fecharCal(); const i = document.getElementById(id); if (i) i.focus(); return; }
    // Esc recolhe menus e calendário; os modais fecham só pelo X
    if (ev.key === 'Escape') { if (E.menu) { E.menu = null; desenhar(); } return; }
    if (ev.key === 'Enter' && ev.target.id === 'f-local-q') { ev.preventDefault(); const b = document.querySelector('.pop-local .op-local:not([hidden])'); if (b) b.click(); return; }
    if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.classList && (ev.target.classList.contains('linha-dem') || ev.target.classList.contains('postit'))) {
      ev.preventDefault(); E.aberta = Number(ev.target.dataset.id); E.aba = 'dados'; desenhar();
    }
  });

  let tBusca;
  document.addEventListener('input', (ev) => {
    const t = ev.target;
    if (t.id === 'f-local-q') { E.localQ = t.value; filtrarLocais(); return; }
    if (t.dataset.campo === 'busca') { E.busca = t.value; E.folha = 1; clearTimeout(tBusca); tBusca = setTimeout(desenhar, 120); return; }
    if (t.dataset.combo !== undefined) { comboAbrir(t); if (t.closest('#form-dados')) marcarSujo(); return; }
    if (t.dataset.mask === 'hora') {
      if (t.closest('#form-dados')) marcarSujo();
      const g = t.value.replace(/\D/g, '').slice(0, 4);
      const f = g.length > 2 ? g.slice(0, 2) + ':' + g.slice(2) : g;
      if (f !== t.value) { t.value = f; t.setSelectionRange(f.length, f.length); }
      return;
    }
    if (t.dataset.mask === 'data') {
      if (t.closest('#form-dados')) marcarSujo();
      const g = t.value.replace(/\D/g, '').slice(0, 8);
      const f = g.length > 4 ? g.slice(0, 2) + '/' + g.slice(2, 4) + '/' + g.slice(4) : g.length > 2 ? g.slice(0, 2) + '/' + g.slice(2) : g;
      if (f !== t.value) { t.value = f; t.setSelectionRange(f.length, f.length); }
      if (CAL && CAL.id === t.id) { const iso = textoISO(f); if (iso) { CAL.ano = +iso.slice(0, 4); CAL.mes = +iso.slice(5, 7) - 1; } desenharCal(); }
      return;
    }
    if (t.dataset.mask === 'sei') {
      if (t.closest('#form-dados')) marcarSujo();
      const f = fmtSei(t.value); if (f !== t.value) { t.value = f; t.setSelectionRange(f.length, f.length); }
      return;
    }
    if (t.closest && t.closest('#form-dados')) marcarSujo();
    if (t.dataset.cont) { const c = document.getElementById(t.id + '-cont'); if (c) c.textContent = t.value.length + '/' + t.dataset.cont; }
  });
  document.addEventListener('change', (ev) => {
    const t = ev.target;
    if (t.dataset.campo && t.dataset.campo !== 'busca') { E[t.dataset.campo] = t.value; E.folha = 1; desenhar(); return; }
    if (t.id === 'tr-dest' && E.erros.transf) { E.erros.transf = ''; const er = document.querySelector('.equipe .erro'); if (er) er.remove(); t.removeAttribute('aria-invalid'); }
    if (t.name === 'tr-d') { const all = [...document.querySelectorAll('input[name="tr-d"]')]; const l = document.querySelector('[data-acao=tr-todas]'); if (l) l.textContent = all.every((c) => c.checked) ? 'Desmarcar todas' : 'Marcar todas'; atualizaTransf(); return; }
    if (t.id === 'n-emp') { E.ultimaEmp = t.value; trocarFinalidade(); return; }
    if (t.dataset.campoSub && precisaDestravar(demanda(E.aberta))) return;
    if ((t.dataset.status || t.dataset.campoSub) && !podeEditar(demanda(E.aberta))) { const d = demanda(E.aberta); if (t.dataset.status && d) t.value = d.situacao; precisaEditar(d); return; }
    if (t.dataset.status) { const d = demanda(Number(t.dataset.status)); if (d) escolherStatus(d, t.value); return; }
    if (t.closest && t.closest('#form-dados')) marcarSujo();
    if (t.dataset.campoSub) {
      const d = demanda(E.aberta); if (!d) return; const sub = d.subtickets[Number(t.dataset.i)];
      // API: PATCH /api/mudancas/{id}/subtickets/{numero} { servico | quantidade }
      if (t.dataset.campoSub === 'quantidade') {
        const q = parseInt(t.value, 10); if (!(q >= 1 && q <= 999)) { t.value = sub.quantidade || ''; return; }
        if (q !== sub.quantidade) { sub.quantidade = q; registrar(d, 'Subticket ' + sub.empresa + ' ' + sub.numero + ': quantidade ' + q + '.'); E.manterRolagem = true; mudou(); }
        return;
      }
      sub.finalidade = t.value.trim(); persistir();
      if (t.tagName === 'SELECT') { registrar(d, 'Subticket ' + sub.empresa + ' ' + sub.numero + ': serviço ' + (sub.finalidade || 'não informado') + '.'); E.manterRolagem = true; mudou(); }
      return;
    }
  });

  // ao trocar a empresa, o select de serviço mostra só os serviços dela
  function trocarFinalidade() {
    const emp = document.getElementById('n-emp'); const fin = document.getElementById('n-fin'); if (!emp || !fin) return;
    if (fin.dataset.emp === emp.value) return;
    const atual = fin.value; fin.innerHTML = opcoesServ(emp.value, atual); fin.dataset.emp = emp.value;
  }
  // botão de transferir mostra quantas demandas vão
  // a descrição do post-it mostra só as linhas inteiras que cabem, com reticências na última
  function ajustaPostits() {
    document.querySelectorAll('.pi-desc').forEach((p) => {
      p.style.webkitLineClamp = 'unset'; p.style.maxHeight = ''; p.style.flex = '';
      const lh = parseFloat(getComputedStyle(p).lineHeight) || 19; const n = Math.max(1, Math.floor((p.clientHeight + 1) / lh));
      p.style.webkitLineClamp = String(n); p.style.maxHeight = (n * lh) + 'px'; p.style.flex = '0 1 auto';
    });
  }
  // ao rolar, o calendário acompanha o campo; se o campo sair da tela, fecha
  window.addEventListener('scroll', () => {
    if (!CAL) return; const i = document.getElementById(CAL.id); if (!i) { fecharCal(); return; }
    const r = i.getBoundingClientRect(); if (r.bottom < 0 || r.top > window.innerHeight) fecharCal(); else desenharCal();
  }, true);
  let tAjuste; window.addEventListener('resize', () => { if (CAL) fecharCal(); clearTimeout(tAjuste); tAjuste = setTimeout(ajustaPostits, 80); });
  function atualizaTransf() {
    const b = document.getElementById('tr-ok'); if (!b || !E.modalDados || !E.modalDados.transf) return;
    const n = document.querySelectorAll('input[name="tr-d"]:checked').length; const des = E.modalDados.transf.desativar;
    b.textContent = n ? 'Transferir ' + n + (n === 1 ? ' demanda' : ' demandas') + (des ? ' e desativar' : '') : (des ? 'Desativar sem transferir' : 'Transferir');
  }
  // lista de locais
  let CB = { inp: null, itens: [], ativo: -1 };
  function marcarTrecho(txt, q) {
    if (!q) return esc(txt);
    const i = normal(txt).indexOf(q); if (i < 0) return esc(txt);
    return esc(txt.slice(0, i)) + '<mark>' + esc(txt.slice(i, i + q.length)) + '</mark>' + esc(txt.slice(i + q.length));
  }
  function comboAbrir(inp, tudo) {
    const lista = document.getElementById(inp.id + '-lista'); if (!lista) return;
    const q = tudo ? '' : normal(inp.value.trim());
    let html = ''; const itens = [];
    // a lista mostra só o nome do local (Agudo, Alegrete…), mais fácil de localizar
    const todos = LOCAIS.poa.concat(LOCAIS.interior).sort((a, b) => normal(a).localeCompare(normal(b), 'pt-BR'));
    (q ? todos.filter((l) => normal(l).includes(q)) : todos).forEach((l) => { const i = itens.length; itens.push(l); html += `<li class="combo-op ${l === inp.value ? 'escolhido' : ''}" role="option" id="${inp.id}-op-${i}" data-i="${i}">${marcarTrecho(l, q)}</li>`; });
    if (!itens.length) html = `<li class="combo-vazio">Nenhum local encontrado. O texto digitado será usado.</li>`;
    lista.innerHTML = html; lista.hidden = false; inp.setAttribute('aria-expanded', 'true');
    CB = { inp, itens, ativo: q && itens.length ? 0 : itens.indexOf(inp.value) };
    comboAtivo();
  }
  function comboAtivo() {
    if (!CB.inp) return;
    const lista = document.getElementById(CB.inp.id + '-lista'); if (!lista) return;
    lista.querySelectorAll('.combo-op').forEach((li) => li.classList.toggle('ativo', Number(li.dataset.i) === CB.ativo));
    const at = document.getElementById(CB.inp.id + '-op-' + CB.ativo);
    if (at) { CB.inp.setAttribute('aria-activedescendant', at.id); at.scrollIntoView({ block: 'nearest' }); } else CB.inp.removeAttribute('aria-activedescendant');
  }
  function comboFechar() {
    if (!CB.inp) return;
    const lista = document.getElementById(CB.inp.id + '-lista'); if (lista) lista.hidden = true;
    CB.inp.setAttribute('aria-expanded', 'false'); CB.inp.removeAttribute('aria-activedescendant');
    CB = { inp: null, itens: [], ativo: -1 };
  }
  function comboEscolher(i) {
    const inp = CB.inp; if (!inp || CB.itens[i] == null) return;
    inp.value = CB.itens[i]; inp.removeAttribute('aria-invalid');
    if (inp.closest('#form-dados')) marcarSujo();
    comboFechar();
  }
  document.addEventListener('focusin', (ev) => { const t = ev.target; if (t.dataset && t.dataset.combo !== undefined) comboAbrir(t, LOCAIS.poa.concat(LOCAIS.interior).includes(t.value)); });
  document.addEventListener('focusout', (ev) => { if (ev.target.dataset && ev.target.dataset.combo !== undefined) setTimeout(() => { if (CB.inp === ev.target && document.activeElement !== ev.target) comboFechar(); }, 100); });
  // mantém o foco no campo ao clicar na lista: sem isso, apertar a barra de rolagem fechava a lista
  document.addEventListener('mousedown', (ev) => {
    if (!ev.target.closest('.combo-lista')) return; ev.preventDefault();
    const op = ev.target.closest('.combo-op'); if (op) comboEscolher(Number(op.dataset.i));
  });
  document.addEventListener('keydown', (ev) => {
    const t = ev.target; if (!t.dataset || t.dataset.combo === undefined) return;
    const aberta = CB.inp === t;
    if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
      ev.preventDefault(); if (!aberta) { comboAbrir(t, true); return; }
      const n = CB.itens.length; if (!n) return;
      CB.ativo = ev.key === 'ArrowDown' ? (CB.ativo + 1) % n : (CB.ativo <= 0 ? n - 1 : CB.ativo - 1); comboAtivo();
    } else if (ev.key === 'Enter' && aberta && CB.ativo >= 0) { ev.preventDefault(); comboEscolher(CB.ativo); }
    else if (ev.key === 'Escape' && aberta) { ev.preventDefault(); ev.stopImmediatePropagation(); comboFechar(); }
    else if (ev.key === 'Tab' && aberta && CB.ativo >= 0 && normal(t.value).length) { comboEscolher(CB.ativo); }
  }, true);


  // dados salvos no navegador passam por uma checagem mínima de formato antes de entrar na tela
  E.demandas = E.demandas.filter((d) => d && Number.isFinite(d.id) && sit(d.situacao) && Array.isArray(d.subtickets) && Array.isArray(d.historico));
  E.equipe = E.equipe.filter((u) => u && typeof u.id === 'string' && typeof u.nome === 'string');
  E.lixeira = E.lixeira.filter((d) => d && Number.isFinite(d.id) && sit(d.situacao) && Array.isArray(d.subtickets) && Array.isArray(d.historico) && d.excluidaEm);
  if (automatizar()) persistir();
  // a data muda com o sistema aberto: confere de hora em hora
  setInterval(() => { if (automatizar()) mudou(); }, 3600000);

  // caixas de texto crescem até mostrar todo o conteúdo (descrição até 250 caracteres sem rolagem)
  function alturaDetalhe() {
    const m = document.querySelector('.modal-content.det'); if (!m) return;
    // altura exata, com fração: offsetHeight arredonda e o cabeçalho, centralizado, pulava ao trocar de aba
    if (E.aba === 'dados') { m.style.height = ''; E.detAlt = m.getBoundingClientRect().height; E.detAltDe = E.aberta; return; }
    // entrou direto em Tickets ou Histórico: mede a aba Detalhes antes de exibir, para o modal não mudar de tamanho depois
    if (E.detAltDe !== E.aberta) {
      const corpo = m.querySelector('.det-corpo'); const filhos = [...corpo.childNodes];
      corpo.innerHTML = abaDados(demanda(E.aberta)); ajustaTextos(); m.style.height = '';
      E.detAlt = m.getBoundingClientRect().height; E.detAltDe = E.aberta;
      corpo.replaceChildren(...filhos);
    }
    m.style.height = E.detAlt + 'px';
  }
  function ajustaTextos() {
    document.querySelectorAll('textarea.txt').forEach((t) => { t.style.height = 'auto'; t.style.height = (t.scrollHeight + 2) + 'px'; });
  }
  document.addEventListener('input', (ev) => { if (ev.target.matches && ev.target.matches('textarea.txt')) { ev.target.style.height = 'auto'; ev.target.style.height = (ev.target.scrollHeight + 2) + 'px'; } });

  desenhar();
})();
