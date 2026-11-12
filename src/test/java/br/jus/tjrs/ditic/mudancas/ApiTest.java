package br.jus.tjrs.ditic.mudancas;

import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

import java.time.LocalDate;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;

/** Regras, permissões e custo pela API, com o banco H2 carregado com os catálogos do script. */
@SpringBootTest
@AutoConfigureMockMvc
class ApiTest {

    private static final String SENHA_ADMIN = "senha-do-admin";
    private static final AtomicInteger SEQ = new AtomicInteger();

    @Autowired
    MockMvc mvc;

    MockHttpSession admin;

    @BeforeEach
    void entrarComoAdmin() throws Exception {
        MvcResult r = mvc.perform(json(post("/api/login"), "{\"usuario\":\"admin\",\"senha\":\"" + SENHA_ADMIN + "\"}")).andReturn();
        if (r.getResponse().getStatus() != 200) {
            r = mvc.perform(json(post("/api/login"), "{\"usuario\":\"admin\",\"senha\":\"admin-inicial\"}")).andReturn();
            assertThat(r.getResponse().getStatus()).isEqualTo(200);
            assertThat((Boolean) JsonPath.read(r.getResponse().getContentAsString(), "$.deveTrocarSenha")).isTrue();
            MockHttpSession s = (MockHttpSession) r.getRequest().getSession();
            assertThat(status(get("/api/mudancas"), s)).as("antes de criar a senha, só a troca de senha").isEqualTo(403);
            assertThat(status(json(post("/api/conta/senha"), "{\"atual\":\"admin-inicial\",\"nova\":\"" + SENHA_ADMIN + "\"}"), s)).isEqualTo(200);
            r = mvc.perform(json(post("/api/login"), "{\"usuario\":\"admin\",\"senha\":\"" + SENHA_ADMIN + "\"}")).andReturn();
        }
        admin = (MockHttpSession) r.getRequest().getSession();
    }

    @Test
    void semLoginNadaAbre() throws Exception {
        assertThat(mvc.perform(get("/api/mudancas")).andReturn().getResponse().getStatus()).isEqualTo(401);
        assertThat(mvc.perform(get("/api/catalogos")).andReturn().getResponse().getStatus()).isEqualTo(401);
        assertThat(mvc.perform(get("/index.html")).andReturn().getResponse().getStatus()).isEqualTo(200);
    }

    @Test
    void contaInicialSeChamaCoordenador() throws Exception {
        String s = body(get("/api/sessao"), admin);
        assertThat((String) JsonPath.read(s, "$.nome")).isEqualTo("Coordenador");
        assertThat((String) JsonPath.read(s, "$.perfil")).isEqualTo("COORDENADOR");
    }

    @Test
    void alteracaoSemTokenCsrfERecusada() throws Exception {
        int st = mvc.perform(post("/api/mudancas").session(admin).contentType(MediaType.APPLICATION_JSON).content("{}")).andReturn().getResponse().getStatus();
        assertThat(st).isEqualTo(403);
    }

    @Test
    void catalogosEPrecosVemDoBanco() throws Exception {
        String cat = body(get("/api/catalogos"), admin);
        assertThat((List<?>) JsonPath.read(cat, "$.locais")).hasSize(177);
        assertThat((List<String>) JsonPath.read(cat, "$.empresas[*].nome")).containsExactly("CADI", "CDS", "Selbetti", "WECOM");
        assertThat((List<String>) JsonPath.read(cat, "$.empresas[?(@.nome=='WECOM')].servicos[*]")).containsExactly("Instalação", "Realocação", "Infraestrutura");
        String pr = body(get("/api/precos"), admin);
        assertThat((List<String>) JsonPath.read(pr, "$.regioes")).containsExactly("Noroeste", "Nordeste", "Centro Ocidental", "Centro Oriental", "Metropolitana", "Sudeste", "Sudoeste");
        assertThat(((Number) JsonPath.read(pr, "$.wecom.metro")).doubleValue()).isEqualTo(164.18);
    }

    @Test
    void fluxoCompletoDoTecnico() throws Exception {
        MockHttpSession tec = novoTecnico();
        String id = criar(tec, LocalDate.now().toString(), "Canoas");
        // acionar exige o ticket principal
        assertThat(status(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"acionada\"}"), tec)).isEqualTo(409);
        assertThat(status(json(put("/api/mudancas/" + id + "/ticket"), "{\"numero\":\"1234567\"}"), tec)).isEqualTo(400);
        assertThat(status(json(put("/api/mudancas/" + id + "/ticket"), "{\"numero\":\"" + ticket() + "\"}"), tec)).isEqualTo(200);
        // agendada para hoje: acionar leva direto para Em atendimento, com o mesmo responsável
        String r = body(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"acionada\"}"), tec);
        assertThat((String) JsonPath.read(r, "$.demanda.situacao")).isEqualTo("atendimento");
        assertThat((String) JsonPath.read(r, "$.demanda.acionadaEm")).isEqualTo(LocalDate.now().toString());
        assertThat((List<String>) JsonPath.read(r, "$.demanda.historico[*].texto")).anyMatch(t -> t.startsWith("Status alterado automaticamente: Acionada → Em atendimento"));
        // o técnico não cancela nem exclui
        assertThat(status(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"cancelada\",\"motivo\":\"x\"}"), tec)).isEqualTo(403);
        assertThat(status(json(delete("/api/mudancas/" + id), "{\"motivo\":\"x\"}"), tec)).isEqualTo(403);
        assertThat(status(json(put("/api/precos"), "{}"), tec)).isEqualTo(403);
        assertThat(status(get("/api/lixeira"), tec)).isEqualTo(403);
        // o coordenador cancela, com motivo, e a demanda fica somente leitura
        assertThat(status(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"cancelada\"}"), admin)).isEqualTo(400);
        assertThat(status(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"cancelada\",\"motivo\":\"Pedido retirado\"}"), admin)).isEqualTo(200);
        assertThat(status(json(put("/api/mudancas/" + id + "/ticket"), "{\"numero\":\"" + ticket() + "\"}"), tec)).isEqualTo(409);
        assertThat(status(json(post("/api/mudancas/" + id + "/historico"), "{\"texto\":\"Anotação depois de encerrada\"}"), tec)).isEqualTo(200);
    }

    @Test
    void demandaAntigaComTicketsVaiParaValidacaoEConclui() throws Exception {
        MockHttpSession tec = novoTecnico();
        String id = criar(tec, LocalDate.now().minusDays(10).toString(), "Pelotas");
        body(json(put("/api/mudancas/" + id + "/ticket"), "{\"numero\":\"" + ticket() + "\"}"), tec);
        String r = body(json(post("/api/mudancas/" + id + "/subtickets"), "{\"empresa\":\"CDS\",\"numeros\":\"" + ticket() + "\",\"servico\":\"Mudança de Local\",\"quantidade\":2}"), tec);
        assertThat((String) JsonPath.read(r, "$.demanda.situacao")).isEqualTo("pendente");
        assertThat((String) JsonPath.read(r, "$.demanda.acionadaEm")).isEqualTo(LocalDate.now().minusDays(10).toString());
        // Para Validação: a Data para Conclusão continua antes de hoje
        assertThat(status(json(put("/api/mudancas/" + id), dados(LocalDate.now().toString(), "Pelotas")), tec)).isEqualTo(400);
        r = body(json(patch("/api/mudancas/" + id + "/situacao"), "{\"situacao\":\"concluida\"}"), tec);
        assertThat((String) JsonPath.read(r, "$.demanda.situacao")).isEqualTo("concluida");
        assertThat((Object) JsonPath.read(r, "$.demanda.responsavel")).isNull();
        // concluída não pode ser excluída
        assertThat(status(json(delete("/api/mudancas/" + id), "{\"motivo\":\"teste\"}"), admin)).isEqualTo(409);
    }

    @Test
    void custoDoRelatorio() throws Exception {
        MockHttpSession tec = novoTecnico();
        String id = criar(tec, LocalDate.now().plusDays(5).toString(), "Canoas");
        String infraSemMetro = ticket();
        // CDS em Canoas (Metropolitana): 2 × R$ 160,00
        body(json(post("/api/mudancas/" + id + "/subtickets"), "{\"empresa\":\"CDS\",\"numeros\":\"" + ticket() + "\",\"servico\":\"Mudança de Local\",\"quantidade\":2}"), tec);
        // Infraestrutura sem metro linear: uma verba de 15 m (R$ 2.462,70), qualquer que seja a quantidade
        body(json(post("/api/mudancas/" + id + "/subtickets"), "{\"empresa\":\"WECOM\",\"numeros\":\"" + infraSemMetro + "\",\"servico\":\"Infraestrutura\",\"quantidade\":3}"), tec);
        // Infraestrutura com metro linear: 2 × R$ 164,18, mesmo com quantidade 1
        body(json(post("/api/mudancas/" + id + "/subtickets"), "{\"empresa\":\"WECOM\",\"numeros\":\"" + ticket() + "\",\"servico\":\"Infraestrutura\",\"quantidade\":1,\"metro\":2}"), tec);
        // Realocação: 1 × R$ 4.121,86
        body(json(post("/api/mudancas/" + id + "/subtickets"), "{\"empresa\":\"WECOM\",\"numeros\":\"" + ticket() + "\",\"servico\":\"Realocação\",\"quantidade\":1}"), tec);
        String c = body(get("/api/mudancas/" + id + "/custo"), tec);
        assertThat(((Number) JsonPath.read(c, "$.infra")).longValue()).isEqualTo(246270 + 32836);
        assertThat(((Number) JsonPath.read(c, "$.total")).longValue()).isEqualTo(32000 + 246270 + 32836 + 412186);
        assertThat((List<String>) JsonPath.read(c, "$.verbas[*].numero")).containsExactly(infraSemMetro);
        // o coordenador muda um valor e o custo acompanha
        String pr = body(get("/api/precos"), admin).replace("164.18", "200.00");
        assertThat(status(json(put("/api/precos"), pr), admin)).isEqualTo(200);
        c = body(get("/api/mudancas/" + id + "/custo"), tec);
        assertThat(((Number) JsonPath.read(c, "$.infra")).longValue()).isEqualTo(300000 + 40000);
        body(json(put("/api/precos"), pr.replace("200.0", "164.18").replace("200.00", "164.18")), admin);
    }

    @Test
    void subticketEUnicoEntreDemandas() throws Exception {
        MockHttpSession tec = novoTecnico();
        String a = criar(tec, LocalDate.now().plusDays(4).toString(), "Canoas");
        String b = criar(tec, LocalDate.now().plusDays(4).toString(), "Canoas");
        String n = ticket();
        body(json(post("/api/mudancas/" + a + "/subtickets"), "{\"empresa\":\"CDS\",\"numeros\":\"" + n + "\",\"servico\":\"Instalação\",\"quantidade\":1}"), tec);
        // repetido em outra demanda: recusa e não inclui nenhum dos números enviados juntos
        MvcResult r = mvc.perform(json(post("/api/mudancas/" + b + "/subtickets"), "{\"empresa\":\"CDS\",\"numeros\":\"" + ticket() + " / " + n + "\",\"servico\":\"Instalação\",\"quantidade\":1}").session(tec)).andReturn();
        assertThat(r.getResponse().getStatus()).isEqualTo(409);
        assertThat(r.getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8)).contains(n);
        assertThat((List<?>) JsonPath.read(body(get("/api/mudancas/" + b), tec), "$.subtickets")).isEmpty();
        // 8 dígitos
        assertThat(status(json(post("/api/mudancas/" + b + "/subtickets"), "{\"empresa\":\"CDS\",\"numeros\":\"123456\",\"servico\":\"Instalação\",\"quantidade\":1}"), tec)).isEqualTo(400);
    }

    @Test
    void localPrecisaSerDaLista() throws Exception {
        MockHttpSession tec = novoTecnico();
        int st = status(json(post("/api/mudancas"), "{\"sei\":\"\",\"comarca\":\"Foro Centl\",\"descricao\":\"Teste\",\"responsavel\":\"\"}"), tec);
        assertThat(st).isEqualTo(400);
        // "Foro da Comarca de Canoas" é o mesmo local do catálogo
        String r = body(json(post("/api/mudancas"), "{\"sei\":\"\",\"comarca\":\"Foro da Comarca de Canoas\",\"descricao\":\"Teste\",\"responsavel\":\"\"}"), tec);
        assertThat((String) JsonPath.read(r, "$.demanda.comarca")).isEqualTo("Canoas");
    }

    @Test
    void lixeiraERestauracao() throws Exception {
        MockHttpSession tec = novoTecnico();
        String id = criar(tec, LocalDate.now().plusDays(3).toString(), "Torres");
        assertThat(status(json(delete("/api/mudancas/" + id), "{\"motivo\":\"\"}"), admin)).isEqualTo(400);
        assertThat(status(json(delete("/api/mudancas/" + id), "{\"motivo\":\"Duplicada\"}"), admin)).isEqualTo(204);
        assertThat(status(get("/api/mudancas/" + id), tec)).isEqualTo(404);
        assertThat((List<Integer>) JsonPath.read(body(get("/api/lixeira"), admin), "$[*].id")).contains(Integer.valueOf(id));
        String r = body(post("/api/lixeira/" + id + "/restaurar").with(csrf()), admin);
        assertThat((String) JsonPath.read(r, "$.situacao")).isEqualTo("nova");
        assertThat(status(get("/api/mudancas/" + id), tec)).isEqualTo(200);
    }

    @Test
    void desativarTecnicoComDemandasExigeTransferir() throws Exception {
        String login = "tec" + SEQ.incrementAndGet();
        String conta = body(json(post("/api/equipe"), "{\"nome\":\"Pessoa " + login + "\",\"login\":\"" + login + "\",\"perfil\":\"TECNICO\",\"cor\":\"#3E7C8A\"}"), admin);
        String pid = JsonPath.read(conta, "$.pessoa.id");
        MockHttpSession tec = entrarPrimeiraVez(login, JsonPath.read(conta, "$.senha"));
        String id = criar(tec, LocalDate.now().plusDays(3).toString(), "Canoas", pid);
        assertThat(status(post("/api/equipe/" + pid + "/desativar").with(csrf()), admin)).isEqualTo(409);
        String t = body(json(post("/api/equipe/" + pid + "/transferir"), "{\"para\":\"\",\"demandas\":[],\"desativar\":true}"), admin);
        assertThat((Integer) JsonPath.read(t, "$.paraCoordenador")).isEqualTo(1);
        assertThat((String) JsonPath.read(body(get("/api/mudancas/" + id), admin), "$.responsavel")).isEqualTo("coordenador");
        // desativado: a sessão dele cai
        assertThat(status(get("/api/mudancas"), tec)).isEqualTo(401);
    }

    @Test
    void redefinirSenhaDerrubaASessao() throws Exception {
        String login = "tec" + SEQ.incrementAndGet();
        String conta = body(json(post("/api/equipe"), "{\"nome\":\"Pessoa " + login + "\",\"login\":\"" + login + "\",\"perfil\":\"TECNICO\"}"), admin);
        MockHttpSession tec = entrarPrimeiraVez(login, JsonPath.read(conta, "$.senha"));
        assertThat(status(get("/api/mudancas"), tec)).isEqualTo(200);
        body(post("/api/equipe/" + JsonPath.read(conta, "$.pessoa.id") + "/redefinir-senha").with(csrf()), admin);
        assertThat(status(get("/api/mudancas"), tec)).isEqualTo(401);
    }

    @Test
    void bloqueiaDepoisDeCincoTentativasErradas() throws Exception {
        String login = "tec" + SEQ.incrementAndGet();
        String conta = body(json(post("/api/equipe"), "{\"nome\":\"Pessoa " + login + "\",\"login\":\"" + login + "\",\"perfil\":\"TECNICO\"}"), admin);
        for (int i = 0; i < 5; i++) {
            assertThat(mvc.perform(json(post("/api/login"), "{\"usuario\":\"" + login + "\",\"senha\":\"errada\"}")).andReturn().getResponse().getStatus()).isEqualTo(401);
        }
        MvcResult r = mvc.perform(json(post("/api/login"), "{\"usuario\":\"" + login + "\",\"senha\":\"" + JsonPath.read(conta, "$.senha") + "\"}")).andReturn();
        assertThat(r.getResponse().getStatus()).isEqualTo(429);
    }

    @Test
    void solicitacaoDeAcessoAprovadaCriaAConta() throws Exception {
        String login = "pedido" + SEQ.incrementAndGet();
        assertThat(mvc.perform(json(post("/api/acesso/solicitar"), "{\"nome\":\"Nome " + login + "\",\"login\":\"" + login + "\"}")).andReturn().getResponse().getStatus()).isEqualTo(204);
        String ls = body(get("/api/acesso/solicitacoes"), admin);
        Integer sid = ((List<Integer>) JsonPath.read(ls, "$[?(@.login=='" + login + "')].id")).get(0);
        String conta = body(json(post("/api/acesso/solicitacoes/" + sid + "/aprovar"), "{\"perfil\":\"TECNICO\",\"cor\":\"#8A6B3D\"}"), admin);
        assertThat((String) JsonPath.read(conta, "$.pessoa.login")).isEqualTo(login);
        assertThat(entrarPrimeiraVez(login, JsonPath.read(conta, "$.senha"))).isNotNull();
    }

    // ------------------------------------------------------------------ apoio

    private MockHttpSession novoTecnico() throws Exception {
        String login = "tec" + SEQ.incrementAndGet();
        String conta = body(json(post("/api/equipe"), "{\"nome\":\"Pessoa " + login + "\",\"login\":\"" + login + "\",\"perfil\":\"TECNICO\"}"), admin);
        return entrarPrimeiraVez(login, JsonPath.read(conta, "$.senha"));
    }

    private MockHttpSession entrarPrimeiraVez(String login, String temporaria) throws Exception {
        MvcResult r = mvc.perform(json(post("/api/login"), "{\"usuario\":\"" + login + "\",\"senha\":\"" + temporaria + "\"}")).andReturn();
        assertThat(r.getResponse().getStatus()).isEqualTo(200);
        MockHttpSession s = (MockHttpSession) r.getRequest().getSession();
        assertThat(status(json(post("/api/conta/senha"), "{\"atual\":\"" + temporaria + "\",\"nova\":\"senha-pessoal-1\"}"), s)).isEqualTo(200);
        return s;
    }

    private String criar(MockHttpSession s, String inicio, String local) throws Exception {
        return criar(s, inicio, local, "");
    }

    private String criar(MockHttpSession s, String inicio, String local, String responsavel) throws Exception {
        String r = body(json(post("/api/mudancas"), "{\"sei\":\"8.2026.9745/000001-1\",\"comarca\":\"" + local + "\",\"descricao\":\"Teste\",\"responsavel\":\"" + responsavel + "\",\"inicio\":\"" + inicio + "\"}"), s);
        return String.valueOf((Integer) JsonPath.read(r, "$.demanda.id"));
    }

    private static String dados(String inicio, String local) {
        return "{\"sei\":\"8.2026.9745/000001-1\",\"comarca\":\"" + local + "\",\"descricao\":\"Teste\",\"responsavel\":\"coordenador\",\"inicio\":\"" + inicio + "\"}";
    }

    private static String ticket() { return String.valueOf(50000000 + SEQ.incrementAndGet()); }

    private static MockHttpServletRequestBuilder json(MockHttpServletRequestBuilder b, String corpo) {
        return b.contentType(MediaType.APPLICATION_JSON).content(corpo).with(csrf());
    }

    private int status(MockHttpServletRequestBuilder b, MockHttpSession s) throws Exception {
        return mvc.perform(b.session(s)).andReturn().getResponse().getStatus();
    }

    private String body(MockHttpServletRequestBuilder b, MockHttpSession s) throws Exception {
        MvcResult r = mvc.perform(b.session(s)).andReturn();
        assertThat(r.getResponse().getStatus()).as(r.getResponse().getContentAsString()).isBetween(200, 299);
        return r.getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8);
    }
}
