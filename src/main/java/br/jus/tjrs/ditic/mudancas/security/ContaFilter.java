package br.jus.tjrs.ditic.mudancas.security;

import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Set;

/**
 * A cada pedido com sessão, confere a conta no banco: desativada ou com a senha redefinida, a sessão cai.
 * Enquanto a pessoa não cria a senha pessoal (primeiro acesso ou senha temporária), só a troca de senha é aceita.
 */
public class ContaFilter extends OncePerRequestFilter {

    private static final Set<String> LIBERADOS_SEM_SENHA = Set.of("/api/sessao", "/api/conta/senha", "/api/logout");

    private final PessoaRepository pessoas;

    public ContaFilter(PessoaRepository pessoas) {
        this.pessoas = pessoas;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith(request.getContextPath() + "/api/");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) throws ServletException, IOException {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof UsuarioLogado u) {
            Pessoa p = pessoas.findById(u.id()).orElse(null);
            if (p == null || !p.isAtivo() || p.getSenhaHash() == null || !p.getSenhaHash().equals(u.credencial())) {
                SecurityContextHolder.clearContext();
                HttpSession s = req.getSession(false);
                if (s != null) s.invalidate();
                RespostaJson.enviar(res, HttpServletResponse.SC_UNAUTHORIZED, "A sessão foi encerrada. Entre de novo.");
                return;
            }
            String caminho = req.getRequestURI().substring(req.getContextPath().length());
            if (p.isDeveTrocarSenha() && !LIBERADOS_SEM_SENHA.contains(caminho)) {
                RespostaJson.enviar(res, HttpServletResponse.SC_FORBIDDEN, "Crie a nova senha para continuar.");
                return;
            }
        }
        chain.doFilter(req, res);
    }
}
