package br.jus.tjrs.ditic.mudancas.dto;

import java.util.List;

/** Equipe, contas e solicitações de acesso. */
public final class EquipeDtos {

    private EquipeDtos() { }

    /** acesso: "aguardando" (primeiro acesso), "ativo" ou "desativado". */
    public record Pessoa(String id, String login, String nome, String curto, String ini, String cor, String perfil,
                         boolean ativo, String acesso, String ultimoAcesso) { }

    public record NovaPessoa(String nome, String login, String perfil, String cor) { }

    public record Edicao(String nome, String cor) { }

    /** para: id do técnico ou "coordenador". Com desativar, as demandas desmarcadas vão para o Coordenador. */
    public record Transferencia(String para, List<Long> demandas, boolean desativar) { }

    /** A senha temporária aparece uma única vez, para o coordenador entregar à pessoa. */
    public record SenhaTemporaria(Pessoa pessoa, String senha, String expiraEm) { }

    public record Solicitacao(Long id, String nome, String login, String pedidaEm) { }

    public record PedidoAcesso(String nome, String login) { }

    public record Aprovacao(String perfil, String cor) { }

    public record Login(String usuario, String senha) { }

    public record TrocaSenha(String atual, String nova) { }

    public record Sessao(String id, String login, String nome, String perfil, boolean deveTrocarSenha) { }
}
