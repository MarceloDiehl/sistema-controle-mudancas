package br.jus.tjrs.ditic.mudancas.controller;

import br.jus.tjrs.ditic.mudancas.dto.DemandaDtos;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.service.DemandaService;
import br.jus.tjrs.ditic.mudancas.service.PrecoService;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/** Demandas: técnico e coordenador. Excluir e a lixeira são só do coordenador (SecurityConfig). */
@RestController
@RequestMapping("/api")
public class DemandaController {

    private final DemandaService servico;
    private final PrecoService precos;

    public DemandaController(DemandaService servico, PrecoService precos) {
        this.servico = servico;
        this.precos = precos;
    }

    @GetMapping("/mudancas")
    public List<DemandaDtos.Demanda> listar() { return servico.listar(); }

    @GetMapping("/mudancas/{id}")
    public DemandaDtos.Demanda buscar(@PathVariable Long id) { return servico.buscar(id); }

    @PostMapping("/mudancas")
    @ResponseStatus(HttpStatus.CREATED)
    public DemandaDtos.Resposta criar(@RequestBody DemandaDtos.Nova req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.criar(req, u);
    }

    @PutMapping("/mudancas/{id}")
    public DemandaDtos.Resposta salvar(@PathVariable Long id, @RequestBody DemandaDtos.Dados req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.salvarDados(id, req, u);
    }

    @PatchMapping("/mudancas/{id}/situacao")
    public DemandaDtos.Resposta situacao(@PathVariable Long id, @RequestBody DemandaDtos.MudancaSituacao req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.mudarSituacao(id, req, u);
    }

    @PutMapping("/mudancas/{id}/ticket")
    public DemandaDtos.Resposta ticket(@PathVariable Long id, @RequestBody DemandaDtos.Ticket req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.registrarTicket(id, req, u);
    }

    @PostMapping("/mudancas/{id}/subtickets")
    public DemandaDtos.Resposta incluirSubtickets(@PathVariable Long id, @RequestBody DemandaDtos.NovosSubtickets req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.incluirSubtickets(id, req, u);
    }

    @PatchMapping("/mudancas/{id}/subtickets/{numero}")
    public DemandaDtos.Resposta alterarSubticket(@PathVariable Long id, @PathVariable String numero, @RequestBody DemandaDtos.CampoSubticket req,
                                                 @AuthenticationPrincipal UsuarioLogado u) {
        return servico.alterarSubticket(id, numero, req, u);
    }

    @DeleteMapping("/mudancas/{id}/subtickets/{numero}")
    public DemandaDtos.Resposta removerSubticket(@PathVariable Long id, @PathVariable String numero, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.removerSubticket(id, numero, u);
    }

    @PostMapping("/mudancas/{id}/historico")
    public DemandaDtos.Resposta nota(@PathVariable Long id, @RequestBody DemandaDtos.Texto req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.registrarNota(id, req, u);
    }

    @PostMapping("/mudancas/{id}/documento")
    public DemandaDtos.Resposta documento(@PathVariable Long id, @RequestBody DemandaDtos.Documento req, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.registrarDocumento(id, req, u);
    }

    @PostMapping("/mudancas/{id}/visto")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void visto(@PathVariable Long id) { servico.marcarVisto(id); }

    @GetMapping("/mudancas/{id}/custo")
    public DemandaDtos.Custo custo(@PathVariable Long id) { return precos.custo(id); }

    @DeleteMapping("/mudancas/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void excluir(@PathVariable Long id, @RequestBody DemandaDtos.Motivo req, @AuthenticationPrincipal UsuarioLogado u) {
        servico.excluir(id, req, u);
    }

    @GetMapping("/lixeira")
    public List<DemandaDtos.Demanda> lixeira() { return servico.lixeira(); }

    @PostMapping("/lixeira/{id}/restaurar")
    public DemandaDtos.Demanda restaurar(@PathVariable Long id, @AuthenticationPrincipal UsuarioLogado u) {
        return servico.restaurar(id, u);
    }
}
