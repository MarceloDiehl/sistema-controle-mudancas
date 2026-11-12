package br.jus.tjrs.ditic.mudancas.controller;

import br.jus.tjrs.ditic.mudancas.dto.EquipeDtos;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.service.AcessoService;
import br.jus.tjrs.ditic.mudancas.service.EquipeService;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/** /api/pessoas é aberta (consulta); /api/equipe e as solicitações, só para o coordenador (SecurityConfig). */
@RestController
@RequestMapping("/api")
public class EquipeController {

    private final EquipeService equipe;
    private final AcessoService acesso;

    public EquipeController(EquipeService equipe, AcessoService acesso) {
        this.equipe = equipe;
        this.acesso = acesso;
    }

    /** Nomes e cores de todos (aparecem nas demandas e no histórico). Sem login, sem o usuário e a situação do acesso. */
    @GetMapping("/pessoas")
    public List<EquipeDtos.Pessoa> pessoas(@AuthenticationPrincipal UsuarioLogado u) {
        List<EquipeDtos.Pessoa> ls = equipe.listar();
        if (u != null) return ls;
        return ls.stream().map(p -> new EquipeDtos.Pessoa(p.id(), null, p.nome(), p.curto(), p.ini(), p.cor(), p.perfil(), p.ativo(), null, null)).toList();
    }

    @PostMapping("/equipe")
    @ResponseStatus(HttpStatus.CREATED)
    public EquipeDtos.SenhaTemporaria criar(@RequestBody EquipeDtos.NovaPessoa req, @AuthenticationPrincipal UsuarioLogado u) {
        return equipe.criar(req, u);
    }

    @PutMapping("/equipe/{id}")
    public EquipeDtos.Pessoa editar(@PathVariable Long id, @RequestBody EquipeDtos.Edicao req) { return equipe.editar(id, req); }

    @PostMapping("/equipe/{id}/desativar")
    public EquipeDtos.Pessoa desativar(@PathVariable Long id, @AuthenticationPrincipal UsuarioLogado u) { return equipe.desativar(id, u); }

    @PostMapping("/equipe/{id}/reativar")
    public EquipeDtos.Pessoa reativar(@PathVariable Long id) { return equipe.reativar(id); }

    @PostMapping("/equipe/{id}/transferir")
    public Map<String, Integer> transferir(@PathVariable Long id, @RequestBody EquipeDtos.Transferencia req, @AuthenticationPrincipal UsuarioLogado u) {
        return equipe.transferir(id, req, u);
    }

    @PostMapping("/equipe/{id}/redefinir-senha")
    public EquipeDtos.SenhaTemporaria redefinirSenha(@PathVariable Long id, @AuthenticationPrincipal UsuarioLogado u) {
        return equipe.redefinirSenha(id, u);
    }

    @GetMapping("/acesso/solicitacoes")
    public List<EquipeDtos.Solicitacao> solicitacoes() { return acesso.pendentes(); }

    @PostMapping("/acesso/solicitacoes/{id}/aprovar")
    public EquipeDtos.SenhaTemporaria aprovar(@PathVariable Long id, @RequestBody EquipeDtos.Aprovacao req, @AuthenticationPrincipal UsuarioLogado u) {
        return acesso.aprovar(id, req, u);
    }

    @PostMapping("/acesso/solicitacoes/{id}/recusar")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void recusar(@PathVariable Long id, @AuthenticationPrincipal UsuarioLogado u) { acesso.recusar(id, u); }
}
