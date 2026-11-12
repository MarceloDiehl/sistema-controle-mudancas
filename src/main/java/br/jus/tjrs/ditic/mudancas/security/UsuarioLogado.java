package br.jus.tjrs.ditic.mudancas.security;

import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import java.io.Serializable;
import java.util.List;

/**
 * Quem está na sessão. {@code credencial} é o hash da senha no momento do login: se a senha for redefinida,
 * deixa de bater com o banco e a sessão cai (ContaFilter).
 */
public record UsuarioLogado(Long id, String login, String nome, Perfil perfil, String credencial, boolean deveTrocarSenha)
        implements Serializable {

    public static UsuarioLogado de(Pessoa p) {
        return new UsuarioLogado(p.getId(), p.getLogin(), p.getNome(), p.getPerfil(), p.getSenhaHash(), p.isDeveTrocarSenha());
    }

    public boolean coordenador() { return perfil == Perfil.COORDENADOR; }

    public Authentication autenticacao() {
        return UsernamePasswordAuthenticationToken.authenticated(this, null, List.of(new SimpleGrantedAuthority("ROLE_" + perfil.name())));
    }
}
