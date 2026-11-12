package br.jus.tjrs.ditic.mudancas.controller;

import br.jus.tjrs.ditic.mudancas.dto.EquipeDtos;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.service.AcessoService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** Entrar, conferir a sessão, criar a senha pessoal e pedir acesso. A saída é o /api/logout do SecurityConfig. */
@RestController
@RequestMapping("/api")
public class SessaoController {

    private final AcessoService acesso;
    private final SecurityContextRepository repositorio;

    public SessaoController(AcessoService acesso, SecurityContextRepository repositorio) {
        this.acesso = acesso;
        this.repositorio = repositorio;
    }

    /** Quem está na sessão (401 sem login). Também entrega o cookie do CSRF para a tela. */
    @GetMapping("/sessao")
    public ResponseEntity<?> sessao(@AuthenticationPrincipal UsuarioLogado u) {
        if (u == null) return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("mensagem", "Entre com o seu usuário para continuar."));
        return ResponseEntity.ok(dto(u));
    }

    @PostMapping("/login")
    public EquipeDtos.Sessao entrar(@RequestBody EquipeDtos.Login req, HttpServletRequest request, HttpServletResponse response) {
        UsuarioLogado u = acesso.entrar(req);
        // sessão nova a cada entrada (evita fixação de sessão)
        HttpSession antiga = request.getSession(false);
        if (antiga != null) antiga.invalidate();
        request.getSession(true);
        guardar(u, request, response);
        return dto(u);
    }

    @PostMapping("/conta/senha")
    public EquipeDtos.Sessao trocarSenha(@RequestBody EquipeDtos.TrocaSenha req, @AuthenticationPrincipal UsuarioLogado u,
                                         HttpServletRequest request, HttpServletResponse response) {
        UsuarioLogado novo = acesso.trocarSenha(u, req);
        guardar(novo, request, response);
        return dto(novo);
    }

    @PostMapping("/acesso/solicitar")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void solicitar(@RequestBody EquipeDtos.PedidoAcesso req) { acesso.solicitar(req); }

    private void guardar(UsuarioLogado u, HttpServletRequest request, HttpServletResponse response) {
        SecurityContext ctx = SecurityContextHolder.createEmptyContext();
        ctx.setAuthentication(u.autenticacao());
        SecurityContextHolder.setContext(ctx);
        repositorio.saveContext(ctx, request, response);
    }

    private static EquipeDtos.Sessao dto(UsuarioLogado u) {
        return new EquipeDtos.Sessao(String.valueOf(u.id()), u.login(), u.nome(), u.perfil().name(), u.deveTrocarSenha());
    }
}
