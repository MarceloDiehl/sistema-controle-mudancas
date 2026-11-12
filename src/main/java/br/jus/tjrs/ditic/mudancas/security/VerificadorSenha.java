package br.jus.tjrs.ditic.mudancas.security;

import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

import java.security.SecureRandom;

/**
 * Único ponto que confere e grava senhas (BCrypt). Se a autenticação passar a ser pelo AD/LDAP do TJRS,
 * muda só esta classe.
 */
@Component
public class VerificadorSenha {

    /** Sem letras e números parecidos (0/O, 1/l/I), para ditar a senha temporária sem engano. */
    private static final String ALFABETO = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    private static final int TAMANHO_TEMPORARIA = 10;

    private final BCryptPasswordEncoder bcrypt = new BCryptPasswordEncoder();
    private final SecureRandom aleatorio = new SecureRandom();
    /** Usado quando o usuário não existe, para a resposta levar o mesmo tempo. */
    private final String hashFalso = bcrypt.encode("senha-que-nao-existe");

    public boolean confere(Pessoa p, String senha) {
        if (senha == null) return false;
        if (p == null || p.getSenhaHash() == null) {
            bcrypt.matches(senha, hashFalso);
            return false;
        }
        return bcrypt.matches(senha, p.getSenhaHash());
    }

    public String codificar(String senha) { return bcrypt.encode(senha); }

    public String gerarTemporaria() {
        StringBuilder s = new StringBuilder(TAMANHO_TEMPORARIA);
        for (int i = 0; i < TAMANHO_TEMPORARIA; i++) s.append(ALFABETO.charAt(aleatorio.nextInt(ALFABETO.length())));
        return s.toString();
    }
}
